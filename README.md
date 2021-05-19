![Letax公式](https://my-picbed.oss-cn-hangzhou.aliyuncs.com/img/20210519103028.png)

# 规则的表示

## 表示方法

使用Backus-Naur Form (BNF)表示各种规则

+ ::= 表示“被定义为”
+ +表示“1个及以上”
+ *表示“0个及以上”
+ [word]表示“word为可选项”
+ | 表示有可能出现的情况

## 基本运算符号

```python
equal ::= "=" # 等于
plus ::= "+"  # 加
minus ::= "-"  # 减
multiply ::= "*"  # 乘
divide ::= "/" # 除
power ::= "**"  # 幂
comma ::= ","  # 逗号
Lparen ::= "("  # 左括号
Rparen ::= ")"  # 右括号
```

## 特殊运算符号

```python
Tanh ::= "tanh"  # 双曲正切
Cos ::= "cos" # 余弦
Sin ::= "sin"  # 正弦
Tan ::= "tan"  # 正切
latexFrac ::= 'frac'  # 分数
latexLn ::= "ln"  # 自然对数
latexPow ::= "^"  # 指数
latexSqrt ::= "sqrt"  # 根号
mathTanh ::= "math.tanh"
mathCos ::= "math.cos"
mathSin ::= "math.sin"
mathTan ::= "math.tan"
mathLog ::= "math.log"  # 对数
mathSqrt ::= "math.sqrt"
mathMax ::= "max"  # 取最大值
mathExp ::= "math.exp"  # e^x
plainSymbol ::= equal | minus | plus | comma | multiply | divide | power
triangleSymbol ::= Tanh | Cos | Sin | Tan 
SpecialSymbol ::= latexFrac | latexLn | latexPow | latexSqrt | triangleSymbol
```

##  参数的形式

```python
nums ::= '0'..'9'
alphas ::= 'A'..'Z''a'..'z'
alphanums ::= nums | alphas
# 数字参数     
numPara ::= ["{"] nums+ ["." nums+] ["}"] # 12  12.13  12.13
# 字母参数
Foot ::= alphanusm+ (comma alphanums+)* # {1} {x} {x,y}
Simple AlphaPara ::= alphas+ ["_{" Foot "}"] ["'"] # A A_{x} 
Complicated AlphaPara ::= "(" alphas+ ["_{" Foot "}"]["'"] ")_{" Foot "}" # (A_{x})_{y}
alphaPara ::= Complicated AlphaPara | Simple AlphaPara # 参数
```

## 特殊计算的形式

```python
calculatingUnit ::= SpecialSymbol | MathSymbol | alphaPara | numPara | PlainSymbol | Lparen | Rparen
bracketUnit ::="{" caculationUnit+ "}"
Ln ::= latexLn bracketUnit
Triangle ::= triangleSymbol bracketUnit
Power ::= latexPow bracketUnit
Sqrt ::= latexSqrt bracketUnit
Frac ::= latexFrac bracketUnit bracketUnit
Multiply =alphaPara Lparen | numPara Lparen | Rparen (alphaPara | numPara) | Rparen Lparen | (alphaPara | numPara) (alphaPara | numPara) | (alphaPara | numPara) MathSymbol
```

​    