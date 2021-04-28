![image-20210426162125638](https://my-picbed.oss-cn-hangzhou.aliyuncs.com/img/20210426162135.png)

## 标准中的公式

<img src="https://my-picbed.oss-cn-hangzhou.aliyuncs.com/img/20210427144743.png" alt="image-20210427144742178" style="zoom:67%;" />

标准中的公式大部分和上图一样，主要用到的计算包括**加减乘除、对数、三角函数、幂、开根号**，很多公式虽然计算方法并不复杂，但是包含了大量的参数，如下图就包含了大量的参数。

<img src="https://my-picbed.oss-cn-hangzhou.aliyuncs.com/img/20210427145325.png" alt="image-20210427145322161" style="zoom: 50%;" />

## formula recognition

将印刷体公式转化为$Latex$，或者其他数字化形式已经有很多商业软件实现了比较理想的公式转化成果，比如Mathpix

![原公式](https://my-picbed.oss-cn-hangzhou.aliyuncs.com/img/20210427143953.png)
$$
F_{\mathrm{a}}=\frac{\left[1-\frac{1}{2 C_{\mathrm{c}}^{2}}\left(\frac{2 L_{\mathrm{v}}}{R_{\mathrm{ge}}}\right)^{2}\right] S_{\mathrm{y}}}{\frac{5}{3}+\frac{3}{8 C_{\mathrm{a}}}\left(\frac{2 L_{\mathrm{v}}}{R_{\mathrm{ge}}}\right)-\frac{1}{8 C_{\mathrm{c}}^{3}}\left(\frac{2 L_{\mathrm{v}}}{R_{\mathrm{gn}}}\right)^{3}}
$$
还有国内的公式识别服务提供商，比如有道公式、腾讯优图。

文献：

1. LPGA: Line-Of-Sight Parsing with Graph-based Attention for Math Formula Recognition

   `2019 International Conference on Document Analysis and Recognition (ICDAR)`

   line-of-sight (LOS) graph

   random forest

   CNN

   数据集**[InftyCDB-2](https://www.inftyproject.org/en/database.html)**

<img src="https://my-picbed.oss-cn-hangzhou.aliyuncs.com/img/20210427145607.png" alt="image-20210427145605048" style="zoom: 67%;" />

## formula to function

几种方式

### 使用正则表达式解析公式

使用正则表达式门槛比较高。可读性和适应性也比较差

### 编写 Pyparsing解析公式，使用sympy计算公式

优势是可读性比较好，纯python，便于后期的维护

实例：

$$\varepsilon_{1}=\frac{\sigma_{1}}{E_{\mathrm{y}}}+\gamma_{\mathrm{1}}+\gamma_{2}

```python
from pyparsing import *
one_original = "\varepsilon_{1}=\frac{\sigma_{1}}{E_{\mathrm{y}}}+\gamma_{\mathrm{1}}+\gamma_{2}"
one_all = "\\varepsilon_{1}=\\frac{\sigma_{1}}{E_{y}}+\gamma_{1}+\gamma_{2}"
paraWithFoot = Word(alphas) + "_{" + Word(alphanums) + "}"  # 有脚标参数
parameter = Word(alphanums)  # 无脚标参数
equal = Literal("=")  # 等于
plus = Literal("+")  # 加
leftBrackets = Literal("(")  # 左括号
rightBrackets = Literal(")")  # 右括号
formula = paraWithFoot | parameter | equal | plus | leftBrackets | rightBrackets
frac = Word("\\frac{") + formula + "}" + "{" + formula + "}"
formulaTokens = formula.searchString(one_all)  # 寻找所有参数
fracTokens = frac.searchString(one_all)  # 分数的两个参数
print(formulaTokens)
print(fracTokens)
>>[['varepsilon', '_{', '1', '}'], ['='], ['frac'], ['sigma', '_{', '1', '}'], ['E', '_{', 'y', '}'], ['+'], ['gamma', '_{', '1', '}'], ['+'], ['gamma', '_{', '2', '}']]
>> [['\\frac{\\', 'sigma', '_{', '1', '}', '}', '{', 'E', '_{', 'y', '}', '}']]
```

