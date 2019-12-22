#!/usr/bin/python3
# -*- coding: utf-8 -*-

#
# Author: Krzysztof Markiewicz
# 2019, www.obbo.pl
# v.0.1 20191214
#
# This program is distributed under the terms of the GNU General Public License v3.0
#
# https://projects.raspberrypi.org/en/projects/getting-started-with-picamera/5
# https://picamera.readthedocs.io/en/release-1.13/

from picamera import PiCamera, Color
import logging
import logging.config
import datetime
import socket
import select
import signal
import re

logger = logging.getLogger('pi-cam')
logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'console': {
            'format': '%(asctime)s pi-cam.py[%(process)d]: [%(levelname)s]%(name)s: %(message)s'
        },
        'syslog': {
            'format': 'pi-cam.py[%(process)d]: [%(levelname)s]%(name)s: %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class':'logging.StreamHandler',
            'level':'DEBUG',
            'formatter': 'console',
            'stream': 'ext://sys.stdout'
        },
        'syslog': {
            'class': 'logging.handlers.SysLogHandler',
            'level': 'DEBUG',
            'formatter': 'syslog',
            'address': '/dev/log',
        },
    },
    'loggers': {
        'pi-cam': {
            'handlers': ['console', 'syslog'],
            'level': 'INFO',
            'propagate': True
        }
   }
})

def main():
    logger.info('Pi-Cam daemon starting...')
    timeout = 1
    local_ip = '127.0.0.1'
    local_port = 1301
    buffer_size = 1024

    daemon_killer = GracefulKillDaemon()
    udp_server = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    udp_server.bind((local_ip, local_port))
    udp_server.setblocking(0)
    logger.info('UDP server up and listening on {}:{}'.format(local_ip, local_port))

    supported_commands = ['start_preview\([\s]*\)', \
        'stop_preview\([\s]*\)', \
        'resolution[\s]*=[\s]*\(\d{,4}[\s]*\,[\s]*\d{,4}\)', \
        'annotate_text_size[\s]*=[\s]*\d{,3}', \
        'annotate_text[\s]*=[\s]*\"[\w\s\%\.\-:;!@#$%&*()+=<>/]*\"', \
        'brightness[\s]*=[\s]*\d{,3}', \
        'rotation[\s]*=[\s]*\d{,3}', \
        'framerate[\s]*=[\s]*\d{,3}', \
        'contrast[\s]*=[\s]*\d{,3}', \
        'iso[\s]*=[\s]*\d{,3}', \
        'capture\([\s]*\"[\w\%/\-\.]*\"[\s]*\)', \
        'start_recording\([\s]*\"[\w\%/\-\.]*\"[\s]*\)', \
        'stop_recording\([\s]*\)', \
        'annotate_background[\s]*=[\s]*Color\([\s]*\"[a-z]*\"[\s]*\)', \
        'annotate_background[\s]*=[\s]*None', \
        'annotate_foreground[\s]*=[\s]*Color\([\s]*\"[a-z]*\"[\s]*\)', \
        'image_effect[\s]*=[\s]*\"[\w]*\"[\s]*', \
        # image_effect: none, negative, solarize, sketch, denoise, emboss, oilpaint, hatch, gpen, pastel, watercolor, film
        # blur, saturation, colorswap, washedout, posterise, colorpoint, colorbalance, cartoon, deinterlace1, deinterlace2
        'exposure_mode[\s]*=[\s]*\"[a-z]*\"[\s]*', \
        # exposure_mode: off, auto, night, nightpreview, backlight, spotlight, sports, snow, beach, verylong, fixedfps, antishake, fireworks
        'awb_mode[\s]*=[\s]*\"[a-z]*\"[\s]*', \
        # awb_mode: off, auto, sunlight, cloudy, shade, tungsten, fluorescent, incandescent, flash, horizon
        ]   
    #text_to_annotate = ' %H:%M:%S on %Y %B %d '
    text_to_annotate = ''
    recording = False

    with PiCamera() as camera:
        # default settings
        camera.rotation = 180
        camera.framerate = 20
        camera.resolution = (2592, 1440)
        camera.start_preview()
        camera.annotate_text_size = 40
        camera.annotate_background = Color('black')
        camera.annotate_foreground = Color('white')

        while not(daemon_killer.kill_now):
            camera.annotate_text = datetime.datetime.now().strftime(text_to_annotate)
            ready = select.select([udp_server], [], [], timeout)
            if ready[0]:
                server_response = 'OK'
                received = udp_server.recvfrom(buffer_size)
                message = received[0].decode().strip()
                address = received[1]
                logger.info('Message from Client {}: "{}"'.format(address, message))
                match = False
                for expression in supported_commands:               
                    if re.match(expression, message):
                        match = True
                        if message.startswith('annotate_text'):
                            message = message[message.index('=') + 1:].strip()
                            text_to_annotate = message.replace('"', '')
                            break
                        if message.startswith('stop_recording'):
                            if not(recording):
                                server_response = 'There is no recording in progress'
                                break
                        elif message.startswith('capture'):
                            message = message[message.index('(') + 1:].strip()
                            message = message.strip(')').strip()
                            message = ''.join(['capture(datetime.datetime.now().strftime(', message, '))'])
                        elif message.startswith('start_recording'):
                            message = message[message.index("(") + 1:].strip()
                            message = message.strip(')').strip()
                            message = message.strip('"').strip()
                            if (message.find('.h264') != (len(message) - 5)) and (message.find('.mjpeg') != (len(message) - 6)):
                                message = ''.join([message, '.h264'])
                            message = ''.join(['start_recording(datetime.datetime.now().strftime("', message, '"))'])
                        try:
                            exec(''.join(['camera.', message]))
                        except (ValueError, TypeError) as e:
                            server_response = '{}'.format(e)
                            logger.warning(server_response)
                        else:
                            if message.startswith('start_recording'):
                                recording = True
                        break
                if not(match):
                    server_response = 'Unsupported command'
                bytes_to_send = str.encode(server_response)    
                udp_server.sendto(bytes_to_send, address)
        camera.stop_preview()
    logger.info('Bye!')

class GracefulKillDaemon(object):
    # https://www.raspberrypi.org/forums/viewtopic.php?t=149939
    def __init__(self):
        self.kill_now = False
        self.kill_reason = []
        signal.signal(signal.SIGCONT, self.exit_gracefully) # 18 daemon restart
        signal.signal(signal.SIGINT, self.exit_gracefully)  #  2 Ctrl+C
        signal.signal(signal.SIGTERM, self.exit_gracefully) # 15 daemon restart, shutdown -r 
        signal.signal(signal.SIGUSR1, self.exit_gracefully) # 10
        signal.signal(signal.SIGUSR2, self.exit_gracefully) # 12

    def exit_gracefully(self, signum, frame):
        self.kill_now = True
        self.kill_reason.append(signum)

        
        
if __name__ == '__main__':
    main()