#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import hashlib
import json
import os
import shutil
import sys
from urllib.parse import quote

CWD = os.path.dirname(os.path.realpath(__file__))


def get_categories():
    output = {}

    for entry in os.scandir(os.path.join(CWD, 'exploits')):
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
                with open(os.path.join(CWD, 'exploits', entry.name, 'meta.json'), 'rb') as buf:
                    new_data = json.loads(buf.read())
            except (IOError, PermissionError, json.decoder.JSONDecodeError):
                pass

            try:
                del new_data['title']
            except KeyError:
                pass
            finished_data[entry.name].update(new_data)
            output.update(finished_data)

    if not output:
        output = {
            'error': True,
            'message': 'No Categories Found'
        }

    return output


def get_entries(entry_path):
    output = {}

    for entry in os.scandir(os.path.join(CWD, 'exploits', entry_path)):
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
                    }, 'author': '',
                    'url': '',
                    'redirect': True,
                    'reload': False,
                    'offline': False
                }
            }
            try:
                with open(os.path.join(CWD, 'exploits', entry_path, entry.name, 'meta.json'), encoding='utf-8') as buf:
                    new_data = json.loads(buf.read())
            except (IOError, PermissionError, json.decoder.JSONDecodeError):
                pass

            try:
                del new_data['title']
            except KeyError:
                pass
            finished_data[entry.name].update(new_data)
            output.update(finished_data)

    if not output:
        output = {
            'error': True,
            'message': 'No Entries Found'
        }

    return output


def get_menu():
    categories = get_categories()

    if categories == {'error': True, 'message': 'No Categories Found'}:
        return categories
    for key, value in categories.items():
        categories[key]['entries'] = get_entries(key)

    return categories


def get_theme_settings(settings_file):
    output = {}

    with open(settings_file, 'rb') as buf:
        data = json.loads(buf.read())
    output['languages'] = data['Languages']

    output['themes'] = []
    for entry in os.scandir(os.path.join(CWD, 'themes')):
        if entry.is_dir(follow_symlinks=False):
            output['themes'].append(entry.name)

    return output


def get_themes_manifest():
    hasher = hashlib.md5()

    manifest = 'CACHE MANIFEST\n\n'
    manifest += 'CACHE:\n'

    manifest += './\n'
    manifest += './index.html\n'
    manifest += './blank.html\n'
    manifest += './api/theme_settings.json\n'
    manifest += './api/menu.json\n'

    for path, subdirs, files in os.walk(os.path.join(CWD, 'themes')):
        for filename in files:
            if not filename.endswith('.es6'):  # Maybe exclued dotfiles and delete them in the clean up phase
                with open(os.path.join(path, filename), 'rb') as buf:
                    data = buf.read()
                hasher.update(data)
                manifest += '.{}\n'.format(quote(os.path.join(path, filename).replace(CWD, '').replace('\\', '/'), safe=';,/?:@&=+$-_.!~*\'()#'))

    manifest += '\nNETWORK:\n'
    manifest += '*\n'

    manifest += '\nSETTINGS:\n'
    manifest += 'prefer-online\n'

    manifest += f'\n# Hash: {hasher.hexdigest().upper()}'

    return manifest


def get_all_manifest():
    hasher = hashlib.md5()

    manifest = 'CACHE MANIFEST\n\n'
    manifest += 'CACHE:\n'

    for path, subdirs, files in os.walk(os.path.join(CWD, 'exploits')):
        for filename in files:
            if filename not in ('meta.json', 'PUT EXPLOITS HERE'):
                with open(os.path.join(path, filename), 'rb') as buf:
                    data = buf.read()
                hasher.update(data)
                manifest += '../..{}\n'.format(quote(os.path.join(path, filename).replace(CWD, '').replace('\\', '/'), safe=';,/?:@&=+$-_.!~*\'()#'))

    manifest += '\nNETWORK:\n'
    manifest += '*\n'

    manifest += f'\n# Hash: {hasher.hexdigest().upper()}'

    return manifest


