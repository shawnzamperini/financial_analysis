import FundamentalInvesting_constants as constants
import time
import urllib
from bs4 import BeautifulSoup
import numpy as np

fundamentals = np.array(['Price/Book', 'Trailing P/E',
                         'PEG Ratio (5 yr expected)', 'Total Debt/Equity',
                         'Trailing Annual Dividend Rate',
                         'Trailing Annual Dividend Yield'])

class Ticker:
    """
    Ticker class object to hold ticker info and a method to query the info
    from Yahoo! Finance.

    symbol:         The ticker symbol.
    key_stats:      The ratios pulled from Yahoo! (if found) as a dictionary.
    search_strings: Internal use only. Strings used in searching the Yahoo!
                      source code.

    Returns 'Fail' if it can't load source code.
    """
    def __init__(self, symbol):
        self.symbol = symbol
        self.source_code = None
        self.key_stats = {'PBR':None, 'PEG':None, 'PE12': None, 'DE':None,
                          'DIVRATE':None, 'DIVYIELD':None}
        self.search_strings = {'PBR':  constants.pbr_strs,
                               'PEG':  constants.peg5_strs,
                               'PE12': constants.pe12_strs,
                               'DE':   constants.de_strs,
                               'DIVRATE':  constants.divrate_strs,
                               'DIVYIELD': constants.divyield_strs}


    def query_yahoo(self, debug=False):
        """
        Method to query Yahoo! Finance for the key ratios.

        debug: Set to True to print out info and see where it fails.
        """
        try:
            # Load all the source code.
            source_code = urllib.request.urlopen('http://finance.yahoo.com/quote/' + self.symbol + '/key-statistics?p='+self.symbol).read()
            self.source_code = source_code
            self.soup = BeautifulSoup(self.source_code, features='lxml')
            if debug:
                print(self.symbol.upper() + ' source code loaded.')

            # Try and locate each fundamental one at a time.
            try:

                # Dictionary to hold results.
                self.fund_dict = {}

                # They are nestled under td tags, so get all those.
                tds = self.soup.find_all('td')

                # Go through each fundamental.
                for fund in fundamentals:

                    # Go through each td tag looking for ones that have a
                    # span child.
                    for i in range(0, len(tds)):
                        td = tds[i]
                        if len(td.findChildren('span')) > 0:

                            # See if this span child has the matching string.
                            if td.findChildren('span')[0].string == fund:

                                # The fund will then be in the following td tag.
                                fund_value = tds[i+1].string
                                self.fund_dict[fund] = fund_value

                if self.fund_dict == {}:
                    raise Exception

            except Exception as e:
                if debug:
                    print('Error: ' + str(e))
                return 'Fail'

        except Exception as e:
            if debug:
                #print('    Error (3)' + str(e))
                print("Error: Could not load source code from Yahoo.")
            return 'Fail'


