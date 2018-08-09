import FundamentalInvesting_constants as constants
import time
import urllib


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
        try: # (1)
            # Load all the source code.
            source_code = urllib.request.urlopen('http://finance.yahoo.com/q/ks?s='+self.symbol).read()
            self.source_code = source_code
            if debug:
                print(self.symbol.upper() + ' source code loaded.')

            # Search through each key stat desired.
            for search_string_name, search_string_options in self.search_strings.items():
                if debug:
                    print('  Searching for ' + search_string_name + '...')
                try: # (2)
                    option_count = 1

                    # Go one search string at a time until you run out.
                    for option in search_string_options:
                        try: # (3)

                            # Will fail if either the number is not found (the [1]
                            # after split will fail) or returns a N/A (the float()
                            # will fail). Remove any commas with replace.
                            key_stat = float(source_code.decode().split(option)[1].split("</td>")[0].replace(',', '').replace('%', ''))
                            if debug:
                                print('    Option #(' + str(option_count) + '/'
                                      + str(len(search_string_options)) + '): '
                                      + str(key_stat) + '.')

                            # Store the value in the Ticker object's dictionary.
                            self.key_stats[search_string_name] = key_stat
                            break
                        except Exception as e: # (3)
                            if debug:
                                #print('    Error (1):' + str(e))
                                print('    Option #(' + str(option_count) + '/'
                                      + str(len(search_string_options)) + '): Fail.')
                            option_count += 1
                except Exception as e: # (2)
                    if debug:
                        #print('    Error (2)' + str(e))
                        print('    Could not find ' + search_string_name)
                    else:
                        pass

        except Exception as e: # (1)
            if debug:
                #print('    Error (3)' + str(e))
                print("Error: Could not load source code from Yahoo.")
            return 'Fail'


def screen(index='djia', pbr_scr=9999, pe_scr=9999, de_scr=9999, divyield_scr=9999, pass_all=False):
    """
    Screen function to screen stocks according to desired ratios.
    """
    if index == 'sp500':
        ticker_symbols = constants.sp500
        index = 'S&P 500'
    elif index == 'ru3000':
        ticker_symbols = constants.ru3000
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
            if ticker.key_stats['PBR'] == None:
                pbr_pass = True
            elif ticker.key_stats['PBR'] < pbr_scr:
                pbr_pass = True
            else:
                pbr_pass = False

            # Price/Earnings (ttm).
            if ticker.key_stats['PE12'] == None:
                pe_pass = True
            elif ticker.key_stats['PE12'] < pe_scr:
                pe_pass = True
            else:
                pe_pass = False

            # Debt/Equity.
            if ticker.key_stats['DE'] == None:
                de_pass = True
            elif ticker.key_stats['DE'] < de_scr:
                de_pass = True
            else:
                de_pass = False

            # Dividend yield.
            if ticker.key_stats['DIVYIELD'] == None:
                divyield_pass = True
            elif ticker.key_stats['DIVYIELD'] < divyield_scr:
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
                           format_stat(ticker.key_stats['PBR']),
                           format_stat(ticker.key_stats['PE12']),
                           format_stat(ticker.key_stats['DE']),
                           format_stat(ticker.key_stats['DIVYIELD'])))
            else:
                if pbr_pass or pe_pass or de_pass:
                    print('\r{:6s} | {:10s} | {:14s} | {:11s} | {:17s}'.format(
                           ticker.symbol,
                           format_stat(ticker.key_stats['PBR']),
                           format_stat(ticker.key_stats['PE12']),
                           format_stat(ticker.key_stats['DE']),
                           format_divrateyield(ticker.key_stats['DIVRATE'],
                                               ticker.key_stats['DIVYIELD'])))

            count += 1

    # Print out the tickers that info wasn't retrieved for.
    print('\rCould not get info for: ', end='        ')
    for fail in failed_tickers:
        print(fail, end=' ')
