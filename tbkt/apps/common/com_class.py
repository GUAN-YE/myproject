# coding: utf-8
"""班级常用函数"""
import datetime
import time
import re
import random

from libs.utils import sms, db, auth, tbktapi
from com_cache import cache
from apps.common.com_user import REGIONMAP


def send_password(user_ids, sender={}):
    """
    功能说明：发送账号密码
    -------------------------------------------
    修改人     修改时间        修改原因
    -------------------------------------------
    徐威       2015-03-22
    王晨光     2017-6-14   支持批量发送
    -------------------------------------------
    """
    if not user_ids:
        return
    users = db.user.auth_user.select('id', 'username', 'phone').filter(id__in=user_ids)[:]
    profiles = db.user.auth_profile.select('user_id', 'password').filter(user_id__in=user_ids)[:]
    profiled = {p.user_id:p.password for p in profiles}
    for user in users:
        plain_password = profiled.get(user.id) or ""
        password = auth.decode_plain_password(plain_password)
        sms_content = u"您的同步课堂账号是:%s 密码是：%s,做作业(除数学知识点视频作业外)功能免费，请放心使用。客户端点此m.tbkt.cn下载安装。咨询电话：12556185" % (user.username, password)
        hub = tbktapi.Hub(user_id=user.id)
        hub.sms.post('/sms/send', {'phone':user.phone, 'content':sms_content})


def create_unit_grade(dept_id, gradeno):
    """
    创建年级节点
    ---------------------------------
    王晨光     2016-09-28
    ---------------------------------
    :param dept_id: 部门节点ID
    :param gradeno: 几年级
    :returns: 年级节点ID or None
    """
    dept = db.default.school_unit_class.get(id=dept_id)
    if not dept:
        return
    id = db.default.school_unit_class.create(
                school_id=dept.school_id,
                unit_type=1,
                unit_name="%s年级"%gradeno,
                learn_length=6 if gradeno<=6 else 3,
                type=1 if gradeno<=6 else 2,
                grade_id=gradeno,
                class_id=0,
                parent_id=dept.id,
                level_id=2,
                is_leaf=0,
                path="",
                is_update=0,
                max_class=30,
                add_time=int(time.time()),
            )
    path = "|%s|%s" % (dept_id, id)
    db.default.school_unit_class.filter(id=id).update(path=path)
    return id


def create_unit(parent_id, classno):
    """
    创建新班级

    王晨光     2016-09-28

    :param parent_id: 年级节点ID
    :param classno: 班级编号
    :returns: 班级ID or None
    """
    node = db.default.school_unit_class.get(id=parent_id)
    if not node:
        return
    gradeno = node.grade_id
    id = db.default.school_unit_class.create(
                school_id=node.school_id,
                unit_type=1,
                unit_name="%d%02d班" % (gradeno, classno),
                learn_length=6 if gradeno<=6 else 3,
                type=1 if gradeno<=6 else 2,
                grade_id=node.grade_id,
                class_id=classno,
                parent_id=node.id,
                level_id=3,
                is_leaf=1,
                path="",
                is_update=0,
                max_class=30,
                add_time=int(time.time()),
                sms_num=0,
                real_num=0,
            )
    path = "%s|%s" % (node.path, id)
    db.default.school_unit_class.filter(id=id).update(path=path)
    return id


def join_unit_class(user, dept_id, grade_number, class_number):
    """
    加入班级
    -------------------------------------------
    徐威       2015-03-22
    王晨光     2017-06-06  将存储过程改为python
    -------------------------------------------
    :param user: 用户User对象
    :param dept_id：部门ID
    :param grade_number：年级编号
    :param class_number：班级编号
    :return: (新班级ID, error)
    """
    if not db.slave.school_unit_class.filter(id=dept_id):
        return None, u"部门不存在"
    
    node = db.slave.school_unit_class.get(parent_id=dept_id, grade_id=grade_number, is_update=0)
    if not node:
        node_id = create_unit_grade(dept_id, grade_number)
        if not node_id:
            return None, u"年级不存在"
    else:
        node_id = node.id

    unit = db.slave.school_unit_class.get(parent_id=node_id, class_id=class_number, is_update=0)
    if not unit:
        unit_id = create_unit(node_id, class_number)
        unit = db.default.school_unit_class.get(id=unit_id, is_update=0)
    if not unit:
        return None, u"班级不存在"

    if user.get_mobile_order_region().filter(user_id=user.id, unit_class_id=unit.id):
        return unit.id, None

    school = db.slave.school.get(id=unit.school_id)
    if not school:
        return None, u"学校不存在"

    # 学生只能加入1个班
    if user.is_student:
        user.get_mobile_order_region(is_slave=False).filter(user_id=user.id).delete()

    nowt = int(time.time())
    user.get_mobile_order_region(is_slave=False).create(
        province=school.county[:2]+'0000',
        city=school.county[:4]+'00',
        county=school.county,
        school_id=school.id,
        school_name=school.name,
        school_type=school.type,
        unit_class_id=unit.id,
        is_update=0,
        add_date=nowt,
        del_state=0,
        user_type=user.type,
        user_id=user.id,
    )
    cache.unit_students.delete(unit.id)
    cache.unitsize.delete(unit.id)
    cache.user_units.delete(user.id)
    # 更新老师当前年级
    if user.is_teacher:
        user.set_grade(grade_number)
        cache.user_profile.delete(user.id)
    # 更新学段
    if user.dept_id != unit.type:
        unit.type = max(1, int(unit.type))
        db.user.auth_user.filter(id=user.id).update(dept_id=unit.type)
        cache.auth_user.delete(user.id)
    return unit.id, None


