'''
    Put-Call Parity on American Options for $SPY
    C - P = Se^-qt - Ke^-rt
'''

# FINANCIAL MODELING PREP KEY
def key():
    return open('auth.txt','r').read()

def quote(ticker='SPY'):
    return f'https://financialmodelingprep.com/stable/quote?symbol={ticker}&apikey={key()}'

def yrates():
    return f'https://financialmodelingprep.com/stable/treasury-rates?apikey={key()}'

import requests
import numpy as np
import json
import time, datetime

stamp = lambda: int(time.time())

def PullChain(index=3, kindex=6):
    chain = json.loads(open('chain.json','r').read())
    chain = chain['options']
    expiry = list(chain.keys())
    cstrikes = list(chain[expiry[index]]['c'].keys())[kindex]
    pstrikes = list(chain[expiry[index]]['p'].keys())[kindex]
    call_price = chain[expiry[index]]['c'][cstrikes]['l']
    put_price = chain[expiry[index]]['p'][pstrikes]['l']
    return [float(u) for u in (call_price, put_price, cstrikes, pstrikes)], expiry[index]

def PullPrice(ticker='SPY'):
    resp = requests.get(quote(ticker=ticker)).json()
    return resp[0]['price']

def PullRiskFreeRate(expiry):
    resp = requests.get(yrates()).json()
    maturity = resp[0]
    times = [1/12, 2/12, 3/12, 6/12, 12/12, 24/12]
    labels = ['month1','month2','month3','month6','year1','year2']
    rates = [float(maturity[l])/100.0 for l in labels]
    T0 = time.mktime(datetime.datetime.strptime(expiry, '%Y-%m-%d').timetuple())
    for i in range(len(rates)):
        if (T0 - stamp())/(60*60*24*30*12) < times[i]:
            return rates[i], (T0 - stamp())/(60*60*24*30*12)
    return None, None


S = PullPrice()
q = 0.0105

(C, P, Kc, Kp), T = PullChain(index=6, kindex=40)
X = 0.5*Kc + 0.5*Kp

rf, t = PullRiskFreeRate(T)

sideA = C - P
sideB = S*np.exp(-q*t) - X*np.exp(-rf*t)

print("Asset: SPY")
print("Stock Price: ", S)
print("Strike Price: ", X)
print("Risk-Free Rate: ", rf)
print("Expiry: ", T)
print("Sides: ", sideA, sideB)

sideA = C
sideB = P + S*np.exp(-q*t) - X*np.exp(-rf*t)

print("XSides: ", sideA, sideB)

sideA = P
sideB = C - S*np.exp(-q*t) + X*np.exp(-rf*t)

print("YSides: ", sideA, sideB)




