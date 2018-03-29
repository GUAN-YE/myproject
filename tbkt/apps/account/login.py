# coding: utf-8
import datetime
import random
import re

import common
from apps.common import com_user
from apps.common.com_cache import cache
from apps.common.com_user import get_portrait
from libs.utils import ajax, is_chinamobile, auth, db, ajax_try, \
    is_chinese_word, thread_pool, validate_phone_platform, tbktapi, Struct
from libs.utils.auth import create_token

RE_TEACHER_USERNAME = re.compile(r'^[0-9]{11}(js){0,1}\d*$')
RE_STUDENT_USERNAME = re.compile(r'^[0-9]{11}(xs){0,1}\d*$')

@ajax_try("")
def p_login(request, role):
    """
    @api {post} /account/login/? [登录]登录
    @apiGroup account
    @apiParamExample {json} 请求示例
        /account/login/s 学生登录
        /account/login/t 老师登录

        {
            "username":"15038035398", 
            "password":"111111",
            "pass_flag": 1      # 0 以前的老接口，不加密，  1 现在的新程序，加密
            "login_type": 90,   # 登录类型 1是网站 其他是手机APP
            "version": "6.0.1", 
            "name": "865f8521b18fe9b",
            "model": "MI 4LTE",
            "platform": "Android",
            "uuid": "A100005064E391",
            "appversion": "1.0.0"
        }
    @apiParam {String} username 手机号或帐号
    @apiParam {String} password 密码
    @apiParam {Integer} login_type (可选)登录类型 88:Android教辅学生 90:Android教辅教师 89:IOS教辅学生 91:IOS教辅教师
    @apiParam {String} version (可选)系统版本号
    @apiParam {String} name (可选)设备名称
    @apiParam {String} model (可选)手机型号
    @apiParam {String} platform (可选)平台名称
    @apiParam {String} uuid (可选)设备序列号
    @apiParam {String} appversion (可选)app版本
    @apiSuccessExample {json} 成功返回
        {
            "next": "",
            "error": "",
            "message": "",
            "tbkt_token": "eHl3dHR3PHF0eHh5dXlzcnY8cXR4eHF4dHVwdQ",
            "app_version": {
                "h5": 0,
                "api": 1,
                "must": 0
            },
            "data": "",
            "response": "ok"
        }

        登录成功后, 服务器会在响应头中添加 Tbkt-Token: xxxx 头域, 分配给客户端一个token.
        客户端应记录这个 tbkt_token 并在之后的请求中带上 Tbkt-Token: xxxx
        到时如果服务器没有收到 tbkt_token 或者 tbkt_token 过期(7天), 则返回:
        {
            "message": "请您先登录",
            "next": "",
            "data": "",
            "response": "fail",
            "error": "no_user"
        }
        
        其他请求也要看下响应头里有没有给新token, 有就更新token.

        检测新版本机制:
        客户端每个请求头加一个 App-Type: 9安卓学生 10安卓教师 11苹果学生 12苹果教师 13 H5学生 14 H5教师
        服务器返回头会加一个 App-Version: {"h5": H5版本号, "api": 客户端版本号, "must": 0不强制升级客户端 1强制升级客户端}
    @apiSuccessExample {json} 失败返回
        {"message": "帐号或密码错误", "error": "", "data": "", "response": "fail", "next": ""}

        如果error=switch就进入切换身份页面让他选角色
    @apiSuccessExample {json} Python示例
        import requests

        r = requests.post('http://127.0.0.1:4000/account/login/t', 
                        params={'username':'15981867201', 'password':'111111'})
        cookies = r.cookies
        r = requests.post('http://127.0.0.1:4000/class/getpwd', 
                        params={'bind_id':'4210824'}, cookies=cookies)
        print r.json()
    @apiSuccessExample {json} Java示例
        public static final MediaType JSON = MediaType.parse("application/json; charset=utf-8");
        OkHttpClient client = new OkHttpClient();
        String post(String url, String json) throws IOException {
            RequestBody body = RequestBody.create(JSON, json);
            Request request = new Request.Builder()
                    .addHeader("Cookie","tbkt_token="+tbkt_token)
                    .url(url)
                    .post(body)
                    .build();
            Response response = client.newCall(request).execute();
            if (response.isSuccessful()) {
                return response.body().string();
            } else {
                throw new IOException("Unexpected code " + response);
            }
        }

        // webview
        CookieManage cookiemanager = CookieManager.getInstance();
        cookiemanager.setAcceptCookie(true);
        cookiemanager.setCookie(url,"sessionid="+sessionid);
    @apiSuccessExample {json} C#示例
        HttpClient client = CreateClientASMtoken("");
        HttpResponseMessage response = client.GetAsync("http://localhost").Result;

        IEnumerable<string> rawCookies = response.Headers.GetValues("Set-Cookie");
    """
    # return ajax.jsonp_fail(request, message=u'系统升级,暂停服务 20点至次日18点', error=u'升级')
    args = request.QUERY.casts(username=str, password=str,
                               login_type=int, version=str, name=unicode, model=unicode, platform=str,
                               uuid=str, appversion=str, pass_flag=int)
    username = args.username or ''
    password = args.password or ''
    pass_flag = int(args.pass_flag or 0)
    username = username.strip().lower()
    if not username:
        return ajax.jsonp_fail(request, message='请输入用户名或手机号')
    if not password:
        return ajax.jsonp_fail(request, message='请输入密码')
    login_type = args.login_type

    if pass_flag:
        password = auth.safe_pass_decode(password)

    # 模糊匹配(根据手机号+密码猜测具体帐号)
    if username.isdigit():
        type = 3 if role == 't' else 1
        encoded_password = auth.encode_plain_password(password)
        sql = """
        select u.username, u.status from auth_user u
        inner join auth_profile p on p.user_id=u.id and p.password='%s'
        where u.phone='%s' and u.type=%s
        """ % (encoded_password, username, type)
        binds = db.user_slave.fetchall_dict(sql)
        if not binds:
            return ajax.jsonp_fail(request, message='账号或密码错误，是否找回密码?')

        now_binds = [b for b in binds if int(b.status) != 2]
        if not now_binds:
            return ajax.jsonp_fail(request, message="该账号已被禁用，请联系客服")

        bind = now_binds[0]
        if bind:
            username = bind.username
        elif role == 't':
            username += 'js'
        else:
            username += 'xs'

    elif role == 't' and not RE_TEACHER_USERNAME.match(username):
        return ajax.jsonp_fail(request, message='请输入正确的教师帐号')
    elif role == 's' and not RE_STUDENT_USERNAME.match(username):
        return ajax.jsonp_fail(request, message='请输入正确的学生帐号')

    user, auth_user = com_user.authenticate(username=username, password=password)
    if not user:
        return ajax.jsonp_fail(request, message='账号或密码错误，是否找回密码?')

    if int(user.status) == 2:
        return ajax.jsonp_fail(request, message='该账号已被禁用，请联系客服')

    # 登录检查
    if login_type > 1:
        error = com_user.app_login_check(user)
        if error:
            # 如果当前角色不让进, 通知他切换到别的角色
            n = db.user_slave.auth_user.filter(phone=user.phone_number, type=user.type).count()
            if n > 1:
                auth.login(request, user.id)
                return ajax.jsonp_fail(request, 'switch', message=error)
            return ajax.jsonp_fail(request, message=error)
    else:
        error = com_user.web_login_check(user)
        if error:
            return ajax.jsonp_fail(request, message=error)

    # 登录日志
    thread_pool.call(common.login_handle, request, args, user)

    data = {
        'flag': "0",
        'user_id': user.id
    }
    auth.login(request, user.id)
    if user.type==1:
        result=common.real_name_filter(user.real_name)
        if not result:
            data = {
                'flag': "1",
                'user_id': user.id
            }
            return ajax.jsonp_ok(request,data)
    return ajax.jsonp_ok(request, data)


