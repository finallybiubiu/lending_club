# naive bayes with cross validation, classes based on logistic regression

import numpy as np
import numpy.random as rnd
import pandas as pd
from sklearn.naive_bayes import GaussianNB
from sklearn.cross_validation import KFold
import matplotlib.pyplot as plt
import re
import os


# to do:
#    add k-fold cross-validation    (done)
#    add automatic random combinations of variables to minimize incorrect number  (done)
#    plot expected IR_TF from logistic regression function, compare w/ naive bayes

# loansData = pd.read_csv('https://spark-public.s3.amazonaws.com/dataanalysis/loansData.csv')
loansData = pd.read_csv('data/loansData.csv')  # downloaded data if no internet
loansData.dropna(inplace=True)

plotdir = 'naive_bayes_kfold_plots/'
if not os.access(plotdir, os.F_OK):
    os.mkdir(plotdir)

pat = re.compile('(.*)-(.*)')  # ()'s return two matching fields

def splitSum(s):
    t = re.findall(pat, s)[0]
    return (int(t[0]) + int(t[1])) / 2

sown = list(set(loansData['Home.Ownership']))
def own_to_num(s):
    return sown.index(s)

slurp = list(set(loansData['Loan.Purpose']))
def purpose_to_num(s):
    return slurp.index(s)

loansData['Interest.Rate'] = loansData['Interest.Rate'].apply(lambda s: float(s.rstrip('%')))
loansData['IR_TF'] = loansData['Interest.Rate'].apply(lambda x: 0 if x<12 else 1)
loansData['Debt.To.Income.Ratio'] = loansData['Debt.To.Income.Ratio'].apply(lambda s: float(s.rstrip('%')))
loansData['Loan.Length'] = loansData['Loan.Length'].apply(lambda s: int(s.rstrip(' months')))
loansData['FICO.Score'] = loansData['FICO.Range'].apply(splitSum)
loansData['Home.Type'] = loansData['Home.Ownership'].apply(own_to_num)
loansData['Loan.Purpose.Score'] = loansData['Loan.Purpose'].apply(purpose_to_num)

print 'loansData head\n', loansData[:5]
print 'loansData describe\n', loansData.describe()

gnb = GaussianNB()
dep_variables = ['IR_TF']
loans_target = loansData['IR_TF']
print 'loans_target head\n', loans_target[:5]

# plot predicted and incorrect target values
def plot_predict(label, correct, incorrect):
    plt.clf()
    plt.scatter(correct['FICO.Score'], correct['Amount.Requested'], c=correct['target'], \
         linewidths=0)
    plt.scatter(incorrect['FICO.Score'], incorrect['Amount.Requested'], c=incorrect['target'], \
         linewidths=1, s=20, marker='x')
    plt.xlim(620, 850)
    plt.ylim(0, 40000)
    locs, labels = plt.yticks()
    plt.yticks(locs, map(lambda x: '$'+str(int(x/1000))+'k', locs))
    plt.xlabel('FICO Score')
    plt.ylabel('Loan Amount Requested, USD')
    plt.title('Naive Bayes Predicted Interest Rates: red > 12%, blue < 12%')
    plt.savefig(plotdir+label+'_bayes_simple_intrate_predict.png')

def plot_theo(label, correct, incorrect):
# plot theoretical predicted not target (IR_TF) values
    plt.clf()
    plt.scatter(correct['FICO.Score'], correct['Amount.Requested'], c=correct['target'], \
         linewidths=0)
    plt.scatter(incorrect['FICO.Score'], incorrect['Amount.Requested'], c=incorrect['predict'], \
         linewidths=1, s=20, marker='x')
    plt.xlim(620, 850)
    plt.ylim(0, 40000)
    locs, labels = plt.yticks()
    plt.yticks(locs, map(lambda x: '$'+str(int(x/1000))+'k', locs))
    plt.xlabel('FICO Score')
    plt.ylabel('Loan Amount Requested, USD')
    plt.title('Naive Bayes Predicted Interest Rates: red > 12%, blue < 12%')
    plt.savefig(plotdir+label+'_bayes_simple_intrate_theo.png')

def naive_bayes_fold(train_data, train_target, test_data, test_target):
    pred = gnb.fit(train_data, train_target).predict(test_data)
#   print "Number of incorrectly labeled predicted points : %d out of %d" \
#         % ( (test_target != pred).sum(), test_target.shape[0] )
#   print "Number of correctly labeled predicted points : %d" % (test_target == pred).sum()
#   return (test_target != pred).sum()
    return pred

def do_naive_bayes(indep_variables, label='_label', predict_plot=False, theo_plot=False):
    if (label != '_label'):
        print 'label:', label
        print 'Dependent Variable(s):', dep_variables
        print 'Independent Variables:', indep_variables

