![Source Image](6_4-4_source.png)
> A circuit diagram is redrawn from the problem statement. The student has added labels for the nodes and outputs. The output of the top op-amp is labeled $v_{o+}$. The output of the bottom op-amp is labeled $v_{o-}$. The node at the inverting input of the top op-amp (at the top of resistor $R_2$) is labeled $v_a$. The node at the inverting input of the bottom op-amp (at the bottom of resistor $R_2$) is labeled $v_b$.

Ohm's Law for $R_2$:
$$ \frac{v_1-v_2}{R_2} = i $$

Ohm's Law for $R_1$:
$$ \frac{v_{o+}-v_1}{R_1} = i $$
$$ \frac{v_{o+}-v_1}{R_1} = \frac{v_1-v_2}{R_2} $$
$$ \Rightarrow v_{o+} = R_1(\frac{v_1-v_2}{R_2}) + v_1 $$

Ohm's Law for $R_3$:
$$ \frac{v_2-v_{o-}}{R_3} = i $$
$$ \frac{v_2-v_{o-}}{R_3} = \frac{v_1-v_2}{R_2} $$
$$ \Rightarrow v_{o-} = v_2 - \frac{R_3(v_1-v_2)}{R_2} $$

Source eq: $v_o = v_{o+} - v_{o-}$

Simplified
$$ v_o = \left[ \frac{R_1(v_1-v_2)}{R_2} + v_1 - v_2 + \frac{R_3(v_1-v_2)}{R_2} \right] $$
$$ = \frac{R_1v_1 - R_1v_2 + R_2v_1 - R_2v_2 + R_3v_1 - R_3v_2}{R_2} $$
$$ = \frac{v_1(R_1+R_2+R_3) - v_2(R_1+R_2+R_3)}{R_2} $$
$$ = \boxed{\frac{(v_1-v_2)(R_1+R_2+R_3)}{R_2}} $$