def get_category_manifest(category):
    hasher = hashlib.md5()

    manifest = 'CACHE MANIFEST\n\n'
    manifest += 'CACHE:\n'

    for path, subdirs, files in os.walk(os.path.join(CWD, 'exploits', category)):
        for filename in files:
            if filename != 'meta.json':
                with open(os.path.join(path, filename), 'rb') as buf:
                    data = buf.read()
                hasher.update(data)
                manifest += '../../..{}\n'.format(quote(os.path.join(path, filename).replace(CWD, '').replace('\\', '/'), safe=';,/?:@&=+$-_.!~*\'()#'))

    manifest += '\nNETWORK:\n'
    manifest += '*\n'

    manifest += f'\n# Hash: {hasher.hexdigest().upper()}'

    return manifest


def get_entry_manifest(category, entry):
    hasher = hashlib.md5()

    manifest = 'CACHE MANIFEST\n\n'
    manifest += 'CACHE:\n'

    for path, subdirs, files in os.walk(os.path.join(CWD, 'exploits', category, entry)):
        for filename in files:
            if filename != 'meta.json':
                with open(os.path.join(path, filename), 'rb') as buf:
                    data = buf.read()
                hasher.update(data)
                manifest += '../../../..{}\n'.format(quote(os.path.join(path, filename).replace(CWD, '').replace('\\', '/'), safe=';,/?:@&=+$-_.!~*\'()#'))

    manifest += '\nNETWORK:\n'
    manifest += '*\n'

    manifest += f'\n# Hash: {hasher.hexdigest().upper()}'

    return manifest


