from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import pyrebase
import secrets
from config import firebase_config as config
import content
import ai_process

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

firebase = pyrebase.initialize_app(config)

db = firebase.database()
auth = firebase.auth()
# storage = firebase.storage()

user = None
questions = content.questions
courses = content.courses
db.child("available_courses").set(courses)


@app.route('/')
def index():
    return render_template('index.html', logged_in='user' in session)


@app.route('/register', methods=['GET', 'POST'])
def register():
    global user
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
            user_data = {
                "username": username,
                "gender": "",
                "age": -1,
                "enrolled_courses": [],
                "courses_completed": [],
                "recommended_courses": [],
                "available_courses": courses,
                "coins": 0
            }

            user["email"] = user["email"].replace("@", "I").replace(".", "I")

            db.child("users").child(user['email']).set(user_data)

            return redirect(url_for('personalized_test'))

        except Exception as e:
            print(e)
            flash(f'Error: {e}')

    return render_template('register.html')


@app.route('/personalized_test', methods=['GET', 'POST'])
def personalized_test():
    return render_template('personalized_test.html')


@app.route('/learn', methods=['GET', 'POST'])
def learn():
    global user
    if not user:
        flash("You're not logged in.")
        return redirect(url_for('index'))
    user_id = user['email']
    user_data = db.child("users").child(user_id).get().val()
    return render_template('learn.html', data=user_data, logged_in='user' in session)


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    global user
    user_id = user['email']
    user_data = db.child("users").child(user_id).get().val()
    return render_template('profile.html', data=user_data, username='%.9s' % user["email"].split("@")[0], logged_in='user' in session)


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
            user["email"] = user["email"].replace("@", "I").replace(".", "I")
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
    user_id = user['email']  # Placeholder for user identification logic
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
    recommendations = ai_process.get_course_recommendations(
        formatted_responses, courses)
    print(recommendations)

    courses_to_move = []
    available_courses = db.child('users').child(user_id).get().val().get("available_courses", {})
    print(">>>>>>>>>>> ", type(available_courses),len(available_courses), available_courses)

    after_removal = []
    del_indices = set()

    for i in range(len(available_courses)):
        if available_courses[i]["title"] in recommendations:
            courses_to_move.append(available_courses[i])
            del_indices.add(i)

    for i in range(len(available_courses)):
        if i not in del_indices:
            after_removal.append(available_courses[i])
    db.child('users').child(user_id).update({
        'available_courses': after_removal,
        'recommended_courses': courses_to_move
    })

    return jsonify({'message': 'Answers received successfully!'})


@app.route('/enroll/<course_title>', methods=['POST'])
def enroll(course_title):
    user_id = user['email']  # Get the user ID from the session
    if not user_id:
        flash('You must be logged in to enroll in courses.')
        return redirect(url_for('login'))

    # Retrieve the user's data
    user_data = db.child('users').child(user_id).get().val()
    available_courses = user_data.get("available_courses", {})
    recommended_courses = user_data.get('recommended_courses', {})
    enrolled_courses = user_data.get('enrolled_courses', [])

    # Check and remove from available courses
    for i in range(len(available_courses)):
        if available_courses[i]["title"] == course_title:
            # Remove the course from available courses
            course = available_courses.pop(i)
            enrolled_courses.append(course)  # Add to enrolled courses
            break

    # Check and remove from recommended courses
    for i in range(len(recommended_courses)):
        if recommended_courses[i]["title"] == course_title:
            # Remove the course from recommended courses
            course = recommended_courses.pop(i)
            enrolled_courses.append(course)  # Add to enrolled courses
            break

    # Update the user's courses in the database
    db.child('users').child(user_id).update({
        'available_courses': available_courses,
        'recommended_courses': recommended_courses,
        'enrolled_courses': enrolled_courses
    })

    flash(f'You have successfully enrolled in {course_title}.')
    return redirect(url_for('learn'))


@app.route('/course/<course_title>', methods=['GET','POST'])
def course_page(course_title):
    global user
    user_id = user['email']
    user_data = db.child("users").child(user_id).get().val()

    # Find the course data based on the course_title
    for course in user_data['enrolled_courses']:
        if course['title'] == course_title:
            selected_course = course
            break
    else:
        flash('Course not found')
        return redirect(url_for('learn'))
    print(selected_course)
    return render_template('course.html',logged_in='user' in session, course=selected_course)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    question = data.get('question')

    print("Received question:", question)  # Debugging print

    # Check if the question is finance-related
    if ai_process.is_finance_related(question):
        # Check if the user is asking to create a course
        if ai_process.is_asking_to_create_course(question):
            # Generate a brief overview
            overview = ai_process.generate_course_overview(question)
            response = {
                'overview': overview,
                'follow_up': "Would you like to create a course on this topic?"
            }
        else:
            # Provide a detailed teaching response
            detailed_response = ai_process.generate_teaching_response(question)
            response = {
                'overview': detailed_response,
                'follow_up': ""
            }
    else:
        response = {
            'overview': "",
            'follow_up': "Sorry, I can only help with finance-related topics. Please ask something related to finance."
        }

    print("Generated response:", response)  # Debugging print

    return jsonify(response)

@app.route('/clear_history', methods=['POST', 'GET'])
def clear_history():
    session.pop('conversation_history', None)
    return jsonify({"message": "Conversation history cleared."})


@app.route('/create-course', methods=['POST'])
def create_course():
    data = request.json
    question = data.get('question')
    user_id = user['email']

    # Create the course and enroll the user
    new_course = ai_process.create_custom_course(question, user_id, db)

    return jsonify(new_course)


# @app.route('/course/<course_title>', methods=['GET'])
# def course(course_title):
#     user_id = user['email']
#     print(f"Fetching data for user: {user_id}")  # Debugging print

#     user_data = db.child("users").child(user_id).get().val()
#     if not user_data:
#         print("User data not found!")  # Debugging print
#         flash("User data not found!")
#         return redirect(url_for('learn'))

#     course_data = None

#     # Find the course data based on the title
#     print(f"Looking for course: {course_title}")  # Debugging print
#     for course in user_data.get('enrolled_courses', []):
#         print(f"Checking course: {course['title']}")  # Debugging print
#         if course['title'].lower() == course_title.lower():
#             course_data = course
#             break

#     if not course_data:
#         print("Course not found!")  # Debugging print
#         flash("Course not found!")
#         return redirect(url_for('learn'))

#     print(f"Course found: {course_data}")  # Debugging print
#     return render_template('course.html',, course=course_data)

if __name__ == '__main__':
    app.run(debug=True)
