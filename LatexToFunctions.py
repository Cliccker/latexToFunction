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

latexList = ["K_{ e , k }=1.0+\frac{(1-n)}{n(m-1)}\left(\frac{\Delta S_{ n , k }}{S_{P S }}-1\right)",
             "v_{ p }=\max \left[0.5-0.2\left(\frac{S_{v, k}}{S_{u,k}}\right) , v_{ e }\right]",
             "\sum_{k=1}^{M} \frac{n_{ k }}{N_{ k }} \leqslant 1.0",
             "\Delta \varepsilon_{ k }=\frac{\Delta \sigma_{ k }}{E_{ ya , k }}+2\left(\frac{\Delta \sigma_{ k }}{2 K_{ cos }}\right)^{\frac{1}{n_{ esn }}}",
             "\sigma_{2}=0.52\left((\sigma_{\theta m }+\sigma_{ sm })-\sqrt{\left(\sigma_{\theta m }-\sigma_{ sm }\right)^{2}+4 \tau^{2}}\right)",
             "(\sigma_{\theta m }+\sigma_{ sm }-\sqrt{\left\sigma_{\theta m }-\sigma_{ sm }\right^{2}+4 \tau^{2}}\right)"]


class Formula:

    def __init__(self, latex):
        self.latexText = latex
        bias = {"\\": "", "\f": "f", "\a": "a", "\b": "b", "\n": "n", "\v": "v", "\t": "t", "\r": "r", "left": "",
                "right": "", "[": "(", "]": ")", " ": ""}  # 所有可能产生歧义的字符，如转义、反斜杠、空格
        # 预处理
        for bia in bias.keys():
            if bia in self.latexText:
                self.latexText = self.latexText.replace(bia, bias[bia])
        # 特殊运算符号
        Symbol = Literal('frac') | Literal("ln") | Literal("^") | Literal("cos") | Literal("sin") | Literal(
            "tan") | Literal("sqrt") | Literal("tanh") | Literal("max") | Literal("leqslant")  # 计算符号
        # 基本运算符号
        equal = Literal("=")  # 等于
        plus = Literal("+")  # 加
        minus = Literal("-")  # 减
        comma = Literal(",")  # 逗号
        Lparen = Literal("(")  # (
        Rparen = Literal(")")  # )
        # 主要参数
        NumPara = Combine(Word(nums) + Optional('.' + Word(nums)))  # 整数和小数
        Foot = Combine(Word(alphanums) + ZeroOrMore(comma + Word(alphanums)))  # 脚标的不同形式
        AlphaPara = Combine(Word(alphas) + Optional("_{" + Foot + "}")).ignore(Symbol)  # 字母、带有脚标的字母
        Para = (NumPara | AlphaPara).ignore(Symbol)
        formula = Symbol | NumPara | AlphaPara | equal | minus | plus | comma | Lparen | Rparen | "{" | "}"  # 公式中包含的各个元素
        ScopePara = Symbol | NumPara | AlphaPara | equal | minus | plus | comma | "{" | "}"
        self.Scope = Combine(Lparen + OneOrMore(ScopePara) + Rparen)  # 括号内
        # 公式、参数和特殊运算符
        self.formulaTokens = sum(formula.searchString(self.latexText))  # 输出公式中的参数和运算符号
        self.ParaTokens = sum(Para.searchString(self.latexText))  # 所有参数
        self.SymbolTokens = sum(Symbol.searchString(self.latexText))  # 所有特殊计算符号
        self.calculateLevel = {}
        self.markDict = {}

    def SearchScope(self):
        """
        依据括号对公式进行分层
        :rtype: object
        """
        latexText = self.latexText
        ScopeTokens = self.Scope.searchString(latexText).asList()
        index = 0
        while ScopeTokens:
            self.calculateLevel[index] = ScopeTokens
            childIndex = 0
            for item in ScopeTokens:
                newName = "PAREN" + "_{" + str(index) + str(childIndex) + "}"
                self.markDict[newName] = str(item[0])
                latexText = latexText.replace(str(item[0]), newName)
                childIndex += 1
            ScopeTokens = self.Scope.searchString(latexText).asList()
            index += 1
        self.calculateLevel[index] = [[latexText]]


f = Formula(latex=latexList[1])
f.SearchScope()

print("简化后的公式：{}".format(f.latexText))
print("计算流程：{}".format(f.formulaTokens))
print("参数：{}".format(f.ParaTokens))
print("特殊运算符：{}".format(f.SymbolTokens))
print(f.markDict)
print(f.calculateLevel)
