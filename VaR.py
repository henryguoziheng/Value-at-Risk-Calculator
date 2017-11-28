# -*- coding: utf-8 -*-

from __future__ import division
from math import sqrt
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import norm
from sklearn.preprocessing import normalize

__author__ = 'Henry'
__date__ = '2017-11-25'


class GetVaR:

    def __init__(self, simulationNum, stockData, position, T):
        '''
        :param simulationNum: int
        :param stockData: DataFrame, columns = ['stock1', 'stock2', ...], no index, already del date
        :param position: list
        :param T: float
        :return: null
        '''

        self.simulationNum = simulationNum
        self.stockData = stockData
        self.position = position
        self.T = T
        self.delta_t = T / simulationNum
        self.beta = 0.01
        self.simuGBM()
        self.getReturn()
        self.getStockVaR(self.beta)

    def simuGBM(self):
        '''
        :return: null, see plotGBM
        '''

        df = self.stockData.copy()
        for i in df.columns:
            df['return_%s'%i] = df[i].pct_change()
            df = df.drop([i], axis = 1)

        miu = []
        sigma = []
        for i in df.columns:
            avrg = np.mean(df[i]) * 252
            vol = np.std(df[i]) * sqrt(252)
            miu2 = avrg + 0.5 * vol**2
            miu.append(miu2)
            sigma.append(vol)

        data = self.stockData.as_matrix()
        data = data.T
        cov_matrix = np.corrcoef(data)

        C = np.linalg.cholesky(cov_matrix)
        s0 = data[:,-1]

        bm = []
        for i in range(len(data)):
            temp = norm.rvs(loc = 0, scale = 1, size = self.simulationNum)
            bm.append(temp)
        bm = np.dot(C,bm)
        dynamics = []
        for x in range(len(data)):
            temp = [s0[x]]
            for j in range(self.simulationNum):
                ds = temp[-1] * (miu[x] * self.delta_t + sigma[x] * np.sqrt(self.delta_t) * bm[x][j])
                temp.append(ds + temp[-1])
            dynamics.append(temp)

        for i in range(len(dynamics)):
            plt.plot(np.linspace(0, self.T, self.simulationNum + 1), dynamics[i])


    def plotGBM(self, num):
        '''
        :param num: int, number of Monte Carlo simulation
        :return: null, plot figure
        '''

        for i in range(num):
            self.simuGBM()
            plt.title("GBM STOCK DYNAMIC",fontsize=20)
            plt.ylabel("STOCK PRICE",fontsize=20)
            plt.grid()
        plt.show()


    def getReturn(self):
        '''
        :return: list
        '''

        df = self.stockData.copy()
        for i in df.columns:
            df['return_%s'%i] = df[i].pct_change()
            df = df.drop([i], axis = 1)

        miu = []
        sigma = []
        for i in df.columns:
            avrg = np.mean(df[i]) * 252
            vol = np.std(df[i]) * sqrt(252)
            miu2 = avrg + 0.5 * vol**2
            miu.append(miu2)
            sigma.append(vol)

        data = self.stockData.as_matrix()
        data = data.T
        cov_matrix = np.corrcoef(data)

        C = np.linalg.cholesky(cov_matrix)
        #print C
        s0 = data[:,0]

        rvs=[]
        for i in range(len(s0)):
            temp = norm.rvs(loc = 0, scale = 1, size = self.simulationNum)
            rvs.append(temp)

        bm = np.dot(C, rvs)

        sum = 0
        df2 = np.zeros([len(bm[0]), len(s0)])
        for i in range(len(s0)):
            for j in range(len(bm[0])):
                st = s0[i] * np.exp(miu[i] * self.T - 0.5 * sigma[i] ** 2 * self.T + sigma[i] * np.sqrt(self.T) * bm[i][j])
                p = self.position[i]*(st - s0[i])
                df2[j][i] = p
                sum += p

        df3 = pd.DataFrame(data = df2, index = range(len(bm[0])), columns = range(len(s0)))
        df3['sum'] = df3.apply(lambda x: x.sum(), axis=1)
        z = df3['sum'].tolist()

        return z


    def getStockVaR(self, alpha):
        '''
        :param alpha: float
        :return: float
        '''

        r = self.getReturn()
        r = sorted(r)

        VaR = r[int(alpha * len(r))]
        return VaR

    def getStockAVaR(self, alpha):
        '''
        :param alpha: float
        :return:
        '''

        nSteps = np.arange(0, alpha, alpha/100)
        varList = []
        for i in nSteps:
            self.beta = i
            stockVaR = self.getStockVaR(float(i))
            varList.append(stockVaR)
        AVaR = sum(varList)/100
        return AVaR


    def plotReturnDis(self):
        '''
        :return: plot the return distribution
        '''

        r = self.getReturn()
        plt.hist(r, bins=400, alpha=0.40, color="cyan")
        plt.show()


'''
simulationNum = 10000
position = [3, 6, -4]

T = 0.08333333

stockData = pd.read_excel("portfolio.xlsx")
stockData = stockData.drop('Date', axis = 1)

#print stockData
var = GetVaR(simulationNum, stockData, position, T)
print var.plotReturnDis()
'''
