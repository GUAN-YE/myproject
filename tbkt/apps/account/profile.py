# coding: utf-8

import datetime
from django.conf import settings

from apps.system.common import get_upload_key
from libs.utils import Struct, ajax, is_chinese_word, db, auth, ajax_try, tbktapi
from apps.common import com_user
from . import common


@ajax_try({})
@com_user.need_login
def p_profile(request):
    """
    @api {get} /account/profile [个人设置]获取个人数据
    @apiGroup account
    @apiSuccessExample {json} 成功返回
        {
            "message": "",
            "next": "",
            "data": {
                "id": 897447,
                "name": "9527",  # 姓名
                "type": 3,  # 用户类型 1学生 3老师
                "dept_type": 部门类型, # 1小学 2初中
                "phone": "15981867201", # 手机号
                "portrait": "http://file.tbkt.cn/upload_media/portrait/2016/11/01/20161101114745587631.png",  # 头像
                "subject_id": 21,  # 老师学科ID
                "grades": [3, 4],  # 老师所在年级列表
                "grade_id": 3, # 老师当前年级
                "platform_id": 用户平台ID,
                "login_version": "IOS 1.3", # 本次登录版本号
                "units": [
                    {
                        "id": 515192,
                        "city": "410100", # 所在城市
                        "county": "411702", # 所在县区
                        "name": "301班", 
                        "class_id": 1, # 班级
                        "type": 1, # 部门类型: 1小学 2初中
                        "school_name": "高新区大谢中学",  # 学校
                        "grade_id": 3, # 年级
                        "unit_class_id": 515192, # 班级ID
                        "school_id": 21  # 学校ID
                    },
                ], # 所在班级
            },
            "response": "ok",
            "error": ""
        }
    """
    user = request.user
    units = user.units

    profile = Struct({
        "id": user.id,
        "name": user.real_name,
        "bind_id": user.id,
        "sex": user.sex,
        "phone": user.phone_number,
        "portrait": user.portrait,
        "border": user.border,
        "units": units,
        "type": user.type,
        "dept_type": user.dept_type,
        "subject_id": user.subject_id,
        "platform_id": user.platform_id
    })
    if user.is_teacher:
        profile.grades = user.grades
        profile.grade_id = user.grade_id

    return ajax.jsonp_ok(request, profile)


@ajax_try({})
@com_user.need_login
def p_units(request):
    """
    @api {get} /account/units [个人设置]获取用户班级
    @apiGroup account
    @apiSuccessExample {json} 成功返回
        {
            "message": "",
            "next": "",
            "data": {
                "units": [
                    {
                        "id": 515192,
                        "city": "410100", # 所在城市
                        "name": "301班", 
                        "class_id": 1, # 班级
                        "type": 1, # 部门类型: 1小学 2初中
                        "school_name": "高新区大谢中学",  # 学校
                        "grade_id": 3, # 年级
                        "unit_class_id": 515192, # 班级ID
                        "school_id": 21,  # 学校ID
                        "size": 9  # 班级学生人数
                    },
                ], # 所在班级
            },
            "response": "ok",
            "error": ""
        }
    """
    user = request.user
    units = user.units
    unit_ids = [u.id for u in units]
    sized = common.gets_unit_size(user, unit_ids)
    for u in units:
        u.size = sized.get(u.id) or 0

    data = {
        'units': units
    }
    return ajax.jsonp_ok(request, data)


@ajax_try("")
@com_user.need_login
def p_name(request):
    """
    @api {post} /account/name [个人设置]修改名字
    @apiGroup account
    @apiParamExample {json} 请求示例
        {"name":"新名字"}
    @apiSuccessExample {json} 成功返回
        {"message": "", "error": "", "data": "", "response": "ok", "next": ""}
    @apiSuccessExample {json} 失败返回
        {"message": "修改失败，请重试", "error": "", "data": "", "response": "fail", "next": ""}
    """
    args = request.QUERY.casts(name=unicode)
    name = args.name
    user = request.user
    data = {
        'flag': "0",
        'user_id': user.id
    }
    if not name:
        return ajax.jsonp_fail(request, message="姓名不能为空")
    if not is_chinese_word(name):
        return ajax.jsonp_fail(request, message="姓名长度为2-5个汉字")
    if user.type==1:
        result=common.real_name_filter(name)
        if not result:
            data = {
                'flag': "1",
                'user_id': user.id
            }
            return ajax.jsonp_ok(request, data)
    user.set_name(name)

    return ajax.jsonp_ok(request,data)


