from flask import Blueprint, render_template, redirect,request,flash,url_for
from db import db
from .models import Users,session
from .forms import Login_Form,Register_Form,Edit_User_Form,Add_User_Form
from .report import report
import hashlib
from flask_paginate import Pagination,get_page_parameter
from flask_login import login_user, logout_user, login_required, \
    current_user


#https://github.com/miguelgrinberg/flasky/
user = Blueprint('user',__name__)

@user.route('/login',methods=['GET','POST'])  #首页登录跳转
def login():
    if request.method == 'GET':
        form = Login_Form()
    if request.method == 'POST':
        form = Login_Form(request.form)
        if form.validate_on_submit():
            participant_name = form.participant_name.data
            pwd = form.pwd.data
            pwd = hashlib.md5(pwd.encode(encoding='utf-8')).hexdigest()
            # print(participant_name)
            # print(pwd)
            user = Users.query.filter_by(participant_name=participant_name).one()
            if user is not None and user.pwd == pwd:
                print(url_for("report.add"))
                flash("登录成功")
                next = request.args.get('next')
                if next is None or not next.startswith('/'):
                    next = url_for('report.add')
                return redirect(next)
                # return redirect(url_for('report.add'))
            else:
                flash("用户名或密码不正确")
    return render_template('index.html', form=form)


@user.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'GET':
        form = Register_Form()
    if request.method == 'POST':
        form = Register_Form(request.form)
        if form.validate_on_submit():
            flash("注册成功,请去登录界面登录")
            return redirect(url_for('user.index'))


    return render_template("register.html", form=form)


@user.route('/list',methods=['GET','POST'])
def list():
    PER_PAGE = 10 #每页项目报告数量
    total = session.query(Users).count() #获取项目总数
    page = request.args.get(get_page_parameter(),type=int,default=1) # 获取页码，默认第一页
    start = (page-1)*PER_PAGE #每一页开始的位置
    end = start+PER_PAGE #每一页结束的位置
    pagination = Pagination(bs_version=3,page=page,total=total)
    users = session.query(Users).slice(start,end)

    context = {'pagination':pagination,
               'users':users}

    return render_template('user_list.html',**context)

@user.route('/edit/<participant_id>',methods=['GET','POST'])
def edit(participant_id):
    form = Edit_User_Form()
    user = Users.getUserById(participant_id)

    if form.validate_on_submit():
        user.participant_name = form.participant_namee.data
        user.telephone = form.telephone.data
        session.add(user)
        try:
            session.commit()
        except Exception as e:
            flash("更新失败")
        flash("更新成功")
        return render_template('302.html')
    form.participant_id.data = user.participant_id
    form.participant_name.data = user.participant_name
    form.telephone.data = user.telephone

    return render_template('user_edit.html',form=form)

@user.route('/delete/<participant_id>',methods=['GET','POST'])
def delete(participant_id):
    user = Users.getUserById(participant_id)
    try:
        session.delete(user)
        session.commit()
        flash("删除成功")
    except Exception as e:
        flash("删除失败")

    return render_template('302.html')


@user.route("/add",methods=['GET','POST'])
def add():
    form = Add_User_Form()
    if form.validate_on_submit():
        participant_name = form.participant_name.data
        telephone = form.telephone.data
        user = Users(participant_name,telephone)
        try:
            session.add(user)
            session.commit()
            flash("新增成功")
        except Exception as e:
            flash("新增失败")
        return render_template("302.html")

    return render_template("user_add.html",form=form)


@user.route('/search',methods=['GET','POST'])
def search():
    search = request.args.get('search')
    print(search)
    # return make_response(search)
    PER_PAGE = 10  # 每页项目报告数量
    total = Users.search(search).count()  # 获取项目总数
    print(total)
    page = request.args.get(get_page_parameter(), type=int, default=1)  # 获取页码，默认第一页
    start = (page - 1) * PER_PAGE  # 每一页开始的位置
    end = start + PER_PAGE  # 每一页结束的位置
    pagination = Pagination(bs_version=3, page=page, total=total)
    users = Users.search(search).slice(start, end)

    context = {'pagination': pagination,
               'users': users}

    return render_template('user_list.html', **context)