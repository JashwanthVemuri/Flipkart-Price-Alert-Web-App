from flask import Flask, render_template, request, redirect, url_for, flash
import requests
from bs4 import BeautifulSoup
import csv
import smtplib
from email.message import EmailMessage

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# CSV file for storing tracked prices
csv_file = open('price.csv', 'w')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['Product Name', 'Current Price'])

def scrap_data(url):
    source = requests.get(url)
    if source.status_code == 200:
        soup = BeautifulSoup(source.text, 'lxml')
        product_name = soup.find('span', class_='B_NuCI').text.strip()
        product_price = soup.find('div', class_='_30jeq3').text.strip()
        return product_name, product_price
    return None, None

def track(url, target_price, receiver_email):
    while True:
        name, price = scrap_data(url)
        if price is not None:
            price = float(price.replace('₹', '').replace(',', ''))
            if price <= target_price:
                csv_writer.writerow([name, price])
                send_notification(name, price, url, receiver_email)
                break  # Exit the loop when the email is sent

def send_notification(product_name, current_price, url, receiver_email):
    sender_email = 'your_email@gmail.com'
    sender_password = 'password'

    # Compose the email message
    subject = f'Price Drop Alert: {product_name}'
    message = f'The price of {product_name} has dropped to ₹{current_price}.\n'
    message += f'You can purchase it here: {url}'

    # Send the email
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        subject = subject.encode('utf-8')
        message = message.encode('utf-8')

        msg = EmailMessage()
        msg.set_content(message.decode('utf-8'))
        msg['Subject'] = subject.decode('utf-8')
        msg['From'] = sender_email
        msg['To'] = receiver_email

        server.send_message(msg)
        print('Notification email sent!')
    except Exception as e:
        print('Error sending email:', str(e))
    finally:
        server.quit()

@app.route('/')
def home():
    return render_template('index_1.html')

@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        product_url = request.form['url']
        target_price = float(request.form['price'])
        receiver_email = request.form['mail']
        track(product_url, target_price, receiver_email)
        flash('Price tracking started successfully!')
        return redirect(url_for('home'))

    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
