import os
import uuid
from flask import *
from database import *
admin = Blueprint('admin',__name__)




@admin.route('/admin_home')
def admin_home():
    
    data={}
    
    
    
    
    data['count'] = select("SELECT COUNT(reply) FROM complaint WHERE reply='pending'")[0]['COUNT(reply)'];    
    data['studcount'] = select("SELECT COUNT(*) FROM student ")[0]['COUNT(*)'];    
    data['tcount'] = select("SELECT COUNT(*) FROM teacher ")[0]['COUNT(*)'];    
    data['decount'] = select("SELECT COUNT(*) FROM department ")[0]['COUNT(*)'];    
    data['ccount'] = select("SELECT COUNT(*) FROM course ")[0]['COUNT(*)'];    
    data['accepted_count'] = select("SELECT COUNT(*) FROM teacher WHERE status = 'approve'")[0]['COUNT(*)']
    data['rejected_count'] = select("SELECT COUNT(*) FROM teacher WHERE status = 'rejected'")[0]['COUNT(*)']
    
    
    
    data['feed'] = select("""SELECT * FROM feedback 
                            INNER JOIN parent USING(parent_id)
                            INNER JOIN student USING(parent_id)""")
    
    data['teach'] = select("select * from teacher")
    
    
    

    return render_template('admin_home.html',data=data)



@admin.route('/admin_manage_department',methods=['get','post'])
def admin_manage_department():
    data={}
    rev = "select * from department"
    data['dept'] = select(rev)
    
    if 'submit' in request.form:
        dept = request.form['dept']
        dept = dept.replace("'","''")
        obj = "insert into department values(null,'%s')"%(dept)
        insert(obj)
        return redirect(url_for('admin.admin_manage_department'))
    
    if 'action' in request.args:
        action=  request.args['action']
        id=  request.args['id']
        
    else:
        action =None
    if action == "Update":
        rev = "select * from department where dept_id = '%s'"%(id)
        data['up'] = select(rev)
        
    if 'update' in request.form:
        dept = request.form['dept']
        dept = dept.replace("'","''")
        obj = "update department set department_name = '%s' where dept_id = '%s'"%(dept,id)
        update(obj)
        return redirect(url_for('admin.admin_manage_department'))
    
    if action=='delete':
        obj = "delete from department where dept_id = '%s'"%(id)
        
        delete(obj)
        return redirect(url_for('admin.admin_manage_department'))
        
    
        
        
    return render_template('admin_manage_department.html',data=data)


@admin.route('/admin_course_manage', methods=['get', 'post'])
def admin_course_manage():
    data = {}
    did = request.args.get('id')  # Safely get 'id' from request args
    data['course'] = select("select * from course")
    
    if 'submit' in request.form:
        course = request.form['course']
        course = course.replace("'", "''")
        obj = "insert into course values(null, '%s', '%s')" % (did, course)
        insert(obj)
        return redirect(url_for('admin.admin_course_manage', id=did))  # Use id instead of did

    action = request.args.get('action')  # Safely get 'action' from request args
    id = request.args.get('id')  # Safely get 'id' from request args

    if action == "Update":
        rev = "select * from course where course_id = '%s'" % (id)
        data['up'] = select(rev)

    if 'update' in request.form:
        course = request.form['course']
        course = course.replace("'", "''")
        obj = "update course set course_name = '%s' where course_id = '%s'" % (course, id)
        update(obj)
        return redirect(url_for('admin.admin_course_manage', id=did))  # Use id instead of did

    if action == 'delete':
        obj = "delete from course where course_id = '%s'" % (id)
        delete(obj)
        return redirect(url_for('admin.admin_course_manage', id=did))  # Use id instead of did

    return render_template('admin_course_manage.html', data=data)




@admin.route('/admin_manage_subject', methods=['get', 'post'])
def admin_manage_subject():
    data = {}
    did = request.args.get('id')  # Safely get 'id' from request args
    data['subject'] = select("select * from subject where course_id='%s'"%(did))
    
    if 'submit' in request.form:
        subject = request.form['subject']
        subject = subject.replace("'","''")
        obj = "insert into subject values(null, '%s', '%s')" % (did, subject)
        insert(obj)
        return redirect(url_for('admin.admin_manage_subject', id=did))  # Use id instead of did

    action = request.args.get('action')  # Safely get 'action' from request args
    ids = request.args.get('ids')  # Safely get 'id' from request args

    if action == "Update":
        rev = "select * from subject where subject_id = '%s'" % (ids)
        data['up'] = select(rev)

    if 'update' in request.form:
        subject = request.form['subject']
        subject = subject.replace("'","''")
        obj = "update subject set subject_name = '%s' where subject_id = '%s'" % (subject, ids)
        update(obj)
        return redirect(url_for('admin.admin_home'))  # Use id instead of did

    if action == 'delete':
        obj = "delete from subject where subject_id = '%s'" % (ids)
        delete(obj)
        return redirect(url_for('admin.admin_manage_subject', id=did))  # Use id instead of did

    return render_template('admin_manage_subject.html', data=data)




