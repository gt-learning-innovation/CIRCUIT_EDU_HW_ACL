![Source Image](8_3-10_source.png)
> [On the left, the student redraws the original circuit but with the inductor removed (open-circuited) to find the initial voltage across where the inductor will be. From left to right there is a 20 V source in series with a 4 Ω resistor, followed by a node that branches downward to a 12 Ω resistor, then to a 9 A current source, then to a 3 Ω resistor, all in parallel. To the right of this parallel network is a 9 Ω resistor whose right terminal is labeled with $+$ at the top and $-$ at the bottom as $v$.  
> The student then replaces the 4 Ω, 12 Ω, and 3 Ω resistors and the 9 A current source with equivalent sources/resistances: first, turning the 20 V source and 4 Ω resistor into an equivalent 5 A current source in parallel with 4 Ω, then showing that 5 A source in parallel with the 12 Ω resistor, the 9 A source, and the 3 Ω resistor, all feeding the 9 Ω resistor where $v$ is measured.  
> Next, the two current sources (5 A and 9 A) are added in parallel to yield a single 14 A source in parallel with an equivalent resistance made from the 4 Ω, 12 Ω, and 3 Ω resistors in parallel.  
> Finally, these parallel resistors are combined into a single 3 Ω resistor in series with the 9 Ω resistor to the right, still labeled $v$ with $+$ at the top and $-$ at the bottom.  
> On the right side of the page, the student draws the circuit for $t>0$ where the inductor is connected: a 3 Ω resistor in series with a 9 Ω resistor, and a $1/2$ H inductor in series with them, with the voltage across the 9 Ω resistor labeled $v$.]

---

**Left side (initial conditions and equivalent circuit)**

$$
\text{(top node currents)} \Rightarrow 5\text{A} \quad 4\Omega \quad 12\Omega \quad 9\text{A} \quad 3\Omega \quad 9\Omega \; v^+
$$

*add curr srcs in parallel*

$$
14\text{A} \quad \boxed{\frac{3}{2}\,\Omega} \quad 9\Omega^{+}_{-}
$$

$$
\boxed{3\Omega} \quad 9\Omega^{+}_{-}
$$

$$
\frac{1}{\frac{1}{4} + \frac{1}{12} + \frac{1}{3}} \Rightarrow \frac{12}{8}
$$

$$
V = 9\left(\frac{21}{9 + \frac{3}{2}}\right)\,V
$$

$$
V = \frac{189}{\frac{21}{2}}\,V
$$

$$
V = 18\,V
$$

---

**Right side (differential equation and solution)**

> [Small circuit: a 3 Ω resistor in series with a $1/2$ H inductor and a 9 Ω resistor, with $+$ at the left of the 9 Ω and $-$ at the right labeled $v$.]

$$
0 = 12\,i_L(t) + \tfrac{1}{2}\frac{d}{dt} i(t)
$$

$$
i_L'(t) = C e^{-24t}
$$

$$
i_{L,c}(t) = B \quad \Rightarrow 0 = 24 B
$$

$$
i_L(t) = C e^{-24t}
$$

$$
V(t) = 9 C e^{-24t}
$$

$$
V(0) = 18 = 9 C e^{0}
$$

$$
C = 2
$$

$$
\boxed{V(t) = 18 e^{-24t},\quad t>0}