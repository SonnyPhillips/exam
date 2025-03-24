from flask import Flask, render_template, request, redirect, url_for, flash
import csv
import re
import pandas as pd

app = Flask(__name__)
app.secret_key = 'your_secret_key'

Login_CSV = '/workspaces/exam/Rolsa Technologies/login.csv'
Consultation_CSV = '/workspaces/exam/consultation.csv'
Admin_CSV = '/workspaces/exam/Rolsa Technologies/admin.csv'
Name = ""
logged_in = False
Admin_status = False



# Email validation criteria
def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

# Password validation criteria
def is_valid_password(password):
    return (
        len(password) >= 7 and
        any(char.isdigit() for char in password) and
        any(char in "!@#$%^&*()" for char in password) 
    )

# Homepage
@app.route('/')
def index():
    return render_template('index.html')

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        with open(Login_CSV, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] == email and row[1] == password:
                    #reroute to the admin window were consultations can be confirmed
                    if email == "admin1@admin.com" and password == "Admin1234!":
                        global Admin_status
                        Admin_status = True
                        return redirect(url_for('admin'))
                    global Name
                    Name = row[2]
                    global logged_in
                    logged_in = True
                    return redirect(url_for('index'))
        flash('Invalid email or password')
    return render_template('login.html')

# Signup page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        if not is_valid_email(email):
            flash('Invalid email address')
        elif not is_valid_password(password):
            flash('Password must be at least 7 characters long, contain a number, and a special character')
        else:
            with open(Login_CSV, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([email, password,name])
            flash('Signup successful! Please login.')
            return redirect(url_for('login'))
    return render_template('signup.html')



# Information page
@app.route('/information')
def information():
    facts = [
        "The average carbon footprint of a British citizen is around 10 tons of CO2 per year.",
        "Non-renewable energy sources like coal and oil contribute significantly to air pollution and global warming.",
        "You can reduce your carbon footprint by using public transport, switching to renewable energy, and reducing waste."
    ]
    return render_template('information.html', facts=facts)

# Book consultation page
@app.route('/book_consultation', methods=['GET', 'POST'])
def book_consultation():
    if logged_in == False:
        return redirect(url_for('login'))
    if request.method == 'POST':
        name = Name
        address = request.form['address']
        date = request.form['date']
        with open('consultation.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([name, address, date])
        flash('Consultation booked successfully!')
    return render_template('book_consultation.html')

# Carbon footprint calculator
@app.route('/carbon_footprint', methods=['GET', 'POST'])
def carbon_footprint():
    if request.method == 'POST':
        drives_to_work = request.form.get('drives_to_work') == 'yes'
        miles = float(request.form.get('miles', 0))
        mpg = float(request.form.get('mpg', 0))
        if drives_to_work and miles > 0 and mpg > 0:
            carbon_footprint = (miles / mpg) * 8.887  # CO2 per gallon of petrol
            return render_template('carbon_footprint.html', carbon_footprint=carbon_footprint)
        else:
            flash('Please provide valid inputs')
    return render_template('carbon_footprint.html')

@app.route('/admin')
def admin():
        with open(Consultation_CSV, 'r') as file:
            data = pd.read_csv(file, header=0) 
            Consultation = data.values 
        return render_template('admin.html', Consultation=Consultation)


if __name__ == '__main__':
    app.run(debug=True)
