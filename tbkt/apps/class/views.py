# coding: utf-8
import re
import random
import datetime

from django.http import HttpResponse

from apps.common.com_cache import cache
from libs.utils import ajax, is_chinese_word, is_chinamobile, db, ajax_try, \
    thread_pool, tbktapi
from apps.common import com_user, com_class
import common

RE_PHONE = re.compile(r"^1[34578]\d{9}$")  # 手机号正则表达式
RE_CHINAMOBILE = re.compile(r"^1(([3][456789])|([5][012789])|([8][23478])|([4][7]))[0-9]{8}$")


@ajax_try([])
def p_province(request):
    """
    @api {get} /class/province [班级]所有省份列表
    @apiGroup class
    @apiParamExample {json} 请求示例
        {'}
    @apiSuccessExample {json} 成功返回
        {
            "message": "",
            "next": "",
            "data": [
                {
                    "id": "110000",
                    "name": "北京市",
                }
            ],
            "response": "ok",
            "error": ""
        }
    """

    data = common.get_province()
    return ajax.jsonp_ok(request, data)


@ajax_try([])
def p_cities(request):
    """
    @api {get} /class/cities [班级]所有地市列表
    @apiGroup class
    @apiParamExample {json} 请求示例
        {'child':1返回地市+县区数据 0只返回地市数据,province_id:410000  省份id}
    @apiSuccessExample {json} 成功返回
        {
            "message": "",
            "next": "",
            "data": [
                {
                    "id": "410200",
                    "name": "开封市",
                    "child": [
                        {
                            "id": "410202",
                            "name": "龙亭区"
                        }
                    ]
                },
            ],
            "response": "ok",
            "error": ""
        }
    """
    args = request.QUERY.casts(child=int, province_id=int)
    child = args.child or 0
    province_id = args.province_id or 410000
    data = common.get_cities(province_id, child=child)
    return ajax.jsonp_ok(request, data)


@ajax_try([])
def p_counties(request):
    """
    @api {get} /class/counties [班级]县区列表
    @apiGroup class
    @apiParamExample {json} 请求示例
        {"city":"地市行政编码"}
    @apiSuccessExample {json} 成功返回
        {
            "message": "",
            "next": "",
            "data": [
                {
                    "id": "410381",
                    "name": "偃师市"
                },
                {
                    "id": "410301",
                    "name": "市辖区"
                }
            ],
            "response": "ok",
            "error": ""
        }
    """
    args = request.QUERY.casts(city=str)
    city = args.city or ''

    data = common.get_counties(city)
    return ajax.jsonp_ok(request, data)


@ajax_try([])
def p_schools(request):
    """
    @api {get} /class/schools [班级]学校列表
    @apiGroup class
    @apiParamExample {json} 请求示例
        {"county":"县区行政编码", "keyword":搜索关键词(学校名或学校ID)}
    @apiSuccessExample {json} 成功返回
        {
            "message": "",
            "next": "",
            "data": [
                {
                    "learn_length": 3,
                    "ecid": "",
                    "type": 2,
                    "id": 744,
                    "name": "洛阳市第七中学"
                },
            ],
            "response": "ok",
            "error": ""
        }
    """
    args = request.QUERY.casts(county=str, keyword=unicode)
    county = args.county or ''
    keyword = args.keyword or u''

    if not county:
        return ajax.jsonp_fail(request, message="缺少参数: county")

    data = common.get_schools(county, keyword)
    return ajax.jsonp_ok(request, data)


@ajax_try([])
def p_departments(request):
    """
    @api {get} /class/departments [班级]部门列表
    @apiGroup class
    @apiParamExample {json} 请求示例
        {"school_id": 学校ID}
    @apiSuccessExample {json} 成功返回
        {
            "message": "",
            "next": "",
            "data": [
                {
                    "id": 部门ID,
                    "name": "小学部",
                    "type": 部门类型 1小学 2初中,
                    "learn_length": 3,  # 学制 3年制 6年制
                    "max_class": 30, # 最大可选班级编号
                },
            ],
            "response": "ok",
            "error": ""
        }
    """
    args = request.QUERY.casts(school_id=str)
    school_id = args.school_id or ''
    depts = common.get_depts(school_id)

    return ajax.jsonp_ok(request, depts)