@admin.route('/admin_view_teacher', methods=['GET', 'POST'])
def admin_view_teacher():
    data = {}
    data['teacher'] = select("SELECT * FROM teacher")

    if 'action' in request.args:
        action = request.args['action']
        lid = request.args['lid']
    else:
        action = None

    if action == 'accept':
        update("UPDATE login SET usertype='teacher' WHERE login_id='%s'" % (lid))
        update("UPDATE teacher SET status='approve' WHERE login_id='%s'" % (lid))
        return redirect(url_for('admin.admin_view_teacher'))  # Fixed here

    if action == 'reject':
        delete("DELETE FROM login WHERE login_id='%s'" % (lid))
        update("UPDATE teacher SET status='rejected' WHERE login_id='%s'" % (lid))
        return redirect(url_for('admin.admin_view_teacher'))  # Fixed here

    data['sub'] = select("SELECT * FROM subject")

    if 'assign' in request.form:
        teacher_id = request.form['teacher_id']
        subject_id = request.form['subject']

        # Check if the subject is already assigned to the teacher
        existing_assignment = select("SELECT * FROM assign_sub WHERE teacher_id='%s' AND subject_id='%s'" % (teacher_id, subject_id))
        
        if existing_assignment:
            # Render template with alert and option to confirm duplicate assignment
            data['alert'] = "This subject is already assigned to this teacher. Do you want to add it again?"
            data['confirm_duplicate'] = True
            data['teacher_id'] = teacher_id
            data['subject_id'] = subject_id
        else:
            # No existing assignment; proceed with insertion
            insert("INSERT INTO assign_sub VALUES (NULL, '%s', '%s')" % (teacher_id, subject_id))
            return redirect(url_for('admin.admin_view_teacher'))  # Fixed here

    if 'confirm_duplicate' in request.form:
        # Process confirmed duplicate insertion
        teacher_id = request.form['teacher_id']
        subject_id = request.form['subject_id']
        insert("INSERT INTO assign_sub VALUES (NULL, '%s', '%s')" % (teacher_id, subject_id))
        return redirect(url_for('admin.admin_view_teacher'))  # Fixed here
    
    # data['assigned_subjects'] = select(("select * from assign_sub where teacher_id='%s'"%(teacher_id)))


    return render_template('admin_view_teacher.html', data=data)


@admin.route('/admin_view_stud')
def admin_view_stud():
    data={}
    data['stud'] = select('select * from student inner join course using(course_id)')
    return render_template("admin_view_stud.html",data=data)


@admin.route('/admin_view_exam')
def admin_view_exam():
    data={}
    data['exam'] = select('select * from exam inner join teacher using(teacher_id)')
    return render_template("admin_view_exam.html",data=data)


@admin.route('/admin_view_participants')
def admin_view_participants():
    
    data={}
    ex_id=request.args['id']
    data['part'] = select("""SELECT * 
        FROM `participants`
        INNER JOIN student USING(student_id)
        INNER JOIN course USING(course_id)
        INNER JOIN exam USING(exam_id) 
        WHERE exam_id = %s"""%(ex_id))
    
    

    if 'action' in request.args:
        act=request.args['action']
        ex_id=request.args['id']
        sid=request.args['sid']
        
    else:
        act=None
        
    if act =='downlaod':
        s=select("select * from report where student_id='%s' and  exam_id='%s'"%(sid,ex_id))
        print(s,'/////////////////////////////')
        if s:
           
            return send_file(s[0]['file'], as_attachment=True)
           
        else:
            flash('There is no report yet :)')
            return redirect(url_for('admin.admin_view_participants',id=ex_id))

    return render_template("admin_view_participants.html",data=data)





@admin.route('/admin_complaint_send_reply',methods=['post','get'])
def admin_complaint_send_reply():
    data={}
    data['comp']=select("select * from complaint inner join student using(student_id)")
    
    if 'sub' in request.form:
        id=request.form['id']
        reply=request.form['reply']
        
        update("update complaint set reply='%s' where complaint_id='%s'"%(reply,id))
        flash('Success !')
        return redirect(url_for('admin.admin_complaint_send_reply'))
    
    return render_template('admin_complaint_send_reply.html',data=data)
