# Class to calculate mortgage payments/amortization:

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def calc_pmt(loan_amount, r_monthly, months, fv=0):
    """
    Finds the monthly payment on a loan using the
    monthly rate and number of months.

    Parameters
    ----------
    loan_amount: float
        Current loan amount
    r_monthly: float
        Monthly interest rate
    months: int
        Number of months remaining on the loan
    fv: float
        Outstanding loan balance in the final period.
        Assumes the loan will be fully paid off.

    Returns
    -------
    pmt: float
        Monthly payment
    """

    pv = loan_amount + (fv/(1 + r_monthly)**months)
    pmt = r_monthly*pv/(1 - (1 + r_monthly)**-months)

    return pmt


def calc_market_value(cashflow, market_rates, month_n, month_i=1):
    """
    Calculates the market value of the mortgage using current market rates.
    Formula uses the present value of the remaining cashflows from month_i to
    the terminal month.

    Parameters
    ----------
    cashflow: array_like
        Array of future cashflows.
        Must be of length month_n + 1.
        First index is typically of value 0.
    market_rates: array_like 
        Current annual interest rate.
        Must be of length month_n + 1.
        First index is typically the same value us the underlying coupon
        rate.
    month_n: int
        Terminal month
    month_i: int
        Current month.
        Assumes the individual has made (month_i - 1) payments.
        Must be between 1 and month_n.
        Defaults to first payment month.

    Returns
    -------
    market_value: float
        Market value of future cash flows
    """

    # Make sure length of cashflow is equal to length of market_rates:
    if len(cashflow) != len(market_rates):
        raise ValueError("cashflow and market_rates are not the same length.")

    # Subset cashflow:
    remaining_payments = cashflow[month_i:]

    # Get remaining market rates:
    remaining_rates = 1.0 + (np.array(market_rates)[month_i:]/12.0)

    # Calculate discount rates:
    discount_rates = np.cumprod(1/remaining_rates)

    # Calculate sum of the present value of the payments from month_i to self.months:
    market_value = sum(remaining_payments*discount_rates)

    return market_value


def calc_wal(cashflow, original_balance):
    """
    Finds the weighted average life of the loan.

    Parameters
    ----------
    cashflow: array_like
        Array of principal payments
    original_balance: float
        Original loan balance

    Returns
    -------
    wal: float
        Weighted average life of the loan
    """

    # Change cashflow to array:
    cashflow = np.ones(1)*cashflow

    # Find the length of cashflow:
    n = len(cashflow)

    # Calculate WAL:
    wal = sum(cashflow*list(range(n)))/original_balance

    return wal


class Mortgage(object):
    """
    Class for different kinds of mortgages.

    Parameters
    ----------
    loan_amount: float 
        Current loan amount
    r_annual: float
        Yearly interest rate
    years: int
        Number of years remaining on the loan
    fv: float
        Outstanding loan balance in the final period.
        Assumes the loan will be fully paid off.
    pts: float
        Discount points paid directly to the lender
    """

    def __init__(self, loan_amount, r_annual, years, fv=0.0, pts=0.0):
        self.loan_amount = loan_amount
        self.r_monthly = r_annual/12.0
        self.months = years*12
        self.fv = fv
        self.pts = pts
        self.vec_pmt = [0.0]
        self.vec_int = [0.0]
        self.vec_principal = [0.0]
        self.vec_balance = [loan_amount]
        self.pmt = calc_pmt(loan_amount, self.r_monthly, self.months, self.fv)
        self.amort = self.create_amortization_schedule()
        self.upfront = loan_amount*(pts/100.0)
        self.legend = None

    def update_loan(self, month_i):
        """
        Updates the current loan amount by the monthly principal paid.
        
        Parameters
        ----------
        month_i: int 
            Current month
        """

        # Check to make sure length of payments is less than total months:
        if len(self.vec_pmt) <= (self.months + 1):
            # Find the interest and principal amount paid for the month:
            interest = self.vec_balance[-1]*self.r_monthly
            principal = self.pmt - interest

            # Update monthly vectors:
            self.vec_pmt.append(self.pmt)
            self.vec_int.append(interest)
            self.vec_principal.append(principal)
            self.vec_balance.append(self.vec_balance[-1] - principal)
        else:
            print(self.months, "payments were already made.")

    def create_amortization_schedule(self):
        """
        Creates full amortization schedule and sets it in pandas DataFrame.
        """

        # Loop through all payments:
        for m in range(self.months):
            self.update_loan(m)

        # Create pandas DataFrame:
        column_names = ["balance", "payment", "interest", "principal"]
        amort = pd.DataFrame(list(zip(self.vec_balance, self.vec_pmt,
                                      self.vec_int, self.vec_principal)),
                             columns=column_names)

        return amort

    def sum_vec_pmt(self):
        """
        Sum the total amount paid up to the current time.
        """

        return sum(self.vec_pmt)

    def sum_vec_int(self):
        """
        Sum the total amount of interest paid up to the current time.
        """

        return sum(self.vec_int)

    def sum_vec_principal(self):
        """
        Sum the total amount of principal paid up to the current time.
        """

        return sum(self.vec_principal)

    def __str__(self):
        return self.legend

    def plot_payments(self, style):
        plt.plot(self.vec_pmt[1:], style, label=self.legend)

    def plot_balance(self, style):
        plt.plot(self.vec_balance, style, label=self.legend)

    def plot_interest(self, style):
        plt.plot(self.vec_int[1:], style, label=self.legend)

    def plot_principal(self, style):
        plt.plot(self.vec_principal[1:], style, label=self.legend)


