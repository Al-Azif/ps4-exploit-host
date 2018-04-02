#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import print_function

try:
    import argparse
    from distutils.version import StrictVersion
    from http.server import BaseHTTPRequestHandler
    from http.server import HTTPServer
    import ipaddress
    import json
    import mimetypes
    import os
    import re
    import socket
    from socketserver import ThreadingMixIn
    import sys
    import threading
    import time
    from urllib.parse import unquote
    import urllib.request

    import fakedns.fakedns as FAKEDNS
except ImportError:
    if sys.version_info.major < 3:
        print('ERROR: This must be run on Python 3')
        try:
            input('Press [ENTER] to exit')
        finally:
            sys.exit()
    else:
        print('ERROR: Import Error')
        print('Download from the releases page or clone with `--recursive`')
        try:
            input('Press [ENTER] to exit')
        finally:
            sys.exit()

VERSION = '0.4.2'
API_URL = 'https://api.github.com/repos/Al-Azif/ps4-exploit-host/releases/latest'
SCRIPT_LOC = os.path.realpath(__file__)
CWD = os.path.dirname(SCRIPT_LOC)
EXPLOIT_LOC = os.path.join(CWD, 'exploits')
PAYLOAD_LOC = os.path.join(CWD, 'payloads')
UPDATE_LOC = os.path.join(CWD, 'updates')
THEME_LOC = os.path.join(CWD, 'themes')
SETTINGS = None
MENU_OPEN = False


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True
    allow_resuse_address = True
    request_queue_size = 16


