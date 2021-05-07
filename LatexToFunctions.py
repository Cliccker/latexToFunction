# -*- coding: utf-8 -*-

"""
@File    : LatexToFunctions.py
@Author  : Hangcheng
@Email   : megamhc@gmail.com
@Time    : 2021/4/26 10:19
"""

import sympy
from pyparsing import *
import math

one_original = "\varepsilon_{1}=\frac{\sigma_{1}}{E_{\mathrm{y}}}+\gamma_{\mathrm{1}}+\gamma_{2}"
one_all = "varepsilon_{1}=frac{sigma_{1}}{E_{y}}+gamma_{1}+gamma_{2}"

two_original = "A_{1}=\frac{\sigma_{ys}\left(1+\varepsilon_{ys}\right)}{\left(\ln \left[1+\varepsilon_{ys}\right]\right)^{m_{1}}}"
two_all = "A_{1}=\\frac{\sigma_{ys}(1+\\varepsilon_{ys})}{(\(ln(1+\\varepsilon_{ys}))^{m_{1}}} "

three_all = "\sigma_{1}=0.5\left(\sigma_{thetam}+\sigma_{sm}+\sqrt{(\sigma_{thetam}-\sigma_{sm}right)^{2}+4tau^{2}}right)"
three_original = "\sigma_{1}=0.5\left(\sigma_{theta m }+\sigma_{ sm }+\sqrt{\left(\sigma_{theta_{ m }}-\sigma_{ sm }right)^{2}+4 tau^{2}}right)"


def HandleLatex(latexText):
    """
    预处理latex公式
    :param latexText: 公式
    """
    mathrm = Word("mathrm") + "{" + Word(alphanums) + "}"  # 新罗马字体
    mathrmTokens = mathrm.searchString(latexText)
    print(mathrmTokens)


HandleLatex(three_original)


class Formula:

    def __init__(self, latexText):
        self.latexText = latexText.replace(" ", "")  # 去除所有空格
        self.latexText = self.latexText.replace("\\", "")  # 去除反斜杠
        self.latexText = self.latexText.replace("left", "")
        self.latexText = self.latexText.replace("right", "")  # 去除标识符
        print(self.latexText)

        # 特殊运算符号
        self.Symbol = Word('frac') | "ln" | Literal("^") | "cos" | "sin" | "tan" | "sqrt" | "tanh"  # 计算符号
        # 基本运算符号
        equal = Literal("=")  # 等于
        plus = Literal("+")  # 加
        minus = Literal("-")  # 减
        # 主要参数
        MainPara = Combine(Word(nums) + Optional('.' + Word(nums))) | Word(alphas)  # 字母、整数和小数
        para = Combine(MainPara + Optional("_{" + Word(alphanums) + "}")).ignore(self.Symbol)  # 是否带有脚标
        # 格式
        formula = self.Symbol | para | equal | minus | plus | "(" | ")" | "{" | "}"  # 公式中包含的各个元素
        part = delimitedList(printables, delim="+", combine=True)
        self.formulaTokens = formula.searchString(self.latexText)  # 输出公式中的参数和运算符号
        self.paraTokens = para.searchString(self.latexText)  # 所有参数
        self.partTokens = part.searchString(self.latexText)


print(Formula(latexText=three_original).partTokens)
