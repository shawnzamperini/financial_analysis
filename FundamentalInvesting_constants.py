import pandas as pd


# DJIA. Easiest to just manually enter it here.
djia = ['MMM', 'AXP', 'AAPL', 'BA', 'CAT', 'CVX', 'CSCO', 'KO', 'DWDP', 'XOM',
        'GS', 'HD', 'IBM', 'INTC', 'JNJ', 'JPM', 'MCD', 'MRK', 'MSFT', 'NKE',
        'PFE', 'PG', 'TRV', 'UNH', 'UTX', 'VZ', 'V', 'WMT', 'WBA', 'DIS']

# Filename of most recent S&P 500 from Wikipedia, copy/pasted into txt file.
sp500_filename = 'sp500_050820.txt'
sp500 = []
with open(sp500_filename) as f:
    for line in f:
        ticker = line.split("\t")[0]
        sp500.append(ticker)

# Filename of the Russell 3000. Get the PDF of all the tickers in it:
# http://www.ftserussell.com/index-series/index-resources/russell-reconstitution
# then copy and paste everything to a txt file. Then delete all the in between
# info. Using the replace tool on Notepad++ works (and delete empty lines with
# Edit > Line Operations > Remove Empty Lines (Containing Blank characters). So
# the file format ends up being every line as:
#    AMAZON COM INC AMZN
# Then use split() to split at all the spaces, and the last element will be
# the ticker symbol we want.

russell3000_filename = 'ru3000_membershiplist_20180625.txt'
russell3000 = []
with open(russell3000_filename) as f:
    for line in f:
        russell3000.append(line.split()[-1])


# Search strings for the Price/Book ratio.
pbr_strs = ["Price/Book</span><!-- react-text: 58 --> <!-- /react-text" \
            " --><!-- react-text: 59 -->(mrq)<!-- /react-text --><sup " \
            "aria-label=\"KS_HELP_SUP_undefined\" data-reactid=\"60\">" \
            "</sup></td><td class=\"Fz(s) Fw(500) Ta(end)\" data-react" \
            "id=\"61\">",
            "Price/Book</span><!-- react-text: 59 --> <!-- /react-text" \
            " --><!-- react-text: 60 -->(mrq)<!-- /react-text --><sup " \
            "aria-label=\"KS_HELP_SUP_undefined\" data-reactid=\"61\">" \
            "</sup></td><td class=\"Fz(s) Fw(500) Ta(end)\" data-react" \
            "id=\"62\">",
            "Price/Book</span><!-- react-text: 60 --> <!-- /react-text" \
            " --><!-- react-text: 61 -->(mrq)<!-- /react-text --><sup " \
            "aria-label=\"KS_HELP_SUP_undefined\" data-reactid=\"62\">" \
            "</sup></td><td class=\"Fz(s) Fw(500) Ta(end)\" data-react" \
            "id=\"63\">"]

# Search strings for the P/E Growth (5 years) ratio.
peg5_strs = ["EG Ratio (5 yr expected)</span><!-- react-text: 44 --> <!-- " \
            "/react-text --><!-- react-text: 45 --><!-- /react-text --><s" \
            "up aria-label=\"Data provided by Thomson Reuters.\" data-rea" \
            "ctid=\"46\">1</sup></td><td class=\"Fz(s) Fw(500) Ta(end)\" " \
            "data-reactid=\"47\">",
            "EG Ratio (5 yr expected)</span><!-- react-text: 45 --> <!-- " \
            "/react-text --><!-- react-text: 46 --><!-- /react-text --><s" \
            "up aria-label=\"Data provided by Thomson Reuters.\" data-rea" \
            "ctid=\"47\">1</sup></td><td class=\"Fz(s) Fw(500) Ta(end)\" " \
            "data-reactid=\"48\">"]

