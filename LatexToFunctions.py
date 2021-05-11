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
             "\sigma_{2}=0.52*\left((\sigma_{\theta m }+\sigma_{ sm })-\sqrt{\left(\sigma_{\theta m }-\sigma_{ sm }\right)^{2}+4 \tau^{2}}\right)",
             "(\sigma_{\theta m }+\sigma_{ sm }-\sqrt{\left\sigma_{\theta m }-\sigma_{ sm }\right^{2}+4 \tau^{2}}\right)",
             "F=\frac{\frac{1}{A_{x}+2}+1}{sqrt{S_{1}}}",
             "frac{((1)/(A_{x}+2))+1}{sqrt{S_{1}}}"]


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
        self.SpecialSymbol = Literal('frac') | Literal("ln") | Literal("^") | Literal("cos") | Literal("sin") | Literal(
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
        AlphaPara = Combine(Word(alphas) + Optional("_{" + Foot + "}")).ignore(
            self.SpecialSymbol)  # 字母、带有脚标的字母，为需要输入的参数
        Symbol = self.SpecialSymbol | equal | minus | plus | comma | multiply | divide | power  # 计算符号
        formula = Symbol | NumPara | AlphaPara | "(" | ")" | "{" | "}"  # 公式中包含的各个元素
        SepNumPara = Combine(Word(nums) + Optional('.' + Word(nums)))  # 特殊计算中的数字不能包含{}
        ScopePara = self.SpecialSymbol | AlphaPara | SepNumPara | equal | minus | plus | comma | multiply | divide | power  # 特殊计算可能包括的参数形式
        self.FracScope = ScopePara | "(" | ")"
        # 特殊计算
        # self.Scope = Combine(Lparen + OneOrMore(ScopePara) + Rparen)  # 括号内
        # self.Frac = Forward()
        self.Frac = Literal("frac") + Group("{" + Combine(OneOrMore(self.FracScope)) + "}") + Group(
            "{" + Combine(OneOrMore(self.FracScope)) + "}")
        self.Sqrt = Literal("sqrt") + Group("{" + Combine(OneOrMore(self.FracScope)) + "}")
        # 公式、参数和特殊运算符
        self.formulaTokens = sum(formula.searchString(self.latexText))  # 输出公式中的参数和运算符号
        self.Answer = self.formulaTokens[0]  # 结果
        self.latexText = self.latexText.replace(self.Answer + "=", "")
        self.AlphaParaTokens = AlphaPara.searchString(self.latexText).asList()  # 所有变量
        self.specialSymbolTokens = sum(self.SpecialSymbol.searchString(self.latexText))  # 所有特殊计算符号
        self.ParaValue = {}

    def SearchSpePara(self):
        """
        搜索特殊计算符号
        """
        self.specialSymbolTokens = self.SpecialSymbol.searchString(self.latexText).asList()

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
            Square = item[1][1] + "**0.5"
            sqrt = item[0] + ''.join(item[1])
            self.latexText = self.latexText.replace(sqrt, Square)

    def TransFrac(self):
        """
        将所有的frac{x}{y}替换为(x)/(y)
        """
        fracTokens = self.Frac.searchString(self.latexText).asList()
        for item in fracTokens:
            head = item[1][1]
            tail = item[2][1]
            Divide = "((" + head + ")/(" + tail + "))"
            Frac = item[0] + ''.join(item[1]) + ''.join(item[2])
            self.latexText = self.latexText.replace(Frac, Divide)

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
        result = eval(self.latexText)
        print("{}={}".format(self.Answer, result))

    def ToFunction(self):
        # print("计算流程：{}".format(f.formulaTokens))
        # print("参数：{}".format(f.AlphaParaTokens))
        # print("特殊运算符：{}".format(f.specialSymbolTokens))
        while self.specialSymbolTokens:
            self.TransPow()
            self.TransSqrt()
            self.TransFrac()
            self.SearchSpePara()
        # print("简化后的公式：{}".format(f.latexText))
        self.InputValue()
        self.Calculate()


f = Formula(latex=latexList[6])
f.ToFunction()
