import csv
import math
from scipy.stats import norm
from datetime import datetime
from math import pi
from math import sqrt
from math import log
from math import exp
#s = stock price
#k = strike
#t = time to maturity
#rf = risk free interest
#cp = +/-1 call/put
#price = option price

def newtonRap(cp, price, s, k, t, rf):
    v = sqrt(2*pi/t)*price/s
    print "initial volatility: ",v
    for i in range(1, 100):
        d1 = (log(s/k)+(rf+0.5*pow(v,2))*t)/(v*sqrt(t))
        d2 = d1 - v*sqrt(t)
        vega = s*norm.pdf(d1)*sqrt(t)
        price0 = cp*s*norm.cdf(cp*d1) - cp*k*exp(-rf*t)*norm.cdf(cp*d2)
        v = v - (price0 - price)/vega
        print "price, vega, volatility\n",(price0, vega, v)
        if abs(price0 - price) < 1e-25 :
            break
    return v


#v = newtonRap(cp=1, price = 504.0, s=8549.1, k=9000.0, t=82.0/365, rf=8.75)
v=newtonRap(cp=1, price = 1.52, s=23.95, k=24, t=71.0/365, rf=0.05)
print v
