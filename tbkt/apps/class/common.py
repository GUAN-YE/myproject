# coding: utf-8
import datetime
import time
import logging
from libs.utils import tbktapi, is_chinamobile, pinyin_abb, db, Struct, auth, from_unixtime
from libs import utils
from apps.common.com_cache import cache
from apps.common import com_class, com_user

STUDENT_SUBJECT_CODE = {2: 'A', 3: 'B', 4: 'C', 9: 'D', 5: 'E'}
TEACHER_SUBJECT_CODE = {2: 'J', 3: 'K', 4: 'L', 9: 'M', 5: 'N'}


def get_province():
    qs = db.slave.common_provincecity.filter(fatherId=0).select('id', 'cityId', 'name')
    province = [Struct({'id': city.cityId, 'name': city.name}) for city in qs]
    return province


def get_cities(province='410000', child=0):
    """
    获得地市列表
    -------------------------
    王晨光     2016-12-06
    -------------------------
    @param province     默认河南省410000
    @param child        1附带县区数据
    @return [{id:县区行政编码, name:县区名, child:[]}]
    """
    qs = db.slave.common_provincecity.filter(fatherId=province).select('id', 'cityId', 'name')
    cities = [Struct({'id': city.cityId,
                      'name': city.name,
                      'child': []
                      })
              for city in qs]

    # 地市数据
    if child:
        cityd = {c.id: c for c in cities}
        city_ids = [c.id for c in cities]
        counties = db.slave.common_provincecity.filter(fatherId__in=city_ids).select('fatherId', 'cityId', 'name')[:]
        for county in counties:
            city = cityd[county.fatherId]
            county_data = {'id': county.cityId, 'name': county.name}
            city.child.append(county_data)
    return cities


def get_counties(city):
    """
    获得县区列表
    -------------------------
    王晨光     2016-12-06
    -------------------------
    @param city 城市行政编码
    @return [{id:县区行政编码, name:县区名}]
    """
    qs = db.slave.common_provincecity.filter(fatherId=city).select('cityId', 'name')[:]
    counties = [{'id': city.cityId,
                 'name': city.name
                 }
                for city in qs]
    return counties


def get_schools(county, keyword=None):
    """
    获得学校列表
    -------------------------
    王晨光     2016-12-06
    -------------------------
    @param county       地市行政编码
    @param keyword      搜索关键词
    @return [{id:学校ID, name:学校名, type:1小学2初中, learn_length:学制, ecid:集团ID}]
    """
    qs = db.slave.school.filter(county=county, type__in=[1, 2], status__gt=0)
    if keyword and keyword.isdigit():
        qs = qs.filter(id=keyword)
    elif keyword:
        keyword = keyword.encode('utf-8')
        qs = qs.filter(name__contains=keyword)
    schools = [{'id': school.id,
                'name': school.name,
                'learn_length': school.learn_length,
                'type': school.type,
                'ecid': school.ecid
                }
               for school in qs]
    return schools


def get_depts(school_id):
    """
    获得部门列表
    -------------------------
    王晨光     2016-12-21
    -------------------------
    @param school_id    学校ID
    @return [{id:部门ID, name:部门名称}]
    """
    school = db.slave.school.get(id=school_id)
    if not school:
        return []
    depts = db.slave.school_unit_class.filter(school_id=school_id, level_id=1, unit_type=1).order_by('type')[:]
    if not depts:
        # 创建部门节点
        type_dict = {1: u'小学部', 2: u'初中部', 3: u'高中部', 4: u'大学部', 5: u'其他部', 8: u'幼儿部'}
        dept_id = db.default.school_unit_class.create(
            school_id=school_id,
            unit_type=1,
            unit_name=type_dict[school.type],
            level_id=1,
            type=school.type,
            learn_length=school.learn_length,
        )
        path = "|%s" % dept_id
        db.default.school_unit_class.filter(id=dept_id).update(path=path)
        dept = db.slave.school_unit_class.wait(id=dept_id)
        depts = [dept] if dept else []
    out = [Struct({
        "id": d.id,
        "name": d.unit_name,
        "type": d.type,
        "learn_length": d.learn_length,
        "max_class": 30
    }) for d in depts]
    return out


