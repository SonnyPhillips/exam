from flask import Flask, render_template, request, redirect, url_for, flash
import csv
import re
import pandas as pd

app = Flask(__name__)

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
                    #if email == "admin1@admin.com" and password == "Admin1234!":
                        #global Admin_status
                        #Admin_status = True
                        #return redirect(url_for('admin'))
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
        with open(Login_CSV, 'r') as file:
                reader = csv.reader(file, delimiter=',') 
                for row in reader:
                    #reading the csv for instances of the email being used
                    #if email is found then user will not be added to login list
                    if row[0] == email:
                        return redirect(url_for('signup'))
        if not is_valid_email(email):
            flash('Invalid email address')
        elif not is_valid_password(password):
            flash('Password must be at least 7 characters long, contain a number, and a special character')
        else:
            with open(Login_CSV, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([email, password,name])
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
        f=open(Consultation_CSV,"r")
        reader=csv.reader(f)
        found = False
        for row in reader:
            if name in row:
                found = True
        f.close()
        if found == False:
            with open('consultation.csv', 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([name, address, date])
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
        bill_electric = float (request.form.get('electric bill',0))
        bill_electric = bill_electric *105
        bill_gas = float (request.form.get('gas bill', 0))
        bill_gas = bill_gas * 105
        recycles = request.form.get('recycles') 
        carbon_footprint =bill_electric + bill_gas
        if drives_to_work == "yes":
            miles = miles * 365
            carbon_footprint = carbon_footprint+ (miles* 0.79) 
        if recycles == "no":
            carbon_footprint = carbon_footprint + 250

        return render_template('carbon_footprint.html', carbon_footprint=carbon_footprint)
    else:
        flash('Please provide valid inputs')
    return render_template('carbon_footprint.html')

@app.route('/admin', methods=['POST'])
def admin():
    if request.method == 'POST':
        row_id = request.form.get('row_id')
        new_value = request.form.get('authorised')
        
        # Read the CSV file and update the authorised field
        rows = []
        with open(Consultation_CSV,'r') as file:
            csv_reader = csv.DictReader(file)
            fieldnames = csv_reader.fieldnames
            for row in csv_reader:
                if row.get('id') == row_id: 
                    row['authorised'] = new_value
                rows.append(row)
        
        # Write the updated data back to the CSV
        with open(Consultation_CSV, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
    
    return redirect(url_for('admin'))




if __name__ == '__main__':
    app.run(debug=True)
