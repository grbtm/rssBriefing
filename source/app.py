from flask import Flask

# WSGI application
app = Flask(__name__)

# use route() decorator to tell Flask what URL should trigger our function
@app.route('/')
# The function is given a name which is also used to generate URLs for that particular function,
# and returns the message we want to display in the user’s browser
def hello_world():
    return "Hello wurd!"