def is_mystudent(user, student_id):
    """
    判断是不是我的学生
    -----------------------
    王晨光     2016-12-07
    -----------------------
    @param user         教师User
    @param student_id   学生user_id
    @return bool
    """
    # 教师班级
    tea_unit_ids = [u.id for u in user.units]
    # 学生班级
    stu_unit_ids = user.get_mobile_order_region().filter(user_id=student_id).select('unit_class_id').flat(
        'unit_class_id')[:]
    return bool(set(tea_unit_ids) & set(stu_unit_ids))


def filter_mystudents(user, student_ids):
    """
    从一组学生ID中过滤出我的学生ID
    ----------------------
    王晨光     2017-6-14
    ----------------------
    @param user         教师User
    @param student_ids  [学生ID]
    @return [学生ID]
    """
    if not student_ids:
        return []
    # 教师班级
    tea_unit_ids = [u.id for u in user.units]
    tea_unit_ids = set(tea_unit_ids)
    # 学生班级
    regions = user.get_mobile_order_region().filter(user_id__in=student_ids).select('unit_class_id', 'user_id')[:]
    out = [r.user_id for r in regions if r.unit_class_id in tea_unit_ids]
    return out


def update_student_info(user_id, name=None, gender=None):
    """
    修改学生信息
    -----------------------
    王晨光     2016-12-07
    -----------------------
    :param user_id: 学生ID
    :param name: 新名字
    :param gender: 性别 1男 2女
    """
    assert name or gender
    auth_user_args = {}
    auth_profile_args = {}
    if name:
        auth_user_args['real_name'] = name
    if gender in (1, 2):
        auth_profile_args['sex'] = gender

    print 'update_student_info:', user_id, auth_user_args, auth_profile_args

    if auth_user_args:
        db.user.auth_user.filter(id=user_id).update(**auth_user_args)
        cache.auth_user.delete(user_id)
    if auth_profile_args:
        db.user.auth_profile.filter(user_id=user_id).update(**auth_profile_args)
        cache.auth_profile.delete(user_id)


def remove_student(user, user_ids):
    """
    移除学生班级
    -----------------------
    王晨光     2016-12-07
    -----------------------
    :param user_ids: [学生ID]
    """
    if not user_ids:
        return
    unit_ids = user.get_mobile_order_region().filter(user_id__in=user_ids).flat('unit_class_id')[:]
    user.get_mobile_order_region(is_slave=False).filter(user_id__in=user_ids).delete()
    for unit_id in unit_ids:
        cache.unit_students.delete(unit_id)
    for user_id in user_ids:
        cache.user_units.delete(user_id)


def getpwd(user_id):
    """
    返回学生帐号和伪密码
    -----------------------
    王晨光     2016-12-07
    -----------------------
    :param user_id: 学生ID
    :return: {"username":"15981867201xs", "password":"111**1"}
    """
    user = com_user.get_user(user_id)
    if not user:
        return
    password = auth.decode_plain_password(user.plain_password)
    print password
    password = '***'
    return {"username": user.username, "password": password}


