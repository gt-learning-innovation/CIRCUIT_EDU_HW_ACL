![Source Image](8_3-10_source.png)
> [A sequence of circuit diagrams shows the simplification of the circuit for t < 0 to find an initial condition. The inductor is omitted and the switch is treated as a short circuit.]
>
> 1.  **Initial Diagram:** A redrawing of the original circuit components relevant for t < 0. A 20V source is in series with a 4Ω resistor. This is in parallel with a 12Ω resistor, a 9A current source, a 3Ω resistor, and a 9Ω resistor. The voltage `v` is marked across the 9Ω resistor.
> 2.  **Source Transformation:** `=>` The 20V source and 4Ω series resistor are transformed into a 5A current source in parallel with a 4Ω resistor.
> 3.  **Combine Parallel Elements:** `=>` The parallel current sources (5A and 9A) are combined into a single 14A source. The parallel resistors (4Ω, 12Ω, and 3Ω) are combined into a single `3/2 Ω` resistor. The circuit is now a 14A source in parallel with a `3/2 Ω` resistor, connected to the 9Ω resistor.
> 4.  **Final Source Transformation:** `=>` The 14A source and `3/2 Ω` parallel resistor are transformed into a 21V voltage source in series with a `3/2 Ω` resistor. This is connected to the 9Ω resistor.

$$
\begin{aligned}
v &= 9 \left( \frac{21}{9 + \frac{3}{2}} \right) v \\
v &= 189 \left( \frac{2}{21} \right) v \\
v &= 18V
\end{aligned}
$$

---
> [A circuit diagram for t > 0 is drawn. It shows a 3Ω resistor, a 9Ω resistor, and a 1/2 H inductor connected in a series loop. The voltage `v` is labeled across the 9Ω resistor with the positive terminal on the left.]

$$
0 = 12 i_L(t) + \frac{1}{2} \frac{di_L}{dt}(t)
$$
$$
i_{Ln}(t) = C e^{-24t}
$$
$$
i_{L_F}(t) = B \rightarrow 0 = 24B
$$
$$
i_L(t) = C e^{-24t}
$$
$$
V(t) = 9 C e^{-24t}
$$
$$
V(0) = 18 = 9 C e^0
$$
$$
C = 2
$$

$$
\boxed{V(t) = 18e^{-24t} V, \quad t > 0s}
$$