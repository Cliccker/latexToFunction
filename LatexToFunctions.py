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
import latexify

latexList = ["K_{ e , k }=1.0+\frac{(1-n)}{n*(m-1)}\left(\frac{\Delta S_{ n , k }}{S_{P S }}-1\right)",
             "v_{ p }=\max \left[0.5-0.2\left(\frac{S_{v, k}}{S_{u,k}}\right) , v_{ e }\right]",
             "\sum_{k=1}^{M} \frac{n_{ k }}{N_{ k }} \leqslant 1.0",
             "\Delta \varepsilon_{ k }=\frac{\Delta \sigma_{ k }}{E_{ ya , k }}+2\left(\frac{\Delta \sigma_{ k }}{2 K_{ COS }}\right)^{\frac{1}{n_{ esn }}}",
             "\sigma_{2}=0.52\left((\sigma_{\theta m }+\sigma_{ sm })-\sqrt{\left(\sigma_{\theta m }-\sigma_{ sm }\right)^{2}+4 \tau^{2}}\right)",
             "(\sigma_{\theta m }+\sigma_{ sm }-\sqrt{\left\sigma_{\theta m }-\sigma_{ sm }\right^{2}+4 \tau^{2}}\right)",
             "F=\frac{\frac{tanh{1}}{A_{x}^{24}+2}+1}{\sqrt{B_{x}\ln{S_{1}}}}",
             "frac{((1)/(A_{x}^{24}+2))+1}{sqrt{S_{1}}}",
             "F=((((math.tanh(1))/(A_{x}**(24)+2))+1)/(math.sqrt(math.log(2S_{1}))))"]