@ajax_try("")
@com_user.need_login
def p_sex(request):
    """
    @api {post} /account/sex [个人设置]修改性别
    @apiGroup account
    @apiParamExample {json} 请求示例
        {"sex":1男 2女}
    @apiSuccessExample {json} 成功返回
        {"message": "", "error": "", "data": "", "response": "ok", "next": ""}
    @apiSuccessExample {json} 失败返回
        {"message": "修改失败，请重试", "error": "", "data": "", "response": "fail", "next": ""}
    """
    args = request.QUERY.casts(sex=int)
    sex = args.sex
    if not sex:
        return ajax.jsonp_fail(request, message="参数不能为空")

    user = request.user
    user.set_sex(sex)

    return ajax.jsonp_ok(request)


@ajax_try("")
@com_user.need_login
def p_portrait(request):
    """
    @api {post} /account/portrait [个人设置]修改头像
    @apiGroup account
    @apiParamExample {json} 请求示例
        {"img_url":"portrait/2009/08/24/small_super.png"}
    @apiSuccessExample {json} 成功返回
        {"message": "", "error": "", "data": "头像url", "response": "ok", "next": ""}
    @apiSuccessExample {json} 失败返回
        {"message": "修改失败，请重试", "error": "", "data": "", "response": "fail", "next": ""}
    """
    args = request.QUERY.casts(img_url=str)
    img_url = args.img_url or ''

    user = request.user
    abs_url = user.set_portrait(img_url)

    return ajax.jsonp_ok(request, abs_url)


@ajax_try("")
@com_user.need_login
def p_password(request):
    """
    @api {post} /account/password [个人设置]修改密码
    @apiGroup account
    @apiParamExample {json} 请求示例
        {"old_pwd":"111111","new_pwd":"2222222"}
    @apiSuccessExample {json} 成功返回
        {"message": "", "error": "", "data": "", "response": "ok", "next": ""}
    @apiSuccessExample {json} 失败返回
        {"message": "两次输入密码不一致", "error": "", "data": "", "response": "fail", "next": ""}
    """
    args = request.QUERY.casts(old_pwd=str, new_pwd=str)
    old_pwd = args.old_pwd or ''
    new_pwd = args.new_pwd or ''
    if len(new_pwd) < 6 or len(new_pwd) > 16:
        return ajax.jsonp_fail(request, message='密码长度为6-16个字符')
    user = request.user
    if old_pwd and not user.check_password(old_pwd):
        return ajax.jsonp_fail(request, message="当前密码错误")

    users = user.set_password(new_pwd)
    # 发短信
    content = u"密码修改成功，" + ','.join(u'账号%s的新密码为%s' % (u.username, new_pwd) for u in users) + u"，请牢记！"
    hub = tbktapi.Hub(request)
    hub.sms.post('/sms/send', {'platform_id': user.platform_id, 'phone': user.phone, 'content': content})

    return ajax.jsonp_ok(request)


@ajax_try("")
@com_user.need_login
def p_grade(request):
    """
    @api {post} /account/grade [个人设置]设置教师当前年级
    @apiGroup account
    @apiParamExample {json} 请求示例
        {"grade_id": 1}
    @apiSuccessExample {json} 成功返回
        {"message": "", "error": "", "data": "", "response": "ok", "next": ""}
    @apiSuccessExample {json} 失败返回
        {"message": "年级错误", "error": "", "data": "", "response": "fail", "next": ""}
    """
    args = request.QUERY.casts(grade_id=int)
    grade_id = args.grade_id or 0
    if grade_id < 1 or grade_id > 9:
        return ajax.jsonp_fail(request, message='参数错误: grade_id')

    user = request.user
    if grade_id not in user.grades:
        return ajax.jsonp_fail(request, message='年级错误')

    if user.grade_id != grade_id:
        user.set_grade(grade_id)

    return ajax.jsonp_ok(request)


@ajax_try([])
@com_user.need_login
def p_accounts(request):
    """
    @api {get} /account/accounts [个人设置]获得当前帐户关联的所有帐号
    @apiGroup account
    @apiSuccessExample {json} 成功返回
        {
            "message": "",
            "next": "",
            "data": [
                {
                    "user_id": 5317130,
                    "name": "9527",
                    "subject_id": 21,  # 老师学科21小学数学 91小学英语
                    "unit_name": "新野县春晖学校710班",
                    "grade_id": 7, # 所在年级
                    "role": "数学老师",
                    "portrait": "http://file.tbkt.cn/upload_media/yyyy",
                    "type": 3  # 帐号类型 1学生 3老师
                }
            ],
            "response": "ok",
            "error": ""
        }
    """
    user = request.user
    if int(user.platform_id) == 4 and int(user.type) == 1:  # 江苏用户切换账号
        accounts = common.get_js_account(user)
    else:
        accounts = common.get_accounts(user)
    return ajax.jsonp_ok(request, accounts)


