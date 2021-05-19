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

