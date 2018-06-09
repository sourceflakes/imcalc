import csv
from math import *
from scipy.stats import norm
from datetime import datetime
import matplotlib.pyplot as plt

#Approximation of implied volatility using Newton-Raphson method
#Alternate to using gold-seek feature in M$ Excel.
#http://www.codeandfinance.com/finding-implied-vol.html
n = norm.pdf
N = norm.cdf

def bs_price(cp_flag,S,K,T,r,v,q=0.0):
#    print("bs_price args are {0} {1} {2} {3} {4} {5}".format(cp_flag, S, K, T, r, v))
    d1 = (log(S/K)+(r+v*v/2.)*T)/(v*sqrt(T))
    d2 = d1-v*sqrt(T)
    if cp_flag == 'c':
        price = S*exp(-q*T)*N(d1)-K*exp(-r*T)*N(d2)
    else:
        price = K*exp(-r*T)*N(-d2)-S*exp(-q*T)*N(-d1)
    return price

def bs_vega(cp_flag,S,K,T,r,v,q=0.0):
#    print("bs_price args are {0} {1} {2} {3} {4} {5}".format(cp_flag,S,K,T,r,v))
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
#       print i, sigma, diff
        if (abs(diff) < PRECISION):
            return sigma
        sigma = sigma + diff/vega # f(x) / f'(x)
    # value wasn't found, return best guess so far
    return sigma


#Set the date format found in the csv file
date_format = "%d-%b-%y"

#Read PUTS data
with open('puts9000.csv', 'rb') as csvfile:
     putsData = csv.reader(csvfile, delimiter=',')
     dateList = []
     expiryListPut = []
     closingOptionListPut = []
     for row in putsData:
          date = row[1]
          expiry = row[2]
          closingOption = row[8]
          dateList.append(date)
          expiryListPut.append(expiry)
          closingOptionListPut.append(closingOption)

#Read CALL data
with open('call9000.csv', 'rb') as csvfile:
     callData = csv.reader(csvfile, delimiter=',')
     closingOptionCallList = []
     for row in callData:
          closingOptionCall = row[8]
          closingOptionCallList.append(closingOptionCall)

#Read FUTS data
with open('futs.csv', 'rb') as csvfile:
     futsData = csv.reader(csvfile, delimiter=',')
     closingFutList = []
     for row in futsData:
          closingFut = row[6]
          closingFutList.append(closingFut)

#Set constants needed for calculations
X_strikePrice = 9000
r_continouslyCompoundedRiskFreeInterest = 8.75 
q_continouslyCompoundedDividendYield = 0.0
IV_impliedVolatilityCallList = []
tList = []          
for date, expiryPut, closingOptionPut, closingOptionCall, closingFut in zip(dateList, expiryListPut, closingOptionListPut, closingOptionCallList, closingFutList):
     #Calculate number of days between date and expiryPut(used to derive "t" by dividing by365)
     sDate = datetime.strptime(date, date_format)
     eDate = datetime.strptime(expiryPut, date_format)
     delta = eDate - sDate
     t = float(delta.days)/365.0
     IV_impliedVolatilityCall = find_vol(float(closingOptionCall), 'c',float(closingFut), X_strikePrice, t, r_continouslyCompoundedRiskFreeInterest/100.0)
     IV_impliedVolatilityPut = find_vol(float(closingOptionPut), 'p',float(closingFut), X_strikePrice, t, r_continouslyCompoundedRiskFreeInterest/100.0)
     print('{} {} {} {} {} {:4.2f}% {:4.2f}%'.format(date, expiryPut, delta.days, closingOptionPut, closingFut, IV_impliedVolatilityCall * 100, IV_impliedVolatilityPut * 100))
     IV_impliedVolatilityCallList.append(IV_impliedVolatilityCall * 100)
     tList.append(delta.days)

#Plotting

plt.plot(tList, IV_impliedVolatilityCallList)
plt.ylabel('Implied Volatility (%)')
plt.xlabel('Time to expiration (in days)')
plt.show()



