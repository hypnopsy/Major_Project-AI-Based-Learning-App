import uuid
from flask import *
# from bert import upload_pdf
from bert import upload_pdf
from database import *
api = Blueprint('api',__name__)




@api.route('/api/applogin')
def applogin():
    data={}
    username=request.args["uname"]
    password=request.args["password"]
          
    qry="select * from login where username='%s' and password='%s'"%(username,password)
    res=select(qry)
    
    print(res,'///////////////////////////////////////////////////')
    
    if res:
        data['status']='success'
        data['data']=res
    else:
        data['status']='failed'
        
    return str(data) 



@api.route('/api/appregister')
def appregister():
    data={}
    
    fname = request.args['fname']
    lname = request.args['lname']
    place = request.args['place']
    phone = request.args['phone']
    email = request.args['email']
    uname = request.args['uname']
    psd = request.args['psd']
    
    
    kp = "insert into login values(null,'%s','%s','parent')"%(uname,psd)
    
    lid = insert(kp)
    
    
    obj = "insert into parent values(null,'%s','%s','%s','%s','%s','%s')"%(lid,fname,lname,place,phone,email)
    
    res = insert(obj)
    
    if res:
        data['status']='success'
        data['data']=res
    else:
        data['status']='failed'
        
    return str(data)
        
@api.route('/api/viewcourse')
def viewcourse():
    data = {}
    qry = "select * from course"
    res = select(qry)
    if res:
        data['status']='success'
        data['data']=res
    else:
        data['status'] = "failed"
        
    return str(data)

@api.route("/api/manage_student",methods=['get','post'])
def manage_student():
    data = {}
    
    image1=request.files['image']
    path = "static/students/"+str(uuid.uuid4())+image1.filename
    image1.save(path)
    lid=request.form['log_id']
    fname=request.form['fname']
    lname=request.form['lname']
    c_id=request.form['course_id']
    dob=request.form['dob']
    gender=request.form['gender']
    phn=request.form['phone']
    email=request.form['email']
    uname=request.form['username']
    pass1=request.form['password']
    
    
    ll=insert("insert into login values(null,'%s','%s','student')"%(uname,pass1))
    
    
    lp="insert into student values(null,'%s',(select parent_id from parent where login_id='%s'),'%s','%s','%s','%s','%s','%s','%s','%s')\
        "%(ll,lid,c_id,fname,lname,dob,gender,email,phn,path)
        
    res = insert(lp)
    
    if res:
        data['status']='insertsuccess'
        # data['data']=res
    else:
        data['status'] = 'failed'
        
    return str(data)



        
@api.route('/api/view_students')
def view_students():
    data = {}
    
    lid=request.args['login']
    
    qry = """SELECT 
    CONCAT(student.fname, ' ', student.lname) AS student_name,
    student.email AS student_email, 
    student.phone AS student_phone, 
    course.course_name, 
    student.*, 
    course.*, 
    parent.*,
    department.*
FROM student
INNER JOIN course USING(course_id)
INNER JOIN department USING(dept_id)
INNER JOIN parent USING(parent_id)
WHERE parent.parent_id =(select parent_id from parent where login_id='%s')"""%(lid)
    res = select(qry)
    if res:
        data['status']='success'
        data['data']=res
    else:
        data['status'] = "failed"
        
    return str(data)


@api.route('/api/delete_stud')
def delete_stud():
    data={}
    stud_id=request.args['stud_id']
    
    obj=delete("delete from student where student_id='%s'"%(stud_id))
    
    if obj:
        data['status']='success'
    else:
        data['status'] ='failed'
        
    return str(data)



@api.route('/api/addfeedback')
def addfeedback():
    data={}
    desc=request.args['desc']
    login_id=request.args['login_id']
    
    
    obj=insert("insert into feedback values(null,'%s',now(),(select parent_id from parent where login_id='%s'))"%(desc,login_id))
    
    if obj:
        data['status']='success'
    else:
        data['status'] ='failed'
        
    return str(data)



@api.route('/api/parent_view_feedback')
def parent_view_feedback():
    data={}
    login_id=request.args['login']
    
    
    obj = select("select * from feedback where parent_id=(select parent_id from parent where login_id='%s')"%(login_id))
    
    if obj:
        data['status']='success'
        data['data'] = obj
    else:
        data['status'] ='failed'
        
    return str(data)




@api.route('/api/student_view_sub')
def student_view_sub():
    data={}
    
    
    obj=select("select * from subject inner join course using(course_id)")
    
    if obj:
        data['status']='success'
        data['data'] = obj
    else:
        data['status'] ='failed'
        
    return str(data)


