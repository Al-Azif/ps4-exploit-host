#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import print_function

try:
    import argparse
    from cgi import parse_header
    from cgi import parse_multipart
    from urllib.parse import parse_qs
    import copy
    import datetime
    from distutils.version import StrictVersion
    from http.cookies import SimpleCookie
    from http.server import BaseHTTPRequestHandler
    from http.server import HTTPServer
    import hashlib
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
    from urllib.parse import quote
    from urllib.parse import unquote
    import urllib.request
    import zlib

    import fakedns.fakedns as FAKEDNS
except ImportError:
    import sys
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

VERSION = '0.4.7'
API_URL = 'https://api.github.com/repos/Al-Azif/ps4-exploit-host/releases/latest'
SCRIPT_LOC = os.path.realpath(__file__)
CWD = os.path.dirname(SCRIPT_LOC)
EXPLOIT_LOC = os.path.join(CWD, 'exploits')
PAYLOAD_LOC = os.path.join(CWD, 'payloads')
UPDATE_LOC = os.path.join(CWD, 'updates')
THEME_LOC = os.path.join(CWD, 'themes')
DEBUG_LOC = os.path.join(CWD, 'debug')
PKG_LOC = os.path.join(CWD, 'pkgs')
SETTINGS = None
MENU_OPEN = False
DEBUG_VAR = {}
SCRIPT_START = (datetime.datetime.utcnow()).strftime('%a, %d %b %Y %H:%M:%S GMT')


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

    def last_mod_time(self, path):
        return datetime.datetime.utcfromtimestamp(os.path.getmtime(path)).strftime('%a, %d %b %Y %H:%M:%S GMT')

    def my_send_error(self, code, message=None, explain=None):
        try:
            self.send_error(code, message, explain)
        except:
            pass  # print('ERROR: Broken Pipe')

    def my_sender(self, mime, content, extra_headers={}):
        if SETTINGS['Compression_Level'] > 0:
            gzip = zlib.compressobj(SETTINGS['Compression_Level'], zlib.DEFLATED, zlib.MAX_WBITS | 16)
            content = gzip.compress(content) + gzip.flush()
        try:
            self.send_response(200)
            self.send_header('Content-Type', mime)
            if SETTINGS['Compression_Level'] > 0:
                self.send_header('Content-Encoding', 'gzip')
            self.send_header('Content-Length', len(content))
            self.send_header('Connection', 'keep-alive')
            for key, value in extra_headers.items():
                self.send_header(key, value)
            self.end_headers()
            self.wfile.write(content)
        except:  # socket.error
            pass  # print('ERROR: Broken Pipe')

    def empty_response(self):
        self.my_sender('text/plain', b'', {'Last-Modified': SCRIPT_START}) # TODO: Cache-Control Headers

    def check_ua(self):
        for user_agent in SETTINGS['Valid_UA']:
            ua_test = re.compile(user_agent)
            if ua_test.match(self.headers['User-Agent']):
                return True
        return False

    def ps4_updatelist(self):
        region = self.path.split('/')[4]
        try:
            ps4_version = re.search(r'^Download\/1.00 libhttp\/(.+?) \(PlayStation 4\)$', self.headers['User-Agent'])
            ps4_net_test = re.match(r'^HttpTestWrapperUser libhttp\/.* \(PlayStation 4\)$', self.headers['User-Agent'])
        except TypeError:
            return self.my_send_error(404)

        try:
            if not ps4_version and not ps4_net_test:
                return self.my_send_error(404)
            if ps4_version:
                fw_version = float(ps4_version.group(1))
        except ValueError:
            return self.my_send_error(404)

        if (ps4_version and fw_version > SETTINGS['Update']['PS4_No_Update']) or ps4_net_test:
            path = os.path.join(UPDATE_LOC, 'ps4-updatelist.xml')
        else:
            return self.my_send_error(404)

        try:
            with open(path, 'rb') as buf:
                xml = buf.read()
            xml = xml.replace(b'{{REGION}}', bytes(region, 'utf-8'))
            try:
                system_size = os.path.getsize(os.path.join(UPDATE_LOC, 'PS4UPDATE_SYSTEM.PUP'))
            except (IOError, PermissionError):
                system_size = 0
            try:
                recovery_size = os.path.getsize(os.path.join(UPDATE_LOC, 'PS4UPDATE_RECOVERY.PUP'))
            except (IOError, PermissionError):
                recovery_size = 0
            xml = xml.replace(b'{{SYSTEM_SIZE}}', bytes(str(system_size), 'utf-8'))
            xml = xml.replace(b'{{RECOVERY_SIZE}}', bytes(str(recovery_size), 'utf-8'))
            self.my_sender('application/xml', xml)  # TODO: Cache-Control/Last-Modified Headers
        except (IOError, PermissionError):
            self.my_send_error(404)

    def vita_updatelist(self):
        region = self.path.split('/')[4]
        vita_version = re.search(r'^libhttp\/(.+?) \(PS Vita\)$', self.headers['User-Agent'])
        vita_net_test = re.match(r'SOMETHING THAT WONT MATCH', self.headers['User-Agent'])  # TODO: Get this UA... if used that is

        try:
            if not vita_version and not vita_net_test:
                return self.my_send_error(404)
            if vita_version:
                fw_version = float(vita_version.group(1))
        except ValueError:
            return self.my_send_error(404)

        if (vita_version and fw_version > SETTINGS['Update']['Vita_No_Update']) or vita_net_test:
            path = os.path.join(UPDATE_LOC, 'psp2-updatelist.xml')
        else:
            return self.my_send_error(404)

        try:
            with open(path, 'rb') as buf:
                xml = buf.read()
            xml = xml.replace(b'{{REGION}}', bytes(region, 'utf-8'))
            try:
                full_size = os.path.getsize(os.path.join(UPDATE_LOC, 'PSP2UPDAT_FULL.PUP'))
            except (IOError, PermissionError):
                full_size = 0
            try:
                systemdata_size = os.path.getsize(os.path.join(UPDATE_LOC, 'PSP2UPDAT_SYSTEMDATA.PUP'))
            except (IOError, PermissionError):
                systemdata_size = 0
            try:
                preinst_size = os.path.getsize(os.path.join(UPDATE_LOC, 'PSP2UPDAT_PREINST.PUP'))
            except (IOError, PermissionError):
                preinst_size = 0
            xml = xml.replace(b'{{FULL_SIZE}}', bytes(str(full_size), 'utf-8'))
            xml = xml.replace(b'{{SYSTEMDATA_SIZE}}', bytes(str(systemdata_size), 'utf-8'))
            xml = xml.replace(b'{{PREINST_SIZE}}', bytes(str(preinst_size), 'utf-8'))
            self.my_sender('application/xml', xml)  # TODO: Cache-Control/Last-Modified Headers
        except (IOError, PermissionError):
            self.my_send_error(404)

    def updatefeature(self):
        path = os.path.join(THEME_LOC, SETTINGS['Theme'], 'ps4-updatefeature.html')
        try:
            with open(path, 'rb') as buf:
                data = buf.read()
            self.my_sender('text/html', data, {'Last-Modified': self.last_mod_time(os.path.join(THEME_LOC, SETTINGS['Theme'], 'ps4-updatefeature.html'))})  # TODO: Cache-Control Headers
        except (IOError, PermissionError):
            self.my_send_error(404)

    def ps4_update_pup(self):
        if re.match(r'^\/update\/ps4\/image\/[0-9]{4}_[0-9]{4}\/sys\_[a-fA-F0-9]{32}\/PS4UPDATE\.PUP', self.path):
            path = 'PS4UPDATE_SYSTEM.PUP'
        elif re.match(r'^\/update\/ps4\/image\/[0-9]{4}_[0-9]{4}\/rec\_[a-fA-F0-9]{32}\/PS4UPDATE\.PUP', self.path):
            path = 'PS4UPDATE_RECOVERY.PUP'
        else:
            return self.my_send_error(404)
        path = os.path.join(UPDATE_LOC, path)
        try:
            with open(path, 'rb') as buf:
                data = buf.read()
            self.my_sender('text/plain', data)  # TODO: Cache-Control/Last-Modified Headers
        except (IOError, PermissionError):
            self.my_send_error(404)

    def vita_update_pup(self):
        if re.match(r'^\/update\/(psp2|psv)\/image\/[0-9]{4}_[0-9]{4}\/rel\_[a-fA-F0-9]{32}\/(PSP2|PSV)UPDAT\.PUP', self.path):
            path = 'PSP2UPDAT_FULL.PUP'
        elif re.match(r'^\/update\/(psp2|psv)\/image\/[0-9]{4}_[0-9]{4}\/sd\_[a-fA-F0-9]{32}\/(PSP2|PSV)UPDAT\.PUP', self.path):
            path = 'PSP2UPDAT_SYSTEMDATA.PUP'
        elif re.match(r'^\/update\/(psp2|psv)\/image\/[0-9]{4}_[0-9]{4}\/pre\_[a-fA-F0-9]{32}\/(PSP2|PSV)UPDAT\.PUP', self.path):
            path = 'PSP2UPDAT_PREINST.PUP'
        else:
            return self.my_send_error(404)
        path = os.path.join(UPDATE_LOC, path)
        try:
            with open(path, 'rb') as buf:
                data = buf.read()
            self.my_sender('application/x-ps3-update', data)  # TODO: Cache-Control/Last-Modified Headers
        except (IOError, PermissionError):
            self.my_send_error(404)

    def network_test(self, size):
        data = b'\0' * size
        self.my_sender('text/plain', data, {'Last-Modified': SCRIPT_START})  # TODO: Cache-Control Headers

    def api_categories(self):
        output = {}

        for entry in os.scandir(EXPLOIT_LOC):
            if entry.is_dir(follow_symlinks=False):
                new_data = {}
                finished_data = {
                    entry.name: {
                        'title': entry.name,
                        'device': '',
                        'firmware': '',
                        'user_agents': [],
                        'notes': {
                            'default': ''
                        },
                        'offline': False
                    }
                }
                try:
                    with open(os.path.join(EXPLOIT_LOC, entry.name, 'meta.json'), encoding='utf-8') as buf:
                        new_data = json.loads(buf.read())
                except (IOError, PermissionError, json.decoder.JSONDecodeError):
                    pass

                try:
                    del new_data['title']
                except KeyError:
                    pass
                finished_data[entry.name].update(new_data)
                output.update(finished_data)

        if output == {}:
            output = {'error': True, 'message': 'No Categories Found'}

        return output

    def api_entries(self, entry_path):
        entry_path = unquote(entry_path)
        output = {}

        for entry in os.scandir(os.path.join(EXPLOIT_LOC, entry_path)):
            if entry.is_dir(follow_symlinks=False):
                new_data = {}
                finished_data = {
                    entry.name: {
                        'title': entry.name,
                        'version': '',
                        'updated': '2001-01-01T00:00:00Z',
                        'device': '',
                        'firmware': '',
                        'description': {
                            'default': ''
                        },
                        'author': '',
                        'url': '',
                        'params': False,
                        'redirect': True,
                        'reload': False,
                        'offline': False
                    }
                }
                try:
                    with open(os.path.join(EXPLOIT_LOC, entry_path, entry.name, 'meta.json'), encoding='utf-8') as buf:
                        new_data = json.loads(buf.read())
                except (IOError, PermissionError, json.decoder.JSONDecodeError):
                    pass

                try:
                    del new_data['title']
                except KeyError:
                    pass
                finished_data[entry.name].update(new_data)
                output.update(finished_data)

        if output == {}:
            output = {'error': True, 'message': 'No Entries Found'}

        return output

    def api_menu(self):
        categories = self.api_categories()
        if categories != {'error': True, 'message': 'No Categories Found'}:
            for key, value in categories.items():
                categories[key]['entries'] = self.api_entries(key)

        self.my_sender('application/json', bytes(json.dumps(categories, sort_keys=True), 'utf-8'), {'Cache-Control': 'public, max-age=604800','Last-Modified': self.last_mod_time(EXPLOIT_LOC)})

    def api_theme_settings(self):
        output = {}

        output['languages'] = SETTINGS['Languages']

        output['themes'] = []
        for entry in os.scandir(THEME_LOC):
            if entry.is_dir(follow_symlinks=False):
                output['themes'].append(entry.name)

        self.my_sender('application/json', bytes(json.dumps(output), 'utf-8'), {'Last-Modified': SCRIPT_START})  # TODO: Cache-Control Headers

    def api_hostname(self):
        hostname = 'http://the.gate'
        if SETTINGS['HTTP_Interface_IP'] == '127.0.0.1' and SETTINGS['DNS_Interface_IP'] == '165.227.83.145':
            hostname = 'https://cthugha.exploit.menu/'
        elif SETTINGS['HTTP_Interface_IP'] == '127.0.0.1' and SETTINGS['DNS_Interface_IP'] == '108.61.128.158':
            hostname = 'https://ithaqua.exploit.menu/'
        elif SETTINGS['HTTP_Port'] != 80:
            hostname = '{}:{}'.format(hostname, SETTINGS['HTTP_Port'])
        else:
            hostname = '{}/'.format(hostname)
        self.my_sender('text/plain', bytes(hostname, 'utf-8'), {'Last-Modified': SCRIPT_START})  # TODO: Cache-Control Headers

    def api_view_settings(self):
        if SETTINGS['Public']:
            return self.empty_response()
        safe_settings = copy.deepcopy(SETTINGS)
        try:
            del safe_settings['Root_Check']
            del safe_settings['DNS']
            del safe_settings['HTTP']
            del safe_settings['DNS_Interface_IP']
            del safe_settings['DNS_Port']
            del safe_settings['HTTP_Interface_IP']
            del safe_settings['HTTP_Port']
        except KeyError:
            pass
        self.my_sender('application/json', bytes(json.dumps(safe_settings), 'utf-8'), {'Last-Modified': SCRIPT_START})  # TODO: Cache-Control Headers

    def api_edit_settings(self, data):
        # TODO:
        if SETTINGS['Public']:
            return self.empty_response()
        self.empty_response()

    def api_pkg_list(self):
        try:
            output = []
            for path, dirs, files in os.walk(PKG_LOC):
                for entry in files:
                    if entry.endswith('.pkg') or entry.endswith('.json'):
                        pkgpath = quote('{}/{}'.format(path.replace(CWD, '').replace('\\', '/'), entry), safe=';,/?:@&=+$-_.!~*\'()#')
                        output.append({'Filename': entry, 'Filesize': os.stat(os.path.join(path, entry)).st_size, 'File_URL': 'http://{}:{}{}'.format(SETTINGS['HTTP_Interface_IP'], SETTINGS['HTTP_Port'], pkgpath)})
            if len(output) == 0:
                data = b'["No PKGs Found"]'
            else:
                data = bytes(json.dumps(output), 'utf-8')
            self.my_sender('application/json', data, {'Last-Modified': self.last_mod_time(PKG_LOC)})  # TODO: Cache-Control Headers
        except (IOError, PermissionError):
            data = b'["I/O Error on Host"]'

    def rpi(self):
        try:
            with open(os.path.join(THEME_LOC, SETTINGS['Theme'], 'rpi.html'), 'rb') as buf:
                data = buf.read()
            self.my_sender('text/html', data, {'Cache-Control': 'public, max-age=31536000', 'Last-Modified': self.last_mod_time(os.path.join(THEME_LOC, SETTINGS['Theme'], 'rpi.html'))})
        except (IOError, PermissionError):
            self.my_send_error(404)

    def pkgs(self):
        if re.match(r'^\/pkgs[\/]?$', self.path):
            self.api_pkg_list()
        elif self.path.endswith('.pkg') or self.path.endswith('.json'):
            path = unquote(self.path.split('/', 2)[-1])
            try:
                with open(os.path.join(PKG_LOC, path), 'rb') as buf:
                    data = buf.read()
                self.my_sender('application/octet-stream', data, {'Cache-Control': 'public, max-age=31536000', 'Last-Modified': self.last_mod_time(os.path.join(PKG_LOC, path))})
            except (IOError, PermissionError):
                self.my_send_error(404)
        else:
            self.my_send_error(403)

    def exploit(self):
        path = unquote(self.path.split('/', 2)[-1])
        if path[-1:] == '/':
            path += 'index.html'
        mime = mimetypes.guess_type(self.path.rsplit('/', 1)[-1])
        if mime[0]:
            mime = mime[0]
        else:
            mime = 'application/octet-stream'
        try:
            with open(os.path.join(EXPLOIT_LOC, path), 'rb') as buf:
                data = buf.read()
            self.my_sender(mime, data, {'Last-Modified': self.last_mod_time(os.path.join(EXPLOIT_LOC, path))})  # TODO: Cache-Control Headers
        except (IOError, PermissionError):
            self.my_send_error(404)

    def favicon(self):
        try:
            with open(os.path.join(THEME_LOC, SETTINGS['Theme'], 'favicon.ico'), 'rb') as buf:
                data = buf.read()
            self.my_sender('image/x-icon', data, {'Cache-Control': 'public, max-age=31536000', 'Last-Modified': self.last_mod_time(os.path.join(THEME_LOC, SETTINGS['Theme'], 'favicon.ico'))})
        except (IOError, PermissionError):
            self.my_send_error(404)

    def robots(self):
        try:
            with open(os.path.join(THEME_LOC, SETTINGS['Theme'], 'robots.txt'), 'rb') as buf:
                data = buf.read()
            self.my_sender('text/plain', data, {'Cache-Control': 'public, max-age=31536000', 'Last-Modified': self.last_mod_time(os.path.join(THEME_LOC, SETTINGS['Theme'], 'robots.txt'))})
        except (IOError, PermissionError):
            self.my_send_error(404)

    def sitemap(self):
        try:
            with open(os.path.join(THEME_LOC, SETTINGS['Theme'], 'sitemap.xml'), 'rb') as buf:
                data = buf.read()
            hostname = 'http://the.gate/'
            if SETTINGS['HTTP_Interface_IP'] == '127.0.0.1' and SETTINGS['DNS_Interface_IP'] == '165.227.83.145':
                hostname = 'https://cthugha.exploit.menu/'
            elif SETTINGS['HTTP_Interface_IP'] == '127.0.0.1' and SETTINGS['DNS_Interface_IP'] == '108.61.128.158':
                hostname = 'https://ithaqua.exploit.menu/'
            self.my_sender('text/plain', data.replace(b'{{HOSTNAME}}', bytes(hostname, 'utf-8')), {'Cache-Control': 'public, max-age=31536000', 'Last-Modified': self.last_mod_time(os.path.join(THEME_LOC, SETTINGS['Theme'], 'sitemap.xml'))})
        except (IOError, PermissionError):
            self.my_send_error(404)

    def success(self):
        self.empty_response()
        if SETTINGS['Public']:
            return
        if not MENU_OPEN:
            payload_brain(self.client_address[0])

    def success_args(self):
        self.empty_response()
        if SETTINGS['Public']:
            return
        result = re.search(r'^\/success\/([0-9]{1,5})\/([0-9]{1,3})\/(.*)$', self.path)
        if int(result.group(1)) < 1 or int(result.group(1)) > 65535:
            print('>> Success request port number is out of range')
        elif int(result.group(2)) < 0 or int(result.group(2)) > 999:
            print('>> Success request timeout is out of range')
        else:
            try:
                with open(os.path.join(PAYLOAD_LOC, result.group(3)), 'rb') as buf:
                    print('>> Sending {}...'.format(result.group(3)))
                    send_payload(self.address_string(), int(result.group(1)), int(result.group(2)), buf.read())
            except (IOError, PermissionError):
                print('>> Success request payload ({}) not found'.format(result.group(2)))

    def theme_loader(self):
        try:
            cookies = SimpleCookie(self.headers.get('Cookie'))

            default_cookie = 'theme={}; expires={}; domain={}; path={};'.format(SETTINGS['Theme'], (datetime.datetime.utcnow() + datetime.timedelta(days=36500)).strftime('%a, %d %b %Y %H:%M:%S GMT'), self.headers.get('Host'), quote(self.path))
            theme_error_html = b'<!DOCTYPE html><html><head><meta charset="utf-8"><title>Theme Error</title></head><body><script>"use strict";window.addEventListener("load",function(){alert("Error retrieving theme data, resetting theme to default and reloading."),window.location.reload(!0)});</script></body></html>'
            extra_headers = {}

            theme = cookies['theme'].value
            if not os.path.isdir(os.path.join(THEME_LOC, theme)):
                self.my_sender('text/html', theme_error_html, {'Cache-Control': 'public, max-age=31536000', 'Last-Modified': SCRIPT_START, 'Set-Cookie': default_cookie})
                return
        except KeyError:
            theme = SETTINGS['Theme']
            extra_headers = {'Cache-Control': 'public, max-age=31536000', 'Last-Modified': SCRIPT_START, 'Set-Cookie': default_cookie}

        try:
            with open(os.path.join(THEME_LOC, theme, 'index.html'), 'rb') as buf:
                data = buf.read()
            self.my_sender('text/html', data, extra_headers)
        except (IOError, PermissionError):
            self.my_sender('text/html', theme_error_html, {'Cache-Control': 'public, max-age=31536000', 'Last-Modified': SCRIPT_START, 'Set-Cookie': default_cookie})

    def index(self):
        if not SETTINGS['UA_Check'] or self.check_ua():
            if self.headers.get('Host') == 'www.playstation.com' or self.headers.get('Host') == 'manuals.playstation.net':
                self.my_sender('text/html', b'<!DOCTYPE html><html manifest="/redirect.manifest"><head><meta charset="utf-8"><title>Redirector</title></head><body><script>"use strict";function redirect(){var a=new XMLHttpRequest;a.open("GET","/api/hostname",!0),a.onload=function(){200<=a.status&&400>a.status?window.location.replace(a.responseText):alert("Error getting server IP")},a.onerror=function(){alert("Error getting server IP")},a.send()}window.addEventListener("load",function(){try{window.applicationCache.oncached=redirect,window.applicationCache.onupdateready=redirect,window.applicationCache.onnoupdate=redirect,window.applicationCache.onerror=redirect}catch(a){redirect()}});</script></body></html>', {'Cache-Control': 'public, max-age=31536000', 'Last-Modified': SCRIPT_START})
            else:
                self.theme_loader()
        else:
            self.my_send_error(400, explain='This device is not supported')
            if not MENU_OPEN:
                print('>> Unsupported device attempted to access exploits')

    def blank(self):
        self.my_sender('text/html', b'<!DOCTYPE html><html><head><meta charset=utf-8><title>Deus Machina</title></head><body><pre>ZmzJCgLnJ43j2FK4NUR/EmFc7hJRN7Ub4adlqCRLfsXoswDsjyvn5vGwLj2FZdOlVLNmi/l0mjiuHgCYSZqPSndVhg6U8ODSl1+/aDxQLZE=</pre></body></html>', {'Cache-Control': 'public, max-age=31536000', 'Last-Modified': SCRIPT_START})

    def debug_var_get(self):
        try:
            result = re.search(r'^\/debug\/var\/([a-zA-Z0-9\-\_\.]*)$', self.path)
            self.my_sender('text/plain', DEBUG_VAR[result.group(1)])  # TODO: Cache-Control/Last-Modified Headers
        except KeyError:
            try:
                self.send_response(404)
                self.send_header('Content-Type', 'text/plain')
                self.send_header('Content-Length', 0)
                self.send_header('Cache-Control', 'must-revalidate')
                self.send_header('Connection', 'keep-alive')
                self.end_headers()
                self.wfile.write(b'')
            except:
                pass  # print('ERROR: Broken Pipe')

    def debug_varclear(self):
        global DEBUG_VAR

        DEBUG_VAR = {}
        self.empty_response()

    def debug_clearlogs(self):
        try:
            with open(os.path.join(DEBUG_LOC, 'js-error.log'), 'w') as buf:
                pass
            with open(os.path.join(DEBUG_LOC, 'httpd.log'), 'w') as buf:
                pass
        except (IOError, PermissionError):
            return self.my_send_error(404)

        self.empty_response()

    def debug_jserrorlog(self, post_data):
        try:
            message = '--------------------------------------------------------------------------------\n'
            message += '    Date:       {}\n'.format(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))
            message += '    Message:    {}\n'.format(post_data['message'])
            message += '    Line:       {}\n'.format(post_data['line'])
            message += '    Column:     {}\n'.format(post_data['column'])
            message += '    URL:        {}\n'.format(post_data['url'])
            message += '    User-Agent: {}\n'.format(post_data['useragent'])
            message += '    Stack:      {}\n'.format(post_data['stack'])
            with open(os.path.join(DEBUG_LOC, 'js-error.log'), 'a') as buf:
                buf.write(message)
            self.empty_response()
        except (KeyError, IOError, PermissionError):
            self.my_send_error(404)

    def debug_filedump(self, post_data):
        try:
            if post_data[b'filename'][0].decode('utf-8') != 'js-error.log' and \
            post_data[b'filename'][0].decode('utf-8') != 'httpd.log':
                with open(os.path.join(DEBUG_LOC, post_data[b'filename'][0].decode('utf-8')), 'rb+') as buf:
                    buf.seek(int(post_data[b'offset'][0]), 0)
                    buf.write(post_data[b'data'][0])
                return self.empty_response()
        except (KeyError, IOError, PermissionError):
            pass

        self.my_send_error(404)

    def debug_filedelete(self, post_data):
        try:
            if post_data[b'filename'][0].decode('utf-8') != 'js-error.log' and \
            post_data[b'filename'][0].decode('utf-8') != 'httpd.log':
                if not os.path.isfile(os.path.join(DEBUG_LOC, post_data[b'filename'][0].decode('utf-8'))):
                    return self.empty_response()
                os.remove(os.path.join(DEBUG_LOC, post_data[b'filename'][0].decode('utf-8')))
                return self.empty_response()
        except (KeyError, IOError, PermissionError):
            pass

        self.my_send_error(404)

    def debug_vardump(self, post_data):
        try:
            if post_data[b'filename'][0].decode('utf-8') != 'js-error.log' and \
            post_data[b'filename'][0].decode('utf-8') != 'httpd.log':
                with open(os.path.join(DEBUG_LOC, post_data[b'filename'][0].decode('utf-8')), 'w') as buf:
                    buf.write(json.dumps(DEBUG_VAR, indent=2, sort_keys=True))
                return self.empty_response()
        except (KeyError, IOError, PermissionError):
            pass

        self.my_send_error(404)

    def debug_var_post(self, post_data):
        result = re.search(r'^\/debug\/var\/([a-zA-Z0-9\-\_\.]*)$', self.path)
        length = int(self.headers['Content-Length'])
        if length != 0:
            try:
                DEBUG_VAR[result.group(1)] = self.rfile.read(length)
                self.my_sender('text/plain', DEBUG_VAR[result.group(1)])  # TODO: Cache-Control/Last-Modified Headers
            except KeyError:
                self.my_send_error(404)
        else:
            try:
                del DEBUG_VAR[result.group(1)]
            except KeyError:
                pass
            self.empty_response()

    def static_request(self):
        path = unquote(self.path.split('/', 2)[-1])
        if path[-1:] == '/':
            path += 'index.html'
        mime = mimetypes.guess_type(self.path.rsplit('/', 1)[-1])
        if mime[0]:
            mime = mime[0]
        else:
            mime = 'application/octet-stream'
        try:
            with open(os.path.join(THEME_LOC, path), 'rb') as buf:
                data = buf.read()
            self.my_sender(mime, data, {'Cache-Control': 'public, max-age=31536000', 'Last-Modified': self.last_mod_time(os.path.join(THEME_LOC, path))})
        except (IOError, PermissionError):
            self.my_send_error(404)

    def news(self):
        try:
            with open(os.path.join(CWD, 'news.json'), 'rb') as buf:
                data = buf.read()
            self.my_sender('application/json', data, {'Cache-Control': 'public, no-cache, must-revalidate', 'Last-Modified': self.last_mod_time(os.path.join(CWD, 'news.json'))})  # TODO: Cache-Control Headers
        except (IOError, PermissionError):
            self.my_send_error(404)

    def generate_cacher(self):
        if re.match(r'^\/cache\/theme\/index.html$', self.path):
            html = b'<!DOCTYPE html><html manifest="./../../theme.manifest"><head><meta charset="utf-8"><title>Cacher</title></head><body><script>"use strict";try{window.applicationCache.ondownloading=function(){parent.cacheInterface("ondownloading-theme")},window.applicationCache.onprogress=function(a){parent.cacheProgress(Math.round(100*(a.loaded/a.total)))},window.applicationCache.oncached=function(){parent.cacheInterface("oncached-theme")},window.applicationCache.onupdateready=function(){parent.cacheInterface("onupdateready-theme")},window.applicationCache.onnoupdate=function(){parent.cacheInterface("onnoupdate-theme")},window.applicationCache.onerror=function(){parent.cacheInterface("onerror-theme")},window.applicationCache.onobsolete=function(){parent.cacheInterface("onobsolete-theme")}}catch(a){parent.cacheInterface("onerror-appcache-theme")}</script></body></html>'
        else:
            html = b'<!DOCTYPE html><html manifest="./offline.manifest"><head><meta charset="utf-8"><title>Cacher</title></head><body><script>"use strict";try{window.applicationCache.ondownloading=function(){parent.cacheInterface("ondownloading")},window.applicationCache.onprogress=function(a){parent.cacheProgress(Math.round(100*(a.loaded/a.total)))},window.applicationCache.oncached=function(){parent.cacheInterface("oncached")},window.applicationCache.onupdateready=function(){parent.cacheInterface("onupdateready")},window.applicationCache.onnoupdate=function(){parent.cacheInterface("onnoupdate")},window.applicationCache.onerror=function(){parent.cacheInterface("onerror")},window.applicationCache.onobsolete=function(){parent.cacheInterface("onobsolete")}}catch(a){parent.cacheInterface("onerror-appcache")}</script></body></html>'

        self.my_sender('text/html', html)  # TODO: Cache-Control/Last-Modified Headers

    def generate_manifest(self):
        relative_path = './../..'
        search_loc = EXPLOIT_LOC
        hasher = hashlib.md5()

        manifest = 'CACHE MANIFEST\n\n'
        manifest += 'CACHE:\n'

        if re.match(r'^\/cache\/category\/.*\/offline.manifest$', self.path):
            relative_path = './../../..'
            search_loc = os.path.join(EXPLOIT_LOC, unquote(self.path.split('/')[3]))
        elif re.match(r'^\/cache\/entry\/.*\/.*\/offline.manifest$', self.path):
            relative_path = './../../../..'
            search_loc = os.path.join(EXPLOIT_LOC, unquote(self.path.split('/')[3]), unquote(self.path.split('/')[4]))
        elif re.match(r'^\/cache\/all\/offline.manifest$', self.path):
            relative_path = './../..'
            search_loc = EXPLOIT_LOC
        else:
            return self.my_send_error(404)

        # TODO: Change to scandir?
        for path, subdirs, files in os.walk(search_loc):
            for filename in files:
                if filename not in ('meta.json', 'PUT EXPLOITS HERE'):
                    try:
                        with open(os.path.join(path, filename), 'rb') as buf:
                            data = buf.read()
                        hasher.update(data)
                        manifest += '{}{}\n'.format(relative_path, quote(os.path.join(path, filename).replace(CWD, '').replace('\\', '/'), safe=';,/?:@&=+$-_.!~*\'()#'))
                    except (IOError, PermissionError):
                        pass

        manifest += '\nNETWORK:\n'
        manifest += '*\n'

        hasher.update(bytes(self.last_mod_time(os.path.join(search_loc)), 'utf-8'))
        manifest += '\n# Hash: {}'.format(hasher.hexdigest().upper())

        self.my_sender('text/cache-manifest', bytes(manifest, 'utf-8'), {'Last-Modified': self.last_mod_time(search_loc)})  # TODO: Cache-Control Headers

    def redirect_manifest(self):
        hasher = hashlib.md5()

        manifest = 'CACHE MANIFEST\n\n'
        manifest += 'CACHE:\n'

        manifest += '/\n'
        manifest += '/index.html\n'
        manifest += '/api/hostname\n'

        manifest += '\nNETWORK:\n'
        manifest += '*\n'

        manifest += '\nSETTINGS:\n'
        manifest += 'prefer-online\n'

        hasher.update(bytes(SETTINGS['HTTP_Interface_IP'] + ':' + str(SETTINGS['HTTP_Port']), 'utf-8'))
        manifest += '\n# Hash: {}'.format(hasher.hexdigest().upper())

        self.my_sender('text/cache-manifest', bytes(manifest, 'utf-8'), {'Cache-Control': 'public, max-age=31536000', 'Last-Modified': SCRIPT_START})

    def theme_manifest(self):
        hasher = hashlib.md5()

        manifest = 'CACHE MANIFEST\n\n'
        manifest += 'CACHE:\n'

        manifest += './\n'
        manifest += './index.html\n'
        manifest += './blank.html\n'
        manifest += './api/themes\n'
        manifest += './api/menu\n'

        try:
            cookies = SimpleCookie(self.headers.get('Cookie'))
            theme = cookies['theme'].value
            if not os.path.isdir(os.path.join(THEME_LOC, theme)):
                theme = SETTINGS['Theme']
        except KeyError:
            theme = SETTINGS['Theme']

        # TODO: Change to scandir?
        for path, subdirs, files in os.walk(os.path.join(THEME_LOC, theme)):
            for filename in files:
                try:
                    with open(os.path.join(path, filename), 'rb') as buf:
                        data = buf.read()
                    hasher.update(data)
                    manifest += '.{}\n'.format(quote(os.path.join(path, filename).replace(CWD, '').replace('\\', '/'), safe=';,/?:@&=+$-_.!~*\'()#'))
                except (IOError, PermissionError):
                    pass

        manifest += '\nNETWORK:\n'
        manifest += '*\n'

        manifest += '\nSETTINGS:\n'
        manifest += 'prefer-online\n'

        categories = self.api_categories()
        if categories != {'error': True, 'message': 'No Categories Found'}:
            for key, value in categories.items():
                categories[key]['entries'] = self.api_entries(key)

        hasher.update(bytes(self.last_mod_time(os.path.join(THEME_LOC, theme)), 'utf-8'))
        hasher.update(bytes(json.dumps(categories), 'utf-8'))
        manifest += '\n# Hash: {}'.format(hasher.hexdigest().upper())

        self.my_sender('text/cache-manifest', bytes(manifest, 'utf-8'), {'Last-Modified': self.last_mod_time(os.path.join(THEME_LOC, theme))})  # TODO: Cache-Control Headers

    def do_GET(self):
        try:
            self.queries = self.path.split('?')[1]
        except IndexError:
            pass
        self.path = self.path.split('?')[0]

        if re.match(r'^\/update\/ps4\/list\/[a-z]{2}\/ps4\-updatelist\.xml', self.path):
            return self.ps4_updatelist()
        if re.match(r'^\/update\/(psp2|psv)\/list\/[a-z]{2}\/(psp2|psv)\-updatelist\.xml', self.path):
            return self.vita_updatelist()
        if re.match(r'^\/update\/ps4\/html\/[a-z]{2}\/[a-z]{2}\/ps4\-updatefeature\.html', self.path):
            return self.updatefeature()
        if re.match(r'^\/update\/ps4\/image\/[0-9]{4}_[0-9]{4}\/(sys|rec)\_[a-fA-F0-9]{32}\/PS4UPDATE\.PUP', self.path):
            return self.ps4_update_pup()
        if re.match(r'^\/update\/(psp2|psv)\/image\/[0-9]{4}_[0-9]{4}\/(rel|sd|pre)\_[a-fA-F0-9]{32}\/(PSP2|PSV)UPDAT\.PUP', self.path):
            return self.vita_update_pup()
        if re.match(r'^\/networktest\/get\_2m', self.path):
            return self.network_test(2097152)
        if re.match(r'^\/networktest\/get\_6m', self.path):
            return self.network_test(6291456)
        if re.match(r'^\/api\/menu$', self.path):
            return self.api_menu()
        if re.match(r'^\/api\/themes$', self.path):
            return self.api_theme_settings()
        if re.match(r'^\/api\/hostname$', self.path):
            return self.api_hostname()
        if re.match(r'^\/api\/settings\/view$', self.path):
            return self.api_view_settings()
        if re.match(r'^\/api\/pkglist$', self.path):
            return self.api_pkg_list()
        if re.match(r'^\/$', self.path) or re.match(r'^\/index\.html$', self.path) or re.match(r'^\/document\/[a-zA-Z\-]{2,5}\/(ps4|psvita)\/index.html$', self.path):
            return self.index()
        if re.match(r'^\/rpi$', self.path):
            return self.rpi()
        if re.match(r'^\/pkgs[\/]?', self.path):
            return self.pkgs()
        if re.match(r'\/favicon.ico$', self.path):
            return self.favicon()
        if re.match(r'\/robots.txt$', self.path):
            return self.robots()
        if re.match(r'\/sitemap.xml$', self.path):
            return self.sitemap()
        if re.search(r'\/redirect\.manifest$', self.path):
            return self.redirect_manifest()
        if re.search(r'\/theme\.manifest$', self.path):
            return self.theme_manifest()
        if re.match(r'^\/cache\/.*\/index.html$', self.path):
            return self.generate_cacher()
        if re.match(r'^\/cache\/.*\/offline.manifest$', self.path):
            return self.generate_manifest()
        if re.match(r'^\/exploits\/.*\/', self.path):
            return self.exploit()
        if re.match(r'^\/success$', self.path):
            return self.success()
        if re.match(r'^\/success\/[0-9]{1,5}\/[0-9]{1,3}\/.*$', self.path):
            return self.success_args()
        if re.match(r'^\/themes\/', self.path):
            return self.static_request()
        if re.match(r'^\/api\/news$', self.path):
            return self.news()
        if re.match(r'^\/blank.html$', self.path):
            return self.blank()
        if re.match(r'^\/debug\/var\/[a-zA-Z0-9\-\_\.]*$', self.path) and not SETTINGS['Public']:
            return self.debug_var_get()
        if re.match(r'\/debug\/varclear$', self.path) and not SETTINGS['Public']:
            return self.debug_varclear()
        if re.match(r'\/debug\/clearlogs$', self.path) and not SETTINGS['Public']:
            return self.debug_clearlogs()

        return self.my_send_error(404)

    def parse_POST(self):
        try:
            ctype, pdict = parse_header(self.headers['content-type'])
            if ctype == 'multipart/form-data':
                postvars = parse_multipart(self.rfile, pdict)
            elif ctype == 'application/x-www-form-urlencoded':
                length = int(self.headers['content-length'])
                postvars = parse_qs(self.rfile.read(length), keep_blank_values=1)
            elif ctype == 'application/json':
                length = int(self.headers['content-length'])
                postvars = json.loads(self.rfile.read(length))
            else:
                postvars = {}
        except (KeyError, TypeError):
            postvars = {}

        # TODO: Standardize parsed data

        return postvars

    def do_POST(self):
        post_data = self.parse_POST()

        if re.match(r'^\/networktest\/post\_128', self.path):
            return self.empty_response()
        if re.match(r'^\/api\/settings\/edit$', self.path):
            return self.api_edit_settings(post_data)
        if re.match(r'^\/debug\/jserrorlog$', self.path):
            return self.debug_jserrorlog(post_data)
        if re.match(r'^\/debug\/filedump$', self.path) and not SETTINGS['Public']:
            return self.debug_filedump(post_data)
        if re.match(r'^\/debug\/filedelete$', self.path) and not SETTINGS['Public']:
            return self.debug_filedelete(post_data)
        if re.match(r'\/debug\/vardump$', self.path) and not SETTINGS['Public']:
            return self.debug_vardump(post_data)
        if re.match(r'^\/debug\/var\/[a-zA-Z0-9\-\_\.]*$', self.path) and not SETTINGS['Public']:
            return self.debug_var_post(post_data)

        return self.my_send_error(404)

    def log_message(self, format, *args):
        if (format % args) == 'code 404, message Not Found':
            return

        try:
            with open(os.path.join(DEBUG_LOC, 'httpd.log'), 'a') as buf:
                buf.write("%s - %s - [%s] %s\n" % (self.address_string(), self.headers.get('Host'), self.log_date_time_string(), format % args))
        except (IOError, PermissionError):
            pass

        if SETTINGS['Debug']:
            sys.stderr.write("%s - %s - [%s] %s\n" % (self.address_string(), self.headers.get('Host'), self.log_date_time_string(), format % args))