def main():
    parser = argparse.ArgumentParser(description='PS4 Exploit Host Static Builder')
    parser.add_argument('--output', dest='output', action='store',
                        default=os.path.join(CWD, 'output'),
                        required=False, help='Specify a output location')
    parser.add_argument('--settings', dest='settings', action='store',
                        default=os.path.join(CWD, 'settings.json'),
                        required=False, help='Specify a settings file')
    args = parser.parse_args()

    try:
        shutil.rmtree(args.output)
    except NotADirectoryError:
        print('Error, specified location already exists as a file')
        sys.exit(1)
    except FileNotFoundError:
        pass
    while os.path.exists(args.output):
        pass
    os.makedirs(args.output)

    # --- Add APIs --------------------------------------------------------------
    os.makedirs(os.path.join(args.output, 'api'))

    # Generate Menu
    menu = get_menu()

    # Add /api/menu
    with open(os.path.join(args.output, 'api', 'menu.json'), 'w+', encoding='utf-8') as buf:
        buf.write(json.dumps(menu, sort_keys=True))

    # Add /api/settings
    with open(os.path.join(args.output, 'api', 'theme_settings.json'), 'w+', encoding='utf-8') as buf:
        buf.write(json.dumps(get_theme_settings(args.settings), sort_keys=True))

    # --- Add theme redirector --------------------------------------------------
    with open(os.path.join(args.output, 'index.html'), 'w+', encoding='utf-8') as buf:
        buf.write('<!DOCTYPE html><html><head><meta charset="utf-8"><title>Theme Loader</title></head><body><script>"use strict";window.addEventListener("load",function(){var a=new Date;a.setTime(a.getTime()+3153600000000);var b=a.toUTCString();2!=="; ".concat(document.cookie).split("; theme=").length&&(document.cookie="theme=Default; expires=".concat(b,"; domain=").concat(window.location.hostname,"; path=").concat(window.location.pathname,";"));var c=new XMLHttpRequest;c.open("GET","./themes/".concat("; ".concat(document.cookie).split("; theme=").pop().split(";").shift(),"/index.html"),!0),c.onload=function(){200<=c.status&&400>c.status?(window.history.replaceState({location:decodeURIComponent(window.location.hash.substr(1)),modal:!1},null,window.location.hash?window.location.hash:" "),document.open(),document.write(c.responseText),document.close()):"Default"==="; ".concat(document.cookie).split("; theme=").pop().split(";").shift()?alert("Error retrieving default theme data. Check your setup."):(document.cookie="theme=Default; expires=".concat(b,"; domain=").concat(window.location.hostname,"; path=").concat(window.location.pathname,";"),navigator.onLine?alert("Error retrieving theme data, resetting theme to default and reloading."):alert("Error retrieving theme data, you are currently offline, it is likely you switched to a theme that you have yet to use while online (So it is not cached). Resetting theme to default and reloading."),window.location.reload())},c.onerror=function(){"Default"==="; ".concat(document.cookie).split("; theme=").pop().split(";").shift()?alert("Error retrieving default theme data. Check your setup."):(document.cookie="theme=Default; expires=".concat(b,"; domain=").concat(window.location.hostname,"; path=").concat(window.location.pathname,";"),navigator.onLine?alert("Error retrieving theme data, resetting theme to default and reloading."):alert("Error retrieving theme data, you are currently offline, it is likely you switched to a theme that you have yet to use while online (So it is not cached). Resetting theme to default and reloading."),window.location.reload())},c.send()});</script></body></html>')

    # --- Add blank.html --------------------------------------------------------
    with open(os.path.join(args.output, 'blank.html'), 'w+', encoding='utf-8') as buf:
        buf.write('<!DOCTYPE html><html><head><meta charset="utf-8"><title>Deus Machina</title></head><body><pre>ZmzJCgLnJ43j2FK4NUR/EmFc7hJRN7Ub4adlqCRLfsXoswDsjyvn5vGwLj2FZdOlVLNmi/l0mjiuHgCYSZqPSndVhg6U8ODSl1+/aDxQLZE=</pre></body></html>')

    # --- Copy News -------------------------------------------------------------
    shutil.copy(os.path.join(CWD, 'news.json'), os.path.join(args.output, 'news.json'))

    # --- Copy Themes------------------------------------------------------------
    shutil.copytree(os.path.join(CWD, 'themes'), os.path.join(args.output, 'themes'))

    # --- Copy Exploits ---------------------------------------------------------
    shutil.copytree(os.path.join(CWD, 'exploits'), os.path.join(args.output, 'exploits'))

    # --- Add Cachers -----------------------------------------------------------

    os.makedirs(os.path.join(args.output, 'cache', 'theme'))
    os.makedirs(os.path.join(args.output, 'cache', 'all'))
    os.makedirs(os.path.join(args.output, 'cache', 'category'))
    os.makedirs(os.path.join(args.output, 'cache', 'entry'))

    # Theme Cacher
    with open(os.path.join(args.output, 'cache', 'theme', 'index.html'), 'w+', encoding='utf-8') as buf:
        buf.write('<!DOCTYPE html><html manifest="./../../themes.manifest"><head><meta charset="utf-8"><title>Cacher</title></head><body><script>"use strict";try{window.applicationCache.ondownloading=function(){parent.cacheInterface("ondownloading-theme")},window.applicationCache.onprogress=function(a){parent.cacheProgress(Math.round(100*(a.loaded/a.total)))},window.applicationCache.oncached=function(){parent.cacheInterface("oncached-theme")},window.applicationCache.onupdateready=function(){parent.cacheInterface("onupdateready-theme")},window.applicationCache.onnoupdate=function(){parent.cacheInterface("onnoupdate-theme")},window.applicationCache.onerror=function(){parent.cacheInterface("onerror-theme")},window.applicationCache.onobsolete=function(){parent.cacheInterface("onobsolete-theme")}}catch(a){parent.cacheInterface("onerror-appcache")}</script></body></html>')

    # All Cacher
    with open(os.path.join(args.output, 'cache', 'all', 'index.html'), 'w+', encoding='utf-8') as buf:
        buf.write('<!DOCTYPE html><html manifest="./offline.manifest"><head><meta charset="utf-8"><title>Cacher</title></head><body><script>"use strict";try{window.applicationCache.ondownloading=function(){parent.cacheInterface("ondownloading")},window.applicationCache.onprogress=function(a){parent.cacheProgress(Math.round(100*(a.loaded/a.total)))},window.applicationCache.oncached=function(){parent.cacheInterface("oncached")},window.applicationCache.onupdateready=function(){parent.cacheInterface("onupdateready")},window.applicationCache.onnoupdate=function(){parent.cacheInterface("onnoupdate")},window.applicationCache.onerror=function(){parent.cacheInterface("onerror")},window.applicationCache.onobsolete=function(){parent.cacheInterface("onobsolete")}}catch(a){parent.cacheInterface("onerror-appcache")}</script></body></html>')

    # Category Cachers
    for category in menu:
        os.makedirs(os.path.join(args.output, 'cache', 'category', category))
        with open(os.path.join(args.output, 'cache', 'category', category, 'index.html'), 'w+', encoding='utf-8') as buf:
            buf.write('<!DOCTYPE html><html manifest="./offline.manifest"><head><meta charset="utf-8"><title>Cacher</title></head><body><script>"use strict";try{window.applicationCache.ondownloading=function(){parent.cacheInterface("ondownloading")},window.applicationCache.onprogress=function(a){parent.cacheProgress(Math.round(100*(a.loaded/a.total)))},window.applicationCache.oncached=function(){parent.cacheInterface("oncached")},window.applicationCache.onupdateready=function(){parent.cacheInterface("onupdateready")},window.applicationCache.onnoupdate=function(){parent.cacheInterface("onnoupdate")},window.applicationCache.onerror=function(){parent.cacheInterface("onerror")},window.applicationCache.onobsolete=function(){parent.cacheInterface("onobsolete")}}catch(a){parent.cacheInterface("onerror-appcache")}</script></body></html>')

        # Entry Cachers
        for entry in menu[category]['entries']:
            os.makedirs(os.path.join(args.output, 'cache', 'entry', category, entry))
            with open(os.path.join(args.output, 'cache', 'entry', category, entry, 'index.html'), 'w+', encoding='utf-8') as buf:
                buf.write('<!DOCTYPE html><html manifest="./offline.manifest"><head><meta charset="utf-8"><title>Cacher</title></head><body><script>"use strict";try{window.applicationCache.ondownloading=function(){parent.cacheInterface("ondownloading")},window.applicationCache.onprogress=function(a){parent.cacheProgress(Math.round(100*(a.loaded/a.total)))},window.applicationCache.oncached=function(){parent.cacheInterface("oncached")},window.applicationCache.onupdateready=function(){parent.cacheInterface("onupdateready")},window.applicationCache.onnoupdate=function(){parent.cacheInterface("onnoupdate")},window.applicationCache.onerror=function(){parent.cacheInterface("onerror")},window.applicationCache.onobsolete=function(){parent.cacheInterface("onobsolete")}}catch(a){parent.cacheInterface("onerror-appcache")}</script></body></html>')

    # --- Add Manifests ---------------------------------------------------------

    # Theme Manifest
    with open(os.path.join(args.output, 'themes.manifest'), 'w+', encoding='utf-8') as buf:
        buf.write(get_themes_manifest())

    # All Manifest
    with open(os.path.join(args.output, 'cache', 'all', 'offline.manifest'), 'w+', encoding='utf-8') as buf:
        buf.write(get_all_manifest())

    # Category Manifests
    for category in menu:
        with open(os.path.join(args.output, 'cache', 'category', category, 'offline.manifest'), 'w+', encoding='utf-8') as buf:
            buf.write(get_category_manifest(category))

        # Entry Manifests
        for entry in menu[category]['entries']:
            with open(os.path.join(args.output, 'cache', 'entry', category, entry, 'offline.manifest'), 'w+', encoding='utf-8') as buf:
                buf.write(get_entry_manifest(category, entry))

    # --- Cleanup ---------------------------------------------------------------

    # Delete all meta.json files
    for path, subdirs, files in os.walk(os.path.join(args.output, 'exploits')):
        for filename in files:
            if filename == 'meta.json':
                os.remove(os.path.join(path, filename))

    # Delete all *.es6 files from theme's folder
    for path, subdirs, files in os.walk(os.path.join(args.output, 'themes')):
        for filename in files:
            if filename.endswith('.es6'):
                os.remove(os.path.join(path, filename))

    # Delete "PUT EXPLOITS HERE" file
    try:
        os.remove(os.path.join(args.output, 'exploits', 'PUT EXPLOITS HERE'))
    except FileNotFoundError:
        pass

    # TODO: Minify HTML, JS, and CSS

    print('\nDone!')


if __name__ == '__main__':
    main()

# Copyright (c) 2017-2022 Al Azif, https://github.com/Al-Azif/ps4-exploit-host

# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:

# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