@ajax_try("")
@com_user.need_login
def p_join(request):
    """
    @api {post} /class/join [班级]加入班级接口
    @apiGroup class
    @apiParamExample {json} 请求示例
        {"dept_id": 部门ID, "grade_id":年级, "class_id":班级}
        或者
        {"unit_id": 班级ID}
    @apiSuccessExample {json} 成功返回
        {
            "message": "",
            "next": "",
            "data": {
                "unit_id": 580564   # 新班级ID
            },
            "response": "ok",
            "error": ""
        }
    @apiSuccessExample {json}  失败返回
        {
            "message": "您已经在当前班级",
            "next": "",
            "data": "",
            "response": "fail",
            "error": ""
        }
    """
    args = request.QUERY.casts(dept_id=int, grade_id=int, class_id=int, unit_id=int)
    dept_id = args.dept_id or 0
    grade_id = args.grade_id or 0
    class_id = args.class_id or 0
    unit_id = args.unit_id or 0

    user = request.user
    cache.user_profile.delete(user.id)
    cache.user_units.delete(user.id)
    if unit_id:
        ok, error = common.joinclass_id(user, unit_id)
        if not ok:
            return ajax.jsonp_fail(request, message=error)
        return ajax.jsonp_ok(request, {'unit_id': unit_id})

    if not dept_id:
        return ajax.jsonp_fail(request, message="缺少参数")
    if grade_id < 1 or grade_id > 9:
        return ajax.jsonp_fail(request, message="参数错误: grade_id")
    if class_id < 0 or class_id > 30:
        return ajax.jsonp_fail(request, message="参数错误: class_id")

    unit_id, error = common.joinclass(user, dept_id, grade_id, class_id)
    if not unit_id:
        return ajax.jsonp_fail(request, message=error)
    return ajax.jsonp_ok(request, {'unit_id': unit_id})


@ajax_try("")
@com_user.need_login
def p_quit(request):
    """
    @api {post} /class/quit [班级]退出班级接口
    @apiGroup class
    @apiParamExample {json} 请求示例
        {"unit_class_id": 班级ID(多个用逗号分割)}
    @apiSuccessExample {json} 成功返回
        {
            "message": "",
            "next": "",
            "data": "",
            "response": "ok",
            "error": ""
        }
    """
    args = request.QUERY.casts(unit_class_id=str)
    unit_ids = args.unit_class_id
    unit_ids = [int(s) for s in unit_ids.split(',') if s]
    if not unit_ids:
        return ajax.jsonp_fail(request, message='缺少参数: unit_class_id')
    user = request.user
    common.quitclass(user, unit_ids)
    return ajax.jsonp_ok(request)


@ajax_try("")
@com_user.need_login
def p_update_student(request):
    """
    @api {post} /class/student/update [班级]更新学生信息
    @apiGroup class
    @apiParamExample {json} 请求示例
        {"user_id":学生ID, "name":姓名, "sex":1男2女}
    @apiSuccessExample {json} 成功返回
        {"message": "", "next": "", "data": "", "response": "ok", "error": ""}
    @apiSuccessExample {json} 失败返回
        {
            "message": "名字必须是2-5个汉字",
            "next": "",
            "data": "",
            "response": "fail",
            "error": ""
        }
    """
    args = request.QUERY.casts(user_id=int, name=unicode, sex=int)
    student_id = args.user_id or 0
    name = args.name or u''
    sex = args.sex or 0
    if name and not is_chinese_word(name):
        return ajax.jsonp_fail(request, message='姓名长度为2-5个汉字')
    user = request.user
    if not common.is_mystudent(user, student_id):
        return ajax.jsonp_fail(request, message='权限错误')
    thread_pool.call(common.update_student_info, student_id, name, sex)
    return ajax.jsonp_ok(request)


@ajax_try("")
@com_user.need_login
def p_remove_student(request):
    """
    @api {post} /class/student/remove [班级]移除班级学生
    @apiGroup class
    @apiParamExample {json} 请求示例
        {"user_id":学生ID(多个用逗号分割)}
    @apiSuccessExample {json} 成功返回
        {"message": "", "next": "", "data": "", "response": "ok", "error": ""}
    """
    args = request.QUERY.casts(user_id=str)
    student_ids = args.user_id
    student_ids = [int(s) for s in student_ids.split(',') if s]
    if not student_ids:
        return ajax.jsonp_fail(request, message='缺少参数: user_id')
    user = request.user
    student_ids = common.filter_mystudents(user, student_ids)
    if not student_ids:
        return ajax.jsonp_fail(request, message='权限错误')
    common.remove_student(user, student_ids)
    return ajax.jsonp_ok(request)


