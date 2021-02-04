import subprocess
import requests
from pathlib import Path
import sys
import os
import json
import datetime


BASE_DIR = Path(__file__).resolve().parent
VIDEOS_DIR = os.path.join(BASE_DIR, 'videos')
FRAME_SYNCED_MS = 500


def create_dir():
    try:
        os.mkdir(VIDEOS_DIR)
    except Exception as e:
        pass


class FreezeFrameValidator:
    def __init__(self, videos):
        self.videos = videos
        self.videoName = []
        self.freezeDetect = {}
        self.results = {"videos": []}
        create_dir()
        self.download()
        for video_name in self.videoName:
            self.data_inverter(self.freeze_detect(video_name))
        self.results['all_videos_freeze_frame_synced'] = self.get_all_videos_freeze_frame_synced()
        self.create_json()

    def download(self):
        # Download and write the videos.
        for i in range(len(self.videos)):
            self.videoName.append(self.videos[i].split('/')[-1])
            video_bin = requests.get(self.videos[i])
            file_path = os.path.join(VIDEOS_DIR, self.videoName[i])
            if not os.path.isfile(file_path):
                with open(file_path, 'wb') as f:
                    for chunk in video_bin.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)

    def freeze_detect(self, video_name):
        video_dir = os.path.join(VIDEOS_DIR, video_name)
        cmd = "ffmpeg -i {} -vf \"freezedetect=n=0.003\" -map 0:v:0 -f null -" \
            .format(video_dir, VIDEOS_DIR)
        output = subprocess.run(cmd, capture_output=True, shell=True, text=True).stderr
        freeze = []
        output = output[output.find('[freezedetect'):]
        for line in output.split('\n'):
            if line.find('[freezedetect') != -1:
                freeze.append(line)
            elif line.find('frame=') != -1:
                freeze.append(line)


        return self.data_formatter(freeze)

    def data_formatter(self, freezeDetect):

        start_duration_end = ['freeze_start', 'freeze_duration', 'freeze_end']
        data = []
        for freeze_frame in freezeDetect:
            for sde in start_duration_end:
                if freeze_frame.find('lavfi.freezedetect.{}:'.format(sde)) != -1:
                    data.append({sde: freeze_frame.split(' ')[-1]})
        last_freeze_detect = freezeDetect[-1]
        if last_freeze_detect.find('time=') != -1:
            time = last_freeze_detect[last_freeze_detect.find('time=')+5:].split(' ')[0]
            t = (datetime.datetime.strptime(time, '%H:%M:%S.%f') - datetime.datetime(1900, 1, 1)).total_seconds()
            data.append({'freeze_start': t})
        return data

    def data_inverter(self, data):
        valid_periods = self.get_valid_periods(data)
        longest_valid_period = self.get_longest_valid_period(valid_periods)
        valid_video_percentage = self.get_valid_video_percentage(valid_periods)
        self.results['videos'].append({'longest_valid_period': longest_valid_period,
                                       'valid_video_percentage': valid_video_percentage,
                                       'valid_periods': valid_periods})



    def get_valid_periods(self, data):
        valid_periods = []
        valid_periods.append([float('0.00'), float(data[0].get('freeze_start'))])
        data_len = len(data[1:-1])
        for i in range(1, data_len):
            freeze_duration = data[i].get('freeze_duration')
            if freeze_duration:
                freeze_end = float(data[i + 1].get('freeze_end'))
                freeze_start = float(data[i + 2].get('freeze_start'))
                valid_periods.append([freeze_end, freeze_start])

        return valid_periods

    def get_longest_valid_period(self, valid_periods):
        longest_valid_period = 0
        for i in range(len(valid_periods)):
            freeze_end = valid_periods[i][0]
            freeze_start = valid_periods[i][1]
            valid_period = freeze_start - freeze_end
            if longest_valid_period < valid_period:
                longest_valid_period = valid_period
        return longest_valid_period

    def get_valid_video_percentage(self, valid_periods):
        valid_video_percentage = 0
        for i in range(len(valid_periods)):
            freeze_end = valid_periods[i][0]
            freeze_start = valid_periods[i][1]
            valid_video_percentage += freeze_start - freeze_end
        return valid_video_percentage/valid_periods[-1][1]

    def get_all_videos_freeze_frame_synced(self):
        all_videos_freeze_frame_synced = False
        videos = self.results.get('videos')
        valid_periods_set = set(map(len, [video.get('valid_periods') for video in videos]))
        valid_periods_len = len(valid_periods_set)

        if valid_periods_len == 1:
            for j in range(list(valid_periods_set)[0]):
                freeze_end_ms = []
                freeze_start_ms = []
                for i in range(len(videos)):
                    freeze_end_ms.append(videos[i].get('valid_periods')[j][0])
                    freeze_start_ms.append(videos[i].get('valid_periods')[j][1])
                if (max(freeze_end_ms) - min(freeze_end_ms))*1000 < FRAME_SYNCED_MS and (max(freeze_start_ms) - min(freeze_start_ms))*1000 < FRAME_SYNCED_MS:
                    all_videos_freeze_frame_synced = True
                else:
                    return False
            return all_videos_freeze_frame_synced

        else:
            return all_videos_freeze_frame_synced

    def create_json(self):
        with open('result.json', 'w') as fp:
            json.dump(self.results, fp)

if __name__ == '__main__':
    urls = sys.argv[1:]
    FreezeFrameValidator(urls)