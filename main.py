# -*- coding: utf-8 -*-

"""
@File    : main.py
@Author  : Hangcheng
@Email   : megamhc@gmail.com
@Time    : 2021/5/12 19:11
"""

from LatexToFunction import Formula

# latexList = ["K_{ e , k }=1.0+\frac{(1-n)}{n*(m-1)}\left(\frac{\Delta S_{ n , k }}{S_{P S }}-1\right)",
# "v_{ p }=\max \left[0.5-0.2\left(\frac{S_{v, k}}{S_{u,k}}\right) , v_{ e }\right]", "\sum_{k=1}^{M} \frac{n_{ k }}{
# N_{ k }} \leqslant 1.0", "\Delta \varepsilon_{ k }=\frac{\Delta \sigma_{ k }}{E_{ ya , k }}+2\left(\frac{\Delta
# \sigma_{ k }}{2 K_{ COS }}\right)^{\frac{1}{n_{ esn }}}", ((\sigma_{\theta m }+\sigma_{ s"\sigma_{2}=0.52\leftm
# })-\sqrt{\left(\sigma_{\theta m }-\sigma_{ sm }\right)^{2}+4 \tau^{2}}\right)", "(\sigma_{\theta m }+\sigma_{ sm
# }-\sqrt{\left\sigma_{\theta m }-\sigma_{ sm }\right^{2}+4 \tau^{2}}\right)", "F=\frac{\frac{tanh{1}}{A_{x}^{
# 24}+2}+1}{\sqrt{B_{x}\ln{S_{1}}}}", "frac{((1)/(A_{x}^{24}+2))+1}{sqrt{S_{1}}}", "F=((((math.tanh(1))/(A_{x}**(
# 24)+2))+1)/(math.sqrt(math.log(2S_{1}))))"]

latexList = ["s=a_{12}",
             "G^{*}=\frac{E^{*}}{2\left(1+v^{*}\right)}",
             "\left(\sigma_{ r }^{*}\right)_{ P }=\left(\sigma_{ T }^{*}\right)_{ a }-\frac{1}{2}\left(G_{ p }^{"
             "*}-G_{ d }^{*}\right)\left(\varepsilon_{ i }^{*}-\varepsilon_{0}^{*}\right)",
             "\sigma_{0}=\frac{1}{\mu^{*}}\left(K_{ x } \sigma_{ x }^{*}+K_{ y } \sigma_{ y }^{*}+K_{ xy } \tau_{ xy }^{*}\right)",
             "\sigma_{ p }^{*}=K_{ skin }\left[\frac{E\alpha\left(T_{ m }-T_{ s }\right)}{(1-v)}\right]",
             "K_{vkin}=\frac{9.43983-421.179 \mu^{*}+6893.05 \mu^{*2}}{1+4991.39 \mu^{*}+6032.92 \mu^{*2}-1466.19 \mu^{*3}}",
             "K_{ e , k }=1.0+\frac{(1-n)}{n*(m-1)}\left(\frac{\Delta S_{ n , k }}{S_{P S }}-1\right)",
             "F=\frac{\frac{tanh{1}}{A_{x}^{24}+2}+1}{\sqrt{B_{x}\ln{S_{1}}}}",
             "v_{ p }=\max \left[0.5-0.2\left(\frac{S_{v, k}}{S_{u,k}}\right) , v_{ e }\right]",
             "A_{2}=\frac{\sigma_{ uts } \exp \left[m_{2}\right]}{m_{2}^{m_{2}}}",
             "\theta=\arcsin \left[\frac{D_{R}-\frac{D_{i}}{2}+r_{k}}{r_{k}}\right]",
             "A_{1}=t\left(L_{R}-\frac{t}{2 \tan [\alpha]}\right) \cdot \max \left[\left(\frac{\lambda}{5}\right)^{0.85}, { 1.0}\right]"]


def Main(index):
    f = Formula(latex=latexList[index])
    f.ToFunction()
    f.SaveAsPython("Formula_" + str(index))
    f.Result()



for index in range(0, len(latexList)):
     Main(index)
