# -*- coding: utf-8 -*-
"""
Statistical methods for CO2 data processing

@author: Colin Dietrich 2017
"""

import numpy as np
import matplotlib.pyplot as plt

from numpy import mean, linspace
from scipy.optimize import curve_fit
from sklearn import linear_model
from sklearn.model_selection import train_test_split

from . import plot_plt
from .algebra import linear, natural_log


def iqr_mask(series, low=0.25, high=0.75):
    """Calculate quantiles and return a boolean mask for values 
    outside the Interquartile Range (IQR)
    
    Parameters
    ----------
    series : array-like, data to create mask for
    low : float, lower quantile boudnary, between 0-1
    high : float, high quantile boudary, between 0-1
    
    Returns
    -------
    array-like, boolean true if point is OUTSIDE the IQR
    """
    q1 = np.percentile(series, low*100)
    q3 = np.percentile(series, high*100)
    iqr = q3 - q1
    iqr_mask = (series < (q1 - 1.5 * iqr)) | (series > (q3 + 1.5 * iqr))
    return iqr_mask

    
class CurveFit(object):
    """Linear regression calculation and application using
    least squares fit from Scipy"""

    def __init__(self):
        self.x = None
        self.y = None

        self.popt = None
        self.pcov = None

        self.a = None
        self.b = None

        self.description = None
        self.solution = False
        self.solution_type = None

    def fit(self):
        """Calculate a 2D linear regression fit using
        scipy.optimize.curve_fit (defaults to LM least squares)
        """

        self.popt, self.pcov = curve_fit(linear, self.x, self.y)
        self.a = self.popt[0]
        self.b = self.popt[1]
        self.solution = True
        self.solution_type = 'linear'

    def fit_log(self):
        self.popt, self.pcov = curve_fit(lambda t, a, b: a*np.log(t)+b,  self.x,  self.y)
        self.a = self.popt[0]
        self.b = self.popt[1]
        self.solution = True
        self.solution_type = 'log'

    def fit_exp(self, p0=(0,0)):
        self.popt, self.pcov = curve_fit(lambda t ,a, b: a*np.log(t)+b,  self.x,  self.y, p0=p0)
        self.a = self.popt[0]
        self.b = self.popt[1]
        self.solution = True
        self.solution_type = 'exp'

    def apply(self, xn):
        """Apply linear curve fit to data, xn

        Parameters
        ----------
        xn : array-like, independent variable data to calculate
            curve fit data, y, at

        Returns
        -------
        yn : array-like, calculated dependent data from fit
        """

        return linear(xn, self.a, self.b)

    def apply_log(self, xn):
        return natural_log(xn, self.a, self.b)

    def plot(self, plot_data=True, x=None, y=None):
        """Plot fit
        Parameters
        ----------
        plot_data : bool
        x : array
        y : array
        """

        if (x is None) & (y is None):
            x = self.x
            y = self.y
        if plot_data:
            plt.scatter(x, y, color='black', marker='+', label='All Data')

        if self.solution:
            sol_types = {'linear': self.apply, 'log': self.apply_log}
            label_types = {'linear': 'Fit: {:3f}(x) + {:3f}'.format(self.a, self.b),
                           'log': 'Fit: {:3f} * ln(x) + {:3f}'.format(self.a, self.b)}
            fapply = sol_types[self.solution_type]
            plt.plot(x, fapply(x), 'r-',
                     label=label_types[self.solution_type])
        plot_plt.show(title=self.description)


class Fit2D(object):
    """Linear regression calculation and application using
    least squares fit from scikitlearn

    Model selection is linear or log based on fit_type.

    Shamelessly refactored from scikit-learn.org :)
    """
    def __init__(self, fit_type='linear'):
        self.x = None
        self.y = None

        self.a = None
        self.b = None

        self.description = None
        self.solution = False

        self.random_seed = 69
        self.x_train = None
        self.x_test = None
        self.y_train = None
        self.y_test = None

        if fit_type == 'log':
            self.regr = linear_model.LogisticRegression()
        else:
            self.regr = linear_model.LinearRegression()

        self.mse = None
        self.variance = None

    def split(self):
        """Splite data into test and train data"""
        (self.x_train, self.x_test,
         self.y_train, self.y_test) = train_test_split(self.x, self.y,
                                                       test_size=0.33,
                                                       random_state=self.random_seed)

    def fit(self):
        """Calculate 2D linear regression fit using
        scikitlearn.linear_model.LinearRegression
        """

        # Train the model using the training sets
        self.regr.fit(self.x_train, self.y_train)
        self.mse = self.regr.predict(self.x_test) - self.y_test
        self.mse = np.mean(self.mse**2)
        self.variance = self.regr.score(self.x_test, self.y_test)
        self.a = self.regr.coef_[0][0]
        self.b = self.regr.intercept_[0]
        self.solution = True

    def plot(self):
        """Plot fit
        Parameters
        ----------
        """

        plt.scatter(self.x_test, self.y_test, color='green', marker='x', label='Train Data')
        plt.scatter(self.x, self.y, color='black', marker='+', label='All Data')
        if self.solution:
            plt.plot(self.x_test, self.regr.predict(self.x_test), 'r-',
                     label='Fit: {:3f}(x) + {:3f}'.format(self.a, self.b))
        #  plot_plt.show(title=self.description)