class Formula:

    def __init__(self, latex):
        self.function = ""
        self.latexText = latex
        bias = {"\\": "", "\f": "f", "\a": "a", "\b": "b", "\n": "n", "\v": "v", "\t": "t", "\r": "r", "left": "",
                "right": "", "[": "(", "]": ")", " ": ""}  # 所有可能产生歧义的字符，如转义、反斜杠、空格
        # 预处理
        for bia in bias.keys():
            if bia in self.latexText:
                self.latexText = self.latexText.replace(bia, bias[bia])
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
        # 特殊运算符号
        TriangleSymbol = Literal("tanh") | Literal("cos") | Literal("sin") | Literal("tan")
        self.SpecialSymbol = Literal('frac') | Literal("ln") | Literal("^") | Literal("sqrt") | Literal(
            "max") | Literal("leqslant") | TriangleSymbol  # 计算符号
        MathSymbol = Literal("math.tanh") | Literal("math.cos") | Literal("math.sin") | Literal("math.tan") | Literal(
            "math.log") | Literal("math.sqrt")
        self.SpecialSymbol = self.SpecialSymbol.ignore(MathSymbol)
        # 主要参数
        NumPara = Combine(Optional("{") + Word(nums) + Optional('.' + Word(nums)) + Optional("}"))  # 整数和小数
        Foot = Combine(Word(alphanums) + ZeroOrMore(comma + Word(alphanums)))  # 脚标的不同形式
        self.AlphaPara = Combine(Word(alphas) + Optional("_{" + Foot + "}")).ignore(
            self.SpecialSymbol)  # 字母、带有脚标的字母，为需要输入的参数
        self.AlphaPara = self.AlphaPara.ignore(MathSymbol)
        Symbol = self.SpecialSymbol | MathSymbol | equal | minus | plus | comma | multiply | divide | power  # 计算符号
        self.formula = Symbol | NumPara | self.AlphaPara | "(" | ")" | "{" | "}"  # 公式中包含的各个元素
        # 特殊计算
        SepNumPara = Combine(Word(nums) + Optional('.' + Word(nums)))  # 特殊计算中的数字不能包含于{}
        ScopePara = self.SpecialSymbol | MathSymbol | self.AlphaPara | SepNumPara | equal | minus | plus | comma | multiply | divide | power  # 特殊计算可能包括的参数形式
        CalculatingUnit = ScopePara | "(" | ")"  # 特殊计算的计算单元
        BracketPara = Group("{" + Combine(OneOrMore(CalculatingUnit)) + "}")  # 特殊计算的参数
        self.Frac = Literal("frac") + BracketPara + BracketPara
        self.Sqrt = Literal("sqrt") + BracketPara
        self.Triangle = TriangleSymbol + BracketPara
        self.Power = Literal("^") + BracketPara
        self.Ln = Literal("ln") + BracketPara
        self.Multiply = MathSymbol + Lparen | self.AlphaPara + Lparen | self.AlphaPara + Lparen | SepNumPara + Lparen | Rparen + (
                self.AlphaPara | SepNumPara) | Rparen + Lparen | (self.AlphaPara | SepNumPara) + (
                                self.AlphaPara | SepNumPara) | (
                                self.AlphaPara | SepNumPara) + MathSymbol
        self.MultiplyMath = MathSymbol + Lparen
        # 公式、参数和特殊运算符
        self.formulaTokens = sum(self.formula.searchString(self.latexText))  # 输出公式中的参数和运算符号
        self.Answer = self.formulaTokens[0]  # 结果
        self.latexText = self.latexText.replace(self.Answer + "=", "")
        self.alphaParaTokens = self.AlphaPara.searchString(self.latexText).asList()  # 所有变量
        self.specialSymbolTokens = sum(self.SpecialSymbol.searchString(self.latexText))  # 所有特殊计算符号

        self.ParaValue = {}

    def SearchSpePara(self):
        """
        搜索特殊计算符号，如果没有，就停止转换
        """
        self.specialSymbolTokens = self.SpecialSymbol.searchString(self.latexText).asList()

    def TransToMath(self, Type):
        """
        将特殊计算转换为math.fun(x)的形式
        :param Type: 特殊计算的类型
        """
        Tokens = Type.searchString(self.latexText).asList()
        for item in Tokens:
            New = "math." + item[0] + "(" + item[1][1] + ")"
            Original = item[0] + ''.join(item[1])
            self.latexText = self.latexText.replace(Original, New)

    def TransLn(self):
        """
        转换对数函数
        """
        Tokens = self.Ln.searchString(self.latexText).asList()
        for item in Tokens:
            New = "math.log(" + item[1][1] + ")"
            Original = item[0] + ''.join(item[1])
            self.latexText = self.latexText.replace(Original, New)

    def TransTriangle(self):
        """
        转换三角函数
        """
        self.TransToMath(self.Triangle)

    def TransPow(self):
        """
        将所有^转换成**
        """
        PowerTokens = self.Power.searchString(self.latexText).asList()
        for item in PowerTokens:
            Square = "**" + "(" + item[1][1] + ")"
            sqrt = item[0] + ''.join(item[1])
            self.latexText = self.latexText.replace(sqrt, Square)

    def TransSqrt(self):
        """
        将所有sqrt转换成math.sqrt(x)1
        """
        self.TransToMath(self.Sqrt)

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

    def TransMultiply(self):
        """
        加上乘号，这些位置需要乘号
        右括号和左括号之间；
        数字或者参数和左括号之间；
        数字和参数之间；
        参数和参数之间。
        """
        A = self.Multiply.searchString(self.latexText).asList()
        B = self.MultiplyMath.searchString(self.latexText).asList()
        A = [item for item in A if item not in B]  # 这里相减是因为AlphaPara +"("会匹配到math.para，所以先匹配字符串中的math.x在减去
        for item in A:
            New = item[0] + "*" + item[1]
            Old = item[0] + item[1]
            self.latexText = self.latexText.replace(Old, New)

    def InputValue(self):
        """
        输入各参数值
        """
        print("Python计算式:{}\n请输入参数值".format(self.Answer + "=" + self.latexText))
        for item in self.alphaParaTokens:
            if item[0] not in self.ParaValue.keys():
                self.ParaValue[item[0]] = input(item[0] + "=")

    def Calculate(self):
        """
        计算结果
        """
        a = self.formula.searchString(self.latexText).asList()
        b = [i[0] for i in a]
        c = [self.ParaValue[i] if i in self.ParaValue else i for i in b]
        self.latexText = "".join(c)
        self.latexText = self.latexText.replace("{", "(")
        self.latexText = self.latexText.replace("}", ")")
        print("数学计算式:{}".format(self.Answer + "=" + self.latexText))
        result = eval(self.latexText)
        print("计算结果:{}={}".format(self.Answer, result))

    def ToFunction(self):
        """
        转化为python计算的公式
        """
        while self.specialSymbolTokens:
            self.TransLn()
            self.TransTriangle()
            self.TransPow()
            self.TransSqrt()
            self.TransFrac()
            self.SearchSpePara()
        self.TransMultiply()
        self.function = self.latexText

    def GetResult(self):
        """
        计算结果
        """
        self.ToFunction()
        self.InputValue()
        self.Calculate()

    def GetPyFunction(self, FunctionName):
        """
        生成py文件
        :param FunctionName: 生成py文件中函数的名称
        """
        self.ToFunction()
        self.ToPyFile(FunctionName)

    def ToPyFile(self, FunctionName):
        """
        将计算公式转换为python文件
        """
        # 为每一个参数找到替换的参数
        newParaName = {}
        Para = [chr(i) for i in range(65, 91)]
        count = 0
        for item in self.alphaParaTokens:
            if item[0] not in newParaName.keys():
                newParaName[item[0]] = Para[count]
                count += 1
        # 重新组织新的Python函数式
        a = self.formula.searchString(self.function).asList()
        b = [i[0] for i in a]
        c = [newParaName[i] if i in newParaName else i for i in b]
        formula = "".join(c)
        NewParas = ",".join(newParaName.values())
        # python文件内容
        Line_0 = "import math,latexify"  # 库
        Line_1 = "\n\nParas=" + str(newParaName)  # 参数索引
        Line_2 = "\n\n@latexify.with_latex"  # 域
        Line_3 = "\n\ndef " + FunctionName + "(" + NewParas + "):" + "\n" + "\t" + "return " + formula  # 函数主体
        Line_4 = "\n\nprint(" + FunctionName + ")"  # 显示latex函数
        Line = Line_0 + Line_1 + Line_2 + Line_3 + Line_4
        with open("Data/" + FunctionName + ".py", "w+") as File:
            File.write(Line)
        print("saved")


f = Formula(latex=latexList[6])
f.GetResult()
f.GetPyFunction("F3_2_2")
