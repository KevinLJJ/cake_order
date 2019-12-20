# -*- coding: utf-8 -*-
# @Time    : 2019-12-19 23:18
# @Author  : ljj0452@gmail.com

from app import db
from orm.Config import DepartmentMap
import time


class Worker(db.Model):
    """
    用户模型
    """
    __tablename__ = 'worker'

    user_id = db.Column(db.Integer, primary_key=True)
    worker_id = db.Column(db.String(255))
    name = db.Column(db.String(255))
    department_id = db.Column(db.Integer)
    choice = db.Column(db.Integer)
    adminType = db.Column(db.Integer)
    status = db.Column(db.Integer)
    chooseTime = db.Column(db.String(255))

    def __init__(self, worker_id, name, department_id):
        self.name = name
        self.worker_id = worker_id
        self.department_id = department_id
        self.adminType = 0
        self.choice = 0
        self.status = 0
        self.chooseTime = 0

    def to_dict(self):
        return {
            'workerID': self.worker_id,  # 教工号
            'name': self.name,  # 姓名,
            'departID': self.department_id,
            'department': DepartmentMap.DEPART.get(str(self.department_id)),  # 学院中文
            'status': self.status,  # 是否已选 0:未选 1:已选
            'adminType': self.adminType,  # 管理员类型 0:普通用户(默认) 1:学院管理员 2:系统管理员
            'choice': self.choice  # 0:未选默认 1:好利来 2:安德鲁森 3:元祖
        }

    def to_simple_dict(self):
        return {
            'workerID': self.worker_id,  # 教工号
            'name': self.name,  # 姓名,
            'department': DepartmentMap.DEPART.get(str(self.department_id)),  # 学院中文
            'status': self.status,  # 是否已选 0:未选 1:已选
        }


class Department(db.Model):
    """
    学院列表
    """
    __tablename__ = 'department'
    dep_id = db.Column(db.Integer, primary_key=True)
    dep_name = db.Column(db.String(255))


class Cake(db.Model):
    """
    蛋糕
    """
    __tablename__ = 'cake'
    cake_id = db.Column(db.Integer, primary_key=True)
    cake_name = db.Column(db.String(255))