def screen(index='djia', pbr_scr=9999, pe_scr=9999, de_scr=9999, divyield_scr=9999, pass_all=False, pass_na=True):
    """
    Screen function to screen stocks according to desired ratios.

    pbr_scr:      Screening value for the price/book ratio.
    pe:           Price/Earning ratio screen.
    de:           Debt/Equity ratio screen.
    divyield_scr: Dividend yield screen as percent.
    pass_all:     Set to true if ticker must pass every screen test. False it will
                    only need to pass one of the tests.
    pass_na:      If True, considers an N/A a pass. Useful if you aren't sure
                    the data is being retrieved (if it is being retrieved, then
                    N/A on say PE ratio means negative earnings).
    """
    if index == 'sp500':
        ticker_symbols = constants.sp500
        index = 'S&P 500'
    elif index == 'ru3000':
        ticker_symbols = constants.russell3000
        index = 'Russell 3000'
    elif index == 'djia':
        ticker_symbols = constants.djia
        index = 'DJIA'
    else:
        print('Error: Incorrect index name entered.')
        return None

    # Create a list of all the Tickers.
    ticker_objs = [Ticker(symbol) for symbol in ticker_symbols]

    def format_screen_val(val):
        if val == 9999:
            return 'No limit'
        else:
            return '(<' + str(val) + ')'

    # Print a header.
    print('\nIndex: ' + index)
    if pass_all == True:
        print('Pass all screens: Yes')
    else:
        print('Pass all screens: No')
    print('{:6s} | {:10s} | {:14s} | {:11s} | {:17s}'.format('Ticker', 'Price/Book', 'Price/Earnings', 'Debt/Equity', 'Trailing Dividend'))
    print('{:6s} | {:10s} | {:14s} | {:11s} | {:17s}'.format('',
                                                    format_screen_val(pbr_scr),
                                                    format_screen_val(pe_scr),
                                                    format_screen_val(de_scr),
                                                    format_screen_val(divyield_scr)))
    print('-----------------------------------------------------------------------')

    # Perform the Yahoo! query and then screen.
    failed_tickers = []
    count = 1
    for ticker in ticker_objs:
        print('\rCurrent ticker: '+ticker.symbol+' ('+str(count)+'/'+str(len(ticker_objs))+')', end='     ', flush=True)
        status = ticker.query_yahoo()

        # Get the name of the failed tickers to print out at the end.
        if status == 'Fail':
            failed_tickers.append(ticker.symbol)
        else:

            # Boolean for each test. Nones (i.e. N/A) will pass to leave it up
            # to the user's discretion. First Price/Book.
            if ticker.fund_dict[fundamentals[0]] == 'N/A':
                if pass_na:
                  pbr_pass = True
                else:
                  pbr_pass = False
            elif float(ticker.fund_dict[fundamentals[0]].replace(',','')) < pbr_scr:
                pbr_pass = True
            else:
                pbr_pass = False

            # Price/Earnings (ttm).
            if ticker.fund_dict[fundamentals[1]] == 'N/A':
                if pass_na:
                  pe_pass = True
                else:
                  pe_pass = False
            elif float(ticker.fund_dict[fundamentals[1]].replace(',','')) < pe_scr:
                pe_pass = True
            else:
                pe_pass = False

            # Debt/Equity.
            if ticker.fund_dict[fundamentals[3]] == 'N/A':
                if pass_na:
                  de_pass = True
                else:
                  de_pass = False
            elif float(ticker.fund_dict[fundamentals[3]].replace(',','')) < de_scr:
                de_pass = True
            else:
                de_pass = False

            # Dividend yield.
            if ticker.fund_dict[fundamentals[4]] == 'N/A':
                if pass_na:
                  divyield_pass = True
                else:
                  divyield_pass = False
            elif float(ticker.fund_dict[fundamentals[4]].replace(',','')) < divyield_scr:
                divyield_pass = True
            else:
                divyield_pass = False

            def format_stat(stat):
                if type(stat) == float:
                    return str(stat)
                else:
                    return 'N/A'

            def format_divrateyield(divrate, divyield):
                if type(divrate) == float and type(divyield) == float:
                    return "{:.2f} ({:.2f}%)".format(divrate, divyield)
                else:
                    return 'N/A'

            # If pass_all, then require all Trues.
            if pass_all:
                if pbr_pass and pe_pass and de_pass:
                    print('\r{:6s} | {:10s} | {:14s} | {:11s} | {:17s}'.format(
                           ticker.symbol,
                           ticker.fund_dict[fundamentals[0]], # PBR
                           ticker.fund_dict[fundamentals[1]], # PE
                           ticker.fund_dict[fundamentals[3]], # DE
                           ticker.fund_dict[fundamentals[4]], # Div. Rate
                           ticker.fund_dict[fundamentals[5]])) # Div. Yield
            else:
                if pbr_pass or pe_pass or de_pass:
                    print('\r{:6s} | {:10s} | {:14s} | {:11s} | {:5s} ({:5s})'.format(
                           ticker.symbol,
                           ticker.fund_dict[fundamentals[0]], # PBR
                           ticker.fund_dict[fundamentals[1]], # PE
                           ticker.fund_dict[fundamentals[3]], # DE
                           ticker.fund_dict[fundamentals[4]], # Div. Rate
                           ticker.fund_dict[fundamentals[5]])) # Div. Yield

            count += 1

    # Print out the tickers that info wasn't retrieved for.
    print('\rCould not get info for: ', end='        ')
    for fail in failed_tickers:
        print(fail, end=' ')