# Search strings for the trailing Price/Earnings (12 months, presumably) ratio.
pe12_strs = ["Trailing P/E</span><!-- react-text: 30 --> <!-- /react-text " \
             "--><!-- react-text: 31 --><!-- /react-text --><sup aria-labe" \
             "l=\"KS_HELP_SUP_undefined\" data-reactid=\"32\"></sup></td><" \
             "td class=\"Fz(s) Fw(500) Ta(end)\" data-reactid=\"33\">"]

# Search strings for debt/equity (mrq).
de_strs = ["Total Debt/Equity</span><!-- react-text: 226 --> <!-- /react-te" \
           "xt --><!-- react-text: 227 -->(mrq)<!-- /react-text --><sup ari" \
           "a-label=\"KS_HELP_SUP_undefined\" data-reactid=\"228\"></sup></" \
           "td><td class=\"Fz(s) Fw(500) Ta(end)\" data-reactid=\"229\">",
           "Total Debt/Equity</span><!-- react-text: 227 --> <!-- /react-te" \
           "xt --><!-- react-text: 228 -->(mrq)<!-- /react-text --><sup ari" \
           "a-label=\"KS_HELP_SUP_undefined\" data-reactid=\"229\"></sup></" \
           "td><td class=\"Fz(s) Fw(500) Ta(end)\" data-reactid=\"230\">",
           "Total Debt/Equity</span><!-- react-text: 228 --> <!-- /react-te" \
           "xt --><!-- react-text: 229 -->(mrq)<!-- /react-text --><sup ari" \
           "a-label=\"KS_HELP_SUP_undefined\" data-reactid=\"230\"></sup></" \
           "td><td class=\"Fz(s) Fw(500) Ta(end)\" data-reactid=\"231\">",
           "Total Debt/Equity</span><!-- react-text: 229 --> <!-- /react-te" \
           "xt --><!-- react-text: 230 -->(mrq)<!-- /react-text --><sup ari" \
           "a-label=\"KS_HELP_SUP_undefined\" data-reactid=\"231\"></sup></" \
           "td><td class=\"Fz(s) Fw(500) Ta(end)\" data-reactid=\"232\">",
           "Total Debt/Equity</span><!-- react-text: 230 --> <!-- /react-te" \
           "xt --><!-- react-text: 231 -->(mrq)<!-- /react-text --><sup ari" \
           "a-label=\"KS_HELP_SUP_undefined\" data-reactid=\"232\"></sup></" \
           "td><td class=\"Fz(s) Fw(500) Ta(end)\" data-reactid=\"233\">",
           "Total Debt/Equity</span><!-- react-text: 231 --> <!-- /react-te" \
           "xt --><!-- react-text: 232 -->(mrq)<!-- /react-text --><sup ari" \
           "a-label=\"KS_HELP_SUP_undefined\" data-reactid=\"233\"></sup></" \
           "td><td class=\"Fz(s) Fw(500) Ta(end)\" data-reactid=\"234\">",
           "Total Debt/Equity</span><!-- react-text: 232 --> <!-- /react-te" \
           "xt --><!-- react-text: 233 -->(mrq)<!-- /react-text --><sup ari" \
           "a-label=\"KS_HELP_SUP_undefined\" data-reactid=\"234\"></sup></" \
           "td><td class=\"Fz(s) Fw(500) Ta(end)\" data-reactid=\"235\">",
           "Total Debt/Equity</span><!-- react-text: 233 --> <!-- /react-te" \
           "xt --><!-- react-text: 234 -->(mrq)<!-- /react-text --><sup ari" \
           "a-label=\"KS_HELP_SUP_undefined\" data-reactid=\"235\"></sup></" \
           "td><td class=\"Fz(s) Fw(500) Ta(end)\" data-reactid=\"236\">",
           "Total Debt/Equity</span><!-- react-text: 234 --> <!-- /react-te" \
           "xt --><!-- react-text: 235 -->(mrq)<!-- /react-text --><sup ari" \
           "a-label=\"KS_HELP_SUP_undefined\" data-reactid=\"236\"></sup></" \
           "td><td class=\"Fz(s) Fw(500) Ta(end)\" data-reactid=\"237\">",
           "Total Debt/Equity</span><!-- react-text: 235 --> <!-- /react-te" \
           "xt --><!-- react-text: 236 -->(mrq)<!-- /react-text --><sup ari" \
           "a-label=\"KS_HELP_SUP_undefined\" data-reactid=\"237\"></sup></" \
           "td><td class=\"Fz(s) Fw(500) Ta(end)\" data-reactid=\"238\">",
           "Total Debt/Equity</span><!-- react-text: 236 --> <!-- /react-te" \
           "xt --><!-- react-text: 237 -->(mrq)<!-- /react-text --><sup ari" \
           "a-label=\"KS_HELP_SUP_undefined\" data-reactid=\"238\"></sup></" \
           "td><td class=\"Fz(s) Fw(500) Ta(end)\" data-reactid=\"239\">",
           "Total Debt/Equity</span><!-- react-text: 237 --> <!-- /react-te" \
           "xt --><!-- react-text: 238 -->(mrq)<!-- /react-text --><sup ari" \
           "a-label=\"KS_HELP_SUP_undefined\" data-reactid=\"239\"></sup></" \
           "td><td class=\"Fz(s) Fw(500) Ta(end)\" data-reactid=\"240\">"]

