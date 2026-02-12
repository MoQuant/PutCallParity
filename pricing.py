import numpy as np
import warnings

# Filter out runtime warnings
warnings.filterwarnings("ignore", message="divide by zero encountered in scalar divide")
warnings.filterwarnings("ignore", message="invalid value encountered in scalar divide")

class OptionTree:

    def __init__(self, S, K, r, q, t, steps=50, optype='call'):
        self.S = S
        self.K = K
        self.r = r
        self.q = q
        self.t = t
        self.N = steps
        self.dt = t/steps
        self.optype = optype
        self.row = 4*steps + 2
        self.col = steps + 1
        self.center = int(self.row / 2 - 1)
        self.tree = [[0 for j in range(self.col)] for i in range(self.row)]

    def params(self, v):
        self.up = np.exp(v*np.sqrt(2.0*self.dt))
        self.down = 1.0/self.up
        self.m = 1.0
        
        A = np.exp((self.r - self.q)*self.dt/2.0)
        B = np.exp(-v*np.sqrt(self.dt/2.0))
        C = np.exp(v*np.sqrt(self.dt/2.0))

        self.pu = pow((A - B)/(C - B), 2)
        self.pd = pow((C - A)/(C - B), 2)
        self.pm = 1.0 - (self.pu + self.pd)

    def optionTree(self):
        self.tree[self.center][0] = self.S
        for j in range(self.col):
            for i in range(1, self.col - j):
                self.tree[self.center - 2*i][i + j] = self.tree[self.center - 2*(i-1)][i-1+j]*self.up
                self.tree[self.center + 2*i][i + j] = self.tree[self.center + 2*(i-1)][i-1+j]*self.down
                self.tree[self.center][i +j] = self.tree[self.center][i - 1 + j]*self.m    

        for i in range(self.row):
            if i % 2 != 0:
                if self.optype == 'call':
                    self.tree[i][-1] = np.max([self.tree[i - 1][-1] - self.K, 0.0])
                else:
                    self.tree[i][-1] = np.max([self.K - self.tree[i - 1][-1], 0.0])

        inc = 2
        for j in range(2, self.col+1):
            for i in range(inc, self.row - inc):
                if i % 2 != 0:
                    A = self.tree[i - 2][-j+1]
                    B = self.tree[i][-j+1]
                    C = self.tree[i + 2][-j+1]
                    cash = self.pu*A + self.pm*B + self.pd*C
                    cash = np.exp(-self.r*self.dt)*cash
                    if np.isnan(cash):
                        return 0
                    if self.optype == 'call':
                        self.tree[i][-j] = np.max([self.tree[i - 1][-j] - self.K, cash])
                    else:
                        self.tree[i][-j] = np.max([self.K - self.tree[i - 1][-j], cash])
            inc += 2
        
        return self.tree[self.center + 1][0]

    def optionVega(self, v):
        dV = 0.01
        self.params(v+dV)
        c1 = self.optionTree()
        self.params(v-dV)
        c0 = self.optionTree()
        vega = (c1 - c0)/(2.0*dV)
        return vega

    def impliedVol(self, option_price):
        v0 = 0.1
        v1 = 0.2
        for i in range(12):
            self.params(v0)
            try:
                v1 = v0 - 0.01*(self.optionTree() - option_price)/self.optionVega(v0)
            except:
                return False
            if abs(v1 - v0) < 0.0001:
                break
            v0 = v1
        if v1 < 0:
            return np.nan
        return v1