@api.route('/api/student_view_exm_details')
def student_view_exm_details():
    data={}
    sub_id=request.args['sub_id']
    print(sub_id,'......................')
    
    obj=select("""
SELECT * FROM `exam` INNER JOIN 
`teacher` USING(teacher_id)
INNER JOIN `assign_sub` USING(teacher_id)
INNER JOIN `lessons` USING(exam_id)
WHERE subject_id='%s'"""%(sub_id))


   
    
    if obj:
        data['status']='success'
        data['data'] = obj
    else:
        data['status'] ='failed'
        
    return str(data)


@api.route('/api/generate_question',methods=['get','post'])
def generate_question():
    data={}
    pdf = request.args['pdf']
    leid = request.args['leid']
    lid = request.args['lid']

    print(lid,'/////////////////////')

    questions = upload_pdf(pdf)

    print("question =====>>",questions)

    
    for question in  questions:
        q=question['question'].replace("'", "")
        # print("",q)
        a=question['options'].get('a').replace("'", "")
        b=question['options'].get('b').replace("'", "")
        c=question['options'].get('c').replace("'", "")
        d=question['options'].get('d').replace("'", "")
        cans=question['correct_answer'].replace("'", "")

        if cans =="a":
            obj=insert("insert into question values(null,'%s','%s',(select student_id from student where login_id='%s'))"%(leid,q,lid))
            insert("insert into options values(null,'%s','%s','yes')"%(obj,a))
            insert("insert into options values(null,'%s','%s','no')"%(obj,b))
            insert("insert into options values(null,'%s','%s','no')"%(obj,c))
            insert("insert into options values(null,'%s','%s','no')"%(obj,d))
        if cans =="b":
            obj=insert("insert into question values(null,'%s','%s',(select student_id from student where login_id='%s'))"%(leid,q,lid))
            insert("insert into options values(null,'%s','%s','no')"%(obj,a))
            insert("insert into options values(null,'%s','%s','yes')"%(obj,b))
            insert("insert into options values(null,'%s','%s','no')"%(obj,c))
            insert("insert into options values(null,'%s','%s','no')"%(obj,d))
        if cans =="c":
            obj=insert("insert into question values(null,'%s','%s',(select student_id from student where login_id='%s'))"%(leid,q,lid))
            insert("insert into options values(null,'%s','%s','no')"%(obj,a))
            insert("insert into options values(null,'%s','%s','no')"%(obj,b))
            insert("insert into options values(null,'%s','%s','yes')"%(obj,c))
            insert("insert into options values(null,'%s','%s','no')"%(obj,d))
        if cans =="d":
            obj=insert("insert into question values(null,'%s','%s',(select student_id from student where login_id='%s'))"%(leid,q,lid))
            insert("insert into options values(null,'%s','%s','no')"%(obj,a))
            insert("insert into options values(null,'%s','%s','no')"%(obj,b))
            insert("insert into options values(null,'%s','%s','no')"%(obj,c))
            insert("insert into options values(null,'%s','%s','yes')"%(obj,d))


    if obj :
        data['status'] = "success"

    else:
        data['status'] = "failed"
    return str(data)





@api.route('/api/View_questions',methods=['get','post'])
def View_questions():
    data={}
    leid=request.args['leid']

    obj=select("""
SELECT  
    q.q_id, 
    q.lesson_id, 
    q.question, 
    a.option_id, 
    a.options
FROM 
    question q
LEFT JOIN 
    OPTIONS a 
ON 
    q.q_id = a.q_id
WHERE 
    q.lesson_id = %s;
"""%(leid))
    
    if obj:
        data['status'] = "success"
    else:
        data['status'] = "failed"

    data['method'] = "view_questions"

    return str(data)




@api.route('/api/Start_exam')
def Start_exam():

    data={}

    leid=request.args['leid']
    lid=request.args['lid']

    obj = select("""
       SELECT 
    q.q_id, 
    q.question, 
    q.student_id, 
    GROUP_CONCAT(CONCAT(o.options, ':', o.status) ORDER BY o.option_id SEPARATOR ',') AS OPTIONS
FROM 
    question AS q 
INNER JOIN 
    `OPTIONS` AS o 
ON 
    q.q_id = o.q_id 
WHERE 
    q.lesson_id = '%s' AND q.student_id = (SELECT student_id FROM student WHERE login_id='%s')
GROUP BY 
    q.q_id, q.question, q.student_id;

    

            """%(leid,lid))
    print(obj,'/////////////////////////')
    
    if obj:

        data['status'] = "success"
        data['data'] = obj
    else:

        data['status'] = "failed"

    return str(data)




