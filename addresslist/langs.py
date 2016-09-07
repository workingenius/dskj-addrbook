# -*- coding:utf8 -*-

import re

from pypinyin import lazy_pinyin


ch_py_ptn = re.compile(r'[^a-zA-Z]')


def ch_pinyin(text):
    py = ''.join(lazy_pinyin(text))
    py = py.upper()
    py = py.replace(' ', '')
    return ch_py_ptn.sub('~', py)  # '~' gt 'z'