class MyHandler(BaseHTTPRequestHandler):
    try:
        with open(os.path.join(THEME_LOC, 'error.html'), 'rb') as buf:
            error_message_format = buf.read().decode('utf-8')
    except (IOError, PermissionError):
        pass
    protocol_version = 'HTTP/1.1'

    def send_response(self, code, message=None):
        self.log_request(code)
        self.send_response_only(code, message)

    def my_sender(self, mime, content):
        try:
            self.send_response(200)
            self.send_header('Content-Type', mime)
            self.send_header('Content-Length', len(content))
            self.send_header('Connection', 'close')
            self.end_headers()
            self.wfile.write(content)
        except socket.error:
            print('ERROR: Broken Pipe (Out of Memory?)')

    def updatelist(self):
        region = self.path.split('/')[4]
        ps4_version = re.search(r'^Download\/1.00 libhttp\/(.+?) \(PlayStation 4\)$', self.headers['user-agent'])
        vita_version = re.search(r'^libhttp\/(.+?) \(PS Vita\)$', self.headers['user-agent'])

        try:
            if not ps4_version and not vita_version:
                self.send_error(404)
                return
            elif ps4_version:
                fw_version = float(ps4_version.group(1))
            elif vita_version:
                fw_version = float(vita_version.group(1))
        except ValueError:
            self.send_error(404)
            return

        if ps4_version and fw_version > SETTINGS['Update']['PS4_No_Update']:
            path = os.path.join(UPDATE_LOC, 'ps4-updatelist.xml')
        elif vita_version and fw_version > SETTINGS['Update']['Vita_No_Update']:
            path = os.path.join(UPDATE_LOC, 'psp2-updatelist.xml')
        else:
            self.send_error(404)
            return

        with open(path, 'rb') as buf:
            xml = buf.read()

        xml = xml.replace(b'{{REGION}}', bytes(region, 'utf-8'))

        self.my_sender('application/xml', xml)

    def updatefeature(self):
        path = os.path.join(THEME_LOC, SETTINGS['Theme'], 'ps4-updatefeature.html')
        with open(path, 'rb') as buf:
            data = buf.read()
        self.my_sender('text/html', data)

    def update_pup(self):
        if re.match(r'^\/update\/ps4\/image\/[0-9]{4}_[0-9]{4}\/sys\_[a-f0-9]{32}\/PS4UPDATE\.PUP', self.path):
            path = 'PS4UPDATE_SYSTEM.PUP'
        elif re.match(r'^\/update\/ps4\/image\/[0-9]{4}_[0-9]{4}\/rec\_[a-f0-9]{32}\/PS4UPDATE\.PUP', self.path):
            path = 'PS4UPDATE_RECOVERY.PUP'
        elif re.match(r'^\/update\/psp2\/image\/[0-9]{4}_[0-9]{4}\/rel\_[a-f0-9]{32}\/PSP2UPDAT\.PUP', self.path):
            path = 'PSP2UPDAT.PUP'
        else:
            path = ''
        path = os.path.join(UPDATE_LOC, path)
        with open(path, 'rb') as buf:
            data = buf.read()
        self.my_sender('text/plain', data)

    def network_test(self, size):
        data = b'\0' * size
        self.my_sender('text/plain', data)

    def exploit_matcher(self):
        with open(os.path.join(THEME_LOC, SETTINGS['Theme'], 'index.html'), 'rb') as buf:
            data = buf.read()
        data = self.inject_exploit_html(data)
        if SETTINGS['Auto_Exploit'] != '':
            refresh_string = '</title>\n<meta http-equiv="refresh" content="0;URL=\'/exploits/{}/index.html\'" />'.format(SETTINGS['Auto_Exploit'])
            data = data.replace(b'</title>', bytes(refresh_string, 'utf-8'))
        self.my_sender('text/html', data)

    def exploit(self):
        path = unquote(self.path.split('/', 2)[-1])
        if path[-1:] == '/':
            path += 'index.html'
        mime = mimetypes.guess_type(self.path.rsplit('/', 1)[-1])
        if mime[0]:
            mime = mime[0]
        else:
            mime = 'application/octet-stream'
        with open(os.path.join(EXPLOIT_LOC, path), 'rb') as buf:
            data = buf.read()
        self.my_sender(mime, data)

    def static_request(self):
        path = unquote(self.path.split('/', 2)[-1])
        if path[-1:] == '/':
            path += 'index.html'
        mime = mimetypes.guess_type(self.path.rsplit('/', 1)[-1])
        if mime[0]:
            mime = mime[0]
        else:
            mime = 'application/octet-stream'
        with open(os.path.join(THEME_LOC, path), 'rb') as buf:
            data = buf.read()
        self.my_sender(mime, data)

    def inject_exploit_html(self, html):
        try:
            firmwares = os.listdir(EXPLOIT_LOC)
            if 'PUT EXPLOITS HERE' in firmwares:
                firmwares.remove('PUT EXPLOITS HERE')
            for entry in firmwares:
                if os.path.isfile(os.path.join(EXPLOIT_LOC, entry)):
                    firmwares.remove(entry)
            firmwares.sort()
            if len(firmwares) == 0:
                data = json.dumps({'firmwares': ['No Exploits Found']})
                return html.replace(b'{{EXPLOITS}}', bytes(data, 'utf-8'))
            else:
                data = {'firmwares': firmwares}

            for firmware in firmwares:
                exploits = os.listdir(os.path.join(EXPLOIT_LOC, firmware))
                for entry in exploits:
                    if os.path.isfile(os.path.join(EXPLOIT_LOC, firmware, entry)):
                        exploits.remove(entry)
                exploits.sort()
                exploits.append('[Back]')
                data[firmware] = exploits

            try:
                data['Lang_Code'] = re.search(r'^\/document\/(.+?)\/ps4\/index\.html', self.path).group(1)
            except AttributeError:
                pass

            data['Host_Version'] = VERSION

            data = bytes(json.dumps(data), 'utf-8')
        except (IOError, PermissionError):
            data = json.dumps({'firmwares': ['I/O Error on Host']})
            return html.replace(b'{{EXPLOITS}}', bytes(data, 'utf-8'))

        return html.replace(b'{{EXPLOITS}}', data)

    def check_ua(self):
        if self.headers['User-Agent'] in SETTINGS['Valid_UA']:
            return True
        else:
            return False

    def do_GET(self):
        try:
            if re.match(r'^\/update\/(ps4|psp2)\/list\/[a-z]{2}\/(ps4|psp2)\-updatelist\.xml', self.path):
                self.updatelist()
            elif re.match(r'^\/update\/ps4\/html\/[a-z]{2}\/[a-z]{2}\/ps4\-updatefeature\.html', self.path):
                self.updatefeature()
            elif re.match(r'^\/update\/(ps4|psp2)\/image\/[0-9]{4}_[0-9]{4}\/(sys|rec|rel)\_[a-f0-9]{32}\/(PS4UPDATE\.PUP|PSP2UPDAT\.PUP)', self.path):
                self.update_pup()
            elif re.match(r'^\/networktest\/get\_2m', self.path):
                self.network_test(2097152)
            elif re.match(r'^\/networktest\/get\_6m', self.path):
                self.network_test(6291456)
            elif re.match(r'^\/$', self.path) or re.match(r'^\/index\.html', self.path) or re.match(r'^\/document\/[a-zA-Z\-]{2,5}\/ps4\/', self.path) or re.match(r'^\/document\/[a-zA-Z\-]{2,5}\/psvita\/', self.path):
                if not SETTINGS['UA_Check'] or self.check_ua():
                    self.exploit_matcher()
                else:
                    self.send_error(400, explain='This PS4 is not on a supported firmware')
                    if not MENU_OPEN:
                        print('>> Unsupported PS4 attempted to access exploits')
            elif re.match(r'^\/exploits\/.*\/', self.path):
                if not SETTINGS['UA_Check'] or self.check_ua():
                    self.exploit()
                else:
                    self.send_error(400, explain='This PS4 is not on a supported firmware')
                    if not MENU_OPEN:
                        print('>> Unsupported PS4 attempted to access exploits')
            elif re.match(r'^\/success$', self.path):
                self.my_sender('text/plain', b'')
                if not MENU_OPEN:
                    payload_brain(self.client_address[0])
            elif re.match(r'^\/themes\/', self.path):
                self.static_request()
            else:
                self.send_error(404)
        except (IOError, PermissionError):
            self.send_error(404)

    def do_POST(self):
        if re.match(r'^\/networktest\/post\_128', self.path):
            self.send_response(200)
            self.end_headers()

    def log_message(self, format, *args):
        if SETTINGS['Debug']:
            sys.stderr.write("%s - - [%s] %s\n" % (self.address_string(), self.log_date_time_string(), format % args))