class Fixed(Mortgage):
    """
    Class for fixed rate mortgages.

    Parameters
    ----------
    loan_amount: float 
        Current loan amount
    r_annual: float
        Yearly interest rate
    years: int
        Number of years remaining on the loan
    fv: float
        Outstanding loan balance in the final period.
        Assumes the loan will be fully paid off.
    pts: float
        Discount points paid directly to the lender
    """

    def __init__(self, loan_amount, r_annual, years, fv=0.0, pts=0.0):
        Mortgage.__init__(self, loan_amount, r_annual, years, fv, pts)
        self.legend = 'Fixed, ' + str(self.r_monthly*100.0) + '%'


class Adjustable(Mortgage):
    """
    Class for adjustable rate mortgages.

    Parameters
    ----------
    loan_amount: float 
        Current loan amount
    r_annual: array_like
        Yearly interest rate after the initial teaser rate.
        Must have either length 1 or length (months - months_teaser).
    years: int
        Number of years remaining on the loan
    r_teaser: float
        Initial annual interest rate for a certain period
    years_teaser: int
        Number of years for the teaser rate
    fv: float
        Outstanding loan balance in the final period.
        Assumes the loan will be fully paid off.
    pts: float
        Discount points paid directly to the lender
    """

    def __init__(self, loan_amount, r_annual, years, r_teaser, years_teaser,
                 fv=0.0, pts=0.0):
        self.months_teaser = years_teaser*12
        self.next_r = self.check_r_annual(r_annual, years)/12.0
        Mortgage.__init__(self, loan_amount, r_teaser, years, fv, pts)
        self.legend = str(self.r_monthly*100.0) + '% for ' \
                      + str(self.months_teaser) \
                      + ' months, then becomes adjustable'

    def check_r_annual(self, r_annual, years):
        """
        Check whether r_annual is either length 1 or length (months - months_teaser).
        If r_annual is length 1, then make it length (months - months_teaser).
        """

        # Get length of r_annual:
        r_annual_length = len(np.ones(1)*r_annual)

        # Set up new length:
        new_length = (years*12) - self.months_teaser

        if r_annual_length == 1:
            r_annual = np.ones(new_length)*r_annual

        if (r_annual_length != 1) and (r_annual_length != new_length):
            raise ValueError("r_annual must be either length 1 or length {}".format(new_length))

        return r_annual

    def update_loan(self, month_i):
        """
        Updates the r_monthly to the new value, recalculates payment, and
        updates the loan amount by the monthly principal paid.

        Parameters
        ----------
        month_i: int 
            Current month
        """

        if len(self.vec_pmt) >= (self.months_teaser + 1):
            self.r_monthly = self.next_r[month_i - self.months_teaser]
            self.pmt = calc_pmt(loan_amount=self.vec_balance[-1],
                                r_monthly=self.r_monthly,
                                months=self.months - month_i)

        Mortgage.update_loan(self, month_i)