def check_root():
    root = True
    try:
        if SETTINGS['Root_Check']:
            root = bool(os.getuid() == 0)
    except AttributeError:
        pass

    return root


def get_lan():
    ip = ''
    soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        soc.connect(('10.255.255.255', 1))
        ip = str(soc.getsockname()[0])
        soc.close()
    except socket.error:
        soc.close()

    return ip


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
    if SETTINGS['HTTP'] and SETTINGS['DNS']:
        server_string = 'Servers are running'
    else:
        server_string = 'Server is running'

    menu = center_menu_item('{}'.format(server_string))

    if SETTINGS['HTTP']:
        if SETTINGS['HTTP_Port'] == 80:
            menu += '\n' + center_menu_item('Your HTTP IP is {}'.format(SETTINGS['HTTP_Interface_IP']))
        else:
            menu += '\n' + center_menu_item('Your HTTP IP is {} on port {}'.format(SETTINGS['HTTP_Interface_IP'], SETTINGS['HTTP_Port']))

    if SETTINGS['DNS']:
        if SETTINGS['DNS_Port'] == 53:
            menu += '\n' + center_menu_item('Your DNS IP is {}'.format(SETTINGS['DNS_Interface_IP']))
        else:
            menu += '\n' + center_menu_item('Your DNS IP is {} on port {}'.format(SETTINGS['DNS_Interface_IP'], SETTINGS['DNS_Port']))

    print_line()
    print(menu)
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

    SETTINGS = {
        "Debug": False,
        "Root_Check": True,
        "Public": False,
        "DNS": True,
        "HTTP": True,
        "DNS_Interface_IP": "",
        "DNS_Port": 53,
        "HTTP_Interface_IP": "",
        "HTTP_Port": 80,
        "Compression_Level": 0,
        "UA_Check": False,
        "Theme": "Default",
        "Auto_Payload": "",
        "Payload_Timeout": 60,
        "DNS_Rules": {
            "Redirect_IP": "",
            "Redirect": [],
            "Block": [],
            "Pass_Through_IP": []
        },
        "Valid_UA": [],
        "Update": {
            "PS4_No_Update": 1.76,
            "Vita_No_Update": 0.00
        },
        "Languages": {
            "English": "en"
        }
    }