def check_root():
    root = True
    try:
        if SETTINGS['Root_Check']:
            root = bool(os.getuid() == 0)
    except AttributeError:
        pass

    return root


def get_lan():
    soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        soc.connect(('10.255.255.255', 1))
        lan = str(soc.getsockname()[0])
        soc.close()
    except socket.error:
        soc.close()
        closer('ERROR: Unable to find LAN IP')

    return lan


def print_line():
    print('##########################################################')


def center_menu_item(entry):
    num = int((56 - len(entry)) / 2)
    entry = '#' + (' ' * num) + entry + (' ' * num) + '#'
    if len(entry) < 58:
        entry = entry[:-1] + ' #'

    return entry


def payload_menu_item(number, entry):
    entry = '#  {}. {}'.format(number, entry)

    if len(entry) > 58:
        entry = entry[:56]
    while len(entry) < 56:
        entry += ' '
    entry += ' #'

    return entry


def payload_menu(input_array):
    i = 1
    choice = 0
    print_line()
    print('#  Payload                                               #')
    print_line()
    for entry in input_array:
        print(payload_menu_item(i, entry))
        i += 1
    print_line()
    while choice < 1 or choice >= i:
        input_prompt = 'Choose a payload to send: '
        choice = input(input_prompt)
        try:
            choice = int(choice)
        except (ValueError, NameError):
            choice = 0

    return choice - 1


def menu_header():
    print_line()
    version_spacing = VERSION
    while len(version_spacing) < 29:
        version_spacing += ' '
    print('#  Exploit Host v{}by Al Azif #'.format(version_spacing))
    print_line()