divrate_strs = ["Trailing Annual Dividend Rate</span><!-- react-text: 430 --> <" \
                "!-- /react-text --><!-- react-text: 431 --><!-- /react-text --" \
                "><sup aria-label=\"Data derived from multiple sources or calcu" \
                "lated by Yahoo Finance.\" data-reactid=\"432\">3</sup></td><td" \
                " class=\"Fz(s) Fw(500) Ta(end)\" data-reactid=\"433\">",
                "Trailing Annual Dividend Rate</span><!-- react-text: 431 --> <" \
                "!-- /react-text --><!-- react-text: 432 --><!-- /react-text --" \
                "><sup aria-label=\"Data derived from multiple sources or calcu" \
                "lated by Yahoo Finance.\" data-reactid=\"433\">3</sup></td><td" \
                " class=\"Fz(s) Fw(500) Ta(end)\" data-reactid=\"434\">",
                "Trailing Annual Dividend Rate</span><!-- react-text: 432 --> <" \
                "!-- /react-text --><!-- react-text: 433 --><!-- /react-text --" \
                "><sup aria-label=\"Data derived from multiple sources or calcu" \
                "lated by Yahoo Finance.\" data-reactid=\"434\">3</sup></td><td" \
                " class=\"Fz(s) Fw(500) Ta(end)\" data-reactid=\"435\">",
                "Trailing Annual Dividend Rate</span><!-- react-text: 433 --> <" \
                "!-- /react-text --><!-- react-text: 434 --><!-- /react-text --" \
                "><sup aria-label=\"Data derived from multiple sources or calcu" \
                "lated by Yahoo Finance.\" data-reactid=\"435\">3</sup></td><td" \
                " class=\"Fz(s) Fw(500) Ta(end)\" data-reactid=\"436\">",
                "Trailing Annual Dividend Rate</span><!-- react-text: 434 --> <" \
                "!-- /react-text --><!-- react-text: 435 --><!-- /react-text --" \
                "><sup aria-label=\"Data derived from multiple sources or calcu" \
                "lated by Yahoo Finance.\" data-reactid=\"436\">3</sup></td><td" \
                " class=\"Fz(s) Fw(500) Ta(end)\" data-reactid=\"437\">",
                "Trailing Annual Dividend Rate</span><!-- react-text: 435 --> <" \
                "!-- /react-text --><!-- react-text: 436 --><!-- /react-text --" \
                "><sup aria-label=\"Data derived from multiple sources or calcu" \
                "lated by Yahoo Finance.\" data-reactid=\"437\">3</sup></td><td" \
                " class=\"Fz(s) Fw(500) Ta(end)\" data-reactid=\"438\">",
                "Trailing Annual Dividend Rate</span><!-- react-text: 436 --> <" \
                "!-- /react-text --><!-- react-text: 437 --><!-- /react-text --" \
                "><sup aria-label=\"Data derived from multiple sources or calcu" \
                "lated by Yahoo Finance.\" data-reactid=\"438\">3</sup></td><td" \
                " class=\"Fz(s) Fw(500) Ta(end)\" data-reactid=\"439\">"]

