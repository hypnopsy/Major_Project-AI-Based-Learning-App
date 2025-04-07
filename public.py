import uuid
from flask import *
from database import *
public = Blueprint('public',__name__)




@public.route('/')
def entry():
    return render_template('index.html')





@public.route('/login', methods=['GET', 'POST'])
def login():
    if 'login' in request.form:
        username = request.form['uname']
        password = request.form['psd']
        
        # Secure SQL query using placeholders to prevent SQL injection
        dd = "SELECT * FROM login WHERE username = '%s' AND password = '%s'"%(username,password)
        res = select(dd) # pass parameters safely
        
        if res:
            session['login_id'] = res[0]['login_id']
            utype = res[0]['usertype']
            
            if utype == 'teacher':
                s = "SELECT * FROM teacher WHERE login_id ='%s'"%(session['login_id'])
                rev = select(s)
                
                session['tid'] = rev[0]['teacher_id']
                return redirect(url_for('teacher.teacher_home'))
            
            elif utype == 'admin':
                return redirect(url_for('admin.admin_home'))
            
            else:
                return """<script>alert("LOGIN FAILED :("); window.location='/login';</script>"""
        
        else:
            return """<script>alert("LOGIN FAILED :("); window.location='/login';</script>"""
    
    return render_template('login.html')

@public.route('/logout')
def logout():
    session.clear()  # Clear the session data
    return redirect(url_for('public.login'))  # Redirect to the login page

@public.after_request
def add_no_cache_header(response):
    response.cache_control.no_store = True  # Prevent caching for the response
    response.cache_control.must_revalidate = True  # Ensure the page is revalidated
    response.headers['Pragma'] = 'no-cache'
    response.headers['Cache-Control'] = 'no-store'
    return response

@public.route('/protected')
def protected():
    if 'login_id' not in session:  # Check if the user is not logged in
        return redirect(url_for('public.login'))  # Redirect to login page if not logged in
    return 'Protected Page'



# @public.route('/login', methods=['GET', 'POST'])
# def login():
    
#     if 'login' in request.form:
#         username = request.form['uname']
#         password = request.form['psd']
        
#         dd="select * from login where username = '%s' and password = '%s'"%(username,password)
        
#         res = select(dd)
        
        
#         if res:
#             session['login_id']=res[0]['login_id']
#             utype=res[0]['usertype']
#             if utype == 'parent':
#                 s="select * from teacher where login_id='%s'"%(session['login_id'])
#                 rev = select(s)
#                 print(rev,'ffffffffffffffffffffffffffff')
#                 session['tid'] = rev[0]['teacher_id']
#                 return redirect(url_for('teacher.teacher_home'))
            
#             elif utype=='admin':
#                 return redirect(url_for('admin.admin_home'))
#             else:
#                 return """<script>alert("LOGIN FAILED :(");window.location='/login'</script>"""
            
#         else:
#             return """<script>alert("LOGIN FAILED :(");window.location='/login'</script>"""

        
#     return render_template('login.html')


@public.route('/Teacher_Registration', methods=['GET', 'POST'])
def Teacher_Registration():
    if request.method == 'POST' and 'teach' in request.form:
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        dob = request.form['dob']
        gender = request.form['gender']
        place = request.form['place']
        email = request.form['email']
        phone = request.form['phone']
        username = request.form['uname']
        password = request.form['psd']

        education_proof = request.files['education_proof']
        path = 'static/teacher_education/' + str(uuid.uuid4())+education_proof.filename
        education_proof.save(path)
        photo = request.files['photo']
        path1 = 'static/teacher_photo/' + str(uuid.uuid4())+photo.filename
        photo.save(path1)
        
        
        obj = """
                insert into login values(null,'%s','%s','pending')
        """%(username,password)
        
        lid = insert(obj)
        print(lid,'lid is ')
        
        srk = """
                insert into teacher values(null,'%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','pending')
            """%(lid,first_name,last_name,dob,gender,place,path,email,phone,path1)

        insert(srk)
      
        return """<script>alert("REGISTRATION SUCCESS :)");window.location='/login'</script>"""
    return render_template('Teacher_Registration.html')