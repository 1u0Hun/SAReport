# from db import db
import hashlib
from flask_login import UserMixin
from flask_ckeditor import CKEditorField
from sqlalchemy import Column, Integer, String,ForeignKey,Table,Date,func,or_
from sqlalchemy.orm import relationship,sessionmaker
# 调用基类Base
from sqlalchemy.ext.declarative import declarative_base
# 调用链接数据库
from sqlalchemy import create_engine

# encoding='utf-8' 链接字符集 ，echo=True 把所有信息打印出来
engine = create_engine("mysql+pymysql://root:toor@127.0.0.1/sangfor_report1",encoding='utf-8',max_overflow=0,pool_size=10,pool_timeout=600,pool_recycle=-1)
# 创建对象的基类:
Base = declarative_base()
# 创建DBSession类型:
DBSession = sessionmaker(bind=engine)
# 创建session对象:
session = DBSession()

#创建project与participant之间的关联表
project_participant = Table('project_participant',Base.metadata,
                            #创建外键 关联project下的id
                            Column('project_id',Integer,ForeignKey('project.project_id')),
                            #创建外键 关联participant下的id
                            Column('participant_id',Integer,ForeignKey('participant.participant_id')),
                            )

#创建project与sys之间的关联表
project_sys = Table('project_sys',Base.metadata,
                    #创建外键，关联project下的id
                    Column('project_id',Integer,ForeignKey('project.project_id')),
                    #创建外键，关联sys下的id
                    Column('sys_id',Integer,ForeignKey('system.sys_id')),
                    )


#创建project与vuln之间的关联表
# project_vuln = Table('project_vuln',Base.metadata,
#                     #主键
#                     Column('id',Integer,primary_key=True),
#                     #创建外键，关联project下的id
#                     Column('project_id',Integer,ForeignKey('project.project_id')),
#                     #创建外键，关联vuln下的id
#                     Column('vul_id',Integer,ForeignKey('vuln.vul_id')),
#                     #创建详情，漏洞详情
#                     Column('detail',String(2048)),
#                     #创建sys_url,存储具体漏洞详情url
#                     Column('sys_url',String(128)),
#                     )

#参与者用户
class Users(Base):
    __tablename__ = 'participant'  # 对应mysql数据库表
    participant_id = Column(Integer, primary_key=True,autoincrement=True)
    participant_name = Column(String(64), unique=True, index=True)
    pwd = Column(String(128))
    telephone = Column(String(11),index=True)
    avator = Column(String(64))

    def __init__(self,participant_name='',telephone=""):
        self.participant_name = participant_name
        self.telephone = telephone


    def __repr__(self):
        return '<User %r>' % self.participant_name

    def checklogin(participant_name,pwd):
        # print(participant_name)
        # print(pwd)
        try:
            user = session.query(Users).filter(Users.participant_name == participant_name).one()
            if user.pwd == hashlib.md5(pwd.encode(encoding='utf-8')).hexdigest():
                return True
            else:
                return False
        except Exception as e:
            raise e
            return False

    @staticmethod
    def getUser():
        users = session.query(Users).all()
        return users

    @staticmethod
    def getUserById(id):
        user = session.query(Users).filter(Users.participant_id==id).first()
        return user

    @staticmethod
    def search(search):
        vulns = session.query(Users).filter(or_(Users.participant_name.like('%'+search+'%'),Users.telephone.like('%'+search+'%')))
        return vulns




