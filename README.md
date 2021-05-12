![image-20210426162125638](https://my-picbed.oss-cn-hangzhou.aliyuncs.com/img/20210426162135.png)

## 标准中的公式

<img src="https://my-picbed.oss-cn-hangzhou.aliyuncs.com/img/20210427144743.png" alt="image-20210427144742178" style="zoom:67%;" />

标准中的公式大部分和上图一样，主要用到的计算包括**加减乘除、对数、三角函数、幂、开根号**，很多公式虽然计算方法并不复杂，但是包含了大量的参数，如下图就包含了大量的参数。

<img src="https://my-picbed.oss-cn-hangzhou.aliyuncs.com/img/20210427145325.png" alt="image-20210427145322161" style="zoom: 50%;" />

## formula recognition

将印刷体公式转化为$Latex$，或者其他数字化形式已经有很多商业软件实现了比较理想的公式转化成果，比如Mathpix

![原公式](https://my-picbed.oss-cn-hangzhou.aliyuncs.com/img/20210427143953.png)
$$
F_{\mathrm{self}}=\frac{\left[1-\frac{1}{2 C_{\mathrm{c}}^{2}}\left(\frac{2 L_{\mathrm{v}}}{R_{\mathrm{ge}}}\right)^{2}\right] S_{\mathrm{y}}}{\frac{5}{3}+\frac{3}{8 C_{\mathrm{self}}}\left(\frac{2 L_{\mathrm{v}}}{R_{\mathrm{ge}}}\right)-\frac{1}{8 C_{\mathrm{c}}^{3}}\left(\frac{2 L_{\mathrm{v}}}{R_{\mathrm{gn}}}\right)^{3}}
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

公式实例：
$$
K_{ e , k }=1.0+\frac{(1-n)}{n(m-1)}\left(\frac{\Delta S_{ n , k }}{S_{PS }}-1\right)
$$

$$
v_{ p }=\max \left[0.5-0.2\left(\frac{S_{v, k}}{S_{u,k}}\right) , v_{ e }\right]
$$

$$
D_{ f , k }=\frac{n_{ k }}{N_{ k }}
$$

$$
\sum_{k=1}^{M} \frac{n_{ k }}{N_{ k }} \leqslant 1.0
$$

$$
\Delta \varepsilon_{ k }=\frac{\Delta \sigma_{ k }}{E_{ ya , k }}+2\left(\frac{\Delta \sigma_{ k }}{2 K_{ COS }}\right)^{\frac{1}{n_{ esn }}}
$$

$$
\sigma_{2}=0.5\left(\sigma_{\theta m }+\sigma_{ sm }-\sqrt{\left(\sigma_{\theta m }-\sigma_{ sm }\right)^{2}+4 \tau^{2}}\right)
$$

## 验证解析结果的准确度

latexify-py
$$
F=\frac{\frac{sin{1}}{A_{x}^{24}+2}+1}{\sqrt{B_{x}\ln{S_{1}}}}
$$

$$
\mathrm{f}(self, b, c, d, e)\triangleq 0.52(self + b - \sqrt{(c - d)^{2} + 4e^{2}})
$$

词表

训练比较方便

LTP 命名实体识别标注集