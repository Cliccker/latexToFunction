# -*- coding: utf-8 -*-

"""
@File    : LatexToFunction.py
@Author  : Hangcheng
@Email   : megamhc@gmail.com
@Time    : 2021/4/26 10:19
"""

from pyparsing import *
import math, latexify  # 必须有


class Formula:

    def __init__(self, latex):
        """
        转换latex文本用以直接计算或输出python函数
        :param latex: latex文本
        """
        self.function = ""
        self.latexText = latex
        bias = {"\\": "", "\f": "f", "\a": "a", "\b": "b", "\n": "n", "\v": "v", "\t": "t", "\r": "r", "left": "",
                "right": "", "[": "(", "]": ")", " ": "", "^{*}": "'", "^{*2}": "'^{2}",
                "^{*3}": "'^{3}", "exp": "math.exp", "cdot": "*"}  # 所有可能产生歧义的字符，如转义、反斜杠、空格，可以直接转换的字符，如exp(x)
        # 预处理
        for bia in bias.keys():
            if bia in self.latexText:
                self.latexText = self.latexText.replace(bia, bias[bia])
        # 基本运算符号（这些符号在python和latex中形式相同）
        equal = Literal("=")  # 等于
        plus = Literal("+")  # 加
        minus = Literal("-")  # 减
        multiply = Literal("*")  # 乘
        divide = Literal("/")  # 除
        power = Literal("**")  # 幂
        comma = Literal(",")  # 逗号
        Lparen = Literal("(")  # (
        Rparen = Literal(")")  # )
        basicSymbol = equal | minus | plus | comma | multiply | divide | power
        # 特殊计算符号（这些符号在python和latex中形式不同）
        # latex中的表示形式
        Max = Literal("max")  # 取最大值
        Min = Literal("min")  # 取最小值
        arcSin = Literal("arcsin")  # 反正弦
        arcCos = Literal("arccos")  # 反余弦
        Tanh = Literal("tanh")  # 双曲正切
        Cos = Literal("cos")  # 余弦
        Sin = Literal("sin")  # 正弦
        Tan = Literal("tan")  # 正切
        self.latexArc = arcSin | arcCos
        self.triangleSymbol = Tanh | Cos | Sin | Tan  # 三角符号
        self.latexFrac = Literal('frac')  # 分数
        self.latexLn = Literal("ln")  # 自然对数
        self.latexPow = Literal("^")  # 指数
        self.latexSqrt = Literal("sqrt")  # 根号
        self.latexSymbol = self.latexFrac | self.latexLn | self.latexPow | self.latexSqrt | self.triangleSymbol | self.latexArc  # 所有特殊计算符号
        # python中的表示形式
        pyASin = Literal("math.asin")
        pyACos = Literal("math.acos")
        pyTanh = Literal("math.tanh")
        pyCos = Literal("math.cos")
        pySin = Literal("math.sin")
        pyTan = Literal("math.tan")
        pyLog = Literal("math.log")  # 对数
        pySqrt = Literal("math.sqrt")
        pyExp = Literal("math.exp")  # e^x
        pySymbol = pyASin | pyACos | pyTanh | pyCos | pySin | pyTan | pyLog | pySqrt | pyExp | Max | Min
        self.latexSymbol = self.latexSymbol.ignore(pySymbol)
        Symbol = self.latexSymbol | pySymbol | basicSymbol  # 所有特殊字符
        # 数字参数
        numPara = Combine(Word(nums) + Optional('.' + Word(nums)))  # 整数和小数
        # 字母参数
        Foot = Combine(Word(alphanums) + ZeroOrMore(comma + Word(alphanums)))  # 脚标的不同形式
        alphaParaUnit = Word(alphas) + Optional("_{" + Foot + "}") + Optional("'")  # 字母、带有脚标的字母
        simAlphaPara = Combine(alphaParaUnit)
        comAlphaPara = Combine("(" + alphaParaUnit + ")_{" + Foot + "}")  # (A_x')_b
        alphaPara = comAlphaPara | simAlphaPara
        alphaPara = alphaPara.ignore(self.latexSymbol)
        alphaPara = alphaPara.ignore(pySymbol)
        # 公式
        self.Formula = Symbol | numPara | alphaPara | Lparen | Rparen | "{" | "}"  # 公式中包含的各个元素
        # 特殊计算
        calculatingUnit = self.latexSymbol | pySymbol | alphaPara | numPara | basicSymbol | Lparen | Rparen  #
        # 特殊计算可能包括的参数形式
        self.bracketUnit = Group("{" + Combine(OneOrMore(calculatingUnit)) + "}")  # 特殊计算的参数（花括号）
        self.parenUnit = Group("(" + Combine(OneOrMore(calculatingUnit)) + ")")  # 特殊计算参数（圆括号）
        # 乘法
        self.Multiply = pySymbol + Lparen | alphaPara + Lparen | numPara + Lparen | Rparen + (
                alphaPara | numPara) | Rparen + Lparen | (alphaPara | numPara) + alphaPara | (
                                alphaPara | numPara) + pySymbol
        self.mathMultiply = pySymbol + Lparen
        # 公式、参数和特殊运算符
        self.formulaTokens = sum(self.Formula.searchString(self.latexText))  # 输出公式中的参数和运算符号
        self.Answer = self.formulaTokens[0]  # 结果
        self.latexText = self.latexText.replace(self.Answer + "=", "")  # 去除答案部分，因为在这里他不重要
        self.alphaParaTokens = alphaPara.searchString(self.latexText).asList()  # 所有变量
        self.specialSymbolTokens = sum(self.latexSymbol.searchString(self.latexText))  # 所有特殊计算符号
        self.ParaValue = {}  # 存储参数值

    def SearchSpePara(self):
        """
        搜索特殊计算符号，如果没有，就停止转换
        """
        self.specialSymbolTokens = self.latexSymbol.searchString(self.latexText).asList()

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
        Ln = self.latexLn + self.bracketUnit
        Tokens = Ln.searchString(self.latexText).asList()
        for item in Tokens:
            New = "math.log(" + item[1][1] + ")"
            Original = item[0] + ''.join(item[1])
            self.latexText = self.latexText.replace(Original, New)

    def TransTriangle(self):
        """
        转换三角函数
        """
        Triangle = self.triangleSymbol + self.bracketUnit
        self.TransToMath(Triangle)

    def ReplaceTriangle(self):
        """
        替换三角函数
        三角函数可能出现tan{x}和tan(x)等多种情况
        """
        Triangle = self.triangleSymbol
        Tokens = Triangle.searchString(self.latexText).asList()
        for item in Tokens:
            New = "math." + item[0]
            Original = item[0]
            self.latexText = self.latexText.replace(Original, New)

    def TransArc(self):
        """
        转换反三角函数
        """
        Arc = self.latexArc
        ArcTokens = Arc.searchString(self.latexText).asList()
        arcDict = {"arcsin": "math.asin", "arccos": "math.acos"}
        for item in ArcTokens:
            New = arcDict[item[0]]
            Old = item[0]
            self.latexText = self.latexText.replace(Old, New)
        # print(ArcTokens)

    def TransPow(self):
        """
        将所有^转换成**
        """
        Power = self.latexPow + self.bracketUnit
        PowerTokens = Power.searchString(self.latexText).asList()
        for item in PowerTokens:
            New = "**(" + item[1][1] + ")"
            Old = item[0] + ''.join(item[1])
            self.latexText = self.latexText.replace(Old, New)

    def TransSqrt(self):
        """
        将所有sqrt转换成math.sqrt(x)
        """
        Sqrt = self.latexSqrt + self.bracketUnit
        self.TransToMath(Sqrt)

    def TransFrac(self):
        """
        将所有的frac{x}{y}替换为(x)/(y)
        """
        Frac = self.latexFrac + self.bracketUnit + self.bracketUnit
        fracTokens = Frac.searchString(self.latexText).asList()

        for item in fracTokens:
            head = item[1][1]
            tail = item[2][1]
            New = "((" + head + ")/(" + tail + "))"
            Old = item[0] + ''.join(item[1]) + ''.join(item[2])
            self.latexText = self.latexText.replace(Old, New)

    def TransMultiply(self):
        """
        加上乘号，这些位置需要乘号
        右括号和左括号之间；
        数字或者参数和左括号之间；
        数字和参数之间；
        参数和参数之间。
        """
        A = self.Multiply.searchString(self.latexText).asList()
        B = self.mathMultiply.searchString(self.latexText).asList()
        A = [item for item in A if item not in B]  # 这里相减是因为AlphaPara +"("会匹配到math.para，所以先匹配字符串中的math.x再将其减去
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
        a = self.Formula.searchString(self.latexText).asList()
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
        count = 1
        while count < 20:
            if self.specialSymbolTokens:
                count += 1
                self.TransLn()  # 对数
                self.TransArc()
                self.TransTriangle()
                self.ReplaceTriangle()
                self.TransPow()
                self.TransSqrt()
                self.TransFrac()
                self.SearchSpePara()
            else:
                break
        else:  # 错误信息，包括不能解析的符号和公式
            pass
            # raise Exception('Early Stop\n{}\n{}'.format(self.specialSymbolTokens, self.latexText))
        self.TransMultiply()

        self.function = self.latexText

    def Result(self):
        """
        计算结果
        """
        self.InputValue()
        self.Calculate()

    def SaveAsPython(self, FunctionName):
        """
        将计算公式转换为python文件
        """
        # 为每一个参数找到替换的参数
        print(self.latexText)
        newParaName = {}
        showPara = {"result_para": self.Answer}  # python文件中的参数索引字典
        Para = [chr(i) for i in range(65, 91)]  # 按照英文字母生成新参数
        count = 0
        for item in self.alphaParaTokens:
            if item[0] not in newParaName.keys():
                newParaName[item[0]] = Para[count]
                showPara[Para[count]] = item[0]
                count += 1
        # 重新组织新的Python函数式
        a = self.Formula.searchString(self.function).asList()
        b = [i[0] for i in a]
        c = [newParaName[i] if i in newParaName else i for i in b]
        formula = "".join(c)
        formula = formula.replace("{", "(")
        formula = formula.replace("}", ")")
        NewParas = ",".join(newParaName.values())
        # python文件内容
        Line_0 = "import math,latexify"  # 库
        Line_1 = "\n\nParas = " + str(showPara)  # 参数索引
        Line_2 = "\n\n@latexify.with_latex"  # 域
        Line_3 = "\n\ndef Formula(" + NewParas + "):" + "\n" + "\t" + "return " + formula  # 函数主体
        Line_4 = "\n\nprint(Formula)"  # 显示latex函数
        Line = Line_0 + Line_1 + Line_2 + Line_3 + Line_4
        SavedFilename = "Data/" + FunctionName + ".py"
        with open(SavedFilename, "w+") as File:
            File.write(Line)
        print("\n")
        print("Validation:")
        fixed = exec(compile(open(SavedFilename, "rb").read(), SavedFilename, "exec"))  # 执行python文件
        return fixed.__str__


if __name__ == "__main__":
    f = Formula("\theta=\arcsin \left[\frac{D_{R}-\frac{D_{i}}{2}+r_{k}}{r_{k}}\right]")
    f.ToFunction()
    f.SaveAsPython("Arc")
