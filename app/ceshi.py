from sqlalchemy import Column, Integer, String,ForeignKey,Table
from sqlalchemy.orm import relationship,sessionmaker
# 调用基类Base
from sqlalchemy.ext.declarative import declarative_base
# 调用链接数据库
from sqlalchemy import create_engine

# encoding='utf-8' 链接字符集 ，echo=True 把所有信息打印出来
engine = create_engine("mysql+pymysql://root:toor@localhost/sangfor_report",encoding='utf-8',echo=True)
# 创建对象的基类:
Base = declarative_base()
# 创建DBSession类型:
DBSession = sessionmaker(bind=engine)
# 创建session对象:
session = DBSession()

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
    def GetAllVul():
        vulns = session.query(Vuln).all()
        return vulns

    @staticmethod
    def GetVul(vul_id):
        vuln = session.query(Vuln).filter(Vuln.vul_id == vul_id).one()
        return vuln

vuln = Vuln.GetAllVul()
for i in vuln:
    print(i.vul_name)