@ajax_try("")
def p_vcode(request):
    """
    @api {post} /account/vcode [登录]发验证码
    @apiDescription 
        输入手机号, 发送验证码到手机
    @apiGroup account
    @apiParamExample {json} 请求示例
        {"platform_id": 平台ID, "phone_number":"15981867201"}
    @apiSuccessExample {json} 成功返回
    {
        "message": "密码将发送到你的手机上,请注意查收",
        "error": "",
        "data": "",
        "response": "ok",
        "next": ""
    }
    @apiSuccessExample {json} 失败返回
    {
        "message": "请填写移动手机号",
        "error": "",
        "data": "",
        "response": "fail",
        "next": ""
    }
    """
    args = request.QUERY.casts(platform_id=int, phone_number=str)
    platform_id = args.platform_id or 1
    phone = args.phone_number

    # if not platform_id:
    #     return ajax.jsonp_fail(request, message='请选择省份')
    if not phone:
        return ajax.jsonp_fail(request, message='请输入正确的移动手机号')
    if not is_chinamobile(phone):
        return ajax.jsonp_fail(request, message='请输入正确的移动手机号')
    if validate_phone_platform(phone, platform_id) == False:
        return ajax.jsonp_fail(request, message='手机号与省份不匹配')

    # 今日获取次数
    today = datetime.date.today()
    times = cache.vcode_sendtimes.get((phone, today)) or 0
    if times >= 3 and phone != "13525352553":
        return ajax.jsonp_fail(request, message='今日获取次数已达上限')
    cache.vcode_sendtimes.set((phone, today), times + 1)

    user = request.user
    code = ''.join(random.sample('0123456789', 6))
    cache.vcode.set(phone, code)
    real_code = cache.vcode.get(phone)
    print real_code, platform_id
    hub = tbktapi.Hub(request)
    r = hub.sms.post("/sms/send",
                     {"platform_id": platform_id, "phone": phone, "content": "同步课堂验证码为:%s, 5分钟内输入有效" % code})
    if not r:
        return ajax.jsonp_fail(request, message='系统异常')
    elif r.response == 'fail':
        return ajax.jsonp_fail(request, message=r.message)
    data = {'code': code}
    return ajax.jsonp_ok(request, data, message='')


