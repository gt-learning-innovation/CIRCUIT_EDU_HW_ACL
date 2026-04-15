![Source Image](9_7-2_source.png)
$V_s = iR + L\frac{di}{dt} + V$
$i = C\frac{dv}{dt}$
$V_s = LC\frac{d^2v}{dt^2} + RC\frac{dv}{dt} + V$
$\frac{d^2v}{dt} + \frac{R}{L}\frac{dv}{dt} + \frac{1}{LC}v = V_s$

a) $V_s = 2$
$0+0+12000V_f = 2$
$$ V_f = 1/6000 V $$

b) $V_s = 0.2t$
Assume $V_f = At+B$
$70A + 12000At + 12000B = 0.2t$
$70A + 12000B = 0$
$12000At = 0.2t$
$A = \frac{1}{60000}$
$B=350$
$$ V_f = \frac{t}{60000} + 350V $$

c) $V_s = e^{-30t}$ assume $V_f = Ae^{-30t}$
$900A - 2100Ae^{-30t} + 12000Ae^{-30t} = e^{-30t}$
$10800Ae^{-30t} = e^{-30t}$
$A = \frac{1}{10800}$
$$ V_f = \frac{e^{-30t}}{10800} V $$