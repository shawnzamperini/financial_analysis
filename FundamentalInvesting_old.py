import time
import urllib
from FundamentalInvesting_constants import *
import pandas as pd


def yahooKeyStats(stock, return_bool=False, print_results=True):

    # First open the webpage and pull all the source code.
    try:
        sourceCode = urllib.request.urlopen('http://finance.yahoo.com/q/ks?s='+stock).read()
        try:

            # Now try the first search string the PBR, then decode (urlopen will return
            # a bytes representation) and use split to find where the PBR is.
            search_str = pbr_strs[0]
            pbr = sourceCode.decode().split(search_str)[1].split("</td>")[0]
        except:
            try:

                # Try another string if the above fails.
                search_str = pbr_strs[1]
                pbr = sourceCode.decode().split(search_str)[1].split("</td>")[0]
            except:
                try:

                    # Try yet another string if the above fails.
                    search_str = pbr_strs[2]
                    pbr = sourceCode.decode().split(search_str)[1].split("</td>")[0]
                except:
                    #print("Error: Can't find PBR search string.")
                    pbr = None
                    pass

        # Now the same as the above, except for the PEG ratio.
        try:
            search_str = peg5_strs[0]
            peg5 = sourceCode.decode().split(search_str)[1].split("</td>")[0]
        except:
            try:
                search_str = peg5_strs[1]
                peg5 = sourceCode.decode().split(search_str)[1].split("</td>")[0]
            except:
                #print("Error: Can't find PEG search string.")
                peg5 = None
                pass

        # Now the same as the above, except for the PE 12 months ratio.
        try:
            search_str = pe12_strs[0]
            pe12 = sourceCode.decode().split(search_str)[1].split("</td>")[0]
        except:
            try:
                search_str = pe12_strs[0]
                peg12 = sourceCode.decode().split(search_str)[1].split("</td>")[0]
            except:
                #print("Error: Can't find PE12 search string.")
                pe12 = None
                pass

        # Now the same as the above, except for the DE (mrq) ratio.
        try:
            search_str = de_strs[0]
            de = sourceCode.decode().split(search_str)[1].split("</td>")[0]
        except:
            try:
                search_str = de_strs[1]
                de = sourceCode.decode().split(search_str)[1].split("</td>")[0]
            except:
                try:
                    search_str = de_strs[2]
                    de = sourceCode.decode().split(search_str)[1].split("</td>")[0]
                except:
                    try:
                        search_str = de_strs[3]
                        de = sourceCode.decode().split(search_str)[1].split("</td>")[0]
                    except:
                        try:
                            search_str = de_strs[4]
                            de = sourceCode.decode().split(search_str)[1].split("</td>")[0]
                        except:
                            #print("Error: Can't find PE12 search string.")
                            de = None
                            pass

        # If you want active feedback.
        if print_results:
            print(stock.upper() + ":")
            print("  PBR        : {}".format(pbr))
            print("  PEG (5 yrs): {}".format(peg5))
            print("  PE (ttm)   : {}".format(pe12))
            print("  DE (mrq)   : {}".format(de))

        # If you want the results returned.
        if return_bool:
            return stock, pbr, peg5, pe12, de
    except:

        # Return None's if the above fails.
        if return_bool:
            return None, None, None, None, None


def screen(index='sp500', pbr_scr = 1.0, peg_scr = 1.0, pe12_scr = 1.0):
    count = 0

    if index == 'sp500':
        tickers = sp500
    elif index == 'russell3000':
        tickers = russell3000
    elif index == 'test':
        tickers = ['CMG', 'CRON', 'BB', 'KEM', 'TSLA', 'ARI']
    else:
        print('Error: Incorrect index entry.')

    df = pd.DataFrame()

    for stonk in tickers:

        # Small delay.
        time.sleep(0.1)
        print("{:4}".format(stonk.upper()))
        stock, pbr, peg, pe12, de = yahooKeyStats(stonk, True, False)
        try:
            if stock == None:
                #print("  Could not find data.")
                #pbr = 999
                print("\033[F", end="")
            elif float(pbr) < pbr_scr and float(peg) < peg_scr and float(pe12) < pe12_scr:
                print("  PBR     : {}".format(pbr))
                print("  PEG     : {}".format(peg))
                print("  PE (ttm): {}".format(pe12))
                print("  DE (mrq): {}".format(de))
                df = df.append({'Stock':stock, 'PBR':pbr, 'PEG':peg, 'PE (ttm)':pe12, 'DE (mrq)':de}, ignore_index=True)
                df = df[['Stock', 'PBR', 'PEG', 'PE (ttm)', 'DE (mrq)']]  # Sort the columns.
                continue
            else:
                print("\033[F", end="")

            if float(pbr) and float(peg) and float(pe12):
                count +=1
        except:
            #print("  Error: Did not return correct PBR type.")
            #print("\033[F", end="")
            pass

    print("Retrieved complete data for {}/{} stocks.".format(count, len(tickers)))

    return df