@ajax_try("")
def p_findpwd(request):
    """
    @api {post} /account/findpwd [登录]找回密码
    @apiDescription 
        输入手机号和验证码, 发送帐号和明文密码到手机
    @apiGroup account
    @apiParamExample {json} 请求示例
        {"platform_id": 平台ID, "phone_number":"15981867201", "code":"6402"}
    @apiSuccessExample {json} 成功返回
    {
        "message": "",
        "error": "",
        "data": "",
        "response": "ok",
        "next": ""
    }
    @apiSuccessExample {json} 失败返回
    {
        "message": "验证码错误，请重新获取",
        "error": "",
        "data": "",
        "response": "fail",
        "next": ""
    }
    """
    args = request.QUERY.casts(platform_id=int, phone_number=str, code=str)
    platform_id = args.platform_id or 1
    phone = args.phone_number
    code = args.code

    if not phone:
        return ajax.jsonp_fail(request, message='请填写手机号')
    if not is_chinamobile(phone):
        return ajax.jsonp_fail(request, message='请输入正确的手机号')
    if not code:
        return ajax.jsonp_fail(request, message='请填写验证码')
    if validate_phone_platform(phone, platform_id) == False:
        return ajax.jsonp_fail(request, message='手机号与省份不匹配')

    real_code = cache.vcode.get(phone)
    print real_code, "real_code"
    if not code or code != real_code:
        return ajax.jsonp_fail(request, message='验证码错误，请重新获取')
    cache.vcode.delete(phone)  # 删除缓存

    user_ids = db.user_slave.auth_user.filter(phone=phone, platform_id=platform_id).select('id').flat('id')[:]
    if not user_ids:
        return ajax.jsonp_fail(request, message='该手机号未注册')
    userd = com_user.get_users(user_ids)
    text = u"您的帐号和密码是:\n"
    for u in userd.itervalues():
        password = u.plain_password
        text += u"%s,%s\n" % (u.username, password)
    text += u"请注意查收."
    hub = tbktapi.Hub(request)
    hub.sms.post('/sms/send', {'platform_id': platform_id, 'phone': phone, 'content': text})
    return ajax.jsonp_ok(request, message='密码将发到您手机上,请注意查收')


