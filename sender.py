#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Easy PS4 Exploit Hosting by Al-Azif
   Source: https://github.com/Al-Azif/ps4-exploit-host
"""

from __future__ import print_function

import argparse
import os
import re
import socket
import time

SCRIPT_LOC = os.path.realpath(__file__)
CWD = os.path.dirname(SCRIPT_LOC)


def netcat(hostname, port, content):
    """Python netcat implementation"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    timeout = time.time() + 60
    while True:
        result = s.connect_ex((hostname, port))
        if result == 0:
            print('>> Connected to PS4')
            timed_out = False
            break
        if time.time() >= timeout:
            print('>> Netcat service timed out')
            timed_out = True
            break
    if not timed_out:
        s.sendall(content)
        s.shutdown(socket.SHUT_WR)
        while 1:
            data = s.recv(1024)
            if not data:
                break
        print('>> Payload Sent!')
    s.close()


def main():
    """The main method"""
    parser = argparse.ArgumentParser(description='PS4 Payload Sender')
    parser.add_argument('--ip', action='store',
                        default='', required=False,
                        help='The IP of the PS4')
    parser.add_argument('--payload', action='store',
                        default='', required=False,
                        help='The location of the payload')
    args = parser.parse_args()

    if not args.ip and not args.payload:
        payloads = []
        for files in os.listdir(os.path.join(CWD, 'payloads')):
            if not files.endswith('PUT PAYLOADS HERE'):
                payloads.append(files)
        if not payloads:
            print('>> No payloads found')
        else:
            i = 1
            choice = 0
            ip = '0.0.0.0'
            print('{} Payloads {}'.format('-' * 4, '-' * 46))
            for payload in payloads:
                print('{}. {}'.format(i, payload))
                i += 1
            print('-'*60)
            while choice < 1 or choice >= i:
                choice = raw_input('Choose a payload to send: ')
                try:
                    choice = int(choice)
                except (ValueError, NameError):
                    choice = 0
            with open(os.path.join(CWD, 'payloads', payloads[choice-1]), 'rb') as f:
                print('>> Sending {}...'.format(payloads[choice-1]))
                content = f.read()
            while ip == '0.0.0.0':
                ip = raw_input('Enter your PS4\'s IP Address: ')
                if not re.match('^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$', ip):
                    ip = '0.0.0.0'
            netcat(ip, 9020, content)
    elif args.ip and args.payload:
        try:
            print('>> Sending "{}" to {}'.format(args.payload, args.ip))
            with open(os.path.join(args.payload), 'rb') as f:
                content = f.read()
                netcat(args.ip, 9020, content)
        except IOError:
            print('>> Could not find payload located at "{}"'.format(args.payload))
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
