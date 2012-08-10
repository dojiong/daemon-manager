#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    daemon-manager.dm
    ~~~~~~~~~~~~~~~~

    client tool for daemon-manager server.

    :copyright: (c) 2012 by Du Jiong.
    :license: BSD, see LICENSE for more details.
'''
import re
import json
import sys
import os
from datetime import datetime
import argparse


class DM(object):
    def __init__(self):
        user_home = os.path.expanduser('~')
        self.home = os.path.join(user_home, '.dm')
        self.home_file = lambda x: os.path.join(self.home, x)
        if not os.path.exists(self.home):
            os.mkdir(self.home)
        elif os.path.isfile(self.home):
            raise OSError('daemon-manager\'s home directory can\'t be created')

    def get_daemons(self):
        files = os.listdir(self.home)
        dm_r = re.compile(r'^(\d+)\.dm$')
        dm_files = filter(lambda x: dm_r.match(x), files)
        daemons = {}
        for fname in dm_files:
            pid, _ = fname.split('.', 1)
            try:
                data = json.loads(file(self.home_file(fname)).read())
            except:
                try:
                    os.unlink(self.home_file(fname))
                except OSError:
                    pass
                continue
            cmdline_path = '/proc/%s/cmdline' % pid
            if os.path.isfile(cmdline_path):
                try:
                    cmdline = file(cmdline_path).read()
                except OSError:
                    continue
                cmdline = cmdline.replace('\x00', ' ').strip()
                if cmdline == data['cmd'].encode('utf8'):
                    daemons[int(pid)] = data
                    continue
            os.unlink(self.home_file(fname))
        return daemons

    def run(self, cmd, logfile=None, chdir=None):
        cmd = cmd.strip()
        if chdir and not os.path.isdir(chdir):
            raise OSError('no such directory: %s' % chdir)
        pid = os.fork()
        if pid < 0:
            raise OSError('create subprocess fail')
        elif pid == 0:
            if chdir:
                os.chdir(chdir)
            os.umask(0)
            os.setsid()
            os.close(0)
            if logfile:
                f = file(logfile, 'a')
                os.dup2(f.fileno(), 1)
                os.dup2(f.fileno(), 2)
            else:
                os.close(1)
                os.close(2)
            args = cmd.split()
            os.execlp(args[0], *args)
            os._exit(-1)
        else:
            dm = file(self.home_file('%d.dm' % pid), 'w')
            dm.write(json.dumps(
                {'cmd': cmd, 'logfile': logfile, 'chdir': chdir,
                 'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}))
            dm.close()
            print 'daemon created, pid:', pid

    def list(self):
        daemons = self.get_daemons()
        if len(daemons) == 0:
            print 'no daemons'
            return
        for pid, dm in daemons.items():
            print 'pid: %d, cmd: %s' % (pid, repr(dm['cmd'].encode('utf8'))),
            if dm['logfile']:
                print ', logfile: %s' % repr(dm['logfile'].encode('utf8')),
            if dm['chdir']:
                print ', chdir: %s' % repr(dm['chdir'].encode('utf8')),
            print ', start at: "%s"' % dm['time']


def main():
    #command line arguments parser
    args_parser = argparse.ArgumentParser(
        description='client tool for daemon-manager')
    sub_parsers = args_parser.add_subparsers(dest='dmcmd')

    run_parser = sub_parsers.add_parser('run', help='start a daemon')
    run_parser.add_argument(dest='cmd',
        help='cmd to run', metavar='commandline')
    run_parser.add_argument('-o', '--stdout', default=None,
        dest='logfile', help='output log file', metavar='log_file')
    run_parser.add_argument('-c', '--chdir', default=None,
        dest='chdir', help='chdir to run', metavar='dir')

    sub_parsers.add_parser('list', help='list daemons')

    dm = DM()
    args = args_parser.parse_args(sys.argv[1:])

    if args.dmcmd == 'run':
        dm.run(args.cmd, args.logfile)
    elif args.dmcmd == 'list':
        dm.list()
