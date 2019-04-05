# -*- coding: utf-8 -*-
# @Time    : 2017/8/1 14:46
# @File    : Form.py
"""
表单类
"""
from db import db
from wtforms import StringField, SubmitField, PasswordField,DateField,IntegerField,SelectField,SelectMultipleField,TextAreaField
from wtforms.validators import Required,data_required,email
from flask_ckeditor import CKEditorField
from flask_wtf import FlaskForm
from .models import Users,Vuln,Sys


# 登录表单
class Login_Form(FlaskForm):
    participant_name = StringField('participant_name', validators=[Required()])
    pwd = PasswordField('pwd', validators=[Required()])
    submit = SubmitField('Login in')


# 注册表单
class Register_Form(FlaskForm):
    name = StringField('name', validators=[Required()])
    pwd = PasswordField('pwd', validators=[Required()])
    email = StringField('email')
    submit = SubmitField('register')

#修改漏洞
class Edit_Vuln_Form(FlaskForm):
    vul_id = IntegerField('漏洞ID', render_kw={
        'hidden': 'hidden','class': 'form-control'
    }) #漏洞ID
    vul_name = StringField("漏洞名称",  validators=[Required()],render_kw={
        'class': 'form-control'
    })
    vul_level = StringField("漏洞程度", render_kw={
        'class': 'form-control'
    })
    vul_description = TextAreaField("漏洞描述", render_kw={
        'class': 'form-control'
    })
    vul_suggest = TextAreaField("漏洞修复", render_kw={
        'class': 'form-control'
    })
    vul_link = StringField("漏洞链接", render_kw={
        'class': 'form-control'
    })

    submit = SubmitField('提交', render_kw={
        'class': 'btn btn-primary'
    }, )


#增加漏洞
class Add_Vuln_Form(FlaskForm):
    vul_name = StringField("漏洞名称",  validators=[Required()],render_kw={
        'class': 'form-control'
    })
    vul_level = SelectField('漏洞程度',render_kw={
            'class': 'form-control'
        },choices=[
                    ("高危","高危"),("中危","中危"),("低危","低危"),("安全","安全")
                          ],
                       )
    vul_description = TextAreaField("漏洞描述", render_kw={
        'class': 'form-control'
    })
    vul_suggest = TextAreaField("漏洞修复", render_kw={
        'class': 'form-control'
    })
    vul_link = StringField("漏洞链接", render_kw={
        'class': 'form-control'
    })

    submit = SubmitField('提交', render_kw={
        'class': 'btn btn-primary'
    }, )


#添加报告
class Add_Report_Form(FlaskForm):
    project_id = IntegerField('项目id',render_kw={
        'type':'hidden'
    })
    project = StringField('项目名称',validators=[Required()],render_kw={
            'class': 'form-control'
        },)  #项目名称
    producer = SelectField(label='制作人',validators=[Required()],render_kw={
            'class': 'form-control'
        },
       choices=[
            (user.participant_name,user.participant_name) for user in Users.getUser()

        ],) #制作人，直接从登录用户获取，因此使用文本字段
    production_date = DateField('制作时间',validators=[Required()],render_kw={
            'class': 'form-control'
        },format='%Y/%m/%d') #制作时间
    participant = SelectField(label='参测者',
        render_kw={
            'class': 'selectpicker show-tick','multiple':1,'data-live-search':'true'
        },
        choices=[
            (user.participant_id,user.participant_name) for user in Users.getUser()

        ],
        ) #参与者姓名
    reviewer = StringField('复审人',validators=[Required()],render_kw={
            'class': 'form-control','value':"欧阳思裕",
        }) #复审人
    start_date = DateField('开始时间',validators=[Required()],render_kw={
            'class': 'form-control'
        },format='%Y/%m/%d') #开始时间

    work_time = StringField('工作量',validators=[Required()],render_kw={
            'class': 'form-control'
        })

    risk_level = SelectField('整体风险程度',render_kw={
            'class': 'form-control'
        },choices=[
                    ("高危","高危"),("中危","中危"),("低危","低危"),("安全","安全")
                          ],
                       )  #整体风险程度
    #漏洞数量一项无需计算，根据添加的数据自动计算
    total_num = IntegerField('总漏洞数',render_kw={
            'class': 'form-control'
        },) #总漏洞数量
    high_num = IntegerField('高危漏洞数',render_kw={
            'class': 'form-control',
        },)  #高危漏洞数量  无需填写自动计算
    mid_num = IntegerField('中危漏洞数',render_kw={
            'class': 'form-control'
        },) #中危数量
    low_num  = IntegerField('低危漏洞数',render_kw={
            'class': 'form-control'
        },) #低危漏洞数量
    #系统详情
    system_name = StringField('系统名称',render_kw={
            'class': 'form-control'
        },)  #系统名称
    system_url = StringField('系统url',render_kw={
            'class': 'form-control'
        },)  #系统url
    system_ip = StringField('系统IP',render_kw={
            'class': 'form-control'
        },)  #系统IP
    system_num = StringField('system_num') #系统数量
    #参与者
    # participant_id = IntegerField('participant_id') #参与者ID

    submit = SubmitField('一键生成报告',render_kw={
            'class': 'btn btn-primary'
        },)

    #漏洞详情
    vul_name = SelectField("漏洞名称",
        render_kw={
            'class': 'selectpicker show-tick','data-live-search':'true'
        },
        choices=[
            (vuln.vul_id,vuln.vul_name) for vuln in Vuln.getAllVul()
        ],)
    vul_level = StringField("漏洞级别", render_kw={
        'class': 'form-control'
    }, )

    systemed_id = SelectField("系统名称", render_kw={
            'class': 'form-control',
        },
        choices=[

        ], )

    system_url1 = StringField('漏洞URL', render_kw={
                                   'class': 'form-control'
                               },
                               )  # 系统名称 将上边添加的系统名称，直接单选过来

    vul_description = TextAreaField("漏洞描述",render_kw={
            'class': 'form-control'
        },)
    vul_suggest = TextAreaField("修复建议",render_kw={
            'class': 'form-control'
        },)
    vul_link = StringField("参考链接", render_kw={
        'class': 'form-control'
    }, )

    content = TextAreaField("漏洞详情")


#编辑用户
class Edit_User_Form(FlaskForm):
    participant_id = IntegerField('用户ID', render_kw={
        'hidden': 'hidden','class': 'form-control'
    }) #用户ID
    participant_name = StringField("用户名称",  validators=[Required()],render_kw={
        'class': 'form-control'
    })
    telephone = StringField("联系方式", render_kw={
        'class': 'form-control'
    })
    submit = SubmitField('提交', render_kw={
        'class': 'btn btn-primary'
    }, )


#增加用户
class Add_User_Form(FlaskForm):
    participant_name = StringField("用户名称",  validators=[Required()],render_kw={
        'class': 'form-control'
    })
    telephone = StringField("联系方式", render_kw={
        'class': 'form-control'
    })
    submit = SubmitField('提交', render_kw={
        'class': 'btn btn-primary'
    }, )