@ajax_try({})
@com_user.need_login
def p_getpwd(request):
    """
    @api {get} /class/getpwd [班级]返回学生帐号和伪密码
    @apiGroup class
    @apiParamExample {json} 请求示例
        {"user_id":学生ID}
    @apiSuccessExample {json} 成功返回
        {
            "message": "",
            "next": "",
            "data": {
                "username": "15981867201xs",
                "password": "11***1"
            },
            "response": "ok",
            "error": ""
        }
    """
    args = request.QUERY.casts(user_id=int)
    user_id = args.user_id or 0
    user = request.user
    if not common.is_mystudent(user, user_id):
        return ajax.jsonp_fail(request, message='权限错误')
    data = common.getpwd(user_id) or {}
    print '+++++', data
    return ajax.jsonp_ok(request, data)


@ajax_try("")
@com_user.need_login
def p_sendpwd(request):
    """
    @api {post} /class/sendpwd [班级]发送学生帐号和密码
    @apiGroup class
    @apiParamExample {json} 请求示例
        {"user_id":学生ID(多个用逗号分割)}
    @apiSuccessExample {json} 成功返回
        {"message": "", "next": "", "data": "", "response": "ok", "error": ""}
    """
    args = request.QUERY.casts(user_id=str)
    student_ids = args.user_id or ''
    if not student_ids:
        return ajax.jsonp_fail(request, message='缺少参数: user_id')
    student_ids = [int(s) for s in student_ids.split(',') if s]
    user = request.user
    student_ids = common.filter_mystudents(user, student_ids)
    if not student_ids:
        return ajax.jsonp_fail(request, message='权限错误: 只能给自己班的学生发送帐号密码')
    user = request.user
    com_class.send_password(student_ids, sender={"send_phone": user.phone_number})
    return ajax.jsonp_ok(request)


@ajax_try("")
@com_user.need_login
def p_add_student(request):
    """
    @api {post} /class/student/add [班级]添加学生接口
    @apiGroup class
    @apiParamExample {json} 请求示例
        {"unit_id":班级ID, name:姓名, sex:性别(1男2女), phone_number:手机号, 
         "status":开通操作(1短信开通 2验证码开通 3暂不开通), "code":验证码(可选),
         "sendpwd":是否下发账号密码(0不下发 1 下发)}
    @apiSuccessExample {json} 成功返回
        {"message": "", "next": "", "data": "", "response": "ok", "error": ""}
    @apiSuccessExample {json} 失败返回
        {
            "message": "添加失败!同一手机号最多可生成1个账号",
            "next": "",
            "data": "",
            "response": "fail",
            "error": ""
        }
    """
    user = request.user
    args = request.QUERY.casts(unit_id=int, name=unicode, sex=int,
                               phone_number=str, status=int, code=str, sendpwd=int)
    unit_class_id = args.unit_id or 0  # 班级
    real_name = args.name or u''  # 姓名
    real_name = real_name.strip()
    sex = args.sex  # 性别
    phone_number = args.phone_number  # 手机号
    status = args.status or 0  # 1短信开通 2验证码开通 3暂不开通
    sncode = args.code  # sncode
    sendpwd = args.sendpwd  # 是否下发账号密码 0 不下发 1 下发

    if not is_chinese_word(real_name):
        return ajax.jsonp_fail(request, message='姓名必须是2-5个汉字')
    if not RE_CHINAMOBILE.match(phone_number):
        return ajax.jsonp_fail(request, message='请输入正确的移动手机号')
    open_option = 'open' if status == 1 else ''
    sncode = '' if status == 3 else sncode
    error = common.import_student(request, user, unit_class_id, real_name, sex, phone_number,
                                  open_option=open_option, sncode=sncode, send_pwd=sendpwd)
    if error:
        return ajax.jsonp_fail(request, message=error)
    return ajax.jsonp_ok(request)


@ajax_try({})
@com_user.need_login
def p_students(request):
    """
    @api {get} /class/students [班级]老师班级学生列表
    @apiGroup class
    @apiParamExample {json} 请求示例
        {"unit_id":班级ID}
    @apiSuccessExample {json} 成功返回
        {
            "message": "",
            "next": "",
            "data": {
                "students": [
                    {
                        "phone_number": "15981867201",
                        "abb": "lq",
                        "user_id": 630445,
                        "portrait": "http://student.tbkt.cn/site_media/images/profile/default-student.png", # 头像
                        "billing": 2, # 1体验状态 2计费状态
                        "ECID": "65489089010800",
                        "send_open": 0, # 0表示未下发开通请求 1表示已经下发了开通请求
                        "is_status": 1, # 0表示非暂存 1表示暂存
                        "sex": 1,   # 性别 1男 2女
                        "state": "open", # 总状态: trial试用 open已开通 unopen未开通
                        "status": 2, # 学科开通状态 2已开通 9永久试用 4以退订 2和9都算开通
                        "billing_date": "2016-08-05 10:57:02", # 计费时间
                        "open_date": "2016-07-05 10:57:02",    # 开通时间
                        "user_name": "洛奇"
                    }
                ],
                "open_num": 1,  # 班级开通人数
                "unopen_num": 0,  # 班级未开通人数
                "trial_count": 0,   # 班级试用人数
                "student_num": 1    # 班级总人数
            },
            "response": "ok",
            "error": ""
        }
    """
    args = request.QUERY.casts(unit_id=int)
    unit_id = args.unit_id or 0
    user = request.user
    data = common.get_user_students(user, unit_id)
    return ajax.jsonp_ok(request, data)