def import_student(request, teacher, unit_class_id, real_name, sex, phone_number, open_option='', sncode='', send_pwd=1,
                   send_open_msg=0):
    """
    导入学生
    -------------------------
    王晨光     2016-12-08
    -------------------------
    参数说明：
    teacher: 教师User对象
    unit_class_id: 要加入的班级unit_class_id
    real_name: 学生姓名
    sex: 性别 1男 2女
    phone_number: 家长手机号
    open_option: 'open'表示短信开通(和 sn_code都为空则暂不开通)
    sncode: 验证码开通
    send_pwd: 是否发送账号密码
    send_open_msg 是否发送开通科目短信 0:不发送 1:发送
    :return: error
    """
    subject_id = teacher.sid

    # 班级学生ID
    user_ids = teacher.get_mobile_order_region().filter(unit_class_id=unit_class_id, user_type=1).select(
        'user_id').flat('user_id')[:]
    if user_ids:
        if db.user_slave.auth_user.filter(id__in=user_ids, real_name=real_name).exists():
            return '添加学生失败。您所添加的学生与班内学生有重名, 您可进行如下操作:<br>1. 移除班内重名学生<br>2. 变更需要添加的学生姓名再添加'

    nowt = int(time.time())
    user = db.user_slave.auth_user.get(phone=phone_number, type=1, real_name=real_name)
    if not user:
        user = db.user_slave.auth_user.get(phone=phone_number, type=1)
    if user:
        # 是否开通
        opened = db.ketang_slave.mobile_subject.filter("cancel_date<=0 or cancel_date>%s" % nowt,
                                                       open_date__gte=nowt, user_id=user.id,
                                                       subject_id=subject_id).exists()

        # 遇到同一班级同一手机号, 直接改名字
        reg = teacher.get_mobile_order_region().filter(
            unit_class_id=unit_class_id,
            user_id=user.id
        ).exists()
        if reg:
            if opened:
                return '添加失败, 该用户已存在并且已开通'
            else:
                return update_student_info(user.id, real_name, sex)

        # 添加学生用户是否已开通过指定科目,如果已开通则不在下发开通短信
        if opened or not is_chinamobile(phone_number):
            open_option = ''
            sncode = ''

        region = teacher.get_mobile_order_region().get(user_id=user.id)
        if region:
            # 是否有开通过的学科
            if region.unit_class_id != unit_class_id and opened:
                return '该学生已在其他班级，无法添加'

        # 加入班级
        com_class.join_unit_class_by_id(user, unit_class_id)
        # 修改姓名
        if user.real_name != real_name or user.sex != sex:
            update_student_info(user.id, real_name, sex)
    else:
        user_id, error = com_class.import_user(
            1,
            phone_number,
            real_name,
            gender=sex,
            join_unit_id=unit_class_id,
            subject_id=subject_id if open_option == 'open' else 0,
            sn_code=sncode,
            send_pwd=send_pwd,
        )
        # 开通科目
        if open_option == "open" or sncode:
            hub = tbktapi.Hub(request)
            open_dict = {"phone_number": phone_number, "subject_id": subject_id, "sn_code": sncode,
                         "platform_id": teacher.platform_id}
            out = hub.bank.post('/cmcc/open', open_dict)
        if error:
            return error


def get_unit_students(user, unit_id):
    """
    获取班级学生信息(不带学科)
    ----------------------
    王晨光     2017-2-19
    ----------------------
    :param unit_id: 班级ID
    :return: [{'user_id':学生ID, 'user_name':姓名, 'phone_number':电话,
               'sex':1男2女, 'is_status':0非暂存1表示暂存, 'abb':拼音缩写}]

    *结果按姓名排序
    """
    if not unit_id:
        return []

    # 获取bind_ids
    user_ids = cache.unit_students.get(unit_id)
    if not user_ids:
        user_ids = user.get_mobile_order_region().filter(unit_class_id=unit_id, user_type=1).select('user_id').flat(
            'user_id')[:]
        user_ids = list(set(user_ids))
        cache.unit_students.set(unit_id, user_ids)

    # 合并结果
    students = []
    userd = com_user.get_users(user_ids)
    for user_id in user_ids:
        u = userd.get(user_id)
        if u:
            student = {
                'user_id': u.id,
                'bind_id': u.id,
                'user_name': u.real_name,
                'phone_number': u.phone,
                'sex': u.sex,
                'is_status': 0,
                'abb': pinyin_abb(u.real_name),
                'portrait': u.portrait,
            }
            student = Struct(student)
            students.append(student)

    students.sort(key=lambda x: x.abb)
    return students


