# Class to calculate stylized version of MBS value with prepayment:

import numpy as np


def calc_smm(coupon_rate, market_rates):
    """
    Calculates the single monthly mortality rate (smm) given the
    coupon rate and market rate. Uses the Richard and Roll (1989)
    prepayment model.

    Parameters
    ----------
    coupon_rate: float
        Interest rate on underlying loan
    market_rates: array_like
        Monthly interest rate

    Returns
    -------
    smm: array_like
        Single monthly mortality is the amount of principal on
        mortgage-backed securities that is prepaid in a given month.
    """

    # Calculate rate difference:
    diff_rate = coupon_rate / market_rates

    # Calculate smm value:
    smm = 0.2406 - 0.1389*np.arctan(5.952*(1.089-diff_rate))
    smm = 1.0 - ((1.0-smm)**(1.0/12.0))

    return smm


def calc_cpr(smm):
    """
    Calculates the conditional prepayment rate (cpr) from the single
    monthly mortality rate (smm).

    Parameters
    ----------
    smm: array_like
        Single monthly mortality is the amount of principal on
        mortgage-backed securities that is prepaid in a given month.

    Returns
    -------
    cpr: float
        A conditional prepayment rate (CPR) indicates a loan
        prepayment rate at which a pool of loans, such as a mortgage
        backed security's (MBS), outstanding principal is paid off.
    """

    cpr = 1.0 - ((1.0-smm)**12)

    return cpr


class Mbs(object):
    """
    Class for mortgage backed securities. Assumes one type of loan
    scaled by a pool factor for now.

    Parameters
    ----------
    mortgage: mortgage
        Instance of class mortgage that will be pooled together for
        the MBS.
    smm: array_like
        Single monthly mortality is the amount of principal on
        mortgage-backed securities that is prepaid in a given month.
        Must have either length one or length mortgage.months + 1
    pool_factor: float
        Amount of the initial principal of the underlying mortgage
        loans that remain in a mortgage-backed security transaction.
    """

    def __init__(self, mortgage, smm, pool_factor=1.0):
        self.mortgage = mortgage
        self.smm = self.check_smm(smm)
        self.cpr = calc_cpr(self.smm)
        self.pool_factor = pool_factor
        self.pooled = self.pool_mortgage()

    def check_smm(self, smm):
        """
        Checks whether smm is of the right type and length.
        """

        # Check if smm is an array:
        if type(smm) is not np.ndarray:
            smm = np.ones(1) * smm

        # Change length if length = 1:
        if len(smm) == 1:
            smm = np.ones(self.mortgage.months+1) * smm

        # Check if smm is of length 1 or length self.mortgage.months
        # + 1:
        if (len(smm) != 1) and (len(smm) != (self.mortgage.months+1)):
            raise ValueError("smm must have length 1 or length {}".
                             format(self.mortgage.months+1))

        return smm

    def pool_mortgage(self):
        """
        Creates a pooled mortgage using the mortgage instance and
        pool factor.
        Uses the instance's amortization schedule and the SMM to
        pull out prepaid principal.
        """

        # Make copy of the amortization schedule:
        pooled = self.mortgage.amortization.copy()

        # Add SMM and pool factor:
        pooled["smm"] = self.smm.tolist()
        pooled["smm"][0] = 0.0
        pooled["pool_factor"] = self.pool_factor

        # Create updated pool factor so that it decreases over time
        # given SMM:
        pooled["pool_factor_shift"] = pooled.pool_factor.shift(1)*(
                1.0-pooled.smm)
        pooled["pool_factor"] = np.cumprod(pooled.pool_factor_shift)
        pooled["pool_factor"][0] = self.pool_factor
        pooled = pooled.drop(columns=["pool_factor_shift"])

        # Re-shift updated pool factor to adjust payment, interest,
        # and principal:
        pooled["pool_factor_shift"] = pooled.pool_factor.shift(1)
        pooled["pool_balance"] = pooled.balance * pooled.pool_factor
        pooled["pool_pmt"] = pooled.payment * pooled.pool_factor_shift
        pooled["pool_interest"] = \
            pooled.interest * pooled.pool_factor_shift
        pooled["pool_principal"] = pooled.pool_pmt - \
                                   pooled.pool_interest
        pooled["prepay_dollars"] = ((pooled.pool_balance -
                                     pooled.pool_principal.shift(
                                         -1))*pooled.smm.shift(
            -1)).shift(
            1)
        pooled["total_principal"] = pooled.pool_principal + \
                                    pooled.prepay_dollars
        pooled["total_cashflow"] = pooled.pool_interest + \
                                   pooled.total_principal

        # Fill NA with 0:
        pooled = pooled.fillna(0)

        # Subset to final columns:
        pooled = pooled.loc[:, ["smm", "pool_factor", "pool_balance",
                                "pool_pmt", "pool_interest",
                                "pool_principal", "prepay_dollars",
                                "total_principal", "total_cashflow"]]

        return pooled