@api.route('/api/VIew_lessons',methods=['get'])
def VIew_lessons():

    data={}

    sub_id=request.args['sub_id']

    obj = select("""

SELECT * FROM `exam` INNER JOIN 
`teacher` USING(teacher_id)
INNER JOIN `assign_sub` USING(teacher_id)
INNER JOIN `lessons` USING(exam_id)
WHERE subject_id='%s'"""%(sub_id))
    print(obj,'/////////////////////////')
    
    if obj: 
        data['status'] = "success"
        data['data'] = obj
    else:

        data['status'] = "failed"

    return str(data)



@api.route('/api/addmark',methods=['get'])
def addmark():
    data={}

    lessonid=request.args['lessonid']
    totalmarks=request.args['totalmarks']
    login_id=request.args['lid']
    total=request.args['total']
    totalm=int(total)*2

    print("lesson=>",lessonid)
    print("login_id=>",login_id)
    print("totalmarks=>",totalmarks)

    obj=insert("insert into mark values(null,'%s',(select student_id from student where login_id='%s'),'%s','%s')"%(lessonid,login_id,totalmarks,totalm))

    if obj:
        data['status'] = "mark_success"
    else:
        data['status'] ="markfailed"

    return str(data)






@api.route('/api/studcomplaint')
def studcomplaint():
    data={}
    desc=request.args['desc']
    login_id=request.args['login_id']
    
    
    obj=insert("insert into complaint values(null,(select student_id from student where login_id='%s'),'%s','pending',curdate())"%(login_id,desc))
    
    if obj:
        data['status']='success'
    else:
        data['status'] ='failed'
        
    return str(data)


@api.route('/api/student_view_result')
def student_view_result():
    data={}

    lid=request.args['lid']
    print(lid,'this is the login id')

    obj=select("""
               SELECT * FROM mark
INNER JOIN lessons USING(lesson_id)
 WHERE student_id=(SELECT student_id FROM student WHERE login_id='%s')"""%(lid))


    if obj:
        data['status'] = "success"

        data['data'] = obj

    else:
        data['status'] = "failed"


    return str(data)



@api.route('/api/checkingonce')
def checkingonce():
    data={}
    
    lesid=request.args['lesid']
    lid=request.args['lid']
    
    obj="select * from mark where lesson_id='%s' and student_id=(select student_id from student where login_id='%s')"%(lesid,lid)
    
    res=select(obj)
    
    if res:
        data['status']='check_success'
    else:
        data['status']='failed'
        
    return str(data)
        
    
    


@api.route('/api/Student_view_solutons')
def Student_view_solutons():
    data={}

    lid=request.args['lid']
    less_id=request.args['less_id']
    print(lid,'this is the login id')

    obj=select("""
              SELECT * 
FROM `question`
INNER JOIN `options` ON question.q_id = options.q_id
INNER JOIN `lessons` ON question.lesson_id = lessons.lesson_id
WHERE options.status = "yes"
AND question.student_id = (SELECT student_id FROM student WHERE login_id = '%s') 
AND lessons.title = "%s";"""%(lid,less_id))


    if obj:
        data['status'] = "success"

        data['data'] = obj

    else:
        data['status'] = "failed"


    return str(data)



@api.route('/api/parent_view_result')
def parent_view_result():
    data={}
    
   
    lid=request.args['lid']
    
    obj="""
SELECT * 
FROM `mark`
INNER JOIN `student` USING (student_id)
INNER JOIN `lessons` USING (lesson_id)
INNER JOIN `exam` USING (exam_id)
WHERE parent_id = (SELECT parent_id FROM parent WHERE login_id='%s');
"""%(lid)
    
    res=select(obj)
    
    if res:
        data['status']='check_success'
        data['data'] = res
    else:
        data['status']='failed'
        
    return str(data)
        
        
# @api.route('/api/view_comaplints')
# def view_comaplints():
#     data = {}
#     lid=request.args['login']
#     qry = "select * from complaints where student_id=(select student_id from student where login_id='%s') "%(lid)
#     res = select(qry)
#     if res:
#         data['status']='success'
#         data['data']=res
#     else:
#         data['status'] = "failed"
        
#     return str(data)




@api.route('/api/view_comaplints')
def view_comaplints():
    data = {}
    lid=request.args['login']
    qry = "select * from complaint where student_id=(select student_id from student where login_id='%s') "%(lid)
    res = select(qry)
    if res:
        data['status']='success'
        data['data']=res
    else:
        data['status'] = "failed"
        
    return str(data)