@ajax_try({})
@com_user.need_login
def p_students_num(request):
    """
    @api {get} /class/studentsNum [班级]老师班级学生数
    @apiGroup class
    @apiSuccessExample {json} 成功返回
        {
            "message": "",
            "next": "",
            "data": {
                123:{name:201班，stu_num:10}
            },
            "response": "ok",
            "error": ""
        }
    """
    user = request.user
    data = {}
    for u in user.units:
        stu = common.get_unit_students(user, u.id)
        d = dict()
        d['stu_num'] = len(stu)
        d['name'] = u.name
        data[u.id] = d
    return ajax.jsonp_ok(request, data)


@ajax_try({})
def p_byphone(request):
    """
    @api {get} /class/byphone [班级]按老师手机号查班级
    @apiGroup class
    @apiParamExample {json} 请求示例
        {"phone_number":"15981867201"}
    @apiSuccessExample {json} 成功返回
        {
            "message": "",
            "next": "",
            "data": [
                {
                    "id": 515192,
                    "name": "301班"
                },
            ],
            "response": "ok",
            "error": ""
        }
    @apiSuccessExample {json} 失败返回
        {
            "message": "未找到该教师",
            "next": "",
            "data": "",
            "response": "fail",
            "error": ""
        }
    """
    args = request.QUERY.casts(phone_number=str)
    phone = args.phone_number or ''
    user = request.user
    units, error = common.get_units_by_phone(user, phone)
    if error:
        return ajax.jsonp_fail(request, message=error)
    return ajax.jsonp_ok(request, units)


@ajax_try({})
def p_teachers(request):
    """
    @api {get} /class/teachers [班级]获取班级老师列表
    @apiGroup class
    @apiParamExample {json} 请求示例
        {"unit_id":班级ID}
    @apiSuccessExample {json} 成功返回
        {
            "message": "",
            "next": "",
            "data": {
                "teachers": [
                    {
                        "id": 4210824, # 老师ID
                        "name": "洛奇", # 老师姓名
                        "sid": 2, # 老师学科ID
                    }
                ],
            },
            "response": "ok",
            "error": ""
        }
    """
    args = request.QUERY.casts(unit_id=int)
    unit_id = args.unit_id or 0
    user = request.user
    data = common.get_class_teachers(user, unit_id)
    return ajax.jsonp_ok(request, data)


@ajax_try("")
@com_user.need_login
def p_sendsms(request):
    """
    @api {post} /class/sendsms [班级]发送班级短信
    @apiGroup class
    @apiParamExample {json} 请求示例
        {"unit_id": 班级ID, "content":短信内容}
    @apiSuccessExample {json} 失败返回
        {
            "message": "您没有该班级的发送权限",
            "next": "",
            "data": null,
            "response": "fail",
            "error": ""
        }
    @apiSuccessExample {json} 成功返回
        {"message": "", "next": "", "data": "", "response": "ok", "error": ""}
    """
    args = request.QUERY.casts(unit_id=int, content=unicode)
    unit_id = args.unit_id
    content = args.content
    if not unit_id:
        return ajax.jsonp_fail(request, message='缺少参数: unit_id')
    if not content:
        return ajax.jsonp_fail(request, message='短信内容不能为空')
    if len(content) > 200:
        return ajax.jsonp_fail(request, message='短信内容不能超过200字')

    user = request.user
    unit_ids = [u.id for u in user.all_units]
    if unit_id not in unit_ids:
        return ajax.jsonp_fail(request, message='您没有该班级的发送权限')

    students = common.get_unit_students(user, unit_id)
    phones = [s.phone_number for s in students]
    phones = list(set(phones))
    if phones:
        phones_s = ','.join(phones)
        hub = tbktapi.Hub(request)
        hub.sms.post('/sms/send', {'platform_id': user.platform_id, 'phone': phones_s, 'content': content})
    return ajax.jsonp_ok(request)
