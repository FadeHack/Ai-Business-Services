from flask import Flask, render_template, request, redirect, session, jsonify
from pymongo import MongoClient

from pymongo.server_api import ServerApi


app = Flask(__name__)
app.secret_key = 'your_secret_key'

uri = 'mongodb+srv://Temp_User:9BH1EM6p6LWStCxt@mongodatabase.ytbk03l.mongodb.net/?retryWrites=true&w=majority'

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
    
    
db = client['ai_buisness']
users_collection = db['users']
companies_collection = db['companies']
services_collection = db['services']
contact_collection = db['contact_form']
    
@app.route('/')
def home():
    companies = companies_collection.find()
    return render_template('home.html', companies=companies)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Check if the user exists in the database
        user = users_collection.find_one({'email': email, 'password': password})
        
        if user:
            # Convert ObjectId to string before storing in session
            user['_id'] = str(user['_id'])
            
            # Store user data in session
            session['user'] = user
            return redirect('/')
        else:
            message = 'Invalid email or password'
            return render_template('login.html', message=message)
    
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Check if the email is already registered
        existing_user = users_collection.find_one({'email': email})
        
        if existing_user:
            message = 'Email already registered'
            return render_template('login.html', message=message)
        
        # Create a new user document
        new_user = {'username': username, 'email': email, 'password': password}
        result = users_collection.insert_one(new_user)
        
        new_user['_id'] = str(result.inserted_id)
        # Store user data in session
        session['user'] = new_user
        
        return redirect('/')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')


@app.route('/services')
def services():
    # Fetch all services from the database
    services = services_collection.find()
    return render_template('services.html', services=services)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        
        # Create a new contact form document
        contact_form_data = {'name': name, 'email': email, 'message': message}
        result = contact_collection.insert_one(contact_form_data)
        
        if result.inserted_id:
            return jsonify({'status': 'success'})
        
        return jsonify({'status': 'failed'})
    
    return render_template('contact.html')

if __name__ == '__main__':
    app.run(debug=True, host="192.168.0.104")
