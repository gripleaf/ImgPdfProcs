#! /usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'gripleaf'

import random


def __gen_random_key(charset, len):
    key = ""
    for i in range(len):
        key += charset[random.randint(0, len - 1)]
    return key


def gen_num_key(len):
    return __gen_random_key("0123456789", len)


def gen_char_key(len):
    return __gen_random_key("abcdefghijklmnopqrstuvwxyz", len)


def gen_char_key(len):
    return __gen_random_key("abcdefghijklmnopqrstuvwxyz0123456789", len)