def get_user_students(user, unit_id):
    """
    获得班级学生列表
    ----------------------------
    方朋       2014-04-15
    王浩       2016-??-?? 增加计费状态
    王晨光     2017-02-20 加缓存
    ----------------------------
    :param user: 教师User
    :param unit_id: 班级ID
    :return: {
        'student_num': 班级人数,
        'open_num': 开通人数,
        'unopen_num': 未开通人数,
        'trial_count': 试用人数,
        'students': [students]
    }
    """
    if user.is_teacher:
        sid = user.sid
        students = get_unit_students(user, unit_id)
        # 读取学科开通信息
        user_ids = [s.user_id for s in students]
        mslist = db.ketang_slave.mobile_subject.select('phone_number', 'user_id',
                                                       'cancel_date', '1 send_open', 'open_date', 'status'
                                                       ).filter(user_id__in=user_ids, subject_id=sid)[:]
        # nowt = int(time.time())
        for m in mslist:
            # m.status = 2 if nowt >= m.open_date and (
            #     m.cancel_date <= 0 or nowt < m.cancel_date) and m.open_date > 0 else 0
            if int(m.status) in (2, 3):             # 待退订和开通 都是开通
                m.status = 2
        msdict = {ms.user_id: ms for ms in mslist}
        for s in students:
            ms = msdict.get(s.user_id)
            if ms:
                s.update(ms)
                # 属性解释：
                # status：mobile_subject 的id；
                # is_status：0表示非暂存；1表示暂存
                # send_open：0表示未下发开通请求；1表示已经下发了开通请求
    else:
        students = []
    student_num = unopen_num = open_num = trial_num = 0

    for obj in students:
        student_num += 1
        now = datetime.datetime.now()
        obj.open_date = from_unixtime(obj.open_date)
        # 计费状态(1体验状态 2计费状态)
        billing = 0
        # 计费时间为开通时加一个月
        billing_date = obj.open_date + datetime.timedelta(days=31) if obj.open_date else None

        if billing_date:
            if billing_date > now:
                billing = 1
            elif billing_date < now:
                billing = 2

        obj.billing = billing
        obj.billing_date = billing_date
        if (obj.status == 2 and obj.billing == 1) or obj.status == 9:
            trial_num += 1
            obj.state = "trial"
        if obj.status == 2 and obj.billing == 2:
            open_num += 1
            obj.state = "open"
        if obj.status not in (2, 9):
            unopen_num += 1
            obj.state = "unopen"

    # 同一手机号只有一个显示为开通, 其余显示体验状态
    open_phones = set()
    for obj in students:
        phone = obj.phone_number
        if obj.status == 2 and obj.billing == 2:
            if phone in open_phones:
                obj.status = 9
                obj.state = "trial"
                trial_num += 1
                open_num -= 1
            else:
                open_phones.add(phone)

    data = {
        'student_num': student_num,
        'open_num': open_num,
        'unopen_num': unopen_num,
        'trial_count': trial_num,
        'students': students
    }
    return data


def user_grade_unitcount(user, grade_id):
    """
    查询老师某个年级下班级个数
    ----------------------------
    王晨光     2017-1-11
    ----------------------------
    """
    return sum(1 for u in user.all_units if u.grade_id == grade_id)


def get_account_school_id(user):
    """获取老师所有帐号所在学校ID"""
    user_ids = db.user_slave.auth_user.filter(phone=user.phone_number, type=3).select('id').flat('id')[:]
    if not user_ids:
        return
    rg = user.get_mobile_order_region().select('school_id').get(user_id__in=user_ids)
    if rg:
        return rg.school_id


def joinclass(user, dept_id, grade_id, class_id):
    """
    加入班级
    ----------------------------
    王晨光     2016-12-21
    ----------------------------
    @param user: User
    @param dept_id: 部门ID
    @param grade_id: 年级(1-9)
    @param class_id: 班级(0-30)
    @return: (班级ID, error)
    """
    unit = user.unit

    dept = db.slave.school_unit_class.get(id=dept_id)
    if not dept:
        return None, "部门不存在"
    school_id = dept.school_id

    if not db.slave.school.filter(id=school_id).exists():
        return None, "部门学校不存在"

    # 老师的判断
    if user.is_teacher:
        # 不支持的学科
        # if user.sid in (3,4,9) and dept.type == 2:
        #     s = {3:u'物理', 4:u'化学', 9:u'英语'}[user.sid]
        #     return None, u"暂不支持初中%s教师, 请登录网站使用" % s
        # account_school_id = get_account_school_id(user)
        # if account_school_id and account_school_id != school_id:
        #     return None, u"不支持跨学校添加班级"
        if unit and school_id != unit.school_id:
            return None, u"不支持跨学校添加班级"
        if unit and dept.type != user.dept_type:
            return None, u"不支持跨部门添加班级"
        if user_grade_unitcount(user, grade_id) >= 6:
            return None, u"每个任课教师最多只能加入6个班级"
        for u in user.units:
            if u.grade_id == grade_id and u.class_id == class_id:
                return None, u"您已经在当前班级"
        # 判断班级已有同学科老师
        unit = db.slave.school_unit_class.select('id').get(school_id=school_id, grade_id=grade_id, class_id=class_id)
        if unit:
            teacher_ids = user.get_mobile_order_region().filter(unit_class_id=unit.id, user_type=3).flat('user_id')[:]
            if teacher_ids:
                if db.user_slave.auth_user.filter(id__in=teacher_ids, type=3, sid=user.sid):
                    return None, u"该班已有%s教师,您不能加入该班级" % user.subject_name

    return com_class.join_unit_class(user, dept_id, grade_id, class_id)