def import_settings(settings_file):
    global SETTINGS

    try:
        with open(settings_file, 'rb') as buf:
            imported = json.loads(buf.read())
    except (IOError, PermissionError):
        print('ERROR: Unable to read settings.json, using defaults')
        return
    except json.decoder.JSONDecodeError:
        print('ERROR: Malformed settings.json, using defaults')
        return

    if validate_setting(imported, 'Debug', bool):
        SETTINGS['Debug'] = imported['Debug']
    else:
        print('WARNING: "Debug" in settings is invalid, using default')

    if validate_setting(imported, 'Root_Check', bool):
        SETTINGS['Root_Check'] = imported['Root_Check']
    else:
        print('WARNING: "Root_Check" in settings is invalid, using default')

    if validate_setting(imported, 'Public', bool):
        SETTINGS['Public'] = imported['Public']
    else:
        print('WARNING: "Public" in settings is invalid, using default')

    if validate_setting(imported, 'DNS', bool):
        SETTINGS['DNS'] = imported['DNS']
        if not SETTINGS['DNS']:
            print('WARNING: DNS is disabled, User\'s Manual method will not work')
    else:
        print('WARNING: "DNS" in settings is invalid, using default')

    if validate_setting(imported, 'HTTP', bool):
        SETTINGS['HTTP'] = imported['HTTP']
        if not SETTINGS['HTTP']:
            print('WARNING: HTTP is disabled, not files will be served by this host')
    else:
        print('WARNING: "HTTP" in settings is invalid, using default')

    if not SETTINGS['DNS'] and not SETTINGS['HTTP']:
        closer('ERROR: Neither the DNS or the HTTP servers are enabled')

    if validate_setting(imported, 'DNS_Interface_IP', str):
        try:
            ipaddress.ip_address(imported['DNS_Interface_IP'])
            SETTINGS['DNS_Interface_IP'] = imported['DNS_Interface_IP']
        except ValueError:
            if imported['DNS_Interface_IP']:
                print('WARNING: "DNS_Interface_IP" in settings is not a valid IP, attempting to set default')

            temp_ip = get_lan()
            if not temp_ip:
                closer('ERROR: Could not determine default for "DNS_Interface_IP"')

            if SETTINGS['DNS_Interface_IP']:
                print('INFO: "DNS_Interface_IP" set to {}'.format(SETTINGS['DNS_Interface_IP']))

            SETTINGS['DNS_Interface_IP'] = temp_ip
    else:
        print('WARNING: "DNS_Interface_IP" in settings is not a valid IP, attempting to set default')
        temp_ip = get_lan()

        if not temp_ip:
            closer('ERROR: Could not determine default for "DNS_Interface_IP"')

        if SETTINGS['DNS_Interface_IP']:
            print('INFO: "DNS_Interface_IP" set to {}'.format(SETTINGS['DNS_Interface_IP']))

        SETTINGS['DNS_Interface_IP'] = temp_ip

    if validate_setting(imported, 'DNS_Port', int) and imported['DNS_Port'] > 0 and imported['DNS_Port'] < 65535:
        SETTINGS['DNS_Port'] = imported['DNS_Port']
        if SETTINGS['DNS_Port'] != 53:
            print('WARNING: DNS is not port 53, this is for VERY advanced users only')
    else:
        print('WARNING: "DNS_Port" in settings is invalid, using default')

    if validate_setting(imported, 'HTTP_Interface_IP', str):
        try:
            ipaddress.ip_address(imported['HTTP_Interface_IP'])
            SETTINGS['HTTP_Interface_IP'] = imported['HTTP_Interface_IP']
        except ValueError:
            if imported['HTTP_Interface_IP']:
                print('WARNING: "HTTP_Interface_IP" in settings is not a valid IP, attempting to set default')

            temp_ip = get_lan()
            if not temp_ip:
                closer('ERROR: Could not determine default for "HTTP_Interface_IP"')

            if SETTINGS['HTTP_Interface_IP']:
                print('INFO: "HTTP_Interface_IP" set to {}'.format(SETTINGS['HTTP_Interface_IP']))

            SETTINGS['HTTP_Interface_IP'] = temp_ip
    else:
        print('WARNING: "HTTP_Interface_IP" in settings is not a valid IP, attempting to set default')
        temp_ip = get_lan()

        if not temp_ip:
            closer('ERROR: Could not determine default for "HTTP_Interface_IP"')

        if SETTINGS['HTTP_Interface_IP']:
            print('INFO: "HTTP_Interface_IP" set to {}'.format(SETTINGS['HTTP_Interface_IP']))

        SETTINGS['HTTP_Interface_IP'] = temp_ip

    if validate_setting(imported, 'HTTP_Port', int) and imported['HTTP_Port'] >= 1 and imported['HTTP_Port'] <= 65535:
        SETTINGS['HTTP_Port'] = imported['HTTP_Port']
        if SETTINGS['HTTP_Port'] != 80:
            print('WARNING: HTTP is not port 80, User\'s Manual method will not work')
    else:
        print('WARNING: "HTTP_Port" in settings is invalid, using default')

    if validate_setting(imported, 'Compression_Level', int) and imported['Compression_Level'] >= 0 and imported['Compression_Level'] <= 9:
        SETTINGS['Compression_Level'] = imported['Compression_Level']
    else:
        print('WARNING: "Compression_Level" in settings is invalid, using default')

    if SETTINGS['DNS_Port'] == SETTINGS['HTTP_Port'] and SETTINGS['DNS_Interface_IP'] == SETTINGS['HTTP_Interface_IP']:
        closer('ERROR: DNS and HTTP cannot share the same port on the same interface')

    if validate_setting(imported, 'UA_Check', bool):
        SETTINGS['UA_Check'] = imported['UA_Check']
    else:
        print('WARNING: "UA_Check" in settings is invalid, using default')

    if validate_setting(imported, 'Theme', str) and \
    os.path.isfile(os.path.join(THEME_LOC, imported['Theme'], 'index.html')):
        SETTINGS['Theme'] = imported['Theme']
    elif os.path.isfile(os.path.join(THEME_LOC, 'Default', 'index.html')):
        closer('ERROR: "Theme" in settings is invalid, and default is missing')
    else:
        print('WARNING: "Theme" in settings is invalid, using default')

    if (validate_setting(imported, 'Auto_Payload', str) and
    os.path.isfile(os.path.join(PAYLOAD_LOC, imported['Auto_Payload']))) or \
        not imported['Auto_Payload']:
        SETTINGS['Auto_Payload'] = imported['Auto_Payload']
    else:
        print('WARNING: "Auto_Payload" in settings is invalid, using default')

    if validate_setting(imported, 'Payload_Timeout', int) and imported['Payload_Timeout'] > 0 and imported['Payload_Timeout'] < 100:
        SETTINGS['Payload_Timeout'] = imported['Payload_Timeout']
    else:
        print('WARNING: "Payload_Timeout" in settings is invalid, using default')

    if validate_setting(imported, 'DNS_Rules', dict):
        if validate_setting(imported['DNS_Rules'], 'Redirect_IP', str):
            try:
                ipaddress.ip_address(imported['DNS_Rules']['Redirect_IP'])
                SETTINGS['DNS_Rules']['Redirect_IP'] = imported['DNS_Rules']['Redirect_IP']
            except ValueError:
                if SETTINGS['DNS_Rules']['Redirect_IP']:
                    print('WARNING: "DNS_Rules[\'Redirect_IP\']" in settings is invalid, using the set "HTTP_Interface_IP": {}'.format(SETTINGS['HTTP_Interface_IP']))
                SETTINGS['DNS_Rules']['Redirect_IP'] = SETTINGS['HTTP_Interface_IP']

            if SETTINGS['HTTP_Interface_IP'] != SETTINGS['DNS_Rules']['Redirect_IP']:
                print('WARNING: DNS is not redirecting directly to this hosts HTTP server')

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

    if validate_setting(imported, 'Languages', dict):
        temp_obj = {}
        for key, value in imported['Languages'].items():
            if validate_setting(value, '', str):
                temp_obj[key] = imported['Languages'][key]
            else:
                print('WARNING: Invalid entry in "Languages" settings, discarding {}'.format(key))
        SETTINGS['Languages'] = temp_obj
    else:
        print('WARNING: "Languages" in settings is invalid, using default')


