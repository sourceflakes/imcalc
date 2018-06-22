from math import log, exp, sqrt, pi
from scipy.stats import norm
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import itertools

class imvc:
    n = norm.pdf
    N = norm.cdf
    
    def __init__(self, X_strikePrice,r_continouslyCompoundedRiskFreeInterest, q_continouslyCompoundedDividendYield):
        self.K = X_strikePrice
        self.r = r_continouslyCompoundedRiskFreeInterest
        self.q = q_continouslyCompoundedDividendYield

    def bs_delta(self,S,T,v,cp_flag):
        if T <= 0.0:
            return 0.0
        d1 = (log(S/self.K)+(self.r+v*v/2.)*T)/(v*sqrt(T))
        if cp_flag == 'c':
            delta = exp(-self.q*T)*self.N(d1)
        else:
            delta = exp(-self.q*T)*(self.N(d1) - 1)
        return delta

    def bs_gamma(self,S,T,v):
        if T <= 0.0:
            return 0.0
        d1 = (log(S/self.K)+(self.r+v*v/2.)*T)/(v*sqrt(T))
        gamma=(exp(-self.q*T)/(S*v*sqrt(T)))*(1/sqrt(2*pi))*(exp(pow(-d1,2)/2))
        return gamma

    #Ignoring the last term of the theta calculation as the q factor is 0(FOR NOW)
    def bs_theta(self,S,T,v,cp_flag):
        if T <= 0.0:
            return 0.0
        d1 = (log(S/self.K)+(self.r+v*v/2.)*T)/(v*sqrt(T))
        d2 = d1-v*sqrt(T)
        if cp_flag == 'c':
            theta = (1/T)*( -(((S*v*exp(self.q*T) / 2*sqrt(T)) * (1/sqrt(2*pi)) * (exp(pow(-d1,2)/2)  ))) - (self.r * S * exp(self.r*T) *self.N(d2)))
        else:
            theta = (1/T)*( -(((S*v*exp(self.q*T) / 2*sqrt(T)) * (1/sqrt(2*pi)) * (exp(pow(-d1,2)/2)  ))) + (self.r * S * exp(self.r*T) *self.N(-d2)))
        return theta

    def bs_realVega(self,S,T,v):
        if T <= 0.0:
            return 0.0
        d1 = (log(S/self.K)+(self.r+v*v/2.)*T)/(v*sqrt(T))
        realVega = (1/100.0) * (self.K * exp(-self.q*T) * sqrt(T)) * (1/sqrt(2*pi)) * (exp(pow(-d1,2)/2))
        return realVega

    #Approximation of implied volatility using Newton-Raphson method
    #Alternate to using gold-seek feature in M$ Excel.
    #http://www.codeandfinance.com/finding-implied-vol.html
    #IMPROVEMENTS define bs_price and bs_vega as static methods as these are used only by the class method find_vol
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

    def find_vol(self, target_value, S, T, call_put):
        MAX_ITERATIONS = 100
        PRECISION = 1.0e-5
        sigma = 0.5
        if T <= 0.0 :
           return 0.0
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
    def __init__(self, putFileName, callFileName, futFileName):
        self.dfPut = pd.read_csv(putFileName)
        self.dfCall = pd.read_csv(callFileName)
        self.dfFut = pd.read_csv(futFileName)
        self.IVDrame  = pd.DataFrame()    

    def imvCalcResults(self,  imcCalc):
        #Create new pandas Data Frame with the required coloums from the separate input CSV files
        self.IVDrame = pd.concat([self.dfPut['Expiry'], self.dfPut['Date'], self.dfPut['Close'], self.dfCall['Expiry'], self.dfCall['Date'], self.dfCall['Close'], self.dfFut['Close']],
                                axis=1,keys=['PutExpiry', 'PutDate', 'PutClose', 'CallExpiry', 'CallDate', 'CallClose', 'FutClose'])
        #Convert dates for pandas style operations
        self.IVDrame['PutExpiry'] =  pd.to_datetime(self.IVDrame['PutExpiry'])
        self.IVDrame['PutDate'] = pd.to_datetime(self.IVDrame['PutDate'])
        self.IVDrame['CallExpiry'] = pd.to_datetime(self.IVDrame['CallExpiry'])
        self.IVDrame['CallDate'] = pd.to_datetime(self.IVDrame['CallDate'])
        #Create new column t were t of type float and value is the calender days between Expiry and Date divided by 365.
        self.IVDrame['t'] = (self.IVDrame['PutExpiry'] - self.IVDrame['PutDate']) / np.timedelta64(365, 'D')
        #start calculating IV, delta, Gamma etc..
        self.IVDrame['IVPut'] = pd.DataFrame(list(map(imcCalc.find_vol, self.IVDrame.PutClose, self.IVDrame.FutClose, self.IVDrame.t, itertools.repeat('p', self.IVDrame.shape[0]))))
        self.IVDrame['IVCall'] = pd.DataFrame(list(map(imcCalc.find_vol, self.IVDrame.CallClose, self.IVDrame.FutClose, self.IVDrame.t, itertools.repeat('c', self.IVDrame.shape[0]))))
        self.IVDrame['deltaPut'] = pd.DataFrame(list(map(imcCalc.bs_delta, self.IVDrame.FutClose, self.IVDrame.t, self.IVDrame.IVPut, itertools.repeat('p', self.IVDrame.shape[0]))))
        self.IVDrame['deltaCall'] = pd.DataFrame(list(map(imcCalc.bs_delta, self.IVDrame.FutClose, self.IVDrame.t, self.IVDrame.IVCall, itertools.repeat('c', self.IVDrame.shape[0]))))
        self.IVDrame['gammaPut'] = pd.DataFrame(list(map(imcCalc.bs_gamma, self.IVDrame.FutClose, self.IVDrame.t, self.IVDrame.IVPut)))
        self.IVDrame['gammaCall'] = pd.DataFrame(list(map(imcCalc.bs_gamma, self.IVDrame.FutClose, self.IVDrame.t, self.IVDrame.IVCall)))
        self.IVDrame['thetaPut'] = pd.DataFrame(list(map(imcCalc.bs_theta, self.IVDrame.FutClose, self.IVDrame.t, self.IVDrame.IVPut, itertools.repeat('p', self.IVDrame.shape[0]))))
        self.IVDrame['thetaCall'] = pd.DataFrame(list(map(imcCalc.bs_theta, self.IVDrame.FutClose, self.IVDrame.t, self.IVDrame.IVCall, itertools.repeat('c', self.IVDrame.shape[0]))))
        self.IVDrame['vegaPut'] = pd.DataFrame(list(map(imcCalc.bs_realVega, self.IVDrame.FutClose, self.IVDrame.t, self.IVDrame.IVPut)))
        self.IVDrame['vegaCall'] = pd.DataFrame(list(map(imcCalc.bs_realVega, self.IVDrame.FutClose, self.IVDrame.t, self.IVDrame.IVCall)))
        return
        
def main():
    imvCalc = imvc(X_strikePrice = 9000, r_continouslyCompoundedRiskFreeInterest = 8.75/100, q_continouslyCompoundedDividendYield = 0.0)
    imvGenerator = imvcHelper(putFileName = 'NiftyJan9000Put.csv',callFileName = 'Jan9000Call2017.csv', futFileName = 'NiftyJanFut.csv')
    imvGenerator.imvCalcResults(imvCalc)
    print (imvGenerator.IVDrame )
    imvGenerator.IVDrame.to_csv('Output.csv', encoding='utf-8', index=False)


if __name__== "__main__":
  main()