@ajax_try({})
@com_user.need_login
def p_switch(request):
    """
    @api {post} /account/switch [个人设置]切换帐号
    @apiGroup account
    @apiParamExample {json} 请求示例
        {"user_id":用户ID, "grade_id":年级}

        *新增grade_id参数: 表示切换到某个帐号的某个年级
    @apiSuccessExample {json} 成功返回
        {
            "message": "",
            "next": "",
            "data": {
                "user_id": 897447
            },
            "response": "ok",
            "error": ""
        }

        这里会重新设置token
    @apiSuccessExample {json} 失败返回
        {
            "message": "",
            "next": "",
            "data": "",
            "response": "fail",
            "error": "缺少参数: user_id"
        }
    """
    args = request.QUERY.casts(user_id=int, bind_id=int, grade_id=int)
    user_id = args.user_id or args.bind_id or 0
    grade_id = args.grade_id
    if not user_id:
        return ajax.jsonp_fail(request, message="缺少参数: user_id")
    user = request.user

    spec = db.user_slave.auth_user.get(id=user_id)
    if not spec:
        return ajax.jsonp_fail(request, message="服务器开小差: spec")
    # 验证spec必须跟当前用户有关联
    if user.phone != spec.phone:
        return ajax.jsonp_fail(request, message="无权登录他人的帐号")
    # 老师只能切换到老师, 学生只能切换到学生
    if user.type != spec.type:
        return ajax.jsonp_fail(request, message="用户类型不匹配")

    user = com_user.User(spec) if spec else None
    if not user:
        return ajax.jsonp_fail(request, message="服务器开小差: user")
    error = com_user.app_login_check(user)
    if error:
        return ajax.jsonp_fail(request, message=error)
    # 切换年级
    if grade_id and grade_id in user.grades:
        user.set_grade(grade_id)
    auth.login(request, user.id)
    return ajax.jsonp_ok(request, {'user_id': user.id})


@ajax_try({})
@com_user.need_login
def p_book(request):
    """
    @api {get} /account/book [个人设置]获取当前教材/教辅
    @apiGroup account
    @apiParamExample {json} 请求示例
        {"subject_id":学科ID, "type":1教材 2教辅}
    @apiSuccessExample {json} 成功返回
        {
            "message": "",
            "next": "",
            "data": {
                "press_name": "西南师范大学出版社",  # 出版社
                "name": "小学数学四年级上册",  # 默认书名
                "subject_id": 21,  # 学科
                "grade_id": 4,  # 年级
                "volume": 1,  # 1上册 2下册 3全册
                "version_name": "2015新版",  # 版本
                "id": 888  # 教材/教辅ID
            },
            "response": "ok",
            "error": ""
        }
    @apiSuccessExample {json} 失败返回
        {
            "message": "缺少参数: type",
            "next": "",
            "data": "",
            "response": "fail",
            "error": ""
        }
    """
    args = request.QUERY.casts(subject_id=int, type=int)
    subject_id = args.subject_id or 0
    type = args.type or 0

    if not subject_id:
        return ajax.jsonp_fail(request, message='缺少参数: subject_id')
    if not type:
        return ajax.jsonp_fail(request, message='缺少参数: type')
    if type not in (1, 2):
        return ajax.jsonp_fail(request, message='参数值错误: type')

    user = request.user
    if type == 1:
        book = user.get_book(subject_id)
    elif type == 2:
        book = user.get_pbook(subject_id)
    return ajax.jsonp_ok(request, book)


@ajax_try({})
def p_uploadurl(request):
    """
    @api {get} /account/uploadurl [个人设置]获取上传URL
    @apiGroup account
    @apiParamExample {json} 请求示例
        {"dir":目录名(头像portrait)}
    @apiSuccessExample {json} 成功返回
        {
            "message": "",
            "next": "",
            "data": {
                "url": "http://file.tbkt.cn/swf_upload/?upcheck=e36637e0019323357cfad92fb9a64d17&upType=portrait"
            },
            "response": "ok",
            "error": ""
        }
        上传步骤:
        1. 先获得上传url
        2. 把图片传上去, 返回正式图片地址
        3. 把正式图片地址传给[修改头像]接口
    @apiSuccessExample {json} 失败返回
        {
            "message": "缺少参数: dir",
            "next": "",
            "data": "",
            "response": "ok",
            "error": ""
        }
    """
    args = request.QUERY.casts(dir=str)
    dir = args.dir or ""
    if not dir:
        return ajax.jsonp_ok(request, message="缺少参数: dir")
    upload_key = get_upload_key()
    url = settings.FILE_UPLOAD_URLROOT + "/swf_upload/?upcheck=%s&upType=%s" % (upload_key, dir)
    data = {
        'url': url
    }
    return ajax.jsonp_ok(request, data)


