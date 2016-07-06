#!/usr/bin/env python
#-*- coding: utf-8 -*-
${monkey}
import os
import sys
import getopt
import ConfigParser
import traceback
import daemonize
import ctypes
import timeit
import gevent
import multiprocessing
from multiprocessing import Pool as ProcessPool
from multiprocessing.dummy import Pool as ThreadPool
import ${app}_proto

libc = ctypes.CDLL('libc.so.6')

