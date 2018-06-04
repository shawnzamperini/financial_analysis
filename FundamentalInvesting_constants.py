import pandas as pd


# Filename of most recent S&P 500 from Wikipedia, copy/pasted into txt file.
sp500_filename = 'sp500_060118.txt'

sp500 = []
with open(sp500_filename) as f:
    for line in f:
        ticker = line.split("\t")[0]
        sp500.append(ticker)

# Filename of the Russell 3000. Get the PDF of all the tickers in it, then convert
# it to a word document using abiword. Copy and paste everything to a txt file. Then
# delete all the in between info. Copy/pasting one of the chunks and then using a
# regex (.*) the replace each of the numbers (this time it was 1-30) gets rid of all
# of them.
# So the file format end up being every line that is a multiple of 4 has the actual
# ticker on it. So grab every 4th line.
russell3000_filename = 'russell3000_060118.txt'

russell3000 = []
with open(russell3000_filename) as f:
    line_num = 0
    for line in f:
        line_num += 1
        if line_num % 4 == 0:
            ticker = line.split("\n")[0]
            russell3000.append(ticker)


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
de_strs = ["Total Debt/Equity</span><!-- react-text: 231 --> <!-- /react-te" \
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
           "Total Debt/Equity</span><!-- react-text: 237 --> <!-- /react-te" \
           "xt --><!-- react-text: 238 -->(mrq)<!-- /react-text --><sup ari" \
           "a-label=\"KS_HELP_SUP_undefined\" data-reactid=\"239\"></sup></" \
           "td><td class=\"Fz(s) Fw(500) Ta(end)\" data-reactid=\"240\">"]
