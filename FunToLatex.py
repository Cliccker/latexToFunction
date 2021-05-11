# -*- coding: utf-8 -*-

"""
@File    : FunToLatex.py
@Author  : Hangcheng
@Email   : megamhc@gmail.com
@Time    : 2021/5/11 10:53
"""

import latexify

import math
import latexify

@latexify.with_latex
def f(a,b):
    return ((1 / (a + 2)) + 1) / b

print(f)