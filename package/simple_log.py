#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime


def log(context, filename='./log/default.log'):
    print(context)
    with open(filename, 'a') as f:
        f.write('%s: %s\n' % (datetime.now(), context))