@ajax_try("")
def p_feedback(request):
    """
    @api {post} /account/feedback [登录]意见反馈
    @apiGroup account
    @apiParamExample {json} 请求示例
        {"type":请求类型(1意见建议 2错误反馈 3其他), "content":"反馈内容", "app":机型(android/ios/pc)}
    @apiSuccessExample {json} 成功返回
    {
        "message": "",
        "error": "",
        "data": "",
        "response": "ok",
        "next": ""
    }
    @apiSuccessExample {json} 失败返回
    {
        "message": "验证码错误，请重新获取",
        "error": "",
        "data": "",
        "response": "fail",
        "next": ""
    }
    """
    args = request.QUERY.casts(type=int, content=unicode, app=str)
    type = args.type or 1
    content = args.content or u''
    app = args.app or ''
    user_id = request.user_id

    if not content:
        return ajax.jsonp_fail(request, '请填写内容')
    common.feedback(user_id, type, content, app)

    return ajax.jsonp_ok(request)


@ajax_try("")
def p_register_student(request):
    """
    @api {post} /account/register/student [登录]快速注册学生帐号
    @apiDescription 
        输入手机号和开通验证码注册
    @apiGroup account
    @apiParamExample {json} 请求示例
        {"platform_id":平台ID, "phone_number":"15981867201", "dept_type":学段(1小学,2初中), 
         "code":二次开通短信验证码}

        *platform_id: 参考平台列表接口
    @apiSuccessExample {json} 成功返回
    {
        "message": "",
        "next": "",
        "data": {
            "username": "15981867223xs",  # 新账号
            "password": "286049",  # 新密码
            "user_id": 10831971    # 用户ID
        },
        "response": "ok",
        "error": ""
    }
    @apiSuccessExample {json} 失败返回
    {
        "message": "请填写移动手机号",
        "error": "",
        "data": "",
        "response": "fail",
        "next": ""
    }
    """
    args = request.QUERY.casts(phone_number=str, platform_id=int, dept_type=int, code=str)
    phone = args.phone_number or ''
    platform_id = args.platform_id or 1
    dept_type = args.dept_type
    code = args.code

    if not phone:
        return ajax.jsonp_fail(request, message='手机号不能为空')
    # if not platform_id:
    #     return ajax.jsonp_fail(request, message='请选择省份')
    if not dept_type or int(dept_type) not in (1, 2):
        return ajax.jsonp_fail(request, message='请选择学段')
    if not code:
        return ajax.jsonp_fail(request, message='验证码不能为空')
    if not code.isdigit() and len(code) != 6:
        return ajax.jsonp_fail(request, message='请输入正确的验证码')
    if not is_chinamobile(phone):
        return ajax.jsonp_fail(request, message='请输入正确的移动手机号')
    if validate_phone_platform(phone, platform_id) == False:
        return ajax.jsonp_fail(request, message='手机号与省份不匹配')
    if db.user_slave.auth_user.filter(phone=phone, type=1):
        return ajax.jsonp_fail(request, error="taken", message='手机号已被注册, 是否找回密码?')

    data = common.register_student(platform_id, phone, dept_type, code)
    if not data:
        return ajax.jsonp_fail(request, message='帐号已存在')
    return ajax.jsonp_ok(request, data)


