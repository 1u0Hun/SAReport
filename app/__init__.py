#encoding: utf-8
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask import request,Flask,render_template,flash, redirect,url_for,jsonify,make_response,send_from_directory
from flask_moment import Moment
from app.forms import Login_Form,Register_Form
from app.models import Users,Vuln,Project,session,Detail
from app import views,models
from .user import user
from .report import report
from .vuln import vuln
from .detail import detail
import os
import datetime
import random
from flask_ckeditor import upload_success,upload_fail,CKEditor

#from flask.ext.bootstrap import Bootstrap
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
bootstrap = Bootstrap(app)
moment=Moment(app)
ckeditor = CKEditor(app)
app.config['CKEDITOR_FILE_UPLOADER'] = 'upload'
app.config['UPLOADED_PATH'] = os.path.join(basedir, 'static/upload')
app.config['DOWNLOAD_PATH'] = os.path.join(basedir, 'static/download')
app.config.from_object('app.config.Config')
# db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.session_protection='strong'
login_manager.login_view = 'user.login'
login_manager.login_message = '未登录无访问权限'
login_manager.init_app(app)

app.register_blueprint(user,url_prefix='/user')
app.register_blueprint(report,url_prefix='/report')
app.register_blueprint(vuln,url_prefix='/vuln')
app.register_blueprint(detail,url_prefix='/detail')


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)


@app.route("/")
def index():
    return redirect(url_for("user.login"))

@app.route("/vuln/<vul_id>")
def vuln(vul_id):                                #根据vul_id查询对应漏洞的信息
    vuln = Vuln.getVulById(vul_id)
    vul = {'vul_level':vuln.vul_level,'vul_description':vuln.vul_description,
           'vul_suggest':vuln.vul_suggest,'vul_link':vuln.vul_link}
    return jsonify(vul)

@app.route("/detailed/<project_id>")
def showvuln(project_id):                                    #展示已经添加的漏洞
    details = Detail.getVulByProjectId(project_id)
    vuls = {}
    total_num = 0
    high_num = 0
    mid_num = 0
    low_num = 0
    j=0
    for detail in details:
        vul = Vuln.getVulById(detail.vul_id)
        if(vul.vul_level=="高危"):
            high_num += 1
            total_num += 1
        elif(vul.vul_level=="中危"):
            mid_num += 1
            total_num += 1
        elif(vul.vul_level=="低危"):
            low_num += 1
            total_num += 1

        vuls[j]={'vuled_name':vul.vul_name,'vuled_level':vul.vul_level,'sysed_url':detail.sys_url,'total_num':total_num,'high_num':high_num,
                 'mid_num':mid_num,'low_num':low_num}
        j+=1
    return jsonify(vuls)


@app.route("/sys/<project_id>",methods=['GET','POST'])
def showsys(project_id):
    if(project_id):
        project = Project.getProjectById(project_id)
        sys = {}
        j=0
        for i in project.sys:
            print(i.sys_url)
            sys[j] = {"sysed_id":i.sys_id,"sysed_name":i.sys_name,"sysed_url":i.sys_url,"sysed_ip":i.sys_ip}
            j+=1

    return jsonify(sys)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404



@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html')

@app.route("/test")    #测试用例
def test():
    return render_template("test.html")


@app.route('/files/<path:filename>')
def uploaded_files(filename):
    path = app.config['UPLOADED_PATH']
    return send_from_directory(path, filename)


def gen_rnd_filename():
    filename_prefix = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    return '%s%s' % (filename_prefix, str(random.randrange(1000, 10000)))
@app.route('/upload', methods=['POST'])
def upload():
    f = request.files.get('upload')  # 获取上传图片文件对象
    # Add more validations here
    extension = f.filename.split('.')[1].lower()
    if extension not in ['jpg', 'gif', 'png', 'jpeg']:  # 验证文件类型示例
        return upload_fail(message='Image only!')  # 返回upload_fail调用
    filename = '%s.%s'%(gen_rnd_filename(),extension)  #将原始文件名重命名，避免由于原文件名一直而覆盖
    f.save(os.path.join(app.config['UPLOADED_PATH'], filename))
    url = url_for('uploaded_files', filename=filename)
    return upload_success(url=url)  # 返回upload_success调用

@app.route("/download/<path:filename>",methods=['GET','POST'])
def download(filename):
    path = app.config['DOWNLOAD_PATH']
    return send_from_directory(path, filename,as_attachment=True)



@app.route('/tool',methods=['GET','POST'])
def tool():
    return render_template("tool.html")


@app.route('/know',methods=['GET','POST'])
def know():
    return render_template("know.html")