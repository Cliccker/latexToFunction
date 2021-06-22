![Letax公式](https://my-picbed.oss-cn-hangzhou.aliyuncs.com/img/20210519103028.png)

# 规则的表示

## 表示方法

使用Backus-Naur Form (BNF)表示各种规则

+ ::= 表示“被定义为”
+ +表示“1个及以上”
+ *表示“0个及以上”
+ [word]表示“word为可选项”
+ | 表示有可能出现的情况

## 基本运算符号（形式一致）

```python
equal ::= "=" # 等于
plus ::= "+"  # 加
minus ::= "-"  # 减
multiply ::= "*"  # 乘
divide ::= "/" # 除
power ::= "**"  # 幂
basicSymbol ::= equal | plus |minus| multiply | divide | power
```

## 标记符号

```python
comma ::= ","  # 逗号
Lparen ::= "("  # 左括号
Rparen ::= ")"  # 右括号
```

## 特殊运算符号

### latex形式

```python
max ::= "max"  # 取最大值
min ::= "min"  # 取最小值
latexFrac ::= "frac"  # 分数
latexLn ::= "ln"  # 自然对数
latexPow ::= "^"  # 指数
latexSqrt ::= "sqrt"  # 根号
latexArcsin ::="arcsin" # 反正弦
latexArccos ::="arccos" # 反余弦
latexTanh ::= "tanh"  # 双曲正切
latexCos ::= "cos" # 余弦
latexSin ::= "sin"  # 正弦
latexTan ::= "tan"  # 正切
triangleSymbol ::= latexArcsin | latexArccos | latexTanh | latexCos | latexSin | latexTan 
SpecialSymbol ::= latexFrac | latexLn | latexPow | latexSqrt | triangleSymbol
```
### python形式

```python
pyTanh ::= "math.tanh"
pyCos ::= "math.cos"
pySin ::= "math.sin"
pyTan ::= "math.tan"
pyLn ::= "math.log"  # 对数
pySqrt ::= "math.sqrt"
pyExp ::= "math.exp"  # e^x
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
calculatingUnit ::= SpecialSymbol | MathSymbol | alphaPara | numPara | basicSymbol | Lparen | Rparen |comma
bracketUnit ::="{" caculationUnit+ "}"
Ln ::= latexLn bracketUnit
Triangle ::= triangleSymbol bracketUnit
Power ::= latexPow bracketUnit
Sqrt ::= latexSqrt bracketUnit
Frac ::= latexFrac bracketUnit bracketUnit
Multiply ::= alphaPara Lparen | numPara Lparen | Rparen (alphaPara | numPara) | Rparen Lparen | (alphaPara | numPara) alphaPara| (alphaPara | numPara) MathSymbol
```

   

# 基于文法的设计公式建模



表1 设计计算公式中的符号

| 操作名称    | Python运算符 | Latex字符   |
| ----------- | ------------ | ----------- |
| plus        | x+y          | x+y         |
| minus       | x-y          | x-y         |
| multiply    | x*y          | x*y         |
| divide      | x/y          | x/y         |
| power       | x**y         | x^y         |
| fraction    | x/y          | \frac{x}{y} |
| square root | math.sqrt(x) | \sqrt{x}    |
| ln          | math.log(x)  | \ln{x}      |
| max         | max(x,y)     | \max(x,y)   |
| min         | min(x,y)     | \min(x,y)   |
| tanh        | math.tanh(x) | \tanh(x)    |
| arccos      | math.acos(x) | \arccos(x)  |
| arcsin      | math.asin(x) | \arcsin(x)  |
| cos         | math.cos(x)  | \cos(x)     |
| sin         | math.sin(x)  | \sin(x)     |
| tan         | math.tan(x)  | \tan(x)     |
| exponential | math.exp(x)  | \exp(x)     |



```python
import math, latexify

Index = {...}


@latexify.with_latex
def Formula(...):
    return ...

```