def ip_display():
    if SETTINGS['HTTP'] and not SETTINGS['DNS']:
        server_type = 'HTTP'
    else:
        server_type = 'DNS'

    if SETTINGS['HTTP'] and SETTINGS['DNS']:
        server_string = 'Servers are running'
    else:
        server_string = 'Server is running'

    server_string = center_menu_item(server_string)

    ip_string = 'Your {} IP is {}'.format(server_type, SETTINGS['Interface_IP'])
    ip_string = center_menu_item(ip_string)

    port_string = 'HTTP server is running on port {}'.format(SETTINGS['HTTP_Port'])
    port_string = center_menu_item(port_string)

    print_line()
    print(server_string)
    print(ip_string)
    if SETTINGS['HTTP_Port'] != 80:
        print(port_string)
    print_line()


def getch():
    """MIT Licensed: https://github.com/joeyespo/py-getch"""
    import termios
    import tty

    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        return sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def closer(message):
    print(message)
    if message != '\r>> Exiting...                                           ':
        print('Press any key to exit...', end='')
        sys.stdout.flush()
        if os.name == 'nt':
            from msvcrt import getch as w_getch
            w_getch()
        else:
            getch()
        print()
    sys.exit()


def default_settings():
    global SETTINGS

    lan_ip = get_lan()

    SETTINGS = {
        "Interface_IP": lan_ip,
        "Debug": False,
        "DNS": True,
        "HTTP": True,
        "HTTP_Port": 80,
        "Root_Check": True,
        "Theme": "default",
        "Auto_Exploit": "",
        "Auto_Payload": "",
        "DNS_Rules": {
            "Redirect_IP": lan_ip,
            "Redirect": [
                "the.gate",
                "www.playstation.com",
                "manuals.playstation.net",
                "(get|post).net.playstation.net",
                "(d|f|h)[a-z]{2}01.(ps4|psp2).update.playstation.net",
                "update.playstation.net",
                "gs2.ww.prod.dl.playstation.net",
                "ctest.cdn.nintendo.net"
            ],
            "Block": [
                ".*.207.net",
                ".*.akadns.net",
                ".*.akamai.net",
                ".*.akamaiedge.net",
                ".*.cddbp.net",
                ".*.ea.com",
                ".*.edgekey.net",
                ".*.edgesuite.net",
                ".*.llnwd.net",
                ".*.playstation.(com|net|org)",
                ".*.ribob01.net",
                ".*.sbdnpd.com",
                ".*.scea.com",
                ".*.sonyentertainmentnetwork.com",
                "sun.hac.lp1.d4c.nintendo.net",
                "beach.hac.lp1.eshop.nintendo.net",
                "atum.hac.lp1.d4c.nintendo.net",
                "atumn.hac.lp1.d4c.nintendo.net",
                "aqua.hac.lp1.d4c.nintendo.net",
                "receive-lp1.(dg|er).srv.nintendo.net"
            ],
            "Pass_Through_IP": []
        },
        "UA_Check": True,
        "Valid_UA": [
            "Mozilla/5.0 (PlayStation 4 1.01) AppleWebKit/536.26 (KHTML, like Gecko)",
            "Mozilla/5.0 (PlayStation 4 1.76) AppleWebKit/536.26 (KHTML, like Gecko)",
            "Mozilla/5.0 (PlayStation 4 4.05) AppleWebKit/537.78 (KHTML, like Gecko)",
            "Mozilla/5.0 (PlayStation 4 5.05) AppleWebKit/537.78 (KHTML, like Gecko)",
            "Mozilla/5.0 (PlayStation 4 4.55) AppleWebKit/601.2 (KHTML, like Gecko)",
            "Mozilla/5.0 (PlayStation 4 5.06) AppleWebKit/601.2 (KHTML, like Gecko)",
            "Mozilla/5.0 (PlayStation Vita 3.60) AppleWebKit/537.73 (KHTML, like Gecko) Silk/3.2",
            "Mozilla/5.0 (PlayStation Vita 3.67) AppleWebKit/537.73 (KHTML, like Gecko) Silk/3.2",
            "Mozilla/5.0 (Nintendo Switch; WebApplet) AppleWebKit/601.6 (KHTML, like Gecko) NF/4.0.0.6.9 NintendoBrowser/5.1.0.14936"
        ],
        "Update": {
            "PS4_No_Update": 1.76,
            "Vita_No_Update": 3.60
        }
    }