# do it all with pd.DataFrame (could also do with np.ndarray)
    loans_data = pd.DataFrame( loansData[indep_variables] )

#   metrics = []
    pred = []
    kf = KFold(loans_data.shape[0], n_folds=4)
    for train, test in kf:
        train_data, test_data, train_target, test_target = loans_data.iloc[train], loans_data.iloc[test], loans_target.iloc[train], loans_target.iloc[test]
#       met = naive_bayes_fold(train_data, train_target, test_data, test_target)
#       metrics.append(met)
        pred_fold = naive_bayes_fold(train_data, train_target, test_data, test_target)
        pred.extend( pred_fold )

#       return pred, append to list or df to make correct, incorrect => plots
#       calc met score = (test_target != pred).sum()
#          or total score = (loans_target != pred_list).sum()

    loans_data['target'] = loans_target
    loans_data['predict'] = pred
#   score = reduce((lambda x,y: x + y), metrics)
    score = (loans_target != pred).sum()

    if (predict_plot):
        print "score: number of incorrectly labeled points: %d out of %d " % \
             ( score, loans_target.shape[0] )

    incorrect = loans_data[ loans_data['target'] != loans_data['predict'] ]
    correct = loans_data[ loans_data['target'] == loans_data['predict'] ]

    if (predict_plot):
        plot_predict(label, correct, incorrect)

    if (theo_plot):
        plot_theo(label, correct, incorrect)

    return score  # return pred?

indep_variables = ['FICO.Score', 'Amount.Requested']
do_naive_bayes(indep_variables, label='fa', predict_plot=True)

indep_variables = ['FICO.Score', 'Amount.Requested', 'Home.Type']
do_naive_bayes(indep_variables, label='fah', predict_plot=True)

indep_variables = ['FICO.Score', 'Amount.Requested', 'Home.Type', 'Revolving.CREDIT.Balance', 'Monthly.Income', 'Open.CREDIT.Lines', 'Debt.To.Income.Ratio']
do_naive_bayes(indep_variables, label='all7', predict_plot=True)

indep_variables = ['FICO.Score', 'Amount.Requested', 'Home.Type', 'Revolving.CREDIT.Balance', 'Monthly.Income', 'Open.CREDIT.Lines', 'Debt.To.Income.Ratio', 'Loan.Length', 'Loan.Purpose.Score', 'Amount.Funded.By.Investors', 'Inquiries.in.the.Last.6.Months']
do_naive_bayes(indep_variables, label='all', predict_plot=True)

indep_variables = ['FICO.Score', 'Amount.Requested', 'Home.Type', 'Loan.Length', 'Loan.Purpose.Score', 'Amount.Funded.By.Investors', 'Inquiries.in.the.Last.6.Months']
do_naive_bayes(indep_variables, label='better', predict_plot=True)

# find optimum set of indep_vars from numeric_vars by random sample, pseudo monte carlo
all_numeric_vars = ['FICO.Score', 'Amount.Requested', 'Home.Type', 'Revolving.CREDIT.Balance', 'Monthly.Income', 'Open.CREDIT.Lines', 'Debt.To.Income.Ratio', 'Loan.Length', 'Loan.Purpose.Score', 'Amount.Funded.By.Investors', 'Inquiries.in.the.Last.6.Months']

print '\nall_vars', all_numeric_vars

def random_opt(varlist, init_list):
    '''Optimize list by randomly adding variables, see if score decreases
    to find local minimum. Repeat many times to find global minimum.'''
    vlist = list(init_list)
    score = do_naive_bayes(vlist)
    offset = len(vlist)  # offset by length of initial vlist
    indices = range(len(varlist) - offset)
    rnd.shuffle(indices)
    for ix in indices:
        ilist  = list(vlist)
        ilist.append(varlist[ix + offset])
        iscore = do_naive_bayes(ilist)
        if iscore < score:
            vlist = list(ilist)
            score = iscore

    print ">>> >>> len %d, score %d" % (len(vlist), score)
#   print "vlist %s" % (vlist)

    return score, vlist

init_list = [all_numeric_vars[0], all_numeric_vars[1]]
opt_list = list(init_list)
opt_score = do_naive_bayes(opt_list, 'opt_init')
for ix in range(len(all_numeric_vars)):
    score, vlist = random_opt(all_numeric_vars, init_list)
    if score < opt_score:
        opt_list = vlist
        opt_score = score

print ">>> opt len %d, opt_score %d" % (len(opt_list), opt_score)
print "opt_list %s" % (opt_list)

do_naive_bayes(opt_list, label='opt', predict_plot=True)

print '\nplots created'


