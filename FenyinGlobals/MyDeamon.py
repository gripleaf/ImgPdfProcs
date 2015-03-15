#! /usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'gripleaf'
import os
import sys
import atexit
import logging
import subprocess


def del_all_pids(pidPath):
    pidfiles = os.listdir(pidPath)
    for pidfile in pidfiles:
        full_file = os.path.join(pidPath, pidfile)
        if os.path.isfile(full_file):
            try:
                pid = open(full_file, "r").read()
                print "killing", pid.replace("\n", ""), "..."
                subprocess.call("kill -9 " + pid, shell=True)
                os.remove(full_file)
            except Exception, e:
                print e.message
    print "***CLEAR***"


def daemonize(pid_file, main):
    cwd = os.getcwd()

    try:
        pid = os.fork()
        if pid > 0:  # father thread exit
            sys.exit(0)
    except OSError, e:
        sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
        sys.exit(1)

    # decoup from parent environment
    os.chdir(cwd)
    os.setsid()
    os.umask(0)

    try:
        pid = os.fork()
        if pid > 0:  # father thread exit
            sys.exit(0)
    except OSError, e:
        sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
        sys.exit(1)

    def delpid():
        os.remove(pid_file)

    # 注册程序退出时的函数，即删掉pid文件
    atexit.register(delpid)
    pid = str(os.getpid())
    try:
        open(pid_file, 'w').write("%s\n" % pid)
    except IOError, ioe:
        logging.warning(ioe.message)

    # redirect standard file descriptors
    sys.stdout.flush()
    sys.stderr.flush()
    si = file("/dev/null", "r")
    so = file("/dev/null", "w")
    se = file("/dev/null", "w")
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())

    # write pid file
    main()