def import_settings(settings_file):
    global SETTINGS

    try:
        with open(settings_file) as buf:
            imported = json.loads(buf.read())
    except (IOError, PermissionError):
        print('ERROR: Unable to read settings.json, using defaults')
        return
    except json.decoder.JSONDecodeError:
        print('ERROR: Malformed settings.json, using defaults')
        return

    if validate_setting(imported, 'Interface_IP', str):
        try:
            ipaddress.ip_address(imported['Interface_IP'])
            SETTINGS['Interface_IP'] = imported['Interface_IP']
        except ValueError:
            if imported['Interface_IP'] != '':
                print('WARNING: "Interface_IP" in settings is not a valid IP, using default')
    else:
        print('WARNING: "Interface_IP" in settings is invalid, using default')

    if validate_setting(imported, 'Debug', bool):
        SETTINGS['Debug'] = imported['Debug']
    else:
        print('WARNING: "Debug" in settings is invalid, using default')

    if validate_setting(imported, 'DNS', bool):
        SETTINGS['DNS'] = imported['DNS']
        if not SETTINGS['DNS']:
            print('WARNING: DNS is disabled, User\'s Manual method will not work')
    else:
        print('WARNING: "DNS" in settings is invalid, using default')

    if validate_setting(imported, 'HTTP', bool):
        SETTINGS['HTTP'] = imported['HTTP']
    else:
        print('WARNING: "HTTP" in settings is invalid, using default')

    if validate_setting(imported, 'HTTP_Port', int):
        SETTINGS['HTTP_Port'] = imported['HTTP_Port']
        if SETTINGS['HTTP_Port'] != 80:
            print('WARNING: HTTP is not port 80, User\'s Manual method will not work')
    else:
        print('WARNING: "HTTP_Port" in settings is invalid, using default')

    if validate_setting(imported, 'Root_Check', bool):
        SETTINGS['Root_Check'] = imported['Root_Check']
    else:
        print('WARNING: "Root_Check" in settings is invalid, using default')

    if validate_setting(imported, 'Theme', str) and \
       os.path.isfile(os.path.join(THEME_LOC, imported['Theme'], 'index.html')):
            SETTINGS['Theme'] = imported['Theme']
    elif os.path.isfile(os.path.join(THEME_LOC, 'default', 'index.html')):
        closer('ERROR: "Theme" in settings is invalid, and default is missing')
    else:
        print('WARNING: "Theme" in settings is invalid, using default')

    if (validate_setting(imported, 'Auto_Exploit', str) and
       os.path.isdir(os.path.join(EXPLOIT_LOC, imported['Auto_Exploit']))) or \
       imported['Auto_Exploit'] == '':
            if imported['Auto_Exploit'][:1] == '/' or imported['Auto_Exploit'][:1] == '\\':
                imported['Auto_Exploit'] = imported['Auto_Exploit'][1:]
            SETTINGS['Auto_Exploit'] = imported['Auto_Exploit']
    else:
        print('WARNING: "Auto_Exploit" in settings is invalid, using default')

    if (validate_setting(imported, 'Auto_Payload', str) and
       os.path.isfile(os.path.join(PAYLOAD_LOC, imported['Auto_Payload']))) or \
       imported['Auto_Payload'] == '':
            SETTINGS['Auto_Payload'] = imported['Auto_Payload']
    else:
        print('WARNING: "Auto_Payload" in settings is invalid, using default')

    if validate_setting(imported, 'DNS_Rules', dict):
        if validate_setting(imported['DNS_Rules'], 'Redirect_IP', str):
            try:
                ipaddress.ip_address(imported['DNS_Rules']['Redirect_IP'])
                SETTINGS['DNS_Rules']['Redirect_IP'] = imported['DNS_Rules']['Redirect_IP']
            except ValueError:
                if imported['DNS_Rules']['Redirect_IP'] != '':
                    print('WARNING: "DNS_Rules[\'Redirect_IP\']" in settings is not a valid IP, using default')

        if validate_setting(imported['DNS_Rules'], 'Redirect', list):
            i = 1
            temp_array = []
            for entry in imported['DNS_Rules']['Redirect']:
                if validate_setting(entry, '', str):
                    temp_array.append(entry)
                else:
                    print('WARNING: Invalid entry in "DNS_Rules[\'Redirect\']" settings, discarding rule # {}'.format(i))
                i += 1
            SETTINGS['DNS_Rules']['Redirect'] = imported['DNS_Rules']['Redirect']
        else:
            print('WARNING: "DNS_Rules[\'Redirect\']" in settings is invalid, using default')

        if validate_setting(imported['DNS_Rules'], 'Block', list):
            i = 1
            temp_array = []
            for entry in imported['DNS_Rules']['Block']:
                if validate_setting(entry, '', str):
                    temp_array.append(entry)
                else:
                    print('WARNING: Invalid entry in "DNS_Rules[\'Block\']" settings, discarding rule # {}'.format(i))
                i += 1
            SETTINGS['DNS_Rules']['Block'] = imported['DNS_Rules']['Block']
        else:
            print('WARNING: "DNS_Rules[\'Block\']" in settings is invalid, using default')

        if validate_setting(imported['DNS_Rules'], 'Pass_Through_IP', list):
            i = 1
            temp_array = []
            for entry in imported['DNS_Rules']['Pass_Through_IP']:
                if validate_setting(entry, '', str):
                    try:
                        if entry:
                            ipaddress.ip_address(entry)
                            temp_array.append(entry)
                    except ValueError:
                        print('WARNING: Invalid entry in "DNS_Rules[\'Pass_Through_IP\']" settings, discarding rule # {}'.format(i))
                else:
                    print('WARNING: Invalid entry in "DNS_Rules[\'Pass_Through_IP\']" settings, discarding rule # {}'.format(i))
                i += 1
            SETTINGS['DNS_Rules']['Pass_Through_IP'] = imported['DNS_Rules']['Pass_Through_IP']
        else:
            print('WARNING: "DNS_Rules[\'Pass_Through_IP\']" in settings is invalid, using default')
    else:
        print('WARNING: "DNS_Rules" in settings is invalid, using default')

    if validate_setting(imported, 'UA_Check', bool):
        SETTINGS['UA_Check'] = imported['UA_Check']
    else:
        print('WARNING: "UA_Check" in settings is invalid, using default')

    if validate_setting(imported, 'Valid_UA', list):
        i = 1
        temp_array = []
        for entry in imported['Valid_UA']:
            if validate_setting(entry, '', str):
                temp_array.append(entry)
            else:
                print('WARNING: Invalid entry in "Valid_UA" settings, discarding rule # {}'.format(i))
            i += 1
        SETTINGS['Valid_UA'] = temp_array
    else:
        print('WARNING: "Valid_UA" in settings is invalid, using default')

    if validate_setting(imported, 'Update', dict):
        if validate_setting(imported['Update'], 'PS4_No_Update', float):
            SETTINGS['Update']['PS4_No_Update'] = imported['Update']['PS4_No_Update']
        else:
            print('WARNING: "Update[\'PS4_No_Update\']" in settings is invalid, using default')

        if validate_setting(imported['Update'], 'Vita_No_Update', float):
            SETTINGS['Update']['Vita_No_Update'] = imported['Update']['Vita_No_Update']
        else:
            print('WARNING: "Update[\'Vita_No_Update\']" in settings is invalid, using default')

    else:
        print('WARNING: "Update" in settings is invalid, using default')


