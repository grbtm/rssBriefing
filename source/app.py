from flask import Flask, escape, url_for

# WSGI application
app = Flask(__name__)

# use route() decorator to tell Flask what URL should trigger our function
# URL --> function
# By default, a route only answers to GET requests
@app.route('/')
# The function is given a name which is also used to generate URLs for that particular function,
# and returns the message we want to display in the user’s browser
def hello_world():
    # The return value from a view function is automatically converted into a response object
    # for you.
    return 'Hello wurd!'


@app.route('/login')
def login():
    return 'login'


@app.route('/user/<username>')
def profile(username):
    return '{}\'s profile'.format(escape(username))


with app.test_request_context():
    print(url_for('hello_world'))  # function --> URL
    print(url_for('login'))
    print(url_for('login', next='/'))
    print(url_for('profile', username='John Doe'))