def validate_setting(imported, value, datatype):
    try:
        if value:
            check_var = imported[value]
        else:
            check_var = imported

        if isinstance(check_var, datatype):
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
        FAKEDNS.main(SETTINGS['DNS_Interface_IP'],
                     SETTINGS['DNS_Port'],
                     generate_dns_rules(),
                     SETTINGS['DNS_Rules']['Pass_Through_IP'],
                     SETTINGS['Debug'])
        print('>> DNS server thread is running...')

    if SETTINGS['HTTP']:
        try:
            server = ThreadedHTTPServer((SETTINGS['HTTP_Interface_IP'], SETTINGS['HTTP_Port']), MyHandler)
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
        send_payload(ipaddr, 9020, SETTINGS['Payload_Timeout'], content)
        return
    elif len(payloads) <= 0 and not SETTINGS['Public']:
        print('>> No payloads in payload folder, skipping payload menu')
    elif not SETTINGS['Public']:
        MENU_OPEN = True
        payloads.insert(0, 'Don\'t send a payload')
        choice = payload_menu(payloads)
        if choice != 0:
            path = os.path.join(PAYLOAD_LOC, payloads[choice])
            print('>> Sending {}...'.format(payloads[choice]))
            with open(path, 'rb') as buf:
                content = buf.read()
            send_payload(ipaddr, 9020, SETTINGS['Payload_Timeout'], content)
        else:
            print('>> No payload sent')
        MENU_OPEN = False


def send_payload(hostname, port, timeout, content):
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    timeout = time.time() + timeout
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
        print('ERROR: Unable to check GitHub for updates')
        print('  ^^ Visit https://github.com/Al-Azif/ps4-exploit-host/releases/latest')
    except ValueError:
        print('WARNING: Unable to check GitHub for updates')
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