def join_unit_class_by_id(user, unit_id):
    """
    指定班级ID加入
    -------------------------------------------
    徐威       2015-03-22
    王晨光     2017-06-06  将存储过程改为python
    -------------------------------------------
    :param user：用户User对象
    :param unit_id: 加入班级ID
    :return: error or None
    """
    if db.ketang_slave[REGIONMAP.get(int(user.platform_id), "mobile_order_region")].filter(user_id=user.id, unit_class_id=unit_id).exists():
        return unit_id, None

    unit = db.slave.school_unit_class.get(id=unit_id)
    if not unit:
        return u"班级不存在"
    school = db.slave.school.get(id=unit.school_id)
    if not school:
        return u"学校不存在"
    current_units = user.units
    # 学生只能加入1个班
    db.ketang_slave[REGIONMAP.get(int(user.platform_id), "mobile_order_region")].filter(user_id=user.id).delete()


    nowt = int(time.time())
    db.ketang[REGIONMAP.get(int(user.platform_id), "mobile_order_region")].create(
        province=school.county[:2]+'0000',
        city=school.county[:4]+'00',
        county=school.county,
        school_id=school.id,
        school_name=school.name,
        school_type=school.type,
        unit_class_id=unit.id,
        is_update=0,
        add_date=nowt,
        del_state=0,
        user_type=user.type,
        user_id=user.id,
    )
    # 先清除当前的班级缓存
    if current_units:
        for u in current_units:
            cache.unit_students.delete(u.id)
            cache.unitsize.delete(u.id)
    cache.unit_students.delete(unit.id)
    cache.unitsize.delete(unit.id)
    cache.user_units.delete(user.id)
    # 更新老师当前年级
    if user.is_teacher:
        user.set_grade(unit.grade_id)


def find_a_username(user_type, phone_number):
    """
    找一个可用的用户名

    王晨光     2017-06-06

    :param user_type: 用户类型 1学生 3老师 
    :param phone_number: 手机号
    :return: 用户名(比如:15981867201xs2)
    """
    prefix = phone_number + ('xs' if user_type==1 else 'js')
    n = db.user_slave.auth_user.filter(username__startswith=prefix).count()
    if n <= 0:
        return prefix
    return prefix + str(n)


def import_user(user_type, phone_number, real_name, gender=1, join_unit_id=0, subject_id=0, sn_code='', send_pwd=0):
    """
    导入用户资料, 如果是短信开通则open_option="open"，如果验证码开通sn_code不能为空，二者选其一
    -------------------------------------------
    徐威       2015-03-22
    王晨光     2017-06-06
    -------------------------------------------
    :param user_type: 用户类型 1学生 3老师
    :param phone_number: 手机号
    :param real_name: 姓名
    :param join_unit_id: 要加入的班级ID
    :param sn_code: 二次短信验证码
    :param subject_id: 开通学科ID
        subject_id 和 sn_code 都为空则暂不开通
    :param send_pwd: 是否发送帐号密码 1是 0否
    :return: (新用户ID, error)
    """
    username = find_a_username(user_type, phone_number)
    nowt = int(time.time())
    password = "".join(random.sample('1234567890', 6))  # 随机生成6位密码
    # 创建auth_user
    if db.user.auth_user.filter(username=username).exists():
        return None, u"用户已存在"
    user_id = db.user.auth_user.create(
        username=username,
        password=auth.encode_password(password),
        type=user_type,
        real_name=real_name,
        date_joined=nowt,
        status=1,
        sid=0,
        grade_id=0,
        phone=phone_number,
        platform_id=1
    )
    db.user.auth_profile.create(
        user_id=user_id,
        nickname=real_name,
        sex=1,
        password=auth.encode_plain_password(password)
    )
    if not user_id:
        return None, u"用户已存在"
    user = db.user.auth_user.get(id=user_id)
    # 加入班级
    join_unit_class_by_id(user, join_unit_id)

    # 是否发送账号密码
    if send_pwd:
        send_password([user_id])
    return user_id, None
 