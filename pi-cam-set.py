#!/usr/bin/python3
# -*- coding: utf-8 -*-

#
# Author: Krzysztof Markiewicz
# 2019, www.obbo.pl
# v.0.1 20191214
#
# This program is distributed under the terms of the GNU General Public License v3.0
#

import socket
import select
import sys


if len(sys.argv) == 2:
    message_to_send = sys.argv[-1]
else:
    print('usage: {} <PiCamera command>'.format(sys.argv[0]))
    exit(1)
       
bytes_to_send = str.encode(message_to_send)
server_address = ('127.0.0.1', 1301)
buffer_size = 1024
timeout = 5

udp_client = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
udp_client.setblocking(0)
udp_client.sendto(bytes_to_send, server_address)

ready = select.select([udp_client], [], [], timeout)
if ready[0]:
    server_response = udp_client.recvfrom(buffer_size)
    message = server_response[0].decode()
    print(message)
    if message == 'OK':
        exit(0)
    else:
        exit(1)
print('Timeout')
exit(1)


