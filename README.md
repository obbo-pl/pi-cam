# Pi-Cam
Simple UDP server for remote control of Raspberry PiCamera

The main goal was to create a simple service to control the Raspberry PiCamera from another service running on the same host.
After a small change (e.g. local_ip = '0.0.0.0') you can also control PiCamera from a remote host. By default, it works on UDP port 1301. The Pi-Cam UDP server is simple and has not been secured, so do not expose it to the Internet or other untrusted network!

##### Supports the basic set of commands:
- start_preview,
- stop_preview,
- resolution,
- annotate_text_size,
- annotate_text,
- annotate_background,
- annotate_foreground,
- brightness,
- rotation,
- framerate,
- contrast,
- iso,
- capture,
- start_recording,
- stop_recording,
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

### Client:
pi-cam-set.py is an example of a client working with a Pi-Cam UDP server. To send a command to PiCamera, use:
```
./pi-cam-set.py <command>
(e.g. ./pi-cam-set.py 'annotate_text_size = 80')
```
