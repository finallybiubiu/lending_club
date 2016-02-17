# test pca decomposition

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import re
import os

# loansData = pd.read_csv('https://spark-public.s3.amazonaws.com/dataanalysis/loansData.csv')
loansData = pd.read_csv('data/loansData.csv')  # downloaded data if no internet
loansData.dropna(inplace=True)

plotdir = 'pca_explore_plots/'
if not os.access(plotdir, os.F_OK):
    os.mkdir(plotdir)

pat = re.compile('(.*)-(.*)')  # ()'s return two matching fields

def splitSum(s):
    t = re.findall(pat, s)[0]
    return (int(t[0]) + int(t[1])) / 2

def convert_own_to_num(s):
    if s == 'RENT':
        return 0
    elif s == 'MORTGAGE':
        return 2
    elif s == 'OWN':
        return 3
    else:   # 'ANY'
        return 1

loansData['Interest.Rate'] = loansData['Interest.Rate'].apply(lambda s: float(s.rstrip('%')))
loansData['Loan.Length'] = loansData['Loan.Length'].apply(lambda s: int(s.rstrip(' months')))
loansData['Debt.To.Income.Ratio'] = loansData['Debt.To.Income.Ratio'].apply(lambda s: float(s.rstrip('%')))
loansData['Home.Ownership.Score'] = loansData['Home.Ownership'].apply(convert_own_to_num)
loansData['FICO.Average'] = loansData['FICO.Range'].apply(splitSum)

print 'loansData head\n', loansData[:5]
print '\nloansData basic stats\n', loansData.describe()   # print basic stats
numeric_keys = loansData.describe().keys()  # contains numeric keys from dataframe
print 'numeric_keys', numeric_keys

# keys = numeric_keys

# pca = PCA(n_components=2)
pca = PCA()
print 'pca dir:', dir(pca)

def do_pca(filename, keys, rescale=True):

    print 'do_pca:', filename, 'keys', keys

    # mp = keys.map( lambda k: np.matrix(loansData[k]).T )
    mp = map( lambda k: np.matrix(loansData[k]).T, keys )
    X = np.column_stack(mp)

    if (rescale):
        X = StandardScaler().fit_transform(X)

#   print 'X', type(X), X.shape

    pout = pca.fit(X) # class sklearn.decomposition.pca.PCA
#   print 'pca.fit dir', dir(pout)
    comps = pout.components_  # class numpy.ndarray
    print '  comps shape', comps.shape
    print comps    # print comps[0,:] # print comps[1,:]
    varratio = pout.explained_variance_ratio_
    varsum = reduce(lambda x,y: x+y, varratio)
    print '  explained_variance_ratio:', varratio.__class__, varratio, ': sum =', varsum
    vartotal = (100 * pd.Series(varratio).cumsum()).values
#   vartotal = map(lambda x: "%.1f%%" % x, vartotal)
    vartotal = map(lambda x: "{:.1f}%".format(x), vartotal)  # python 3 preferred
    print '  vartotal', vartotal.__class__, vartotal

    # plot pca components
    plt.clf()
    compx = comps[0,:]
    compy = comps[1,:]
    fig = plt.figure()
    ax = fig.add_subplot(111)
    plt.plot(compx, compy, 'o', color='blue', alpha=0.5)
    plt.plot([0.0], [0.0], '+', color='black', alpha=1.0)  # center position
    for i, txt in enumerate(keys):
        ax.annotate(txt, (compx[i], compy[i]), size='x-small')
    plt.xlim([-1.2,1.2])
    plt.ylim([-1.2,1.2])
    plt.xlabel('PCA-1')
    plt.ylabel('PCA-2')
    plt.title('Lending Club, PCA Components')
    plotname = plotdir + filename + '_comps' + '.png'
    plt.savefig(plotname)

    # plot pca component ratios
    plt.clf()
    fig = plt.figure()
    ax = fig.add_subplot(111)
    hscale = len(varratio)
    plt.bar(range(hscale), varratio, color='blue', align='center')
    for i, txt in enumerate(vartotal):
        ax.annotate(txt, (i-0.2+0.2/hscale, varratio[i]+0.002), size='x-small')
    plt.xlim([-0.6, hscale-0.4])
    plt.xlabel('PCA Component Number')
    plt.ylabel('Ratio')
    plt.title('Explained Variance Ratio by Component')
    plt.text(0.7, 0.85, 'Cumulative percentage of    \nexplained variance is shown',
        bbox=dict(edgecolor='black', fill=False), 
        transform=ax.transAxes, horizontalalignment='center', verticalalignment='center')
    plotname = plotdir + filename + '_var' + '.png'
    plt.savefig(plotname)

    pfit = pca.fit_transform(X)   # class numpy.ndarray
    print '  pfit shape', pfit.shape
    print pfit

    # plot transformed data
    plt.clf()
    plt.plot(pfit[:,0], pfit[:,1], 'o', color='blue', alpha=0.3)
    plt.xlabel('PCA-1')
    plt.ylabel('PCA-2')
    plt.title('Lending Club Data, PCA Axes')
    plotname = plotdir + filename + '_fit' + '.png'
    plt.savefig(plotname)

    print '  plot done: %s' % filename

print ''
# what is the minimum number of features needed in PCA model?
# as I add more above seven, not much change
do_pca(filename='all', keys=numeric_keys)
do_pca(filename='three', keys=['Amount.Requested', 'Interest.Rate', 'FICO.Average'])
do_pca(filename='three_unscale', keys=['Amount.Requested', 'Interest.Rate', 'FICO.Average'], rescale=False)
do_pca(filename='six', keys=['Amount.Requested', 'Interest.Rate', 'Debt.To.Income.Ratio', 'Monthly.Income', 'Revolving.CREDIT.Balance', 'FICO.Average'])
do_pca(filename='seven', keys=['Amount.Requested', 'Interest.Rate', 'Debt.To.Income.Ratio', 'Monthly.Income', 'Open.CREDIT.Lines', 'Revolving.CREDIT.Balance', 'FICO.Average'])

# see also linear_plots/scatter_matrix.png
# see also linear_plots/LoanPurpose_Histogram.png

