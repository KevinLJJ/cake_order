import json

from flask import Flask, request, session
from flask_cors import *
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, exists, and_

from orm.Config import *

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config.from_object(Config)

db = SQLAlchemy(app)

from orm.models import *


@app.route('/api/v1/login', methods=['POST'])
def login():
    response = {
        'status': -1,
        'data': [],
        'msg': ''
    }
    data = request.get_json()
    try:
        current_user = db.session.query(Worker).filter(Worker.worker_id == data['workerID']).first()
        if current_user:
            user=current_user.to_dict()
            session['departID'] = user['departID']
            session['adminType'] = user['adminType']
            session['wid'] = user['workerID']
            response['status'] = 1
            response['data'] = user
            response['msg'] = '登陆成功'
        else:
            response['msg'] = f'账号密码错误'
        return response
    except Exception as e:
        response['msg'] = f'error: {e}'
        db.session.rollback()
        return response
    finally:
        db.session.close()



@app.route('/api/v1/getUserInfo', methods=['GET'])
def get_user_info():
    response = {
        'status': -1,
        'data': [],
        'msg': ''
    }
    wid = session.get('wid', '')
    try:
        if wid:
            user = db.session.query(Worker).filter(Worker.worker_id == wid).first()
            response['status'] = 0
            response['data'] = user.to_dict()
            response['msg'] = 'success'
        else:
            response['status'] = -2
            response['msg'] = f'error: 会话过期，请重新登录'
        return response
    except Exception as e:
        response['msg'] = f'error: {e}'
        db.session.rollback()
        return response
    finally:
        db.session.close()


@app.route('/api/v1/countResult', methods=['GET'])
def count_result():
    result = {
        'departID': '',
        'department': '',
        'selected': 0,
        'unselected': 0,
        'Holiland': 0,
        'Andersen': 0,
        'Yuanzu': 0
    }
    response = {
        'status': -1,
        'data': [],
        'msg': ''
    }
    depart_id = request.args.get("departID", "")
    wid = session.get('wid', '')
    try:
        if wid:
            if depart_id:
                result['departID'] = depart_id
                result['department'] = DepartmentMap.DEPART.get(depart_id)
                result['selected'] = db.session.query(func.count(Worker.worker_id)) \
                    .filter(Worker.status == 1, Worker.department_id == depart_id).scalar()
                result['unselected'] = db.session.query(func.count(Worker.worker_id)) \
                    .filter(Worker.status == 0, Worker.department_id == depart_id).scalar()
                result['Holiland'] = db.session.query(func.count(Worker.worker_id)) \
                    .filter(Worker.status == 1, Worker.choice == 1, Worker.department_id == depart_id).scalar()
                result['Andersen'] = db.session.query(func.count(Worker.worker_id)) \
                    .filter(Worker.status == 1, Worker.choice == 2, Worker.department_id == depart_id).scalar()
                result['Yuanzu'] = db.session.query(func.count(Worker.worker_id)) \
                    .filter(Worker.status == 1, Worker.choice == 3, Worker.department_id == depart_id).scalar()
            else:
                result['department'] = 'ALL'
                result['selected'] = db.session.query(func.count(Worker.worker_id)).filter(Worker.status == 1).scalar()
                result['unselected'] = db.session.query(func.count(Worker.worker_id)).filter(
                    Worker.status == 0).scalar()
                result['Holiland'] = db.session.query(func.count(Worker.worker_id)) \
                    .filter(Worker.status == 1, Worker.choice == 1).scalar()
                result['Andersen'] = db.session.query(func.count(Worker.worker_id)) \
                    .filter(Worker.status == 1, Worker.choice == 2).scalar()
                result['Yuanzu'] = db.session.query(func.count(Worker.worker_id)) \
                    .filter(Worker.status == 1, Worker.choice == 3).scalar()
            response['status'] = 0
            response['data'] = result
            response['msg'] = 'success'
        else:
            response['status'] = -2
            response['msg'] = f'error: 会话过期，请重新登录'
        return response
    except Exception as e:
        response['msg'] = f'error: {e}'
        db.session.rollback()
        return response
    finally:
        db.session.close()


@app.route('/api/v1/getUnselectList', methods=['GET'])
def get_unselect_list():
    response = {
        'status': -1,
        'data': [],
        'msg': ''
    }
    unselect_list = {
        'unselect': [],
        'count': 0
    }
    try:
        depart_id = request.args.get("departID", "")
        if session:
            if session.get('adminType', 0) == 1 or depart_id:
                user_list = db.session.query(Worker).filter(Worker.department_id == session.get('departID', ''),
                                                            Worker.status == 0).all()
            elif session.get('adminType', 0) == 2:
                user_list = db.session.query(Worker).filter(Worker.status == 0).all()
                print(len(user_list))
            else:
                response['msg'] = '用户权限不足'
                return response
            for user in user_list:
                unselect_list['unselect'].append(user.to_simple_dict())
                unselect_list['count'] = unselect_list['count'] + 1
            response['status'] = 1
            response['msg'] = 'success'
            response['data'] = unselect_list
            return response
        else:
            response['status'] = -2
            response['msg'] = f'error: 会话过期，请重新登录'
            return response
    except Exception as e:
        response['msg'] = f'error: {e}'
        db.session.rollback()
        return response
    finally:
        db.session.close()


@app.route('/api/v1/chooseCake', methods=['post'])
def choose_cake():
    response = {
        'status': -1,
        'data': [],
        'msg': ''
    }
    cake_id = request.get_json().get('cakeId', 0)
    try:
        if session:
            if (time.time() - 1577250000) > 0:
                response['status'] = -4
                response['msg'] = f'error: 超过选择时间，不能选择，感谢参与。'
                return response
            if not db.session.query(
                    exists().where(and_(Worker.worker_id == session.get('wid', ''), Worker.status == 0))).scalar():
                response['status'] = -3
                response['msg'] = f'error: 已经选择，不能再次修改。'
                return response
            if cake_id != 0:
                Worker.query.filter_by(worker_id=session.get('wid', '')).update({
                    'status': '1',
                    'choice': cake_id,
                    'chooseTime': str(int(time.time()))
                })
                db.session.commit()
                response['status'] = 1
                response['msg'] = '提交成功，感谢您的参与，即将为您退出。'
                return response
        else:
            response['status'] = -2
            response['msg'] = f'error: 会话过期，请重新登录'
            return response
    except Exception as e:
        response['msg'] = f'error: {e}'
        db.session.rollback()
        return response
    finally:
        db.session.close()


if __name__ == '__main__':
    app.run()
