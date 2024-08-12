from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import pyrebase, secrets
from config import firebase_config as config
import content, ai_process 

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

firebase = pyrebase.initialize_app(config)

db = firebase.database()
auth = firebase.auth()
# storage = firebase.storage()

user = None
questions = content.questions
courses = content.courses

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
            user = auth.sign_in_with_email_and_password(email, password)
            print(user)
            session['user'] = user['idToken'] 
            return redirect(url_for('personalized_test'))

        except Exception as e:
            flash(f'Error: {e}')

    return render_template('register.html')


@app.route('/personalized_test', methods=['GET', 'POST'])
def personalized_test():
    return render_template('personalized_test.html')

@app.route('/learn', methods=['GET', 'POST'])
def learn():
    return render_template('learn.html', logged_in='user' in session)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    return render_template('profile.html',username='%.9s' % user["email"].split("@")[0], logged_in='user' in session)

@app.route('/login', methods=['GET', 'POST'])
def login():
    global user
    # print("ello")
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        # print("ello")
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            print(user)
            session['user'] = user['idToken']  # Save user token in session
            # print("Session set:", session.get('user'))
            # print("Huhhhh")
            flash('Login successful!')
            return redirect(url_for('index'))
        except Exception as e:
            print(e)
            flash(f'Error: {e}')
    print("But why")
    return render_template('login.html')


@app.route('/about')
def about():
    return render_template('about.html', logged_in='user' in session)


@app.route('/logout')
def logout():
    session.pop('user', None)  # Remove user token from session
    flash('You have been logged out.')
    return redirect(url_for('index'))

@app.route('/get-questions', methods=['GET'])
def get_questions():
    return jsonify(questions)


@app.route('/submit-answers', methods=['GET', 'POST'])
def submit_answers():
    request_data = request.get_json()
    user_id = 'some_user_id'  # Placeholder for user identification logic
    answers = request_data['answers'].split('%')[0].split("\n")
    formatted_responses = ""
    index = 0

    print("Processing answers...")
    print(answers)

    while index < len(answers) - 1:
        line = answers[index]
        if not line:
            index += 1
            continue

        print(line)
        question_key = line.split(" ")[1]
        print(questions[question_key])

        if line.startswith("Q"):
            question_number = line.split(" ")[0]
            formatted_responses += f"{question_number} {questions[question_key]['text']}\n"
            formatted_responses += f"{answers[index + 1]}\n"
            index += 1  # Skip the next line as it's already processed

        index += 1

    print(formatted_responses)
    recommendations = ai_process.get_course_recommendations(formatted_responses, courses)
    print(recommendations)

    return jsonify({'message': 'Answers received successfully!'})

if __name__ == '__main__':
    app.run(debug=True)
