import requests


def get_live():
    r = requests.get(
        "https://www.tradingview.com/markets/stocks-usa/market-movers-gainers/"
    )

    from bs4 import BeautifulSoup

    soup = BeautifulSoup(r.text, "html.parser")

    result = soup.find_all("script", attrs={"type": "application/prs.init-data+json"})
    data = result[1].contents[0]

    import json

    d = json.loads(data)
    a = dict(d)
    b = a[list(a.keys())[0]]
    c1 = b[list(b.keys())[1]]
    e = c1["data"]

    live = []
    for i in e:
        live.append(i["d"][0])
    return live


def get_pre():
    r = requests.get(
        "https://www.tradingview.com/markets/stocks-usa/extended-hours-pre-market-gainers/"
    )

    from bs4 import BeautifulSoup

    soup = BeautifulSoup(r.text, "html.parser")

    result = soup.find_all(
        "a",
        attrs={"class": "tv-screener__symbol"},
    )
    live = []
    for i in result:
        d = i.contents[0]
        live.append(d)
    return live


def get_after():
    r = requests.get(
        "https://www.tradingview.com/markets/stocks-usa/extended-hours-after-hours-gainers/"
    )

    from bs4 import BeautifulSoup

    soup = BeautifulSoup(r.text, "html.parser")

    result = soup.find_all(
        "a",
        attrs={"class": "tv-screener__symbol"},
    )
    live = []
    for i in result:
        d = i.contents[0]
        live.append(d)
    return live


live = get_live()
pre = get_pre()
post = get_after()

final_list = live + pre + post
final_list = set(final_list)

yesterdays = None

from datetime import date, timedelta
import os
import pandas as pd

yesterday = date.today() - timedelta(days=1)
today = date.today()

today_name = str(today) + ".csv"
yesterday_name = str(yesterday) + ".csv"
updated_final_list = final_list

outdir = "./tradingview"
if not os.path.exists(outdir):
    os.mkdir(outdir)

fullname = os.path.join(outdir, yesterday_name)

if os.path.exists(fullname):

    stocks = pd.read_csv(fullname)
    stocks = stocks.loc[:, "Unnamed: 0"]
    stocks = stocks.unique()
    stocks = set(stocks)
    yesterdays = stocks
else:
    yesterdays = None


if yesterdays != None:
    updated_final_list = final_list - yesterdays

updated_final_list = list(updated_final_list)

if os.path.exists(today_name):
    idk = None
else:

    import os

    outdir = "./tradingview"
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    fullname = os.path.join(outdir, today_name)

    df = pd.DataFrame(index=updated_final_list)
    df.to_csv(fullname)

if os.path.exists(today_name):
    import ssl
    import smtplib

    email_body = "".join(updated_final_list)
    port = 465  # For SSL
    password = "Saskatoon09"
    smtp_server = "smtp.gmail.com"
    sender_email = "krishnanaveen858@gmail.com"
    receiver_email = "nijoy4@gmail.com"
    message = (
        """
    Subject: Good Morning Newsletter
    %s
    This message is sent from Python."""
        % email_body
    )
    # Create a secure SSL context
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)


print(updated_final_list)
