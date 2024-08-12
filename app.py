from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import pyrebase
import secrets
import content

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

config = {
    "apiKey": "",
    'authDomain': "vitc-hackathon.firebaseapp.com",
    'databaseURL': "https://vitc-hackathon-default-rtdb.asia-southeast1.firebasedatabase.app",
    'projectId': "vitc-hackathon",
    'storageBucket': "vitc-hackathon.appspot.com",
    'messagingSenderId': "101699835554",
    'appId': "1:101699835554:web:45b404e97ff504610029fb",
    'measurementId': "G-H8VQGB4S1Y"
}

firebase = pyrebase.initialize_app(config)

db = firebase.database()
auth = firebase.auth()
# storage = firebase.storage()


@app.route('/')
def index():
    return render_template('index.html', logged_in='user' in session)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords do not match!')
            return redirect(url_for('register'))

        try:
            auth.create_user_with_email_and_password(email, password)
            flash('Registration successful! Please log in.')
            return redirect(url_for('personalized_test'))

        except Exception as e:
            flash(f'Error: {e}')

    return render_template('register.html')


@app.route('/personalized_test', methods=['GET', 'POST'])
def personalized_test():
    return render_template('personalized_test.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            session['user'] = user['idToken']  # Save user token in session
            flash('Login successful!')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Error: {e}')
    return render_template('login.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/logout')
def logout():
    session.pop('user', None)  # Remove user token from session
    flash('You have been logged out.')
    return redirect(url_for('index'))


questions = content.questions


@app.route('/get-questions', methods=['GET'])
def get_questions():
    return jsonify(questions)


@app.route('/submit-answers', methods=['GET', 'POST'])
def submit_answers():
    data = request.get_json()
    user_id = 'some_user_id'  # Replace with actual user ID or identifier
    # Store or process the answers
    # For demo, just print them
    print(data)
    return jsonify({'message': 'Answers received successfully!'})


if __name__ == '__main__':
    app.run(debug=True)
