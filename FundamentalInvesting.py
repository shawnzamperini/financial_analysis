import time
import urllib
from FundamentalInvesting_constants import *
import pandas as pd


def yahooKeyStats(stock, return_bool=False, verbal=True):

    # First open the webpage and pull all the source code.
    try:
        sourceCode = urllib.request.urlopen('http://finance.yahoo.com/q/ks?s='+stock).read()
    except:
        print('Error opening source code.')
        return stock, None, None, None, None

    # Search process to get PBR. Works by getting progressively smaller chunks of strings.
    try:
        # First get the first 300 characters after the name.
        chunk1 = sourceCode.decode().split('Price/Book')[1][:300]
        # Expect the next chunk to start ta the second 'data-reactid'.
        chunk2 = chunk1.split('data-reactid')[2]
        # Then get the '>' right before the PBR number.
        chunk3 = chunk2.split('>')[1]
        # Finally cut it off at the '<' on the other side of the PBR number.
        chunk4 = chunk3.split('<')[0]
    except Exception as err:
        if verbal:
            print('PBR Error: {}'.format(err))
        pbr = None
    try:
        pbr = float(chunk4)
    except Exception as err:
        if verbal:
            print('PBR Error: {}'.format(err))
        pbr = None

    # Same process, now just for the trailing price/earnings ratio.
    try:
        chunk1 = sourceCode.decode().split('Trailing P/E')[1][:300]
        chunk2 = chunk1.split('data-reactid')[2]
        chunk3 = chunk2.split('>')[1]
        chunk4 = chunk3.split('<')[0]
    except Exception as err:
        if verbal:
            print('TPE Error: {}'.format(err))
        tpe = None
    try:
        tpe = float(chunk4)
    except Exception as err:
        if verbal:
            print('TPE Error: {}'.format(err))
        tpe = None

    # Same process, now just for the debt/equity ratio.
    try:
        chunk1 = sourceCode.decode().split('Total Debt/Equity')[1][:300]
        chunk2 = chunk1.split('data-reactid')[2]
        chunk3 = chunk2.split('>')[1]
        chunk4 = chunk3.split('<')[0]
    except Exception as err:
        if verbal:
            print('DE Error: {}'.format(err))
        de = None
    try:
        de = float(chunk4)
    except Exception as err:
        if verbal:
            print('DE Error: {}'.format(err))
        de = None

    # Same process, now just for the PEG ratio.
    try:
        chunk1 = sourceCode.decode().split('PEG Ratio (5 yr expected)')[1][:300]
        chunk2 = chunk1.split('data-reactid')[2]
        chunk3 = chunk2.split('>')[1]
        chunk4 = chunk3.split('<')[0]
    except Exception as err:
        if verbal:
            print('PEG Error: {}'.format(err))
        peg = None
    try:
        peg = float(chunk4)
    except Exception as err:
        if verbal:
            print('PEG Error: {}'.format(err))
        peg = None

    # Print out results if wanted.
    if verbal:
        print(stock.upper() + ":")
        if pbr == None:
            print("  Price/Book  : N/A")
        else:
            print("  Price/Book  : {}".format(pbr))
        if tpe == None:
            print("  Trailing P/E: N/A")
        else:
            print("  Trailing P/E: {}".format(tpe))
        if de == None:
            print("  Debt/Equity:  N/A")
        else:
            print("  Debt/Equity:  {}".format(de))
        if peg == None:
            print("  P/E Growth:   N/A")
        else:
            print("  P/E Growth:   {}".format(peg))

    # Return results if wanted.
    if return_bool:
        return stock, pbr, tpe, de, peg


def screen(index='sp500', pbr_scr = 1.0, peg_scr = 1.0, tpe_scr = 1.0):
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

        print("Now serving {}/{}: {}".format(count, len(tickers), stonk))
        # Small delay.
        time.sleep(0.1)
        try:
            stock, pbr, tpe, de, peg = yahooKeyStats(stonk, True, False)
        except:
            print('Error: Could not retrieve stats for {}'.format(stonk))
            continue

        # If a None was returned, then we don't want that stock anyways.
        try:
            if float(pbr) < pbr_scr and float(peg) < peg_scr and float(tpe) < tpe_scr:
                yahooKeyStats(stonk, False, True)
                df = df.append({'Stock':stock, 'PBR':pbr, 'PE (ttm)':tpe, 'PEG':peg, 'DE (mrq)':de}, ignore_index=True)
                df = df[['Stock', 'PBR', 'PE (ttm)', 'PEG', 'DE (mrq)']]  # Sort the columns.
            else:
                print("\033[F", end="")
        except:
            print("\033[F", end="")

        count += 1


    print("Retrieved complete data for {}/{} stocks.".format(count, len(tickers)))

    return df
