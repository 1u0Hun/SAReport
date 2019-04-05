from flask import Blueprint, render_template, redirect,request,flash,url_for,jsonify,send_from_directory,make_response
from sqlalchemy import Column, Integer, String,ForeignKey,Table,Date,func
from .models import Users,Project,Sys,session,Vuln,Detail
from .forms import Login_Form,Register_Form,Add_Report_Form
from flask_login import login_required
from flask_paginate import Pagination,get_page_parameter
import json
import os
from reporeter import repoter

basedir = os.path.abspath(os.path.dirname(__file__))


report = Blueprint('report',__name__)


@report.route("/add/",methods=['GET','POST'])
def add():
    if request.method == 'GET':
        form = Add_Report_Form()
        # return render_template('report_add.html',form=form)
    if request.method == 'POST':
        form = Add_Report_Form(request.form)
        # if form.validate_on_submit():
        project_id = form.project_id.data
        total_num = form.total_num.data
        high_num = form.high_num.data
        mid_num = form.mid_num.data
        low_num = form.low_num.data
        print(form.project_id.data)
        print(form.total_num.data)
        project = {"project_id":project_id}
        data = json.dumps(project)
        if(Project.updateNum(project_id,total_num,high_num,mid_num,low_num)):
            print("进入")
            path = os.path.join(basedir, 'static/download')
            filename = repoter(data)
            # return redirect(url_for('/download/'+filename))
            if(Project.updatePath(project_id,filename)):
                return send_from_directory(path, filename, as_attachment=True)
            # return redirect("http://www.baidu.com")
        else:
            return redirect("http://edr.sangfor.com.cn/")


    return render_template('report_add.html',form=form)


@report.route('/add_project',methods=['GET','POST'])
def add_project():
    data = request.get_json()
    project = Project(data['project'],data['producer'],data['production_date'],data['reviewer'],data['start_date'],data['risk_level'],data['work_time'])
    for i in data['participant']:
        # print(i)
        participant1 = Users.getUserById(i)
        project.participant.append(participant1)
    session.add(project)
    info = ""
    status = ""
    project_id = 1
    try:
        session.commit()
        info="项目创建成功"
        status = "OK"
        project_id = Project.getNewProjectId()
        print(project_id)
    except Exception as e:
        info = "项目名重复"
        status = "Error"

    session.rollback()
    return jsonify({'info':info,'status':status,'project_id':project_id})


@report.route("/add_system",methods=['GET','POST'])
def add_system():
    data = request.get_json()
    print(data['project_id'])
    print(data['system_name'])
    print(data['system_url'])
    print(data['system_ip'])
    project = Project.getProjectById(int(data['project_id']))
    print(project)
    system2 = Sys(sys_name=data['system_name'],sys_url=data['system_url'],sys_ip=data['system_ip'])
    project.sys.append(system2)
    session.add(project)
    info = ""
    status = ""
    try:
        session.commit()
        info = "添加成功"
        status = "OK"
    except:
        status = "Error"
        info = "添加失败"

    session.rollback()
    return jsonify({'info':info,'status':status})


@report.route('/add_vuln',methods=['GET','POST'])
def add_vuln():
    data = request.get_json()
    print(data['project_id'])
    print(data['vul_name'])
    print(data['systemed_id'])
    print(data['system_url1'])
    print(data['detail'])

    detail1 = Detail(project_id=data['project_id'],vul_id=data['vul_name'],sys_url=data['system_url1'],sys_id=data['systemed_id'],detail=data['detail'])
    detail1.updateName(data['project_id'],data['vul_name'],data['systemed_id'])
    session.add(detail1)
    info = ""
    status = ""
    try:
        session.commit()
        info = "添加成功"
        status = "OK"
    except:
        status = "Error"
        info = "添加失败"

    session.rollback()
    return jsonify({'info': info, 'status': status})


@report.route('/list',methods=['GET','POST'])
def list():
    PER_PAGE = 10 #每页项目报告数量
    total = session.query(Project).count() #获取项目总数
    page = request.args.get(get_page_parameter(),type=int,default=1) # 获取页码，默认第一页
    start = (page-1)*PER_PAGE #每一页开始的位置
    end = start+PER_PAGE #每一页结束的位置
    pagination = Pagination(bs_version=3,page=page,total=total)
    projects = session.query(Project).slice(start,end)

    context = {'pagination':pagination,
               'projects':projects}

    return render_template('report_list.html',**context)

@report.route('/search',methods=['GET','POST'])
def search():
    search = request.args.get('search')
    print(search)
    # return make_response(search)
    PER_PAGE = 10  # 每页项目报告数量
    total = Project.search(search).count()  # 获取项目总数
    page = request.args.get(get_page_parameter(), type=int, default=1)  # 获取页码，默认第一页
    print(total/PER_PAGE)
    start = (page - 1) * PER_PAGE  # 每一页开始的位置
    end = start + PER_PAGE  # 每一页结束的位置
    pagination = Pagination(bs_version=3, page=page, total=total)
    projects = Project.search(search).slice(start, end)

    context = {'pagination': pagination,
                   'projects': projects,}

    return render_template('report_list.html', **context)