def joinclass_id(user, unit_id):
    """
    按班级ID加入班级
    ----------------------------
    王晨光     2016-12-26
    ----------------------------
    """
    if user.is_teacher:
        # 老师加班级的判断
        unit = db.slave.school_unit_class.select('id', 'grade_id').get(id=unit_id, is_update=0)
        # 不支持的学科
        if user.sid in (3, 4, 9) and unit and unit.type == 2:
            sbname = {3: '物理', 4: '化学', 9: '英语'}[user.sid]
            return None, "暂不支持初中%s教师, 请登录网站使用" % sbname
        account_school_id = get_account_school_id(user)
        if account_school_id and account_school_id != unit.school_id:
            return None, "不支持跨学校添加班级"
        if unit and unit.school_id != unit.school_id:
            return None, "不支持跨学校添加班级"
        if user.dept_type and unit.type != user.dept_type:
            return None, "不支持跨部门添加班级"
        if unit and user_grade_unitcount(user, unit.grade_id) >= 6:
            return None, "每个任课教师最多只能加入6个班级"
        for u in user.units:
            if u.id == unit_id:
                return None, "您已经在当前班级"
        # 判断该班已有同学科老师
        teacher_ids = user.get_mobile_order_region().filter(unit_class_id=unit_id, user_type=3).select('user_id').flat(
            'user_id')[:]
        if teacher_ids:
            if db.user_slave.auth_user.filter(id__in=teacher_ids, type=3, sid=user.sid):
                return None, u"该班已有%s教师,您不能加入该班级" % user.subject_name

    com_class.join_unit_class_by_id(user, unit_id)
    return unit_id, None


def quitclass(user, unit_ids):
    """
    用户退出班级
    ----------------------------
    王晨光     2016-12-21
    王晨光     2017-06-23
    ----------------------------
    @param user: User
    @param unit_ids: [班级ID]
    """
    if not unit_ids:
        return
    user.get_mobile_order_region(is_slave=False).filter(user_id=user.id, unit_class_id__in=unit_ids).delete()
    for unit_id in unit_ids:
        cache.unit_students.delete(unit_id)
    cache.user_units.delete(user.id)
    cache.auth_profile.delete(user.id)
    cache.user_profile.delete(user.id)


def get_units_by_phone(user, phone):
    """
    按老师手机号查班级列表
    ----------------------------
    王晨光     2016-12-26
    ----------------------------
    @:param user:
    @param phone: 老师手机号
    @return: (result, error)
        [{"id":班级ID, "name":班级名}]
    """
    if not phone:
        return [], '老师手机号不能为空'
    users = db.user_slave.auth_user.select('id').filter(phone=phone, type=3)[:]
    if not users:
        return [], '未找到该教师'
    user_ids = [u.id for u in users]
    unit_ids = db.ketang_slave.mobile_order_region.filter(user_id__in=user_ids, is_update=0
                                                          ).select('unit_class_id').flat('unit_class_id')[:]
    if not unit_ids:
        return [], '未找到该教师的班级'
    units = db.slave.school_unit_class.filter(id__in=unit_ids, is_update=0).select('id', 'unit_name name').order_by(
        'grade_id', 'class_id')[:]
    return units, None


def get_class_teachers(user, unit_id):
    """
    获取班级所有老师信息
    ---------------------------
    王晨光     2017-5-16
    ---------------------------
    @param unit_id 班级ID
    @return [{id:老师ID, name:老师姓名, sid:老师学科ID}]
    """
    if not unit_id:
        return []
    user_ids = user.get_mobile_order_region().filter(unit_class_id=unit_id, user_type=3).select('user_id').flat(
        'user_id')[:]
    if not user_ids:
        return []
    users = db.user_slave.auth_user.filter(id__in=user_ids).select('id', 'real_name name', 'sid')[:]
    return users
