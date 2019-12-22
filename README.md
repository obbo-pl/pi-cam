# pi-cam
Simple UDP server for remote control of Raspberry PiCamera

##### Supports the basic set of commands:
- start_preview,
- stop_preview,
- resolution,
- annotate_text_size,
- annotate_text,
- brightness,
- rotation,
- framerate,
- contrast,
- iso,
- capture,
- start_recording,
- stop_recording,
- annotate_background,
- annotate_foreground,
- image_effect,
- exposure_mode,
- awb_mode.

### Installation:

Create a directory:
```
sudo mkdir /usr/local/pi-cam 
```
put all files in directory

add execute permission to *.py files
```
sudo chmod +x *.py
```

go to the directory and just run:
```
cd /usr/local/pi-cam
sudo ./pi-cam.py
```
or install as a service:
```
cd /etc/systemd/system/ 
sudo ln -s /usr/local/pi-cam/pi-cam.service pi-cam.service
sudo systemctl daemon-reload
sudo systemctl enable pi-cam.service
sudo systemctl start pi-cam.service
```
