#Class to calculate mortgage payments/amortization:

import matplotlib.pyplot as plt

def calc_pmt(loan_amount, r_monthly, months, fv=0):
    """
    Finds the monthly payment on a loan using the
    monthly rate and number of months.

    Parameters
    ----------
    loan_amount: float
        Loan amount
    r_monthly: float
        Monthly interest rate
    months: int
        Number of months of the loan
    fv: float
        Outstanding loan balance in the final period.
        Assumes the loan is full paid off.

    Returns
    -------
    pmt: float
        Monthly payment
    """

    pv = loan_amount + (fv / (1+r_monthly)**months)
    pmt = r_monthly*pv / (1 - (1+r_monthly)**-months)

    return pmt

class mortgage(object):
    """
    Class for different kinds of mortgages.

    Parameters
    ----------
    loan_amount: float 
        Loan amount
    r_annual: float
        Yearly interest rate
    years:
        Number of years of the loan
    """

    def __init__(self, loan_amount, r_annual, years):
        self.loan_amount = loan_amount
        self.r_monthly = r_annual / 12.0
        self.months = years * 12
        self.vec_pmt = [0.0]
        self.vec_int = [0.0]
        self.vec_principal = [0.0]
        self.vec_balance = [loan_amount]
        self.pmt = calc_pmt(loan_amount, self.r_monthly, self.months)
        self.legend = None

    def update_loan(self):
        """
        Updates the loan amount by the monthly amount paid.
        """

        #Find the interest and principal amount paid for the month:
        interest = self.vec_balance[-1] * self.r_monthly
        principal = self.pmt - interest

        #Update monthly vectors:
        self.vec_pmt.append(self.pmt)
        self.vec_int.append(interest)
        self.vec_principal.append(principal)
        self.vec_balance.append(self.vec_balance[-1] - principal)

    def sum_vec_pmt(self):
        """
        Calculates the total amount paid up to the current time.
        """

        return sum(self.vec_pmt)

    def sum_vec_int(self):
        """
        Calculates the total amount of interest paid up to the current time.
        """

        return sum(self.vec_int)

    def sum_vec_principal(self):
        """
        Calculates the total amount of principal paid up to the current time.
        """

        return sum(self.vec_principal)

    def __str__(self):
        return self.legend

    def plot_payments(self, style):
        plt.plot(self.vec_pmt[1:], style, label = self.legend)

    def plot_balance(self, style):
        plt.plot(self.vec_balance, style, label = self.legend)

    def plot_interest(self, style):
        plt.plot(self.vec_int[1:], style, label = self.legend)

    def plot_principal(self, style):
        plt.plot(self.vec_principal[1:], style, label = self.legend)

class fixed(mortgage):
    """
    Class for fixed rate mortgages.

    Parameters
    ----------
    loan_amount: float
        Loan amount
    r_monthly: float
        Monthly interest rate
    months: int
        Number of months of the loan
    """

    def __init__(self, loan_amount, r_monthly, months):
        mortgage.__init__(self, loan_amount, r_monthly, months)
        self.legend = 'Fixed, ' + str(r_monthly*100.0) + '%'

class fixed_with_points(mortgage):
    """
    Class for fixed rate mortgages with points.

    Parameters
    ----------
    loan_amount: float
        Loan amount
    r_monthly: float
        Monthly interest rate
    months: int
        Number of months of the loan
    pts: float
        Discount points paid directly to the lender
    """

    def __init__(self, loan_amount, r_monthly, months, pts):
        mortgage.__init__(self, loan_amount, r_monthly, months)
        self.pts = pts
        self.paid = [loan_amount * (pts/100.0)]
        self.legend = 'Fixed, ' + str(r_monthly*100.0) + '%, ' \
                      + str(pts) + ' points'

class adjustable(mortgage):
    """
    Class for adjustable rate mortgages.

    Parameters
    ----------
    loan_amount: float
        Loan amount
    r_monthly: float
        Monthly interest rate
    months: int
        Number of months of the loan
    teaser_r: float
        Initial annual interest rate for a certain period
    teaser_months: int
        Number of months for the teaser rate
    """

    def __init__(self, loan_amount, r_monthly, months, teaser_r, teaser_months):
        mortgage.__init__(self, loan_amount, r_monthly, months)
        self.teaser_months = teaser_months
        self.teaser_r = teaser_r
        self.next_r = r / 12.0
        self.legend = str(teaser_r*100.0) + '% for ' \
                      + str(teaser_months) \
                      + ' months, then ' + str(r*100.0) + '%'

    def update_loan(self):
        """
        Updates the loan amount by the monthly amount paid.
        """

        if len(self.vec_pmt) == self.teaser_months + 1:
            self.r_monthly = self.next_r
            self.pmt = calc_pmt(loan_amount = self.vec_balance[-1],
                                r_monthly = self.r_monthly,
                                months = self.months - self.teaser_months)

        mortgage.update_loan(self)