divyield_strs = ["Trailing Annual Dividend Yield</span><!-- react-text: 437 --" \
                 "> <!-- /react-text --><!-- react-text: 438 --><!-- /react-te" \
                 "xt --><sup aria-label=\"Data derived from multiple sources o" \
                 "r calculated by Yahoo Finance.\" data-reactid=\"439\">3</sup" \
                 "></td><td class=\"Fz(s) Fw(500) Ta(end)\" data-reactid=\"440\">",
                 "Trailing Annual Dividend Yield</span><!-- react-text: 438 --" \
                 "> <!-- /react-text --><!-- react-text: 439 --><!-- /react-te" \
                 "xt --><sup aria-label=\"Data derived from multiple sources o" \
                 "r calculated by Yahoo Finance.\" data-reactid=\"440\">3</sup" \
                 "></td><td class=\"Fz(s) Fw(500) Ta(end)\" data-reactid=\"441\">",
                 "Trailing Annual Dividend Yield</span><!-- react-text: 439 --" \
                 "> <!-- /react-text --><!-- react-text: 440 --><!-- /react-te" \
                 "xt --><sup aria-label=\"Data derived from multiple sources o" \
                 "r calculated by Yahoo Finance.\" data-reactid=\"441\">3</sup" \
                 "></td><td class=\"Fz(s) Fw(500) Ta(end)\" data-reactid=\"442\">",
                 "Trailing Annual Dividend Yield</span><!-- react-text: 440 --" \
                 "> <!-- /react-text --><!-- react-text: 441 --><!-- /react-te" \
                 "xt --><sup aria-label=\"Data derived from multiple sources o" \
                 "r calculated by Yahoo Finance.\" data-reactid=\"442\">3</sup" \
                 "></td><td class=\"Fz(s) Fw(500) Ta(end)\" data-reactid=\"443\">",
                 "Trailing Annual Dividend Yield</span><!-- react-text: 441 --" \
                 "> <!-- /react-text --><!-- react-text: 442 --><!-- /react-te" \
                 "xt --><sup aria-label=\"Data derived from multiple sources o" \
                 "r calculated by Yahoo Finance.\" data-reactid=\"443\">3</sup" \
                 "></td><td class=\"Fz(s) Fw(500) Ta(end)\" data-reactid=\"444\">",
                 "Trailing Annual Dividend Yield</span><!-- react-text: 442 --" \
                 "> <!-- /react-text --><!-- react-text: 443 --><!-- /react-te" \
                 "xt --><sup aria-label=\"Data derived from multiple sources o" \
                 "r calculated by Yahoo Finance.\" data-reactid=\"444\">3</sup" \
                 "></td><td class=\"Fz(s) Fw(500) Ta(end)\" data-reactid=\"445\">",
                 "Trailing Annual Dividend Yield</span><!-- react-text: 443 --" \
                 "> <!-- /react-text --><!-- react-text: 444 --><!-- /react-te" \
                 "xt --><sup aria-label=\"Data derived from multiple sources o" \
                 "r calculated by Yahoo Finance.\" data-reactid=\"445\">3</sup" \
                 "></td><td class=\"Fz(s) Fw(500) Ta(end)\" data-reactid=\"446\">"]
