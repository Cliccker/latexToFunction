# -*- coding: utf-8 -*-

"""
@File    : LatexToFunctions.py
@Author  : Hangcheng
@Email   : megamhc@gmail.com
@Time    : 2021/4/26 10:19
"""
import pyparsing
from pyparsing import *

one_original = "\varepsilon_{1}=\frac{\sigma_{1}}{E_{\mathrm{y}}}+\gamma_{\mathrm{1}}+\gamma_{2}"
one_all = "\\varepsilon_{1}=\\frac{\sigma_{1}}{E_{y}}+\gamma_{1}+\gamma_{2}"


two_original = "A_{1}=\frac{\sigma_{ys}\left(1+\varepsilon_{ys}\right)}{\left(\ln \left[1+\varepsilon_{ys}\right]\right)^{m_{1}}}"
two_all = "A_{1}=\\frac{\sigma_{ys}(1+\\varepsilon_{ys})}{(\ln(1+\\varepsilon_{ys}))^{m_{1}}} "


paraWithFoot = Word(alphas) + "_{" + Word(alphanums) + "}"  # 有脚标参数
parameter = Word(alphanums)  # 无脚标参数
equal = Literal("=")  # 等于
plus = Literal("+")  # 加
leftBrackets = Literal("(")  # 左括号
rightBrackets = Literal(")")  # 右括号
formula = paraWithFoot | parameter | equal | plus | leftBrackets | rightBrackets
formulaTokens = formula.searchString(one_all)  # 寻找所有参数
print(formulaTokens)
