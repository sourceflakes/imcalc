import csv
from math import *
from scipy.stats import norm
from datetime import datetime
import matplotlib.pyplot as plt

#Set constants needed for calculations
X_strikePrice = 9000
r_continouslyCompoundedRiskFreeInterest = 8.75 
q_continouslyCompoundedDividendYield = 0.0

class imc:
    n = norm.pdf
    N = norm.cdf
    
    #def __init__(self):
    #equivalent of constructor, can do initialisation and stuff
        #self.data = []

    #Calculate Delta, Theta, Gamma, Vega
    def bs_theta(self,cp_flag,S,K,T,r,v,q=0.0):
    #    print("bs_price args are {0} {1} {2} {3} {4} {5}".format(cp_flag, S, K, T, r, v))
        d1 = (log(S/K)+(r+v*v/2.)*T)/(v*sqrt(T))
        if cp_flag == 'c':
            theta = exp(-q*T)*self.N(d1)
        else:
            theta = exp(-q*T)*(self.N(d1) - 1)
        return theta

    def bs_gamma(self,S,K,T,r,v,q=0.0):
        d1 = (log(S/K)+(r+v*v/2.)*T)/(v*sqrt(T))
        gamma=(exp(-q*T)/(S*v*sqrt(T)))*(1/sqrt(2*pi))*(exp(pow(-d1,2)/2))
        return gamma

    #Approximation of implied volatility using Newton-Raphson method
    #Alternate to using gold-seek feature in M$ Excel.
    #http://www.codeandfinance.com/finding-implied-vol.html


    def bs_price(self,cp_flag,S,K,T,r,v,q=0.0):
    #    print("bs_price args are {0} {1} {2} {3} {4} {5}".format(cp_flag, S, K, T, r, v))
        d1 = (log(S/K)+(r+v*v/2.)*T)/(v*sqrt(T))
        d2 = d1-v*sqrt(T)
        if cp_flag == 'c':
            price = S*exp(-q*T)*self.N(d1)-K*exp(-r*T)*self.N(d2)
        else:
            price = K*exp(-r*T)*self.N(-d2)-S*exp(-q*T)*self.N(-d1)
        return price

    def bs_vega(self,cp_flag,S,K,T,r,v,q=0.0):
    #    print("bs_price args are {0} {1} {2} {3} {4} {5}".format(cp_flag,S,K,T,r,v))
        d1 = (log(S/K)+(r+v*v/2.)*T)/(v*sqrt(T))
        return S * sqrt(T)*self.n(d1)

    def find_vol(self,target_value, call_put, S, K, T, r):
        MAX_ITERATIONS = 100
        PRECISION = 1.0e-5
        sigma = 0.5
        for i in range(0, MAX_ITERATIONS):
            price = self.bs_price(call_put, S, K, T, r, sigma)
            vega = self.bs_vega(call_put, S, K, T, r, sigma)
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

#class myCSVReader:
#    def(self,filename, ):

#Read PUTS data
with open('puts9000.csv', 'r') as csvfile:
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
with open('call9000.csv', 'r') as csvfile:
     callData = csv.reader(csvfile, delimiter=',')
     closingOptionCallList = []
     for row in callData:
          closingOptionCall = row[8]
          closingOptionCallList.append(closingOptionCall)

#Read FUTS data
with open('futs.csv', 'r') as csvfile:
     futsData = csv.reader(csvfile, delimiter=',')
     closingFutList = []
     for row in futsData:
          closingFut = row[6]
          closingFutList.append(closingFut)


#Initialize the class with q,r,strike values etc..

IV_impliedVolatilityCallList = []
tList = []
imcCalc = imc()   
for date, expiryPut, closingOptionPut, closingOptionCall, closingFut in zip(dateList, expiryListPut, closingOptionListPut, closingOptionCallList, closingFutList):
     #Calculate number of days between date and expiryPut(used to derive "t" by dividing by365)
     sDate = datetime.strptime(date, date_format)
     eDate = datetime.strptime(expiryPut, date_format)
     delta = eDate - sDate
     t = float(delta.days)/365.0

     IV_impliedVolatilityCall = imcCalc.find_vol(float(closingOptionCall), 'c',float(closingFut), X_strikePrice, t, r_continouslyCompoundedRiskFreeInterest/100.0)

     IV_impliedVolatilityPut = imcCalc.find_vol(float(closingOptionPut), 'p',float(closingFut), X_strikePrice, t, r_continouslyCompoundedRiskFreeInterest/100.0)

     thetaCall = imcCalc.bs_theta('c',float(closingFut), X_strikePrice,t,r_continouslyCompoundedRiskFreeInterest/100.0, IV_impliedVolatilityCall)

     thetaPut = imcCalc.bs_theta('p',float(closingFut), X_strikePrice,t,r_continouslyCompoundedRiskFreeInterest/100.0, IV_impliedVolatilityPut)

     
     gammaCall = imcCalc.bs_gamma(float(closingFut), X_strikePrice,t,r_continouslyCompoundedRiskFreeInterest/100.0, IV_impliedVolatilityCall)

     gammaPut = imcCalc.bs_gamma(float(closingFut), X_strikePrice,t,r_continouslyCompoundedRiskFreeInterest/100.0, IV_impliedVolatilityPut)

     print('{} {} {} {} {} {:4.2f}% {:4.2f}% {} {} {} {}'.format(date, expiryPut,\
      delta.days, closingOptionPut, closingFut, IV_impliedVolatilityCall * 100, \
      IV_impliedVolatilityPut * 100, thetaCall, thetaPut, gammaCall, gammaPut))

     IV_impliedVolatilityCallList.append(IV_impliedVolatilityCall * 100)
     tList.append(delta.days)

#Plotting

plt.plot(tList, IV_impliedVolatilityCallList)
plt.ylabel('Implied Volatility (%)')
plt.xlabel('Time to expiration (in days)')
plt.show()


