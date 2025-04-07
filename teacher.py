import uuid
from flask import *
from database import *
teacher = Blueprint('teacher',__name__)




@teacher.route('/teacher_home')
def teacher_home():
    return render_template('teacher_home.html')



# view Exams

@teacher.route('/teacher_view_exams')
def teacher_view_exams():
    data={}
    data['exms'] = select("select * from exam  where teacher_id='%s'"%(session['tid']))
    
    return render_template('teacher_view_exams.html',data=data)


# data['less'] = select("""SELECT * FROM exam 
    # INNER JOIN teacher USING(teacher_id)
    # INNER JOIN assign_sub USING(teacher_id)
    # INNER JOIN SUBJECT USING(subject_id) WHERE exam_id='%s'"""%exm_id)


from bert import *

@teacher.route('/teacher_add_lessons',methods=['get','post'])
def teacher_add_lessons():
    data={}
    exm_id=request.args['id']
    data['exam_id']=exm_id
    data['sel'] = select("""SELECT * 
FROM lessons 
INNER JOIN exam ON lessons.exam_id = exam.exam_id
INNER JOIN teacher ON lessons.teacher_id = teacher.teacher_id
WHERE teacher.teacher_id ='%s'"""%(session['tid']))
    print(data['sel'])
    
    if 'submit' in request.form:
        pdf=request.files['pdf']
        name=request.form['name']
        
        path = "static/pdf/"+str(uuid.uuid4())+pdf.filename
        pdf.save(path)
        
        insert("insert into lessons values(null,'%s','%s','%s','%s',curdate())"%(exm_id,session['tid'],name,path))
        
        flash('Inserted :!')
        return redirect(url_for('teacher.teacher_add_lessons',id=exm_id))     
        
            
         
        # question = upload_pdf(path)
        # print("Full Question Dictionary:")
        
        # insert("insert into question values(null,'%s','%s','%s','%s','%s','%s','%s')"%
        #        (lesson_id,question['question'], question['correct_answer'],question['options'].get('a'),question['options'].get('b'),question['options'].get('c'),
        #         question['options'].get('d')
        #         ))
        
        
       
        # if 'options' in question:
        #     print("Option A:", question['options'].get('a'))
        #     print("Option B:", question['options'].get('b'))
        #     print("Option C:", question['options'].get('c'))
        #     print("Option D:", question['options'].get('d'))
        # if 'correct_answer' in question:
        #     print("Correct Answer:", question['correct_answer'])
            
    if 'action'in request.args:
        action=request.args['action']
        less_id=request.args['lid']
        
    else:
        action=None
        
    if action == 'delete':
        delete("delete from lessons where lesson_id='%s'"%(less_id))
        
    
        flash('delete successfully')
        return redirect(url_for('teacher.teacher_add_lessons',id=exm_id))      


    

    
    return render_template('teacher_add_lessons.html',data=data)


@teacher.route('/teacher_view_result')
def teacher_view_result():
    data={}
    les_id = request.args['lid']
    
    print(les_id,'///////////////////////////')
    
    obj=select("select * from mark inner join student using(student_id) where lesson_id='%s' group by student_id"%(les_id))
    data['result']=obj
    return render_template('teacher_view_result.html',data=data)
    