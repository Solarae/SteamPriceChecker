import os
import smtplib
import csv
import requests
from decimal import Decimal
from email.message import EmailMessage

APP_DETAILS_URL = 'http://store.steampowered.com/api/appdetails/'
email = "YOUR PASSWORD"
password = "YOUR EMAIL"

dir_path = os.path.dirname(os.path.realpath(__file__))
email_file = os.path.join(dir_path, 'email.txt')
list_file = os.path.join(dir_path, 'list.csv')

if os.path.exists(email_file) == False or os.path.getsize(email_file) == 0:
    print('Quitting')
    quit()

with open(email_file, 'r') as f:
    receiver = f.read()

body = ""

with open(list_file, 'r') as f:
    items = csv.reader(f)
    app_ids = ','.join(x[1] for x in items)

with open(list_file, 'r') as f:
    items = csv.reader(f)
    
    if items:
        params = {
            'filters': 'price_overview',
            'appids': app_ids
        }
        response = requests.get(APP_DETAILS_URL, params=params)
        data = response.json()

        for item in items:
            desired_price = Decimal(item[3])
            curr_price = Decimal(data[item[1]]['data']['price_overview']['final_formatted'].strip('$'))

            if desired_price >= curr_price:
                body += '{} is on sale for ${}\n'.format(item[0], curr_price)

        if body:
            msg = EmailMessage()
            msg['Subject'] = 'Steam Price Checker'
            msg['From'] = email
            msg['To'] = receiver
            msg.set_content(body)

            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            try:
                server.login(email, password)
                print("Logged in...")
                server.send_message(msg)
                print("Email has been sent!")
            except smtplib.SMTPAuthenticationError:
                print("Unable to sign in")

