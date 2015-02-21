# -*- coding: utf-8 -*-
"""Copyright (c) 2015 Sergio Gabriel Teves
All rights reserved.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.

"""
import os
import subprocess
import logging
import dateutil.parser
import collections
import xml.etree.ElementTree
import re

_logger = logging.getLogger('svnclient')

class ClientNotifyAction:
    noadded = '?'
    added = 'A'
    deleted = 'D'
    updated = 'U'
    conflict = 'C'
    merged = 'G'
    existed = 'E'
    replaced = 'R'
    missing = '!'
    unversioned = 'X'
    obstructed = '~'
    
notify_action = ClientNotifyAction()

class ClientError(Exception):
    pass

class Client:

    _cache_auth = False
    _default_username = None
    _default_password = None
    _location = None
    _trust_server_cert = False
    
    def __init__(self, location, username=None, password=None):
        self._location = location
        self._default_username = username
        self._default_password = password

    def _mask_command_password(self, cmd):
        p = '--password\s(.+)\s'
        s = re.search(p, cmd)
        if s:
            lidx = s.group(1).find(' ')
            return re.sub(s.group(1)[:lidx],'*', cmd)
        return cmd
    
    def _run_command(self, subcommand, args, combine=True):
        #if os.name == "posix":
        #    command = '{ svn ' + cmd + '; } 2>&1'
        #else:
        #    command = 'svn ' + cmd + ' 2>&1'
        cmd = ['svn', subcommand, '--non-interactive']
        if self._trust_server_cert is True:
            cmd += ['--trust-server-cert']
        cmd += args
        runcmd = " ".join(cmd)
        _logger.debug("RUN: %s" % (self._mask_command_password(runcmd),))
        p = subprocess.Popen(runcmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        (stdout, stderr) = p.communicate()
        
#        if p.returncode != 0:
#            raise ClientError("Command failed with (%d): %s\n%s\n%s" % (p.returncode, " ".join(cmd), stdout, stderr))
        if stderr:
            errmsg = "Command failed with (%d): %s\n%s\n%s" % (p.returncode, runcmd, stdout, stderr)
            errmsg = self._mask_command_password(errmsg)
            raise ClientError(errmsg)
            #raise ClientError(stderr.decode('ASCII'))

        s = stdout.decode('ASCII')
        return s if combine is True else s.split('\n')

    def set_trust_server_cert(self, b):
        self._trust_server_cert = b
        
    def set_username(self, username):
        self._default_username = username

    def set_password(self, password):
        self._default_password = password

    def _parse_output(self, lines):
        output = []
        for line in lines:
            _logger.debug(line)
            m = re.match('^([a-z|\s|\?|\!|\~|\+|\*])\s+(.*)$', line, re.IGNORECASE | re.UNICODE)
            if m:
                action, fileline = m.groups()
                output.append({'action': action, 'path': fileline})
        return output

    def _get_revision(self, line):
        m = re.match('^(.*)\s(\d+).*$', line, re.UNICODE)
        if m:
            return m.group(2)
        return None
    
    def status(self):
        resp = self._run_command('status', [self._location], combine=False)
        if len(resp) > 1:        
            return self._parse_output(resp)
        return None
        
    def update(self, revision=None, force=False):
        cmd = []

        if revision is not None:
            cmd += ['-r', str(revision)]

        if force is True:
            cmd += ['--accept','theirs-full']
            
        if self._default_username is not None:
            cmd += ['--username', self._default_username]
            cmd += ['--password', self._default_password]
            if self._cache_auth is False:
                cmd += ['--no-auth-cache']

        cmd += [self._location]

        resp = self._run_command('update', cmd, combine=False)
        if len(resp) > 1:
            rev = self._get_revision(resp[-2])
            return rev, self._parse_output(resp)
        return None

    def checkout(self, url, revision=None):
        cmd = []
        if revision is not None:
            cmd += ['-r', str(revision)]

        if self._default_username is not None:
            cmd += ['--username', self._default_username]
            cmd += ['--password', self._default_password]
            if self._cache_auth is False:
                cmd += ['--no-auth-cache']

        cmd += [url, self._location]

        resp = self._run_command('checkout', cmd, combine=False)
        if len(resp) > 1:
            rev = self._get_revision(resp[-2])
            return rev, self._parse_output(resp)
        return None

    def add(self, filelist):
        resp = self._run_command('add', filelist, combine=False)
        return self._parse_output(resp)

    def commit(self, message=None, encoding='utf-8'):
        cmd = []

        if self._default_username is not None:
            cmd += ['--username', self._default_username]
            cmd += ['--password', self._default_password]
            if self._cache_auth is False:
                cmd += ['--no-auth-cache']
                
        if message is not None:
            cmd += ['--message', '"%s"' % message]

        if encoding is not None:
            cmd += ['--encoding',encoding]

        cmd += [self._location]
        
        resp = self._run_command('commit', cmd, combine=False)
        _logger.debug("%s" % ("\n".join(resp),))
        if len(resp) > 1:
            return self._get_revision(resp[-2])
        return None

    def info(self):
        cmd = ['--xml']
        if self._default_username is not None:
            cmd += ['--username', self._default_username]
            cmd += ['--password', self._default_password]
            if self._cache_auth is False:
                cmd += ['--no-auth-cache']
        cmd += [self._location]
        result = self._run_command(
                    'info', 
                    cmd, 
                    combine=True)

        root = xml.etree.ElementTree.fromstring(result)

        entry_attr = root.find('entry').attrib
        commit_attr = root.find('entry/commit').attrib

        relative_url = root.find('entry/relative-url')
        author = root.find('entry/commit/author')
        wcroot_abspath = root.find('entry/wc-info/wcroot-abspath')
        wcinfo_schedule = root.find('entry/wc-info/schedule')
        wcinfo_depth = root.find('entry/wc-info/depth')

        info = {        
            'entry_kind': entry_attr['kind'],
            'entry_path': entry_attr['path'],
            'entry_revision': int(entry_attr['revision']),
            'url': root.find('entry/url').text,

            'relative_url': relative_url.text \
                                if relative_url is not None and \
                                   len(relative_url) \
                                else None,

            'repository_root': root.find('entry/repository/root').text,
            'repository_uuid': root.find('entry/repository/uuid').text,

            'wcinfo_wcroot_abspath': wcroot_abspath.text \
                                        if wcroot_abspath is not None and \
                                           len(wcroot_abspath) \
                                        else None,
            'wcinfo_schedule': wcinfo_schedule.text \
                                    if wcinfo_schedule is not None and \
                                       len(wcinfo_schedule) \
                                    else None,
            'wcinfo_depth': wcinfo_depth.text \
                                    if wcinfo_depth is not None and \
                                       len(wcinfo_depth) \
                                    else None,
            'commit_author': author.text \
                                    if author is not None and \
                                       len(author) \
                                    else None,
            'commit_date': dateutil.parser.parse(
                            root.find('entry/commit/date').text),
            'commit_revision': int(commit_attr['revision']),
        }

        return info
    
    def get_remote_url(self):
        return self.info()['url']
        
    def get_local_path(self):
        return self._location

    def cleanup(self):
        self._run_command('cleanup', [self._location], combine=True)
        
    def relocate(self, currentUrl, newUrl):
        cmd = ['--relocate']
        if self._default_username is not None:
            cmd += ['--username', self._default_username]
            cmd += ['--password', self._default_password]
            if self._cache_auth is False:
                cmd += ['--no-auth-cache']
        cmd += [self.parseurl(currentUrl), self.parseurl(newUrl), self._location]
        self._run_command('sw', cmd, combine=False)
    
    def parseurl(self, url):
        from urlparse import urlparse
        p = urlparse(url)
        return '%s://%s' % (p.scheme, p.netloc)
    
    def revert(self, filelist=None):
        cmd = []

        if self._default_username is not None:
            cmd += ['--username', self._default_username]
            cmd += ['--password', self._default_password]
            if self._cache_auth is False:
                cmd += ['--no-auth-cache']
        
        if filelist is not None:
            cmd += filelist
        
        _logger.debug(self._run_command('revert', cmd, combine=True))