def validate_setting(imported, value, type):
    try:
        if value:
            check_var = imported[value]
        else:
            check_var = imported

        if isinstance(check_var, type):
            return True
    except (KeyError, ValueError):
        pass

    return False


def generate_dns_rules():
    rules = []

    for entry in SETTINGS['DNS_Rules']['Redirect']:
        rules.append('A {} {}'.format(entry, SETTINGS['DNS_Rules']['Redirect_IP']))

    for entry in SETTINGS['DNS_Rules']['Block']:
        rules.append('A {} 0.0.0.0'.format(entry))

    return rules


def start_servers():
    if SETTINGS['DNS']:
        FAKEDNS.main(SETTINGS['Interface_IP'],
                     generate_dns_rules(),
                     SETTINGS['DNS_Rules']['Pass_Through_IP'],
                     SETTINGS['Debug'])
        print('>> DNS server thread is running...')

    if SETTINGS['HTTP']:
        try:
            server = ThreadedHTTPServer((SETTINGS['Interface_IP'], SETTINGS['HTTP_Port']), MyHandler)
            thread = threading.Thread(name='HTTP_Server',
                                      target=server.serve_forever,
                                      args=(),
                                      daemon=True)
            thread.start()
            print('>> HTTP server thread is running...')
        except socket.error:
            closer('ERROR: Could not start server, is another program on tcp:{}?'.format(SETTINGS['HTTP_Port']))
        except OSError:
            print('ERROR: Could not start server, is another program on tcp:{}?'.format(SETTINGS['HTTP_Port']))
            closer('    ^^This could also be a permission error^^')
        except UnicodeDecodeError:
            print('ERROR: Python failed to get a FQDN (This is a Python Bug)')
            closer('    ^^Change your computers name to be [a-zA-Z0-9]^^')


