When $t > 1.5$ and $t < 0$, the circuit can be reduced to:
> [A circuit diagram shows a 10V voltage source in series with an 8Ω resistor and a 0.05F capacitor. The voltage across the capacitor is labeled v(t) with the positive terminal on top.] => [The same circuit is redrawn for clarity.]

When $0 < t < 1.5$:
> [A circuit diagram shows a 1.25A current source (labeled 10/8) in parallel with two 8Ω resistors and a 0.05F capacitor.] => [The two 8Ω resistors in parallel are combined into a single 4Ω resistor. The student notes this is from $1/(1/8 + 1/8)$. The circuit now shows the 1.25A current source in parallel with the 4Ω resistor and the 0.05F capacitor.] => [A source transformation is performed on the current source and parallel resistor, resulting in a 5V voltage source (from $1.25 \times 4$) in series with a 4Ω resistor and the 0.05F capacitor. The voltage across the capacitor is labeled v(t).]

Since circuit will be at steady state, we know $v(0) = 10V$
When $0 < t < 1.5$, $R_t = 4\Omega$ and $V_{oc} = 5V$.
$$ \tau = R_t \cdot C = 4 \times 0.05 = 0.2s $$
$$ v(t) = V_{oc} + (v(0) - V_{oc})e^{-t/\tau} = 5 + (10 - 5)e^{-5t} = 5 + 5e^{-5t} \text{ V for } 0 < t < 1.5s $$
$v(1.5) \approx 5V$

When $t > 1.5s$, $V_{oc} = 10V$ and $R_t = 8\Omega$.
$$ \tau = R_t \cdot C = 8 \times 0.05 = 0.4s $$
$$ v(t) = 10 + (5 - 10)e^{-(t-1.5)/\tau} = 10 - 5e^{-2.5(t-1.5)} \text{ V for } t > 1.5s $$

$$ v(t) = \begin{cases} 5 + 5e^{-5t} \text{ V}, & 0 < t < 1.5s \\ 10 - 5e^{-2.5(t-1.5)} \text{ V}, & t > 1.5s \end{cases} $$