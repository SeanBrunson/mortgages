# File to test the mbs class to get the market value given different market
# rates and dynamic SMM. Assumes a flat market rate over the life of the MBS and
# a flat SMM value.

import numpy as np
import mortgages
import matplotlib.pyplot as plt


def main():
    # Fixed Rate Mortgage Terms:
    loan_amount = 100000
    r_yearly = 0.04
    years = 30

    # Fixed rate:
    fixed = mortgages.Fixed(loan_amount, r_yearly, years)

    # Market rates:
    market_rates = np.arange(0.1, 15.0, 0.1)/100.0

    # Calculate flat SMM values for each market value:
    smm = mortgages.calc_smm(r_yearly, market_rates)

    # Initialize market value list to append final values:
    market_value_no_smm = []
    market_value_smm = []

    # Loop through each smm/market rate pair:
    for i in range(len(smm)):
        # Get cashflows from the MBS:
        mbs_no_smm = mortgages.Mbs(fixed, 0.0)
        mbs_with_smm = mortgages.Mbs(fixed, smm[i])

        # Make market_rates right length:
        market_rate_adjust = np.repeat(market_rates[i], mbs_no_smm.mortgage.months + 1)

        # Calculate market value of the MBS:
        market_value_no_smm.append(mortgages.calc_market_value(mbs_no_smm.pooled.total_cashflow,
                                                               market_rate_adjust, mbs_no_smm.mortgage.months))
        market_value_smm.append(mortgages.calc_market_value(mbs_with_smm.pooled.total_cashflow,
                                                            market_rate_adjust, mbs_with_smm.mortgage.months))

    # Plot SMM/CPR curve:
    plt.figure()
    plt.plot(market_rates, market_value_no_smm)
    plt.plot(market_rates, market_value_smm)
    plt.xlabel("Market Rate")
    plt.ylabel("Market Value")
    plt.ylim(30000, 250000)
    plt.legend(["Market Value No Prepays", "Market Value With Dynamic Prepays"])
    plt.show()


if __name__ == "__main__":
    main()