def payload_brain(ipaddr):
    global MENU_OPEN

    payloads = []
    try:
        for files in os.listdir(os.path.join(PAYLOAD_LOC)):
            if not files.endswith('PUT PAYLOADS HERE'):
                payloads.append(files)
    except (IOError, PermissionError):
        pass

    if SETTINGS['Auto_Payload'] in payloads:
        print('>> Sending {}...'.format(SETTINGS['Auto_Payload']))
        with open(os.path.join(PAYLOAD_LOC, SETTINGS['Auto_Payload']), 'rb') as buf:
            content = buf.read()
        send_payload(ipaddr, 9020, content)
        return
    elif len(payloads) <= 0:
        print('>> No payloads in payload folder, skipping payload menu')
    else:
        MENU_OPEN = True
        payloads.insert(0, 'Don\'t send a payload')
        choice = payload_menu(payloads)
        if choice != 0:
            path = os.path.join(PAYLOAD_LOC, payloads[choice])
            print('>> Sending {}...'.format(payloads[choice]))
            with open(path, 'rb') as buf:
                content = buf.read()
            send_payload(ipaddr, 9020, content)
        else:
            print('>> No payload sent')
        MENU_OPEN = False


def send_payload(hostname, port, content):
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    timeout = time.time() + 60
    while True:
        result = soc.connect_ex((hostname, port))
        if result == 0:
            print('>> Connected to PS4')
            timed_out = False
            break
        if time.time() >= timeout:
            print('ERROR: Payload sender timed out')
            timed_out = True
            break
    if not timed_out:
        try:
            soc.sendall(content)
            soc.shutdown(socket.SHUT_WR)
            while True:
                data = soc.recv(1024)
                if not data:
                    break
            print('>> Payload Sent!')
        except socket.error:
            print('ERROR: Broken Pipe')
    soc.close()


def version_check():
    try:
        with urllib.request.urlopen(API_URL) as buf:
            response = buf.read()
        response = json.loads(response.decode('utf-8'))

        version_tag = response['tag_name'].replace('v', '')

        if StrictVersion(VERSION) < StrictVersion(version_tag):
            print('WARNING: There is an update availible')
            print('  ^^ Visit https://github.com/Al-Azif/ps4-exploit-host/releases/latest')
    except urllib.error.URLError:
        print('ERROR: Unable to check Github repo to check for updates')
    except ValueError:
        print('WARNING: Unable to check Github repo to check for updates')
        print('  ^^ Visit https://github.com/Al-Azif/ps4-exploit-host/releases/latest')


def main():
    parser = argparse.ArgumentParser(description='PS4 Exploit Host')
    parser.add_argument('--settings', dest='settings', action='store',
                        default=os.path.join(CWD, 'settings.json'),
                        required=False, help='Specify a settings file')
    args = parser.parse_args()
    menu_header()

    try:
        version_check()

        default_settings()
        import_settings(args.settings)

        if not check_root():
            closer('ERROR: This must be run by root')

        start_servers()

        ip_display()

        while True:
            time.sleep(24 * 60 * 60)

    except KeyboardInterrupt:
        closer('\r>> Exiting...                                           ')


if __name__ == '__main__':
    main()
