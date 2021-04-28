I need to convert a math formula written in the Latex style to the function of a C/C++ code. For example: **y = sin(x)^2** would become something like

```
double y = sin(x) * sin(x);
```

or

```
double y = pow(sin(x), 2);
```

where **x** is a variable defined somewhere before. I mean that it should convert the latex formula to the C/C++ syntax. So that if there is a function **y = G(x, y)^F(x)** it doesn't matter what is **G(x,y)** and **F(x)**, it is a problem of the programmer to define it. It will just generate

```
double y = pow(G(x, y), F(x)); 
```

When the formula is too complicated it will take some time to make include it in the C/C++ formula, that is why I need such a converter. Is there any?

asked Oct 25 '11 at 8:24

2

A mathematical equation, such as the ones in LaTeX, and a C expression are not interchangeable. The former states a relation between two terms, the latter defines an entity that can be evaluated, unambiguously yielding one value. ```a = b``` in C means 'take the value in variable ```b``` and store it in variable ```a```', wheres in Math, it means 'in the current context, a and b are equal'. The first describes a computation process, the second describes a static fact. Consequently, the Math equation can be reversed: ```a = b``` is equivalent to ```b = a```, but doing the same to the C equation yields something quite different.

To make matters worse, LaTeX formulae only contain the information needed to render the equations; often, this is not enough to capture their meaning.

Of course some LaTeX formulae, like your example, can be converted into C computations, but many others cannot, so any automated way of doing so would only make limited sense.

answered Oct 25 '11 at 8:33

19.3k1 gold badge34 silver badges53 bronze badges

Emacs' built-in calculator calc-mode can do this (and much more). Your examples can be converted like this:

Put the formula in some emacs buffer

```
$ y = sin(x)^2 $
```

With the cursor in the formula, activate calc-embedded mode

```
M-x calc-embedded
```

Switch the display language to C:

```
M-x calc-c-language
```

There you are:

```
$ y == pow(sin(x), 2) $
```

Note that it interprets the '=' sign in latex as an equality, which results in '==' for C. The latex equivalent to Cs assignment operator '=' would be '\\gets'.

More on this topic on [Turong's blog](http://truongnghiem.wordpress.com/2010/07/12/make-typing-mathematical-equations-in-latex-easier-with-emacs-calc/)

answered May 8 '12 at 13:28

[

![](https://www.gravatar.com/avatar/92e5e528653dbfb0c02e628b3e0bdc42?s=32&d=identicon&r=PG)

](https://stackoverflow.com/users/1215860/vonschlotzkow)

0

I know the question is too old, but I'll just add a reply anyway as a think it might help someone else later. The question popped up a lot for me in my searches.

I'm working on a tool that does something similar, in a [public git repo](https://github.com/mtarek/compitex)

You'll have to put some artificial limitations on your latex input, that's out of question. Currently the tool I wrote only supports mul, div, add, sub, sqrt, pow, frac and sum as those are the only set of operations I need to handle, and the imposed limitations can be a bit loose by providing a preprocessor (see preproc.l for an \[maybe not-so-good\] example) that would clean away the raw latex input.

answered Jul 29 '12 at 2:04

[

![](https://www.gravatar.com/avatar/dbf826408611197863d67b16b7a9adb4?s=32&d=identicon&r=PG)

](https://stackoverflow.com/users/1159107/mohamed-tarek)

I'm not sure there is a simple answer, because mathematical formulaes (in LaTeX documents) are actually ambiguous, so to automate their translation to some code requires automating their understanding.

And the MathML standard has, IIRC, two forms representing formulaes (one for displaying, another for computing) and there is some reason for that.

answered Oct 25 '11 at 8:27
