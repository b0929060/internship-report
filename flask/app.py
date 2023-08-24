from flask import Flask,render_template,redirect,url_for,request, session
import pymysql,os,pathlib,time,re
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config['SECRET_KEY']='dd06be55a06c03312b2ab109b5f8f6ab'


db = pymysql.connect(host="localhost", port=3306,user= "root",password="12345678", database="practice")
cursor = db.cursor()

SRC_PATH =  pathlib.Path(__file__).parent.absolute()
UPLOAD_FOLDER_IMG = os.path.join(SRC_PATH,  'static', 'img')
UPLOAD_FOLDER_VIDEO= os.path.join(SRC_PATH,  'static', 'video')

@app.route('/')
def root():
    return redirect(url_for('course'))

@app.route('/online_course')
def course():
    select_course = 'SELECT * FROM `course` ORDER BY `course`.`time` DESC;'
    cursor.execute(select_course)
    course_data = cursor.fetchall()
    length=len(course_data)
    
    return render_template('course.html',course_data=course_data,length=length)

@app.route('/register')
def on_register():
    return render_template('register.html')
@app.route('/register/data',methods=['POST'])
def reg():
    if request.method=='POST':
        name=request.form['user_name']
        email=request.form['email']
        password=request.form['passwd']
        insert_user_sql = 'INSERT INTO `user_info`(`user_id`, `user_name`, `user_accout`, `user_password`) VALUES ("", "%s", "%s", "%s");' % (name, email,password)
        cursor.execute(insert_user_sql)
        db.commit()
        return redirect('/login')
@app.route('/login')
def login():
    msg = ''
    return render_template('login.html',msg = msg)
@app.route('/login/data', methods =['GET', 'POST'])
def logincheck():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        select_user_sql = 'SELECT * FROM `user_info` WHERE user_name = "%s" AND user_password = "%s";'% (username,password)
        cursor.execute(select_user_sql)
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account[0]
            session['username'] = account[1]
            if account[1]=='csie54':
                return redirect(url_for('upload'))
            return redirect(url_for('course'))
        else:
            msg = '帳號或密碼錯誤!'
    return render_template('login.html', msg = msg)
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/online_course/course_detail',methods=['POST'])
def course_detail():
    if request.method=='POST':
        course_id=request.form['alink']
        select_course_chap = 'SELECT chapter FROM `chapters` WHERE `course_id`="%s" ORDER BY `chapters`.`time` ASC;'% (course_id)
        cursor.execute(select_course_chap)
        course_chap = cursor.fetchall()
        select_course_units = 'SELECT `chapter`,`unit`,`video_addr` FROM `units` WHERE `course_id`="%s";'% (course_id)
        cursor.execute(select_course_units)
        course_units = cursor.fetchall()
        chap_length=len(course_chap)
        return render_template('detail.html',course_chap=course_chap,course_units=course_units,chap_length=chap_length)
    
@app.route('/upload')
def upload():
    if session:
        if session['username']=='csie54':
            return render_template('upload.html')
        else:
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))
@app.route('/upload/data',methods=['POST'])
def upload_data():
    i=1
    course_id=str(time.time()).replace('.','')
    print(course_id)
    course_name=request.form['course_name']
    img_file = request.files['poster']
    format=img_file.filename[img_file.filename.index('.'):]
    if img_file.filename != '':
        img_file.save(os.path.join(UPLOAD_FOLDER_IMG, str(course_name)+str(format)))
        poster_path="img/"+str(course_name)+str(format)
        insert_course_sql = 'INSERT INTO `course`(`course_id`, `course_name`, `course_poster`, `course_like`,`time`) VALUES ("%s","%s","%s","",current_timestamp(3));' % (course_id,course_name,poster_path)
        cursor.execute(insert_course_sql)
        db.commit()
    while (True):
        chap_check="chapter_"+str(i)
        if chap_check in request.form:
            chap="章節"+str(i)+"  "+request.form[chap_check]
            insert_chap_sql = 'INSERT INTO `chapters`(`course_id`, `chapter`, `time`) VALUES ("%s","%s", current_timestamp(3));' % (course_id,chap)
            cursor.execute(insert_chap_sql)
            db.commit()
            j=1
            while (True):
                if 'chapter_'+str(i)+'_unit_'+str(j) in request.form:
                    unit="單元"+str(j)+"  "+request.form['chapter_'+str(i)+'_unit_'+str(j)]
                    video_file=request.files['chap_'+str(i)+'_unit_'+str(j)+'_video']
                    new_name=str(course_name)+"chapter_"+str(i)+"_unit_"+str(j)
                    video_format=video_file.filename[video_file.filename.index('.'):]
                    video_file.save(os.path.join(UPLOAD_FOLDER_VIDEO,new_name+str(video_format)))
                    video_file_addr="video/"+new_name+str(video_format)
                    insert_unit_sql = 'INSERT INTO `units`(`course_id`, `chapter`, `unit`, `video_addr`) VALUES ("%s","%s","%s","%s");' % (course_id,chap,unit,video_file_addr)
                    cursor.execute(insert_unit_sql)
                    db.commit()
                    j=j+1
                else:
                    break     
            i=i+1   
        else:
            break

    return redirect(url_for('upload'))

if __name__=='__main__':
    app.run(host='0.0.0.0')


    cursor.close()
    db.close()

# @app.route('/')
# def lesson():,course_units=course_units
#     return