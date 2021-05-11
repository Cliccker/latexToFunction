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
def f(a, b, c, d, e):
    return 0.52 * ((a + b) - math.sqrt((c - d) ** 2 + 4 * e ** 2))


print(f)