#漏洞
class Vuln(Base):
    __tablename__ = 'vuln'
    vul_id = Column(Integer, primary_key=True,autoincrement=True)
    vul_name = Column(String(64), unique=True, index=True)
    vul_level = Column(String(64))
    vul_description = Column(String(1024))
    vul_suggest = Column(String(1024))
    vul_link = Column(String(64))

    def __init__(self,vul_name='',vul_level='',vul_description="",vul_suggest="",vul_link=""):
        self.vul_name = vul_name
        self.vul_level = vul_level
        self.vul_description = vul_description
        self.vul_suggest = vul_suggest
        self.vul_link = vul_link

    @staticmethod
    def getAllVul():
        vulns = session.query(Vuln).all()
        return vulns

    @staticmethod
    def getVulById(vul_id):
        vuln = session.query(Vuln).filter(Vuln.vul_id == vul_id).one()
        return vuln

    @staticmethod
    def search(search):
        vulns = session.query(Vuln).filter(Vuln.vul_name.like('%' + search + '%'))
        return vulns


#项目
class Project(Base):
    __tablename__="project"
    project_id = Column(Integer,primary_key=True,autoincrement=True)   #项目id
    project = Column(String(64),index=True) #项目名称
    producer = Column(String(64))  #项目制作人
    production_date = Column(Date)  #制作时间
    reviewer = Column(String(64))   #复审人
    start_date = Column(Date)  #开始时间
    total_num = Column(Integer)         #漏洞总数
    high_num = Column(Integer)          #高危数量
    mid_num = Column(Integer)           #中危数量
    low_num = Column(Integer)           #低危数量
    risk_level = Column(String(64))       #整体风险程度
    path = Column(String(64))       #报告保存的路径
    work_time = Column(Integer)    #实际工作量：人/天


    participant = relationship("Users",backref='project',secondary='project_participant')
    sys = relationship("Sys",backref='project',secondary='project_sys')
    # vuln = relationship("Vuln",backref='project',secondary='project_vuln')


    def __init__(self,project="",producer="",production_date="",reviewer="",start_date="",risk_level="",work_time=""):
        self.project = project
        self.producer = producer
        self.production_date = production_date
        self.reviewer = reviewer
        self.start_date = start_date
        self.risk_level = risk_level
        self.work_time = work_time

    @staticmethod
    def getProjectById(id):
        project = session.query(Project).filter(Project.project_id == id).first()
        return project

    @staticmethod
    def getNewProjectId():
        # session.flush()
        id = session.query(func.max(Project.project_id)).one()[0]
        return id

    @staticmethod
    def updateNum(id,total_num,high_num,mid_num,low_num):
        try:
            session.query(Project).filter(Project.project_id == id).update({"total_num":total_num,"high_num":high_num,"mid_num":mid_num,"low_num":low_num})
            session.commit()
            return True
        except Exception as e:
            return False

    @staticmethod
    def updatePath(id,filename):
        try:
            session.query(Project).filter(Project.project_id == id).update(
                {"path": filename})
            session.commit()
            return True
        except Exception as e:
            return False

    @staticmethod
    def search(search):
        projects = session.query(Project).filter(or_(Project.project.like('%'+search+'%'),Project.producer.like('%'+search+'%')))
        return projects




#系统
class Sys(Base):
    __tablename__ = "system"  #表
    sys_id = Column(Integer, primary_key=True, autoincrement=True)  # 系统id
    sys_name = Column(String(64),index=True)  # 系统名称
    sys_url = Column(String(64))  # 系统url
    sys_ip = Column(String(64))  # 系统ip



    def __init__(self, sys_name='',sys_url='',sys_ip=''):
        self.sys_name = sys_name
        self.sys_url = sys_url
        self.sys_ip = sys_ip

    @staticmethod
    def getSysById(id):
        sys = session.query(Sys).filter(Sys.sys_id==id).one()
        return sys

    @staticmethod
    def getNewSystem():      #通过project的project.sys获取到新添加的该项目的系统
        session.flush()
        id = session.query(func.max(Project.project_id)).one()[0]
        project = Project.getProjectById(id)
        return project




