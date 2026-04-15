![Source Image](10_6-1_source.png)
> A frequency-domain circuit diagram is drawn. A phasor voltage source is labeled $48 \angle 45^\circ$. The inductor to its right is labeled $.02(2500)j$. The resistor below it is labeled $20$ with a downward current arrow labeled $i(t)$. A dependent voltage source is shown. To its right is a capacitor (unlabeled impedance). To the right in parallel with the capacitor is a resistor labeled $30$ in series with an inductor (unlabeled impedance). The output voltage across the rightmost inductor is labeled $V_o$.

$V_3 - V_2 = 25 \, i(t) = 25 \left(\frac{V_2}{20}\right)$
$V_3 = 2.25 V_2$

**Supernode KCL:**
$$ \frac{48 \angle 45 - V_2}{j50} = \frac{V_2}{20} + \frac{V_3 - V_o}{30} + \frac{V_3}{-j40} $$
$$ \frac{48 \angle 45}{j50} - \frac{V_2}{j50} = \frac{V_2}{20} + \frac{V_3 - V_o}{30} + \frac{V_3}{-j40} $$
$$ \frac{48 \angle 45}{j50} = \left(\frac{1}{j50} + \frac{1}{20}\right)V_2 + \left(\frac{1}{30} + \frac{1}{-j40}\right)V_3 - \frac{1}{30}V_o $$
$$ \frac{48 \angle 45}{j50} = \left(\frac{1}{j50} + \frac{1}{20} + \frac{2.25}{30} + \frac{2.25}{-j40}\right)V_2 - \frac{1}{30}V_o $$

**KCL @ Vo**
$$ \frac{V_3 - V_o}{30} = \frac{V_o}{j25} $$
$$ 0 = \left(-\frac{1}{30}\right) 2.25 V_2 + \left(\frac{1}{30} + \frac{1}{j25}\right)V_o $$

$$ V_o(t) = 14.67 \cos(2500t + 5.6^\circ) \, \text{V} $$