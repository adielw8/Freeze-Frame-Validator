# Freeze-Frame-Validator


the code downloads a set of video files from a given set of URLs, runs a filter on each one, and exposes its output into a useful format for consumption by other APIs

### Installation
Download and install [FFmpeg CLI](https://ffmpeg.org). 

```sh
$ git clone https://github.com/adielw8/Freeze-Frame-Validator.git
$ cd Freeze-Frame-Validator
$ pip install virtualenv
$ source  venv/bin/activate
$ pip install -r requirements.txt
```
## Usage

```sh
$ cd  'Freeze-Frame-Validator'
```
- Make sure virtualenv is activated

```sh
$ source  venv/bin/activate
```

```sh
$ python ffv.py "<video1>" "<video2>" .... "<video{n}>"
```
- See the result.json output. 

#### Demo 
```sh
$ python ffv.py https://storage.googleapis.com/hiring_process_data/freeze_frame_input_b.mp4 https://storage.googleapis.com/hiring_process_data/freeze_frame_input_c.mp4 https://storage.googleapis.com/hiring_process_data/freeze_frame_input_a.mp4

```