#项目漏洞详情
class Detail(Base):
    __tablename__ = "project_vuln"
    id = Column(Integer, primary_key=True, autoincrement=True)  #
    project_id = Column(Integer)  #项目id
    vul_id = Column(Integer)  # 漏洞id
    sys_id = Column(Integer)  # 系统id
    detail = Column(String(2048)) #详情
    sys_url = Column(String(128))  # 漏洞url
    project_name = Column(String(128))  #项目名称
    vuln_name = Column(String(128))    #漏洞名称
    sys_name = Column(String(128))    #系统名称


    def __init__(self, project_id='',vul_id='',sys_id='',detail='',sys_url=''):
        self.project_id = project_id
        self.vul_id = vul_id
        self.sys_id = sys_id
        self.detail = detail
        self.sys_url = sys_url
        # self.project_name = Project.getProjectById(project_id).project
        # self.vuln_name = Vuln.getVulById(vul_id).vul_name
        # self.sys_name = Sys.getSysById(sys_id).sys_name


    def updateName(self,project_id,vul_id,sys_id):
        self.project_name = Project.getProjectById(project_id).project
        self.vuln_name = Vuln.getVulById(vul_id).vul_name
        self.sys_name = Sys.getSysById(sys_id).sys_name

    @staticmethod
    def getVulByProjectId(project_id):
        detail = session.query(Detail).filter(Detail.project_id==project_id).all()
        return detail

    @staticmethod
    def getDetailById(detail_id):
        detail = session.query(Detail).filter(Detail.id==detail_id).first()
        return detail

    @staticmethod
    def search(search):
        projects = session.query(Detail).filter(
            or_(Detail.project_name.like('%' + search + '%'),Detail.detail.like('%' + search + '%'),Detail.vuln_name.like('%' + search + '%'), Detail.sys_name.like('%' + search + '%')))
        return projects










    # def updatePwd(participant_name,pwd):
    #     try:
    #
    #     except Exception as e:
    #         raise e
    #         return False






# vulns = Vuln.GetAllVul()
# for vul in vulns:
#     print(vul.vul_name)

# vuln = Vuln.GetVul(1)
# print(vuln.vul_name)
# print(vuln.vul_level)

# Base.metadata.drop_all(engine)
# Base.metadata.create_all(engine)
# project1 = Project('测试项目9','尹普','2019-01-21','欧阳思裕','2019-01-21','高危')
# sys1 = Sys('门户1','http://www.xxx.com','1.1.1.1')
# project1.sys.append(sys1)
# data = ['1','3']
# for i in data:
#     user1 = Users.getUserById(i)
# print(user1.participant_name)
# user1 = Users('王','123456','13412345678')
# project1.participant.append(user1)
# vul1 = Vuln.getVulById(1)
# print(vul1.vul_name)
# project1.vuln.append(vul1)
# user2 = Users('郑','123456','18734043324')
# project1.participant = [user1,user2]
# session.add(project1)
# session.commit()
# project1 = session.query(Project).filter(Project.project_id=='6').first()
# print(project1.participant)
# session.flush()
# id=Project.getNewProjectId()
# print(id)
# project = Project.getProjectById(50)
# system1 = Sys('wuyif','1','2')
# project.sys.append(system1)
# session.add(project)
# session.commit()
# for i in project.sys:
#     print(i.sys_name)

# vulns = Detail.getVulByProjectId(2)
# for i in vulns:
#     print(i.vul_id)
#     vul = Vuln.getVulById(i.vul_id)
#     print(vul.vul_name)
#     print(vul.vul_level)


# Project.updateNum( 1,10,3,4,2)


# total = session.query(Project).count()
# print(total)

# projects = session.query(Project).filter(Project.project.like('%1%')).count()
# print(projects)

# vuls = Vuln.search("明文传输登录口令").count()
# print(vuls)


# details = session.query(Detail).all()
# for detail in details:
#     detail.project_name = Project.getProjectById(detail.project_id).project
#     detail.vuln_name = Vuln.getVulById(detail.vul_id).vul_name
#     detail.sys_name = Sys.getSysById(detail.sys_id).sys_name

# for detail in details:
#     print(detail.project_name)
