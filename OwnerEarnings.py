import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import yfinance as yf


# The tableau20 set of colors.
tableau20 = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),
             (44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),
             (148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),
             (227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),
             (188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)]

# Scale the tableau20 RGBs to numbers between (0,1) since this is how mpl accepts them.
for i in range(len(tableau20)):
    r, g, b = tableau20[i]
    tableau20[i] = (r / 255., g / 255., b / 255.)

class OwnerEarnings:
    """
    This class handles loading in past financial data from Yahoo Finance.
    """

    def __init__(self, ticker):
        """
        Initialize class by loading in the relevant data from the saved csv
        files.
        """
        self.ticker = ticker.lower()

        # Load in data from csv that is saved from Yahoo Finance. Do a couple
        # data organizing things. Have a couple options for the file names just
        # depending if I want to name them something clean or stick with what
        # Yahoo gives me.
        income_path  = '/mnt/c/Users/shawn/Documents/financial_statements/' + \
                       '{}_income.csv'.format(self.ticker)
        balance_path = '/mnt/c/Users/shawn/Documents/financial_statements/' + \
                       '{}_balance.csv'.format(self.ticker)
        cash_path    = '/mnt/c/Users/shawn/Documents/financial_statements/' + \
                       '{}_cash.csv'.format(self.ticker)
        income_path2  = '/mnt/c/Users/shawn/Documents/financial_statements/' + \
                       '{}_annual_financials.csv'.format(self.ticker.upper())
        balance_path2 = '/mnt/c/Users/shawn/Documents/financial_statements/' + \
                       '{}_annual_balance-sheet.csv'.format(self.ticker.upper())
        cash_path2    = '/mnt/c/Users/shawn/Documents/financial_statements/' + \
                       '{}_annual_cash-flow.csv'.format(self.ticker.upper())

        # Load in and swap index with columns.
        try:
            income  = pd.read_csv(income_path, thousands=',').set_index('name').T
        except:
            income  = pd.read_csv(income_path2, thousands=',').set_index('name').T
        try:
            balance = pd.read_csv(balance_path, thousands=',').set_index('name').T
        except:
            balance = pd.read_csv(balance_path2, thousands=',').set_index('name').T
        try:
            cash    = pd.read_csv(cash_path, thousands=',').set_index('name').T
        except:
            cash    = pd.read_csv(cash_path2, thousands=',').set_index('name').T

        # Clean up column names.
        income.columns  = [c.strip() for c in income.columns]
        balance.columns = [c.strip() for c in balance.columns]
        cash.columns    = [c.strip() for c in cash.columns]

        # Remove any duplicate column names.
        income  = income.loc[:,~income.columns.duplicated()]
        balance = balance.loc[:,~balance.columns.duplicated()]
        cash    = cash.loc[:,~cash.columns.duplicated()]

        # Save to class.
        self.income  = income
        self.balance = balance
        self.cash    = cash

        # Initialize an empty DataFrame that will be easier handle and only
        # have the data we care about.
        self.working = pd.DataFrame(index=self.income.index)

    def get_col_data(self, df, col_name, verbal=True):
        """
        Helper function to return data and appropriately handle NaNs, warning
        the user about them when necessary.

        df (pd.DataFrame): One of self.cash, balance or income.
        col_name (str):    The column name for the data.
        verbal (bool):     Print out warning or not.
        """

        # Find years where the data was NaN. Sometime it just means zero, but
        # requires double checking.
        try:
            nan_years = df.index[np.isnan(df[col_name])]

            # Replace the NaNs with zeros.
            df[col_name].loc[nan_years] = 0.0

            # Print warning if desired.
            if verbal:
                if len(nan_years) > 0:
                    years = [i.split('/')[-1] for i in nan_years]
                    print("Warning: NaN data detected for {:}: ".format(col_name), end="")
                    for y in years:
                        if y == years[-1]:
                            print(y)
                        else:
                            print(y, end=", ")

            # Return the data as a Series so it can be added together and all that.
            return df[col_name]

        # Some companies may not have data for an item, i.e. no DeferredIncomeTax,
        # so just return zeros.
        except KeyError:
            print("Warning: No data for {:}".format(col_name))
            return np.zeros(len(df.index))


    def fill_working(self):
        """
        Add to our working DataFrame data that just needs to be copied.
        """

        self.working['Shares Outstanding'] = self.get_col_data(self.income, 'BasicAverageShares')
        self.working['Stockholder Equity'] = self.get_col_data(self.balance, 'StockholdersEquity')
        self.working['Dividends'] = self.get_col_data(self.cash, 'CashDividendsPaid')
        self.working['Repurchased'] = self.get_col_data(self.cash, 'RepurchaseOfCapitalStock')
        self.working['Revenue'] = self.get_col_data(self.income, 'TotalRevenue')
        self.working['Net Income'] = self.get_col_data(self.income, 'NetIncome')

    def calc_owners(self):
        """
        Calculate owner's earnings and put it in our working df.
        """

        self.working['Owner Earnings'] = \
            self.get_col_data(self.cash, 'NetIncome') \
          + self.get_col_data(self.cash, 'DepreciationAndAmortization') \
          + self.get_col_data(self.cash, 'DeferredIncomeTax') \
          + self.get_col_data(self.cash, 'ChangeInWorkingCapital') \
          + self.get_col_data(self.cash, 'OtherNonCashItems') \
          - self.get_col_data(self.cash, 'CapitalExpenditure')

    def calc_intrinsic(self, risk_free):
        """
        Calculate the intrinsic value assuming a certain risk free rate.

        risk_free (float): The assumed risk free rate of return. Enter as
                           decimal (i.e. for 8% do 0.08 not 8).
        """

        if 'Owner Earnings' in self.working.columns:
            self.working['Intrinsic Value'] = self.working['Owner Earnings'] / risk_free
        else:
            print("Error: Must calculate owner earnings first. Run calc_owners.")

    def calc_percentages(self):
        """
        Calculate the return on equity, just using the most recent
        stockhholder's equity value instead of an average.
        """

        if 'Stockholder Equity' in self.working.columns:
            self.working['ROE'] = self.working['Net Income'] / self.working['Stockholder Equity']
            self.working['Profit Margin'] = self.working['Net Income'] / self.working['Revenue']
        else:
            print("Error: Must fill DataFrame first. Run fill_working.")

    def get_prices(self):
        """
        Get the most recent closing price on the days the report was filed.
        """

        # First get the date of the reports, ignoring the "ttm" entry.
        dates = [datetime.strptime(d, '%m/%d/%Y') for d in self.working.index[1:]]

        # Load the history of the prices from Yahoo.
        ticker = yf.Ticker(self.ticker)
        prices = ticker.history(period='max')

        # Get the most recent entry from the statement date. Note this gets
        # the adjusted closing column from the website.
        try:
            closing = []
            for d in dates:
                closing.append(prices[prices.index <= d].iloc[-1]['Close'])
        except IndexError:
            closing = []
            try:
                for d in dates[:-1]:
                    closing.append(prices[prices.index <= d].iloc[-1]['Close'])
                closing.append(0)
            except:
                print("Error: Unable to calculate value.")
                closing = np.full(len(self.working.index[1:]), 0)
            #closing = [prices[prices.index <= d].iloc[-1]['Close'] for d in dates]
        #except IndexError:

            # If the price data starts after the first financial statement,
            # just skip that first year.
        #    closing = [prices[prices.index <= d].iloc[-1]['Close'] for d in dates[:-1]]
        #    closing.append(0)

        # Make this a Series and put in working.
        self.working['Price'] = pd.Series(closing, index=self.working.index[1:])

        # Also put in as what percentage was is trading off of assuming the risk
        # free rate of return was constant the whole time and thus the
        # corresponding intrinsic value.
        #self.working['Value'] = (self.working['Intrinsic Value'] \
        #  - self.working['Price'] * self.working['Shares Outstanding']) / \
        #  (self.working['Price'] * self.working['Shares Outstanding'])
        #self.working['Value'] = (self.working['Intrinsic Value'] \
        #  - self.working['Price'] * self.working['Shares Outstanding']) / \
        #  self.working['Intrinsic Value']
        self.working['Value'] = 1 - self.working['Price'] * self.working['Shares Outstanding'] / self.working['Intrinsic Value']

    def calc_dollar(self):
        """
        See if they pass the one-dollar rule.
        """

        # Don't include the ttm entry at the top.
        earnings = self.working['Net Income'][1:].sum()
        earnings10 = self.working['Net Income'][1:11].sum()

        # Total amount given back (represented as a negative value here).
        div_repur = self.working['Dividends'][1:].sum() + self.working['Repurchased'][1:].sum()
        div_repur10 = self.working['Dividends'][1:11].sum() + self.working['Repurchased'][1:11].sum()

        # Retained earnings.
        ret_earn = earnings + div_repur
        ret_earn10 = earnings10 + div_repur10

        # Calculate difference in market capitalization.
        start_cap = self.working['Price'][-1] * self.working['Shares Outstanding'][-1]
        end_cap = self.working['Price'][1] * self.working['Shares Outstanding'][1]
        cap_change = end_cap - start_cap
        start_cap10 = self.working['Price'][11] * self.working['Shares Outstanding'][11]
        end_cap10 = self.working['Price'][1] * self.working['Shares Outstanding'][1]
        cap_change10 = end_cap10 - start_cap10

        dollar_rule = cap_change / ret_earn
        dollar_rule10 = cap_change10 / ret_earn10

        print("One Dollar Rule")
        print("  {} - {}: {:.2f}".format(self.working.index[-1], self.working.index[1], dollar_rule))
        #print("    Net Earnings: ${}".format(earnings))
        #print("    Div/Repurchase: ${}".format(div_repur))
        #print("    Retained: ${}".format(ret_earn))
        #print("    Cap Increase: ${}".format(cap_change))
        print("  {} - {}: {:,.2f}".format(self.working.index[11], self.working.index[1], dollar_rule10))
        print("    Net Earnings: ${:,}".format(earnings10))
        print("    Div/Repurchase: ${:,}".format(div_repur10))
        print("    Retained: ${:,}".format(ret_earn10))
        print("    Cap Increase: ${:,}".format(cap_change10))

    def current_value(self, target_value=None):
        """
        """

        ticker = yf.Ticker(self.ticker)
        if target_value == None:

            # Load the most recent market capital.
            current_market_cap = ticker.info["marketCap"]

            # Compare value to ttm owner earnings.
            ttm_value = 1 - current_market_cap / self.working["Intrinsic Value"]["ttm"]

            print("Current value: {:.2f}%".format(ttm_value * 100))

        else:

            # target_value is the percentage value we want, see what market capital
            # is necessary to meet that target.
            target_cap = (1 - target_value / 100) * self.working["Intrinsic Value"]["ttm"]

            # Translate to price.
            target_price = target_cap / ticker.info["sharesOutstanding"]

            print("Price for {}% value: ${:.2f}".format(target_value, target_price))

    def plot_summary(self):
        """
        Plot a summary of the data.
        """

        # Make sure all the data has been calculated first.
        if 'Net Income' not in self.working.columns:
            self.fill_working()
        if 'Owner Earnings' not in self.working.columns:
            self.calc_owners()
        if 'Intrinsic Value' not in self.working.columns:
            print("Assuming risk-free rate of 8%.")
            self.calc_intrinsic(0.08)
        if 'ROE' not in self.working.columns:
            self.calc_percentages()
        if 'Value' not in self.working.columns:
            self.get_prices()
        self.calc_dollar()
        self.current_value()

        # For labels.
        years = np.array([i.split('/')[-1] for i in self.working.index])[::-1]

        # Needed below to have nice xticks.
        def set_xticks(ax):
            for tick in ax.get_xticklabels():
                tick.set_rotation(315)
            for tick in ax.get_xticklabels()[::2]:
                tick.set_visible(False)

        # ROE and Profit Margin and Value plot limits.
        roe_low = max(self.working['ROE'].min() * 100.1, -50)
        roe_high = min(self.working['ROE'].max() * 100.1, 50)
        prof_low = max(self.working['Profit Margin'].min() * 100.1, -50)
        prof_high = min(self.working['Profit Margin'].max() * 100.1, 50)
        val_low = max(self.working['Value'].min() * 100.1, -100)
        val_high = min(self.working['Value'].max() * 100.1, 250)

        # Plotting commands.
        grid_alpha = 0.25
        fontsize1 = 12
        fig = plt.figure(figsize=(15,10))
        ax1 = fig.add_subplot(221)
        ax1.bar(years, self.working['Owner Earnings'][::-1], color=tableau20[5])
        ax1.set_title('Owner Earnings ($)', fontsize=18)
        ax1.tick_params(labelsize=fontsize1)
        set_xticks(ax1)
        ax1.grid(alpha=grid_alpha)
        ax1.set_axisbelow(True)
        ax2 = fig.add_subplot(222)
        ax2.bar(years, self.working['ROE'][::-1] * 100, color=tableau20[7])
        ax2.set_title('ROE (%)', fontsize=18)
        ax2.tick_params(labelsize=fontsize1)
        ax2.set_ylim([roe_low, roe_high])
        set_xticks(ax2)
        ax2.grid(alpha=grid_alpha)
        ax3 = fig.add_subplot(223)
        ax3.bar(years, self.working['Profit Margin'][::-1] * 100, color=tableau20[9])
        ax3.set_title('Profit Margin (%)', fontsize=18)
        ax3.tick_params(labelsize=fontsize1)
        ax3.set_ylim([prof_low, prof_high])
        set_xticks(ax3)
        ax3.grid(alpha=grid_alpha)
        ax4 = fig.add_subplot(224)
        ax4.bar(years, self.working['Value'][::-1] * 100, color=tableau20[19])
        ax4.set_title("Value (%)", fontsize=18)
        ax4.tick_params(labelsize=fontsize1)
        ax4.set_ylim([val_low, val_high])
        set_xticks(ax4)
        ax4.grid(alpha=grid_alpha)
        fig.tight_layout()
        fig.show()
