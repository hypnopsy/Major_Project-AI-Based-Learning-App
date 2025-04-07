from flask import *
from public import *
from teacher import *
from api import *
from admin import *

app = Flask(__name__,template_folder='templates')

app.register_blueprint(public)
app.register_blueprint(teacher)
app.register_blueprint(api)
app.register_blueprint(admin)

app.secret_key = 'sssbd5dvshd66efentjndjsdf@@@'


@app.route('/logout')
def logout():
    session.clear()  # Clear the session data
    return redirect(url_for('public.login')) 


@app.route('/protected')
def protected():
    if 'user_id' not in session:  # Check if the user is not logged in
        return redirect(url_for('login'))  # Redirect to login page if not logged in
    return 'Protected Page'


@app.after_request
def add_header(response):
    response.cache_control.no_store = True  # Prevents caching
    return response

app.run(debug=True,port=5100,host='0.0.0.0')