@ajax_try("")
def p_register(request):
    """
    @api {post} /account/register [登录]注册帐号
    @apiDescription 
        学生老师都可以注册, 支持较多注册信息
    @apiGroup account
    @apiParamExample {json} 请求示例
        {
            "platform_id": 平台ID,
            "user_type": 用户类型(1学生 3老师), 
            "phone_number": "15981867201", 
            "name": 姓名, 
            "subject_id": 老师注册需要提供学科ID,
            "dept_type": 学段(1小学 2初中 学生必传,老师不用传)
            "code": 注册短信验证码
        }
    @apiSuccessExample {json} 成功返回
    {
        "message": "",
        "next": "",
        "data": {
            "username": "15981867223xs",  # 新账号
            "password": "286049",  # 新密码
            "user_id": 10831971    # 用户ID
        },
        "response": "ok",
        "error": ""
    }
    @apiSuccessExample {json} 失败返回
    {
        "message": "请填写移动手机号",
        "error": "",
        "data": "",
        "response": "fail",
        "next": ""
    }
    """
    args = request.QUERY.casts(platform_id=int, user_type=int, phone_number=str,
                               name=unicode, subject_id=int, dept_type=int, code=str)
    platform_id = args.platform_id or 1
    user_type = args.user_type or 1
    phone = args.phone_number or ''
    name = args.name or u''
    subject_id = args.subject_id
    dept_type = args.dept_type or 1
    code = args.code

    # if not platform_id:
    #     return ajax.jsonp_fail(request, message='缺少参数: platform_id')
    if user_type not in (1, 3):
        return ajax.jsonp_fail(request, message='参数错误: user_type')
    if user_type == 1 and not dept_type:
        return ajax.jsonp_fail(request, message='参数错误: dept_type')
    if int(dept_type) not in (1, 2):
        return ajax.jsonp_fail(request, message='参数错误: dept_type')
    if not phone:
        return ajax.jsonp_fail(request, message='手机号不能为空')
    if not code:
        return ajax.jsonp_fail(request, message='验证码不能为空')
    if not code.isdigit():
        return ajax.jsonp_fail(request, message='请输入正确的验证码')
    if not is_chinamobile(phone):
        return ajax.jsonp_fail(request, message='请输入正确的移动手机号')
    if user_type == 3 and not name:
        return ajax.jsonp_fail(request, message="姓名不能为空")
    if user_type == 3 and not is_chinese_word(name):
        return ajax.jsonp_fail(request, message="姓名长度为2-5个汉字")
    if user_type == 3 and subject_id not in (2, 3, 4, 5, 9):
        return ajax.jsonp_fail(request, message="请选择一个学科")
    # print validate_phone_platform(phone, platform_id)

    if validate_phone_platform(phone, platform_id) == False:
        return ajax.jsonp_fail(request, message='手机号与省份不匹配')

    # 验证验证码
    real_code = cache.vcode.get(phone)
    if not code or code != real_code:
        return ajax.jsonp_fail(request, message='验证码错误，请重新获取')
    cache.vcode.delete(phone)  # 删除缓存

    data = common.register(platform_id, user_type, phone, name, subject_id, dept_type)
    if not data:
        return ajax.jsonp_fail(request, message='帐号已存在')
    common.sendpwd(request, phone, data['username'], data['password'], platform_id)
    return ajax.jsonp_ok(request, data)


