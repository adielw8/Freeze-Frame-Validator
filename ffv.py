import subprocess
import requests
from pathlib import Path
import os
import json


BASE_DIR = Path(__file__).resolve().parent
VIDEOS_DIR = os.path.join(BASE_DIR, 'videos')


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
        self.results = {"all_videos_freeze_frame_synced": False, "videos": []}
        create_dir()
        self.download()
        for video_name in self.videoName:
            self.data_inverter(self.freeze_detect(video_name))


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
        for line in output.split('\n'):
            if line.find('[freezedetect') != -1:
                freeze.append(line)
        return self.data_formatter(freeze)

    def data_formatter(self, freezeDetect):
        start_duration_end = ['freeze_start', 'freeze_duration', 'freeze_end']
        data = []
        for freeze_frame in freezeDetect:
            for sde in start_duration_end:
                if freeze_frame.find('lavfi.freezedetect.{}:'.format(sde)) != -1:
                    data.append({sde : freeze_frame.split(' ')[-1]})
        return data

    def data_inverter(self, data):
        valid_periods = self.get_valid_periods(data)
        longest_valid_period = self.get_longest_valid_period(valid_periods)
        self.results['videos'].append({'longest_valid_period': longest_valid_period, 'valid_periods': valid_periods})

        with open('result.json', 'w') as fp:
            json.dump(self.results, fp)


    def get_valid_periods(self, data):
        valid_periods = []
        valid_periods.append([float('0.00'), float(data[0].get('freeze_start'))])
        for i in range(1, len(data[1:-1])):
            freeze_duration = data[i].get('freeze_duration')
            if freeze_duration:
                freeze_end = float(data[i + 1].get('freeze_end'))
                freeze_start = float(data[i + 2].get('freeze_start'))
                valid_periods.append([freeze_end, freeze_start])
        # if data[-1].get('freeze_end'):
        #     valid_periods.append([float(data[0].get('freeze_end')), ])
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



if __name__ == '__main__':
    urls = ['https://storage.googleapis.com/hiring_process_data/freeze_frame_input_c.mp4',
            'https://storage.googleapis.com/hiring_process_data/freeze_frame_input_a.mp4',
            'https://storage.googleapis.com/hiring_process_data/freeze_frame_input_b.mp4']

    FreezeFrameValidator(urls)
