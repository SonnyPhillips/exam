from flask import Flask, render_template, request, redirect, url_for, flash
import csv
import re
import pandas as pd
import os


app = Flask(__name__)

Login_CSV = '/workspaces/exam/Rolsa Technologies/login.csv'
Consultation_CSV = '/workspaces/exam/Rolsa Technologies/consultation.csv'
Admin_CSV = '/workspaces/exam/Rolsa Technologies/adminlogin.csv'
Name = ""
logged_in = False
Admin_status = False
presence = False



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
        with open(Admin_CSV, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] == email and row[1] == password:
                    return redirect(url_for('admin'))
                else:
                    pass
        with open(Login_CSV, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] == email and row[1] == password:
                    #reroute to the admin window were consultations can be confirmed
                    #if email == "admin1@admin.com" and password == "Admin1234!":
                        #global Admin_status
                        #Admin_status = True
                        #return redirect(url_for('admin'))
                    global Name
                    Name = row[2]
                    global logged_in
                    logged_in = True
                    return redirect(url_for('index'))
                else:
                    flash('Invalid email or password')
    return render_template('login.html')

# Signup page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        email_exists = False
        try:
            with open('login.csv', mode='r', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if row == email.lower():
                        email_exists = True
                        break
        except FileNotFoundError:
            # If file doesn't exist, it means no users are registered yet
            pass
    
        if email_exists:
            flash('Email already in use', 'error')
            return redirect(url_for('signup_page'))
        if not is_valid_email(email):
            flash('Invalid email address')
        elif not is_valid_password(password):
            flash('Password must be at least 7 characters long, contain a number, and a special character')
        elif presence == True:
            #presence check of email in csv
            flash('email already in use')
            return redirect(url_for('signup'))
        else:
            #if all requirements are satisfied then account is added
            with open(Login_CSV, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([email, password,name])
            return redirect(url_for('login'))
    return render_template('signup.html', presence = presence)



# Information page
@app.route('/information')
def information():
    facts = [
        "The average carbon footprint of a British citizen is around 10 tons of CO2 per year.",
        "Non-renewable energy sources like coal and oil contribute significantly to air pollution and global warming.",
        "You can reduce your carbon footprint by using public transport, switching to renewable energy, and reducing waste."
    ]
    return render_template('information.html', facts=facts)


#Products page

products = [
    {
        "id": 1, 
        "image": "product1.jpg", 
        "description": "A Portable solar energy generator created by Anker,\n Typically costing around £500, provides green energy\nwhereever you are!"
    },
    {
        "id": 2, 
        "image": "product2.jpg", 
        "description": "Bladeless wind turbines that are much more eco friendly\nthan that of bladed turbines retailing\nfor £1850."
    },
    {
        "id": 3, 
        "image": "product3.jpg", 
        "description": "A portable energy storage device to bring your solar\npower to drearier climates or even in an emergency\nblackout going for just £600"
    }
]

@app.route('/products')
def show_products():
    return render_template('products.html', products=products)



# Book consultation page
@app.route('/book_consultation', methods=['GET', 'POST'])
def book_consultation():
    if logged_in == False:
        return redirect(url_for('login'))
    if request.method == 'POST':
        global Name
        name = Name
        #name will be automatically entered based on account details

        address = request.form['address']
        date = request.form['date']
        f=open(Consultation_CSV,"r")
        reader=csv.reader(f)
        found = False
        for row in reader:
            #if name is found then booking will not be added to avoid dupplicated bookings
            if name in row:
                found = True
        f.close()
        if found == False:
            with open('consultation.csv', 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([name, address, date])
                #this will then be accessed via the admin page to be confirmed
            flash('Consultation booked successfully!')
            return redirect(url_for('index'))
        else:
            flash('User has already booked a consultation')

        return render_template('book_consultation.html')

# Carbon footprint calculator
@app.route('/carbon_footprint', methods=['GET', 'POST'])
def carbon_footprint():
    if request.method == 'POST':
        drives_to_work = request.form.get('drives_to_work') 
        miles = float(request.form.get('miles', 0))
        #yearly average of milage
        miles = miles * 365
        recycles = request.form.get('recycles')
        bill_electric = float (request.form.get('bill_electric'))
        bill_electric = bill_electric *105
        bill_gas = float (request.form.get('bill_gas'))
        bill_gas = bill_gas * 105
        #numbers to multiply by come from justenergy.com
        if drives_to_work and miles > 0:
            #this will be a calculation on users who drive to work
            carbon_footprint = miles
            carbon_footprint = carbon_footprint = bill_electric +bill_gas
            if recycles == 'no':
                carbon_footprint = carbon_footprint +250 
            return render_template('carbon_footprint.html', carbon_footprint=carbon_footprint)
        elif drives_to_work == 'no':
            #users who do not drive to work
            carbon_footprint = carbon_footprint = bill_electric +bill_gas
            if recycles == 'no':
                carbon_footprint = carbon_footprint +250 
            return render_template('carbon_footprint.html', carbon_footprint=carbon_footprint)


@app.route('/admin', methods=['POST'])
def admin():
    if request.method == 'POST':
        # Handle form submission to update confirmation status
        name = request.form.get('name')
        date = request.form.get('date')
        
        # Create a temporary file to write updated data
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, newline='')
        fieldnames = ['name', 'address', 'date', 'confirmed']
        
        with open(Consultation_CSV, mode='r') as csvfile, temp_file:
            reader = csv.DictReader(csvfile)
            writer = csv.DictWriter(temp_file, fieldnames=fieldnames)
            writer.writeheader()
            
            for row in reader:
                # Update the specific entry that matches name and date
                if row['name'] == name and row['date'] == date:
                    row['confirmed'] = 'yes'
                writer.writerow(row)
        
        # Replace the original file with the updated one
        os.replace(temp_file.name, 'consultation.csv')
        
        return redirect(url_for('admin'))
    
    else:
        # GET request - display unconfirmed consultations
        unconfirmed_consultations = []
        
        try:
            with open('consultation.csv', mode='r') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if row['confirmed'].lower() == 'no':
                        unconfirmed_consultations.append({
                            'name': row['name'],
                            'address': row['address'],
                            'date': row['date']
                        })
        except FileNotFoundError:
            pass  # Handle case where file doesn't exist yet
        
        return render_template('admin.html', consultations=unconfirmed_consultations)




if __name__ == '__main__':
    app.run(debug=True)
