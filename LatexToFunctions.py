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
             "(\sigma_{\theta m }+\sigma_{ sm }-\sqrt{\left\sigma_{\theta m }-\sigma_{ sm }\right^{2}+4 \tau^{2}}\right)",
             "F=\frac{\frac{1}{A_{x}}+1}{S_{1}}"]


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
        SepSymbol = Literal('frac') | Literal("ln") | Literal("^") | Literal("cos") | Literal("sin") | Literal(
            "tan") | Literal("sqrt") | Literal("tanh") | Literal("max") | Literal("leqslant")  # 计算符号
        # 基本运算符号
        equal = Literal("=")  # 等于
        plus = Literal("+")  # 加
        minus = Literal("-")  # 减
        multiply = Literal("*")  # 乘
        divide = Literal("/")  # 除
        power = Literal("**")  # 幂
        comma = Literal(",")  # 逗号
        Lparen = Literal("(")  # (
        Rparen = Literal(")")  # )
        # 主要参数
        NumPara = Combine(Optional("{") + Word(nums) + Optional('.' + Word(nums)) + Optional("}"))  # 整数和小数
        Foot = Combine(Word(alphanums) + ZeroOrMore(comma + Word(alphanums)))  # 脚标的不同形式
        AlphaPara = Combine(Word(alphas) + Optional("_{" + Foot + "}")).ignore(SepSymbol)  # 字母、带有脚标的字母，为需要输入的参数
        Para = (NumPara | AlphaPara).ignore(SepSymbol)
        Symbol = SepSymbol | NumPara | AlphaPara | equal | minus | plus | comma | multiply | divide | power
        formula = Symbol | "(" | ")" | "{" | "}"  # 公式中包含的各个元素
        ScopePara = Symbol | "{" | "}"
        FracScope = Symbol | "(" | ")"
        # 特殊计算
        self.Scope = Combine(Lparen + OneOrMore(ScopePara) + Rparen)  # 括号内
        self.Frac = Literal("frac") + Combine("{" + OneOrMore(FracScope) + "}") + Combine(
            "{" + OneOrMore(FracScope) + "}")
        left = Literal("{")
        self.Sqrt = Literal("sqrt") + Combine("{" + OneOrMore(FracScope) + "}")
        # 公式、参数和特殊运算符
        self.formulaTokens = sum(formula.searchString(self.latexText))  # 输出公式中的参数和运算符号
        self.Answer = self.formulaTokens[0]  # 结果
        self.latexText = self.latexText.replace(self.Answer + "=", "")
        self.AlphaParaTokens = AlphaPara.searchString(self.latexText).asList()  # 所有参数
        self.SymbolTokens = sum(SepSymbol.searchString(self.latexText))  # 所有特殊计算符号
        self.ParaValue = {}
        # self.calculateLevel = {}
        # self.markDict = {}

    def TransPow(self):
        """
        将所有^转换成**
        """
        self.latexText = self.latexText.replace("^", "**")

    def TransSqrt(self):
        """
        将所有sqrt转换成**0.5
        """
        sqrtTokens = self.Sqrt.searchString(self.latexText).asList()
        for item in sqrtTokens:
            Square = item[1] + "**0.5"
            sqrt = item[0] + item[1]
            self.latexText = self.latexText.replace(sqrt, Square)
        # print(self.latexText)

    def TransFrac(self):
        """
        将所有的frac{x}{y}替换为(x)/(y)
        """
        fracTokens = self.Frac.searchString(self.latexText).asList()
        print(fracTokens)
        for item in fracTokens:
            Divide = "(" + item[1] + "/" + item[2] + ")"
            Frac = item[0] + item[1] + item[2]
            # print(Frac, Divide)
            self.latexText = self.latexText.replace(Frac, Divide)
        # print(self.latexText)

    def InputValue(self):
        """
        输入各参数值
        """
        print("计算式:\n{}\n请输入参数对应值".format(self.Answer + "=" + self.latexText))
        for item in self.AlphaParaTokens:
            self.ParaValue[item[0]] = input(item[0] + "=")

    def Calculate(self):
        """
        计算结果
        """
        for key in self.ParaValue.keys():
            self.latexText = self.latexText.replace(key, self.ParaValue[key])
        self.latexText = self.latexText.replace("{", "(")
        self.latexText = self.latexText.replace("}", ")")
        print(self.latexText)
        result = eval("0.52*((23+4)-((23-4)**(2)+45**(2))**0.5)")
        print("{}={}".format(self.Answer, result))

    # def SearchParen(self):
    #     """
    #     依据括号对公式进行分层
    #     :rtype: object
    #     """
    #     latexText = self.latexText
    #     ScopeTokens = self.Scope.searchString(latexText).asList()
    #     index = 0
    #     while ScopeTokens:
    #         self.calculateLevel[index] = ScopeTokens
    #         childIndex = 0
    #         for item in ScopeTokens:
    #             newName = "PAREN" + "_{" + str(index) + str(childIndex) + "}"
    #             self.markDict[newName] = str(item[0])
    #             latexText = latexText.replace(str(item[0]), newName)
    #             childIndex += 1
    #         ScopeTokens = self.Scope.searchString(latexText).asList()
    #         index += 1
    #     self.calculateLevel[index] = [[latexText]]

    def ToFunction(self):
        self.TransPow()
        self.TransSqrt()
        self.TransFrac()
        self.InputValue()


f = Formula(latex=latexList[6])
f.ToFunction()

print("简化后的公式：{}".format(f.latexText))
print("计算流程：{}".format(f.formulaTokens))
print("参数：{}".format(f.AlphaParaTokens))
print("特殊运算符：{}".format(f.SymbolTokens))
