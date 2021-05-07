# -*- coding: utf-8 -*-

"""
@File    : LatexToFunctions.py
@Author  : Hangcheng
@Email   : megamhc@gmail.com
@Time    : 2021/4/26 10:19
"""

from pyparsing import *
import sympy
import math

one_original = "\varepsilon_{1}=\frac{\sigma_{1}}{E_{\mathrm{y}}}+\gamma_{\mathrm{1}}+\gamma_{2}"
one_all = "varepsilon_{1}=frac{sigma_{1}}{E_{y}}+gamma_{1}+gamma_{2}"

two_original = "A_{1}=\frac{\sigma_{ys}\left(1+\varepsilon_{ys}\right)}{\left(\ln \left[1+\varepsilon_{ys}\right]\right)^{m_{1}}}"
two_all = "A_{1}=\\frac{\sigma_{ys}(1+\\varepsilon_{ys})}{(\(ln(1+\\varepsilon_{ys}))^{m_{1}}} "

three_all = "\sigma_{1}=0.5\left(\sigma_{thetam}+\sigma_{sm}+\sqrt{(\sigma_{thetam}-\sigma_{sm}right)^{2}+4tau^{2}}right)"
three_original = "\sigma_{1}=0.5\left(\sigma_{theta m }+\sigma_{ sm }+\sqrt{\left(\sigma_{thetam}-\sigma_{ sm }right)^{2}+4 tau^{2}}right)"


class Formula:

    def __init__(self, latex):
        self.latexText = latex
        bias = {"\\": "", "\f": "f", "\a": "a", "\b": "b", "\n": "n", "\v": "v", "\t": "v", "\r": "r", "left": "",
                "right": "", "[": "(", "]": ")", " ": ""}  # 所有可能产生歧义的字符，如转义、反斜杠、空格
        # 预处理
        for bia in bias.keys():
            if bia in self.latexText:
                self.latexText = self.latexText.replace(bia, bias[bia])
        # 特殊运算符号
        self.Symbol = Literal('frac') | Literal("ln") | Literal("^") | Literal("cos") | Literal("sin") | Literal(
            "tan") | Literal("sqrt") | Literal("tanh")  # 计算符号
        # 基本运算符号
        equal = Literal("=")  # 等于
        plus = Literal("+")  # 加
        minus = Literal("-")  # 减
        # 主要参数
        NumPara = Combine(Word(nums) + Optional('.' + Word(nums)))  # 整数和小数
        AlphaPara = Combine(Word(alphas) + Optional("_{" + Word(alphanums) + "}")).ignore(self.Symbol)  # 字母、带有脚标的字母
        Para = (NumPara | AlphaPara).ignore(self.Symbol)
        formula = self.Symbol | NumPara | AlphaPara | equal | minus | plus | "(" | ")" | "{" | "}"  # 公式中包含的各个元素
        # 公式、参数和特殊运算符
        self.formulaTokens = formula.searchString(self.latexText)  # 输出公式中的参数和运算符号
        self.ParaTokens = Para.searchString(self.latexText)  # 所有参数
        self.SymbolTokens = self.Symbol.searchString(self.latexText)


f = Formula(latex=one_original)
print("简化后的公式：{}".format(f.latexText))
print("计算流程：{}".format(f.formulaTokens))
print("参数：{}".format(f.ParaTokens))
print("特殊运算符：{}".format(f.SymbolTokens))
