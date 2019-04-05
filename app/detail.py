from flask import Blueprint, render_template, redirect,request,flash,url_for,jsonify,send_from_directory,make_response
from sqlalchemy import Column, Integer, String,ForeignKey,Table,Date,func
from .models import Users,Project,Sys,session,Vuln,Detail
from .forms import Login_Form,Register_Form,Add_Report_Form,Edit_Vuln_Form,Add_Vuln_Form
from flask_login import login_required
from flask_paginate import Pagination,get_page_parameter
import json
import os
import time

detail = Blueprint('detail',__name__)


@detail.route('/list',methods=['GET','POST'])
def list():
    PER_PAGE = 10  # 每页项目报告数量
    total = session.query(Detail).count()  # 获取项目总数
    page = request.args.get(get_page_parameter(), type=int, default=1)  # 获取页码，默认第一页
    start = (page - 1) * PER_PAGE  # 每一页开始的位置
    end = start + PER_PAGE  # 每一页结束的位置
    pagination = Pagination(bs_version=3, page=page, total=total)
    details = session.query(Detail).slice(start, end)

    context = {'pagination': pagination,
               'details': details}

    return render_template('detail_list.html', **context)

@detail.route('/search',methods=['GET','POST'])
def search():
    search = request.args.get('search')
    print(search)
    PER_PAGE = 10  # 每页项目报告数量
    total = Detail.search(search).count()  # 获取项目总数
    page = request.args.get(get_page_parameter(), type=int, default=1)  # 获取页码，默认第一页
    start = (page - 1) * PER_PAGE  # 每一页开始的位置
    end = start + PER_PAGE  # 每一页结束的位置
    pagination = Pagination(bs_version=3, page=page, total=total)
    details = Detail.search(search).slice(start, end)

    context = {'pagination': pagination,
               'details': details}

    return render_template('detail_list.html', **context)

@detail.route('/view/<id>',methods=['GET','POST'])
def view(id):
    detail = Detail.getDetailById(id)
    return render_template("detail_view.html",detail=detail)