@ajax_try("")
def phone_login(request):
    """
    @api {post} /account/login/web [登录]WEB登录
    @apiGroup account
    @apiParamExample {json} 请求示例
    {
        "username":"15038035398",
        "password":"111111",
        "pass_flag": 1      # 0 以前的老接口，不加密，  1 现在的新程序，加密
    }
    @apiParam {String} username 手机号或帐号
    @apiParam {String} password 密码
    @apiSuccessExample {json} 成功返回
    {
        "next": "",
        "error": "",
        "message": "",
        "data": [
            {
                "real_name": "张三",
                "school_name": "创恒中学",
                "unit_name": "100班",
                "type":1,
                "portrait": "头像",
                "tbkt_token": "有效期7天的token"
            },
        ],
        "response": "ok"
    }
    * type = 1 学生
    * type = 3 教师
    """
    args = request.QUERY.casts(username=str, password=str, pass_flag=int)
    username = args.username or ''
    password = args.password or ''
    pass_flag = int(args.pass_flag or 0)
    username = username.strip().lower()
    out = []
    if not username:
        return ajax.jsonp_fail(request, message='请输入用户名或手机号')
    if not password:
        return ajax.jsonp_fail(request, message='请输入密码')

    if pass_flag:
        password = auth.safe_pass_decode(password)

    # 模糊匹配(根据手机号+密码猜测具体帐号)
    if username.isdigit():
        encoded_password = auth.encode_plain_password(password)
        sql = """
        select u.username, u.status from auth_user u
        inner join auth_profile p on p.user_id=u.id and p.password='%s'
        where u.phone='%s'
        """ % (encoded_password, username)
        binds = db.user_slave.fetchall_dict(sql)
        if not binds:
            return ajax.jsonp_fail(request, message="账号或密码错误！")

        now_binds = [b for b in binds if int(b.status) != 2]
        if not now_binds:
            return ajax.jsonp_fail(request, message="该账号已被禁用，请联系客服")
    else:
        user, auth_user = com_user.authenticate(username=username, password=password)
        if not user:
            return ajax.jsonp_fail(request, message='账号或密码错误，是否找回密码?')

        if int(user.status) == 2:
            return ajax.jsonp_fail(request, message='该账号已被禁用，请联系客服')

        # 登录检查
        error = com_user.web_login_check(user)
        if error:
            return ajax.jsonp_fail(request, message=error)

        # 登录日志
        thread_pool.call(common.login_handle, request, args, user)
        # 输入后缀xs,js 准确返回用户信息
        if not username.isdigit():
            d = dict(
                real_name=user.real_name,
                school_name=user.school_name if user.school_name else "",
                unit_name=user.unit.name if user.unit else "",
                portrait=user.portrait,
                type=user.type,
                tbkt_token=auth.login(request, user.id),
                dept_id=user.dept_id,

            )
            out.append(d)
            return ajax.jsonp_ok(request, out)

    # 手机号下的所有账号
    sql = """
    select  u.id, u.real_name, p.portrait, u.type,p.password,u.sid,u.dept_id, u.status
    from auth_user u inner join auth_profile p on u.id = p.user_id and u.phone = "%s"
    where u.type in (1,3) and u.dept_id in (1,2) and u.status != 2
    order by u.type desc
        """ % username
    users = db.user_slave.fetchall_dict(sql)
    if not users:
        return ajax.jsonp_fail(request, message='账号或密码错误，是否找回密码?')

    user_ids = [i.id for i in users]
    regions = db.ketang.mobile_order_region.select("school_name", "unit_class_id", "user_id") \
                  .filter(user_id__in=user_ids).group_by("user_id")[:]
    units_id = [i.unit_class_id for i in regions]
    region_map = {i.user_id: i for i in regions}
    units = db.slave.school_unit_class.select("unit_name", "id").filter(id__in=units_id)[:]
    units_map = {i.id: i.unit_name for i in units}
    for i in users:
        region = region_map.get(i.id)
        unit_id = region.unit_class_id if region else 0
        school_name = region.school_name if region else ""
        unit_name = units_map.get(unit_id, "")

        d = dict(
            real_name=i.real_name,
            school_name=school_name,
            unit_name=unit_name,
            type=i.type,
            portrait=get_portrait(i, i.type),
            # 'portrait': com_user.get_portrait(u, u.type),
            tbkt_token=create_token(i.id),
            sid=i.sid,
            dept_id=i.dept_id
        )
        out.append(d)
    return ajax.jsonp_ok(request, out)


@ajax_try("")
@com_user.need_login
def logininfo(request):
    """
    记录用户app唤醒后的登录信息
        @apiParam {String} username 手机号或帐号
        @apiParam {String} password 密码
        @apiParam {Integer} login_type (可选)登录类型 88:Android教辅学生 90:Android教辅教师 89:IOS教辅学生 91:IOS教辅教师
        @apiParam {String} version (可选)系统版本号
        @apiParam {String} name (可选)设备名称
        @apiParam {String} model (可选)手机型号
        @apiParam {String} platform (可选)平台名称
        @apiParam {String} uuid (可选)设备序列号
        @apiParam {String} appversion (可选)app版本
    :param request: 
    :return: 
    """
    args = request.QUERY.casts(login_type=int, version=str, name=unicode, model=unicode, platform=str,
                               uuid=str, appversion=str)
    common.login_info(request, args, request.user_id)
    return ajax.jsonp_ok(request)