@ajax_try({})
@com_user.need_login
def p_third(request):
    """
    @api {get} /account/third [个人设置]获取对应第三方信息
    @apiGroup account
    @apiSuccessExample {json} 成功返回
    {
        "message": "",
        "next": "",
        "data": {
            "third_id": 第三方用户id,       
            "province_id": 第三方用户城市信息
            "name":xxxx
        },
        "response": "ok",
        "error": ""
    }
    """
    user = request.user
    data = common.get_third_info(user)
    return ajax.jsonp_ok(request, data)


@ajax_try({})
@com_user.need_login
def p_third_open(request):
    """
    @api {get} /account/third/open [个人设置]获取对应第三方信息
    @apiGroup account
    @apiParamExample {json} 请求示例
    {"third_id": 第三方,
     "product_id": 资费id,
     "pay_type": 开通,
     "success_url": 成功回调url,
     "fail_url": 失败回调url
    }
    @apiSuccessExample {json} 成功返回
    {
        "message": "",
        "next": "",
        "data": {
            第三方url
        },
        "response": "ok",
        "error": ""
    }
    """
    args = request.QUERY.casts(third_id=str, product_id=str, pay_type=int, success_url=str, fail_url=str)
    third_id = args.third_id
    product_id = args.product_id
    pay_type = args.pay_type
    success_url = args.success_url
    fail_url = args.fail_url
    if not third_id or not product_id or not success_url or not fail_url:
        return ajax.jsonp_fail(request, message='缺少参数！')
    data = common.qg_open_subject(third_id, product_id, pay_type, success_url, fail_url)
    return ajax.jsonp_ok(request, data)


@ajax_try({})
@com_user.need_login
def p_qg_tiyan(request):
    """
    @api {post} /account/third/qg_tiyan [个人设置]北京免费体验
    @apiGroup account
    @apiParamExample {json} 请求示例
    {"third_id": 第三方,
     "groupId": 子组合ID,
     "province_id": 第三方省份id,
    }
    @apiSuccessExample {json} 成功返回
    {
        "message": "",
        "next": "",
        "data": {
        },
        "response": "ok",
        "error": ""
    }
    """
    args = request.QUERY.casts(third_id=str, groupId=str, province_id=int)
    third_id = args.third_id
    groupId = args.groupId
    province_id = args.province_id
    hub = tbktapi.Hub()
    url = '/api/openFree/'
    data = dict(
        third_id=third_id,
        groupId=groupId,
        provinceId=province_id,
        terminalType=4,
        serviceType=2
    )
    r = hub.qg.post(url, data)
    data = {}
    if r['response'] == 'fail':
        return ajax.jsonp_fail(request, data)
    return ajax.jsonp_ok(request, data)


@ajax_try({})
@com_user.need_login
def p_border_status(request):
    """
    @api {get} /account/border/status [个人设置]判断更换边框按钮是否显示
    @apiGroup account
    @apiSuccessExample {json} 成功返回
    {
        "message": "",
        "next": "",
        "data": {
            status:1  1：开启，0：不开
        },
        "response": "ok",
        "error": ""
    }
    """
    status = 1
    return ajax.jsonp_ok(request, {'status': status})


@ajax_try({})
@com_user.need_login
def p_border(request):
    """
    @api {get} /account/border/list [个人设置]获取用户边框列表
    @apiGroup account
    @apiSuccessExample {json} 成功返回
    {
        "message": "",
        "next": "",
        "data": {
            list :[
                id:1
                border_url:'http://file.tbkt.cn/swf_upload/?upcheck=e36637e0019323357cfad92fb9a64d17&upType=portrait'

            ]
            user_border_id:1    没有为0
        },
        "response": "ok",
        "error": ""
    }
    """
    user_id = request.user_id
    user_border = db.slave.user_border_detail.filter(user_id=user_id)
    if not user_border:
        border_list = common.get_borders(user_id)
        return ajax.jsonp_ok(request, {'list': border_list, 'user_border_id': 0})
    for i in user_border:
        user_border_id = 0
        if i.status == 1:
            user_border_id = i.border_id
            break
    border_list = common.get_borders(user_id)
    return ajax.jsonp_ok(request, {'list': border_list, 'user_border_id': user_border_id})


@ajax_try({})
@com_user.need_login
def p_change_border(request):
    """
    @api {get} /account/border/change [个人设置]用户更换边框
    @apiGroup account
    @apiParamExample {json} 请求示例
    {
        "border_id":1
    }
    @apiSuccessExample {json} 成功返回
    {
        "message": "",
        "next": "",
        "data": {},
        "response": "ok",
        "error": ""
    }
    """
    user_id = request.user_id
    args = request.QUERY.casts(border_id=int)
    border_id = args.border_id
    if not border_id:
        return ajax.jsonp_fail(request, u'缺少参数')
    success, why = common.change_border(user_id, border_id)
    if not success:
        return ajax.jsonp_fail(request, why)
    return ajax.jsonp_ok(request, success)
