from flask import Blueprint, render_template, redirect,request,flash,url_for,jsonify,send_from_directory,make_response
from sqlalchemy import Column, Integer, String,ForeignKey,Table,Date,func
from .models import Users,Project,Sys,session,Vuln,Detail
from .forms import Login_Form,Register_Form,Add_Report_Form,Edit_Vuln_Form,Add_Vuln_Form
from flask_login import login_required
from flask_paginate import Pagination,get_page_parameter
import json
import os
import time

vuln = Blueprint('vuln',__name__)

@vuln.route('/list',methods=['GET'])
def list():
    PER_PAGE = 10 #每页项目报告数量
    total = session.query(Vuln).count() #获取项目总数
    page = request.args.get(get_page_parameter(),type=int,default=1) # 获取页码，默认第一页
    start = (page-1)*PER_PAGE #每一页开始的位置
    end = start+PER_PAGE #每一页结束的位置
    pagination = Pagination(bs_version=3,page=page,total=total)
    vulns = session.query(Vuln).slice(start,end)

    context = {'pagination':pagination,
               'vulns':vulns}

    return render_template('vuln_list.html',**context)


@vuln.route('/edit/<vul_id>',methods=['GET','POST'])
def edit(vul_id):
    form = Edit_Vuln_Form()
    vul = Vuln.getVulById(vul_id)

    if form.validate_on_submit():
        vul.vul_name = form.vul_name.data
        vul.vul_level = form.vul_level.data
        vul.vul_description = form.vul_description.data
        vul.vul_suggest = form.vul_suggest.data
        vul.vul_link = form.vul_link.data
        session.add(vul)
        try:
            session.commit()
        except Exception as e:
            flash("更新失败")
        flash("更新成功")
        return render_template('302.html')
    form.vul_id.data = vul_id
    form.vul_name.data = vul.vul_name
    form.vul_level.data = vul.vul_level
    form.vul_description.data = vul.vul_description
    form.vul_suggest.data = vul.vul_suggest
    form.vul_link.data = vul.vul_link

    return render_template('vuln_edit.html',form=form)

@vuln.route('/delete/<vul_id>',methods=['GET','POST'])
def delete(vul_id):
    vul = Vuln.getVulById(vul_id)
    try:
        session.delete(vul)
        session.commit()
        flash("删除成功")
    except Exception as e:
        flash("删除失败")

    return render_template('302.html')


@vuln.route("/add",methods=['GET','POST'])
def add():
    form = Add_Vuln_Form()
    if form.validate_on_submit():
        vul_name = form.vul_name.data
        vul_level = form.vul_level.data
        vul_description = form.vul_description.data
        vul_suggest = form.vul_suggest.data
        vul_link = form.vul_link.data
        vul = Vuln(vul_name,vul_level,vul_description,vul_suggest,vul_link)
        try:
            session.add(vul)
            session.commit()
            flash("新增成功")
        except Exception as e:
            flash("新增失败")
        return render_template("302.html")

    return render_template("vuln_add.html",form=form)


@vuln.route('/search',methods=['GET','POST'])
def search():
    search = request.args.get('search')
    print(search)
    # return make_response(search)
    PER_PAGE = 10  # 每页项目报告数量
    total = Vuln.search(search).count()  # 获取项目总数
    print(total)
    page = request.args.get(get_page_parameter(), type=int, default=1)  # 获取页码，默认第一页
    start = (page - 1) * PER_PAGE  # 每一页开始的位置
    end = start + PER_PAGE  # 每一页结束的位置
    pagination = Pagination(bs_version=3, page=page, total=total)
    vulns = Vuln.search(search).slice(start, end)

    context = {'pagination': pagination,
                   'vulns': vulns,}

    return render_template('vuln_list.html', **context)