# -*- coding: utf-8 -*-

"""
@File    : LatexToFunctions.py
@Author  : Hangcheng
@Email   : megamhc@gmail.com
@Time    : 2021/4/26 10:19
"""

from pyparsing import *
import math

one_original = "\varepsilon_{1}=\frac{\sigma_{1}}{E_{\mathrm{y}}}+\gamma_{\mathrm{1}}+\gamma_{2}"
one_all = "varepsilon_{1}=frac{sigma_{1}}{E_{y}}+gamma_{1}+gamma_{2}"

two_original = "A_{1}=\frac{\sigma_{ys}\left(1+\varepsilon_{ys}\right)}{\left(\ln \left[1+\varepsilon_{ys}\right]\right)^{m_{1}}}"
two_all = "A_{1}=\\frac{\sigma_{ys}(1+\\varepsilon_{ys})}{(\(ln(1+\\varepsilon_{ys}))^{m_{1}}} "

three_all = "\sigma_{1}=0.5\left(\sigma_{thetam}+\sigma_{sm}+\sqrt{(\sigma_{thetam}-\sigma_{sm}right)^{2}+4tau^{2}}right)"
three_original = "\sigma_{1}=0.5\left(\sigma_{theta m }+\sigma_{ sm }+\sqrt{\left(\sigma_{thetam}-\sigma_{ sm }right)^{2}+4 tau^{2}}right)"


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
        NumPara = Combine(Word(nums) + Optional('.' + Word(nums)))  # 整数和小数
        AlphaPara = Combine(Word(alphas) + Optional("_{" + Word(alphanums) + "}")).ignore(self.Symbol)  # 字母、带有脚标的字母
        # 格式
        Para = NumPara | AlphaPara
        formula = self.Symbol | NumPara | AlphaPara | equal | minus | plus | "(" | ")" | "{" | "}"  # 公式中包含的各个元素
        self.formulaTokens = formula.searchString(self.latexText)  # 输出公式中的参数和运算符号
        self.ParaTokens = Para.searchString(self.latexText)  # 所有参数


print(Formula(latexText=three_original).ParaTokens)
