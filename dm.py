#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    daemon-manager.dm
    ~~~~~~~~~~~~~~~~

    client tool for daemon-manager server.

    :copyright: (c) 2012 by Du Jiong.
    :license: BSD, see LICENSE for more details.
'''

import sys
import os
from datetime import datetime
import time
import argparse
import signal
import fcntl

try:
    import cPickle as pickle
except ImportError:
    import pickle


user_home = os.path.expanduser('~')
dm_home = os.path.join(user_home, '.dm')
dm_home_file = os.path.join(dm_home, '.dmlock')


def file_lock(func):
    def infunc(*argv, **kwargv):
        f = file(dm_home_file, 'a')
        fcntl.lockf(f, fcntl.LOCK_EX)
        try:
            func(*argv, **kwargv)
        finally:
            fcntl.lockf(f, fcntl.LOCK_UN)
            f.close()
            try:
                os.unlink(dm_home_file)
            except OSError:
                pass
    return infunc


class Daemon(object):
    def __init__(self, cmdline, logfile=None,
            chdir=None, name=None, group=None, **ignore):
        if chdir and not os.path.isdir(chdir):
            raise OSError('no such directory: "%s"' % chdir)
        self.cmdline = cmdline.strip()
        self.proc_cmdline = self.cmdline
        self.logfile = logfile
        self.chdir = chdir
        self.name = name
        self.group = group
        self.pid = None
        if self.chdir:
            self.dir = self.chdir
        else:
            self.dir = os.getcwd()

    @staticmethod
    def load(dm_path):
        try:
            return pickle.load(file(dm_path))
        except:
            try:
                os.unlink(dm_path)
            except OSError:
                pass

    def run(self):
        self_cmdline = self.get_cmdlime(os.getpid())
        pid = os.fork()
        if pid < 0:
            raise OSError('create subprocess fail')
        elif pid == 0:
            if self.chdir:
                os.chdir(self.chdir)
            os.umask(0)
            os.setsid()
            os.close(0)
            if self.logfile:
                f = file(self.logfile, 'a', 0)
                os.dup2(f.fileno(), 1)
                os.dup2(f.fileno(), 2)
            else:
                os.close(1)
                os.close(2)
            args = self.cmdline.split()
            os.execlp(args[0], *args)
            os._exit(-1)
        else:
            self.pid = pid
            self.time = datetime.now().strftime('%Y-%m-%d %H:%m:%S')
            while True:
                cmdline = self.get_cmdlime(pid)
                if cmdline is None or cmdline != self_cmdline:
                    break
                time.sleep(0.05)
            if cmdline is None:
                raise OSError('daemon exit')
            self.proc_cmdline = cmdline
            return pid

    def is_alive(self):
        cmdline = self.get_cmdlime(self.pid)
        if cmdline == self.proc_cmdline:
            return True
        return False

    @staticmethod
    def get_cmdlime(pid):
        cmdline_path = '/proc/{0}/cmdline'.format(pid)
        if os.path.isfile(cmdline_path):
            try:
                cmdline = file(cmdline_path).read()
            except OSError:
                return False
            return cmdline.replace('\x00', ' ').strip().decode('utf8')


class DM(object):
    def __init__(self):
        user_home = os.path.expanduser('~')
        self.home = os.path.join(user_home, '.dm')
        self.home_file = lambda x: os.path.join(self.home, x)
        if not os.path.exists(self.home):
            os.mkdir(self.home)
        elif os.path.isfile(self.home):
            raise OSError('daemon-manager\'s home directory can\'t be created')

    def get_daemons(self, name=None, group=None):
        if name:
            dm_path = self.home_file('%s.dm' % name)
            dm = Daemon.load(dm_path)
            if dm:
                return {dm.name: dm}
            return {}
        files = os.listdir(self.home)
        dm_files = filter(lambda x: x.endswith('.dm'), files)
        daemons = {}
        for fname in dm_files:
            dm_path = self.home_file(fname)
            dm = Daemon.load(dm_path)
            if dm and dm.is_alive():
                if group is None or group == dm.group:
                    daemons[dm.name or dm.pid] = dm
                continue
            os.unlink(dm_path)
        return daemons

    @file_lock
    def run(self, cmdline, logfile=None,
            chdir=None, name=None, group=None):
        if name:
            dm_path = self.home_file('%s.dm' % name)
            if dm_path:
                dm = Daemon.load(dm_path)
                if dm and dm.is_alive():
                    print 'this named daemon is alive!'
                    return
        else:
            dm_path = None
        dm = Daemon(cmdline=cmdline, logfile=logfile, chdir=chdir,
            name=name, group=group)
        pid = dm.run()
        if pid > 0:
            print 'pid:', pid
            f = file(dm_path or self.home_file('%d.dm' % pid), 'wb')
            f.write(pickle.dumps(dm))
            f.close()
        else:
            print 'start daemon fail'

    @file_lock
    def list(self, name=None, group=None):
        daemons = self.get_daemons(name=name, group=group)
        if len(daemons) == 0:
            print 'no daemons'
            return
        for pid, dm in daemons.items():
            print 'pid: %d, cmd: %s' % (dm.pid, repr(dm.cmdline.encode('utf8'))),
            if dm.logfile:
                print ', logfile: %s' % repr(dm.logfile.encode('utf8')),
            if dm.chdir:
                print ', chdir: %s' % repr(dm.chdir.encode('utf8')),
            if dm.name:
                print ', name:', dm.name,
            if dm.group:
                print ', group:', dm.group,
            print ', start at: "%s"' % dm.time

    @file_lock
    def kill(self, name=None, group=None, quiet=False, sigkill=False):
        daemons = self.get_daemons(name, group)
        if len(daemons) > 0:
            print '%d daemon to kill' % len(daemons),
            if quiet == False:
                yn = raw_input(', are you sure? [Y/n]')
            else:
                yn = 'Y'
                print ''
            if len(yn) == 0 or yn.upper() == 'Y':
                for pid, dm in daemons.iteritems():
                    try:
                        if sigkill:
                            os.kill(dm.pid, signal.SIGKILL)
                        else:
                            os.kill(dm.pid, signal.SIGTERM)
                    except OSError:
                        pass
        else:
            print 'no daemons to kill'


def main():
    #command line arguments parser
    args_parser = argparse.ArgumentParser(
        description='client tool for daemon-manager')
    sub_parsers = args_parser.add_subparsers(dest='dmcmd')

    run_parser = sub_parsers.add_parser('run', help='start a daemon')
    run_parser.add_argument(dest='cmdline',
        help='cmdline to run', metavar='cmdline')
    run_parser.add_argument('-o', '--log', default=None,
        dest='logfile', help='output log file', metavar='log_file')
    run_parser.add_argument('-c', '--chdir', default=None,
        dest='chdir', help='chdir to run', metavar='dir')
    run_parser.add_argument('-n', '--name', default=None,
        dest='name', help='daemon name', metavar='name')
    run_parser.add_argument('-g', '--group', default=None,
        dest='group', help='daemon group', metavar='group')

    list_parser = sub_parsers.add_parser('list', help='list daemons')
    list_parser.add_argument('-n', '--name', default=None,
        dest='name', help='filter by daemon name', metavar='name')
    list_parser.add_argument('-g', '--group', default=None,
        dest='group', help='filter by daemon group', metavar='group')

    kill_parser = sub_parsers.add_parser(
        'kill', help='kill daemons, default to all')
    kill_parser.add_argument('-n', '--name', default=None,
        dest='name', help='filter by daemon name', metavar='name')
    kill_parser.add_argument('-g', '--group', default=None,
        dest='group', help='filter by daemon group', metavar='group')
    kill_parser.add_argument('-q', '--quiet', default=False,
        dest='quiet', help='quiet to kill, no prompt', action='store_true')
    kill_parser.add_argument('-9', default=False,
        dest='sigkill', help='use SIGKILL to kill', action='store_true')

    dm = DM()
    args = args_parser.parse_args(sys.argv[1:])

    if args.dmcmd == 'run':
        dm.run(cmdline=args.cmdline, logfile=args.logfile,
            name=args.name, group=args.group)
    elif args.dmcmd == 'list':
        dm.list(name=args.name, group=args.group)
    elif args.dmcmd == 'kill':
        dm.kill(name=args.name, group=args.group, quiet=args.quiet,
            sigkill=args.sigkill)

if __name__ == '__main__':
    main()
