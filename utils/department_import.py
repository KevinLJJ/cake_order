import json
import xlrd
from orm.Config import DepartmentMap


def to_json():
    dep_dict = {}
    index = 1
    with open('a', 'r', encoding='utf-8') as file:
        deps = file.readlines()
        for dep in deps:
            dep_dict[dep.strip()] = index
            index = index + 1
    print(json.dumps(dep_dict, ensure_ascii=False))


def insert():
    file = 'info.xls'
    wb = xlrd.open_workbook(filename=file)  # 打开文件
    sheet1 = wb.sheet_by_index(0)  # 通过索引获取表格
    rows = sheet1.row_values(1)  # 获取行内容
    index = 1
    user_list = []
    for i in range(2276):
        row = sheet1.row_values(i)
        user = {
            'user_id': index,
            'worker_id': row[1],
            'name': row[0],
            'department_id': DepartmentMap.F_DEPART.get(row[2]),
            'choice': 0,
            'adminType': 0,
            'status': 0,
            'chooseTime': 0
        }
        index = index + 1
        user_list.append(user)
    data = {
        "user": user_list
    }
    print(json.dumps(data, ensure_ascii=False))


if __name__ == '__main__':
    insert()
