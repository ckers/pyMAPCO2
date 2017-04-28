# -*- coding: utf-8 -*-
"""
Statistical methods for CO2 data processing

@author: Colin Dietrich 2017
"""

import matplotlib.pyplot as plt

from numpy import mean, linspace
from scipy.optimize import curve_fit
from sklearn import linear_model
from sklearn.model_selection import train_test_split

from . import plot_plt
from .algebra import linear


class Linear2dCurveFit(object):
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

    def fit(self):
        """Calculate a 2D linear regression fit using
        scipy.optimize.curve_fit (defaults to LM least squares)
        """

        self.popt, self.pcov = curve_fit(linear, self.x, self.y)
        self.a = self.popt[0]
        self.b = self.popt[1]
        self.solution = True

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

    def plot(self):
        """Plot fit
        """

        plt.scatter(self.x, self.y, color='black', marker='.', label='All Data')
        if self.solution:
            plt.plot(self.x, self.apply(self.x), 'r-',
                     label='Fit: {:3f}(x) + {:3f}'.format(self.a, self.b))
        plot_plt.show(title=self.description)


class Linear2dSKL(object):
    """Linear regression calculation and application using
    least squares fit from scikitlearn

    Shamelessly refactored from scikit-learn.org :)
    """
    def __init__(self):
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
        self.mse = mean((self.regr.predict(self.x_test) - self.y_test) ** 2)
        self.variance = self.regr.score(self.x_test, self.y_test)
        self.a = self.regr.coef_[0][0]
        self.b = self.regr.intercept_[0]
        self.solution = True

    def plot(self):
        """Plot fit
        """

        plt.scatter(self.x_test, self.y_test, color='green', marker='x', label='Train Data')
        plt.scatter(self.x, self.y, color='black', marker='.', label='All Data')
        if self.solution:
            plt.plot(self.x_test, self.regr.predict(self.x_test), 'r-',
                     label='Fit: {:3f}(x) + {:3f}'.format(self.a, self.b))
        plot_plt.show(title=self.description)
