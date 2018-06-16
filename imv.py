import csv
from math import *
from scipy.stats import norm
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd

class imvc:
    n = norm.pdf
    N = norm.cdf
    
    def __init__(self, X_strikePrice,r_continouslyCompoundedRiskFreeInterest, q_continouslyCompoundedDividendYield):
        self.K = X_strikePrice
        self.r = r_continouslyCompoundedRiskFreeInterest
        self.q = q_continouslyCompoundedDividendYield

    def bs_theta(self,cp_flag,S,T,v):
        d1 = (log(S/self.K)+(self.r+v*v/2.)*T)/(v*sqrt(T))
        if cp_flag == 'c':
            theta = exp(-self.q*T)*self.N(d1)
        else:
            theta = exp(-self.q*T)*(self.N(d1) - 1)
        return theta

    def bs_gamma(self,S,T,v):
        d1 = (log(S/self.K)+(self.r+v*v/2.)*T)/(v*sqrt(T))
        gamma=(exp(-self.q*T)/(S*v*sqrt(T)))*(1/sqrt(2*pi))*(exp(pow(-d1,2)/2))
        return gamma

    #Approximation of implied volatility using Newton-Raphson method
    #Alternate to using gold-seek feature in M$ Excel.
    #http://www.codeandfinance.com/finding-implied-vol.html
    def bs_price(self,cp_flag,S,T,v):
        d1 = (log(S/self.K)+(self.r+v*v/2.)*T)/(v*sqrt(T))
        d2 = d1-v*sqrt(T)
        if cp_flag == 'c':
            price = S*exp(-self.q*T)*self.N(d1)-self.K*exp(-self.r*T)*self.N(d2)
        else:
            price = self.K*exp(-self.r*T)*self.N(-d2)-S*exp(-self.q*T)*self.N(-d1)
        return price

    def bs_vega(self,cp_flag,S,T,v):
        d1 = (log(S/self.K)+(self.r+v*v/2.)*T)/(v*sqrt(T))
        return S * sqrt(T)*self.n(d1)

    def find_vol(self, target_value, call_put, S, T):
        MAX_ITERATIONS = 100
        PRECISION = 1.0e-5
        sigma = 0.5
        for i in range(0, MAX_ITERATIONS):
            price = self.bs_price(call_put, S, T, sigma)
            vega = self.bs_vega(call_put, S, T, sigma)
            price = price
            diff = target_value - price  # our root
    #       print i, sigma, diff
            if (abs(diff) < PRECISION):
                return sigma
            sigma = sigma + diff/vega # f(x) / f'(x)
        # value wasn't found, return best guess so far
        return sigma

class imvcHelper:
    date_format = "%d-%b-%y"
    
    def __init__(self, putFileName, callFileName, futFileName):
        self.dfPut = pd.read_csv(putFileName)
        self.dfCall = pd.read_csv(callFileName)
        self.dfFut = pd.read_csv(futFileName)

    def imvCalcResults(self,  imcCalc):
        for (putIndex,putRow), (callIndex,callRow), (futIndex,futRow) in zip (self.dfPut.iterrows(), self.dfCall.iterrows(), self.dfFut.iterrows()):
            t = float((datetime.strptime(putRow['Expiry'], self.date_format) - datetime.strptime(putRow['Date'], self.date_format)).days)/365.0
            if t > 0:
                IV_impliedVolatilityCall = imcCalc.find_vol(float(callRow['Close']), 'c',float(futRow['Close']), t)
                IV_impliedVolatilityPut = imcCalc.find_vol(float(putRow['Close']), 'p',float(futRow['Close']), t)

                thetaCall = imcCalc.bs_theta('c',float(futRow['Close']), t, IV_impliedVolatilityCall)
                thetaPut = imcCalc.bs_theta('p',float(futRow['Close']), t, IV_impliedVolatilityPut)

                gammaCall = imcCalc.bs_gamma(float(futRow['Close']), t, IV_impliedVolatilityCall)
                gammaPut = imcCalc.bs_gamma(float(futRow['Close']), t, IV_impliedVolatilityPut)

                print('{} {} {} {} {:4.2f}% {:4.2f}% {} {} {} {}'.format(putRow['Date'], putRow['Expiry'], putRow['Close'], callRow['Close'], IV_impliedVolatilityCall * 100, IV_impliedVolatilityPut * 100, thetaCall, thetaPut, gammaCall, gammaPut))

imvCalc = imvc(X_strikePrice = 9000, r_continouslyCompoundedRiskFreeInterest = 8.75/100, q_continouslyCompoundedDividendYield = 0.0)
imvGenerator = imvcHelper(putFileName = 'NiftyJan9000Put.csv',callFileName = 'Jan9000Call2017.csv', futFileName = 'NiftyJanFut.csv')
imvGenerator.imvCalcResults(imvCalc)



