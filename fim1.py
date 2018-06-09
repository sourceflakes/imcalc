import csv
import math
from scipy.stats import norm
from datetime import datetime
from math import pi
from math import sqrt
from math import log
from math import exp


n = norm.pdf
N = norm.cdf

def bs_price(cp_flag,S,K,T,r,v,q=0.0):
    print("bs_price args are {0} {1} {2} {3} {4} {5}".format(cp_flag, S, K, T, r, v))
    d1 = (log(S/K)+(r+v*v/2.)*T)/(v*sqrt(T))
    d2 = d1-v*sqrt(T)
    if cp_flag == 'c':
        price = S*exp(-q*T)*N(d1)-K*exp(-r*T)*N(d2)
    else:
        price = K*exp(-r*T)*N(-d2)-S*exp(-q*T)*N(-d1)
    return price

def bs_vega(cp_flag,S,K,T,r,v,q=0.0):
fg#    print("bs_price args are {0} {1} {2} {3} {4} {5}".format(cp_flag,S,K,T,r,v))
    d1 = (log(S/K)+(r+v*v/2.)*T)/(v*sqrt(T))
    return S * sqrt(T)*n(d1)

def find_vol(target_value, call_put, S, K, T, r):
    MAX_ITERATIONS = 100
    PRECISION = 1.0e-5

    sigma = 0.5
    for i in xrange(0, MAX_ITERATIONS):
        price = bs_price(call_put, S, K, T, r, sigma)
        vega = bs_vega(call_put, S, K, T, r, sigma)

        price = price
        diff = target_value - price  # our root

        print i, sigma, diff

        if (abs(diff) < PRECISION):
            return sigma
        sigma = sigma + diff/vega # f(x) / f'(x)

    # value wasn't found, return best guess so far
    return sigma


date_format = "%d-%b-%y"

V_market = 17.5
K = 585
T = float((datetime.strptime('25-Jan-17', date_format) - datetime.strptime('4-Nov-16', date_format)).days)/365.0
S = 586.08
r = 0.0002
cp = 'c' # call option

#implied_vol = find_vol(V_market, cp, S, K, T, r)
#implied_vol = find_vol(1.52, cp, 23.95, 24.0, 71.0/365.0, 0.05)
implied_vol = find_vol(504.0, cp, 8549.1, 9000, T, .0875)

print 'Implied vol: %.2f%%' % (implied_vol * 100)

#print 'Market price = %.2f' % V_market
#print 'Model price = %.2f' % bs_price(cp, S, K, T, r, implied_vol)
