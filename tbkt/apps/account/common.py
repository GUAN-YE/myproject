# coding: utf-8
import datetime
import hashlib
import logging
import random
import time

from django.conf import settings
from libs.utils import pinyin_abb, Struct, db, auth, get_ip, tbktapi, get_absurl
from libs import utils
from apps.common import com_user
from apps.common.com_cache import cache


# import sys
# reload(sys)
# sys.setdefaultencoding( "utf-8" )

def get_class_teacher_id(unit_id, subject_id):
    """
    返回班级某一科的老师ID

    王晨光     2016-10-11

    :param unit_id: 班级ID
    :param subject_id: 学科ID
    :return: 老师user_id, 失败返回None
    :rtype: int
    """
    user_ids = db.ketang_slave.mobile_order_region.filter(unit_class_id=unit_id, user_type=3).select('user_id').flat(
        'user_id')[:]
    if not user_ids:
        return
    user = db.user_slave.auth_user.select('id').get(id__in=user_ids, subject_id=subject_id)
    if user:
        return user.id


def get_class_teacher(unit_id, subject_id):
    """
    返回班级某一科的老师

    王晨光     2016-10-11

    :param unit_id: 班级ID
    :param subject_id: 学科ID
    :returns: 老师User, 失败返回None
    :rtype: User
    """
    user_id = get_class_teacher_id(unit_id, subject_id)
    if user_id:
        return com_user.get_user(user_id)


def class_teacher_exists(unit_id, subject_id):
    """
    返回班级是否存在某一科的老师
    -----------------------
    王晨光     2016-10-11
    -----------------------
    @param unit_id      班级ID
    @param subject_id   学科ID
    @returns            True/False
    """
    return bool(get_class_teacher_id(unit_id, subject_id))


def get_unit(unit_id):
    """
    返回班级

    王晨光     2016-10-11
    """
    return db.slave.school_unit_class.get(id=unit_id)


def feedback(user_id, type, content, app):
    """
    填写用户反馈
    -----------------------
    王晨光     2016-10-19
    -----------------------
    @param user_id      用户ID
    @param type         1意见建议 2错误反馈 3其它
    @param content      内容
    @param app          手机类型
    """
    nowt = int(time.time())
    db.default.system_feedback.create(user_id=user_id, type=type, title='',
                                      content=content, email='', app=app, add_time=nowt, reply_status=0,
                                      status=0)


def login_handle(request, args, user):
    """
    登录后记录相关信息
    --------------------------------
    王晨光     2016-11-10
    --------------------------------
    @param request  django.http.Request
    @param args     request.loads() JSON参数
    @param user     登录用户
    """
    if not args:
        return

    ip = get_ip(request)
    login_type = int(args.login_type or 0)

    version = args.version or ""  # 系统版本号 version:Android 2.1
    name = args.name or ""  # 设备名称 name:Nexus One
    model = args.model or ""  # 手机型号 model:Nexus One
    platform = args.platform or ""  # 平台名称 platform:Android
    uuid = args.uuid or ""  # 设备序列号 uuid:*****
    appversion = args.appversion or ""  # app版本 appversion:0.2.1
    nowt = int(time.time())
    # 用户每次登录增加登录信息
    id = db.user.tbkt_logins.create(user_id=user.id,
                                    version=version,
                                    name=name,
                                    model=model,
                                    platform=platform,
                                    uuid=uuid,
                                    appversion=appversion,
                                    login_type=login_type,
                                    ip=ip,
                                    login_time=nowt)
    db.user.auth_user.filter(id=user.id).update(last_login=nowt)


def login_info(request, args, userid):
    """
    登录后记录相关信息
    --------------------------------
    王晨光     2016-11-10
    --------------------------------
    @param request  django.http.Request
    @param args     request.loads() JSON参数
    @param user     登录用户
    """
    if not args:
        return

    ip = get_ip(request)
    login_type = int(args.login_type or 0)

    version = args.version or ""  # 系统版本号 version:Android 2.1
    name = args.name or ""  # 设备名称 name:Nexus One
    model = args.model or ""  # 手机型号 model:Nexus One
    platform = args.platform or ""  # 平台名称 platform:Android
    uuid = args.uuid or ""  # 设备序列号 uuid:*****
    appversion = args.appversion or ""  # app版本 appversion:0.2.1
    nowt = int(time.time())
    # 用户每次登录增加登录信息
    id = db.user.tbkt_logins.create(user_id=userid,
                                    version=version,
                                    name=name,
                                    model=model,
                                    platform=platform,
                                    uuid=uuid,
                                    appversion=appversion,
                                    login_type=login_type,
                                    ip=ip,
                                    login_time=nowt)


def get_accounts(user):
    """
    获得本用户下所有帐号
    --------------------------------
    王晨光     2016-12-26
    --------------------------------
    @param user 用户
    @return [{"user_id":用户ID, "name":姓名, "role":"数学教师", "portrait":头像url, "unit_name":东风路小学403班}]
    """
    users = db.user_slave.auth_user.filter(phone=user.phone_number, type=user.type, status__ne=2
                                           ).select('id', 'type', 'real_name', 'grade_id', 'sid')[:]
    if not users:
        return []
    user_ids = [u.id for u in users]
    profiles = db.user_slave.auth_profile.filter(user_id__in=user_ids).select('user_id', 'portrait')[:]
    profiled = {p.user_id: p for p in profiles}
    for u in users:
        p = profiled.get(u.id)
        u.portrait = p.portrait if p else ''
    subject_t = {2: '数学', 3: '物理', 4: '化学', 9: '英语', 5: '语文'}
    role_t = {1: '学生', 3: '老师'}
    # 查班级
    unit_groups = user.get_mobile_order_region().filter(
        user_id__in=user_ids, unit_class_id__gt=0, is_update=0
    ).select('user_id', 'unit_class_id', 'school_name')[:]
    unit_ids = [g.unit_class_id for g in unit_groups]
    units = db.slave.school_unit_class.filter(id__in=unit_ids).select('id', 'unit_name', 'grade_id')[:]
    unitd = {u.id: u for u in units}
    regiond = {}  # {user_id: [units]}
    user_grade_set = set()  # set((user_id, grade_id)) 一个年级只取一个班
    for ug in unit_groups:
        regs = regiond.get(ug.user_id) or []
        reg = unitd.get(ug.unit_class_id)
        if reg:
            k = (ug.user_id, reg.grade_id)
            if k not in user_grade_set:
                reg.school_name = ug.school_name
                regs.append(reg)
                user_grade_set.add(k)
        regiond[ug.user_id] = regs

    accounts = []
    for u in users:
        user_type = u.type if u else None
        regs = regiond.get(u.id) or [None]  # [None]保证至少有一条帐号数据
        for reg in regs:
            grade_id = reg.grade_id if reg else 0
            unit_name = reg.unit_name if reg else ''
            # 学生显示学校名
            if user.type == 1:
                school_name = reg.school_name if reg else ''
                unit_name = school_name + unit_name
            account = {'user_id': u.id, 'bind_id': u.id, 'name': u.real_name, 'type': user_type,
                       'subject_id': u.sid, 'grade_id': grade_id, 'unit_name': unit_name,
                       'role': subject_t.get(u.sid, '') + role_t.get(u.type, ''),
                       'portrait': com_user.get_portrait(u, u.type)
                       }
            accounts.append(account)
    return accounts


def get_unopen_count(user):
    """
    获得教师所有班级下未开通人数
    ----------------------
    王晨光     2017-1-3
    ----------------------
    :param user: 教师User
    """
    units = user.units
    if not units:
        return 0

    # 老师学科ID
    sid = user.sid
    if not sid:
        return 0

    unit_ids = [u.id for u in units]
    # 获得班级下所有学生ID
    user_ids = user.get_mobile_order_region().filter(unit_class_id__in=unit_ids).select('user_id').flat('user_id')[:]
    if not user_ids:
        return 0
    # 所有学生ID和电话
    users = db.user_slave.auth_user.filter(id__in=user_ids, type=1).select('id', 'phone')[:]
    if not users:
        return 0
    # 所有开通的手机号
    nowt = int(time.time())
    user_ids = [u.id for u in users]
    open_ids = db.ketang_slave.mobile_subject.filter("cancel_date<=0 or cancel_date>%s" % nowt, open_date__lte=nowt,
                                                     user_id__in=user_ids, subject_id=sid).select('user_id').flat(
        'user_id')[:]
    open_ids = set(open_ids)
    # 没开通的学生个数
    return sum(1 for u in users if u.id not in open_ids)


def get_addtask_count(user):
    """
    获得教师本月发作业次数
    ----------------------
    王晨光     2017-1-3
    ----------------------
    """
    now = datetime.datetime.now()
    month_begin = datetime.date(now.year, now.month, 1)
    stamp = int(time.mktime(month_begin.timetuple()))
    unit_ids = [u.id for u in user.units]
    if not unit_ids:
        return 0
    unit_ids_s = ','.join(str(i) for i in unit_ids)
    sql = """
    select count(distinct m.id) from
    message m
    inner join message_class c on c.message_id=m.id and c.unit_class_id in (%s)
    where m.add_user=%s and m.status >= 0 and m.type in (1,2,7,8,9,10) and m.begin_time>=%s and m.begin_time <= %s
    """ % (unit_ids_s, user.id, stamp, int(time.time()))
    row = db.slave.fetchone(sql)
    return row[0] if row else 0


def gets_unit_size(user, unit_ids):
    """
    获取班级学生数
    ---------------------
    王晨光     2017-2-6
    ---------------------
    @return {班级ID: 人数}
    """
    if not unit_ids:
        return {}

    cached = cache.unitsize.get_many(unit_ids)
    unit_ids = [i for i in unit_ids if i not in cached]
    if unit_ids:
        rows = user.get_mobile_order_region().select('unit_class_id', 'count(*) size').filter(
            unit_class_id__in=unit_ids, user_type=1
        ).group_by('unit_class_id')

        # sql = """
        # select unit_class_id, count(*) size from mobile_order_region r
        # where unit_class_id in (%s) and user_type=1
        # group by unit_class_id
        # """ % (utils.join(unit_ids))
        # rows = db.ketang_slave.fetchall(sql)
        # sized = {r[0]:r[1] for r in rows}
        sized = {r.unit_class_id: r.size for r in rows}
        cache.unitsize.set_many(sized)
    else:
        sized = {}
    sized.update(cached)
    return sized


def alloc_username(phone, user_type):
    """
    分配新用户名
    """
    username = phone + ('xs' if user_type == 1 else 'js')
    # 分配新用户名
    xn = db.user.auth_user.filter(username__startswith=username).count()
    if xn > 0:
        username = username + '%s' % (xn + 1)
    return username


def register(platform_id, user_type, phone, real_name, subject_id, dept_type):
    """
    注册一个帐号, 生成随机密码, 名字留空
    ----------------------
    王晨光     2017-2-21
    ----------------------
    @param platform_id  平台ID
    @param user_type    用户类型 1学生 3老师
    @param phone        手机号
    @param real_name    姓名
    @param subject_id   老师学科ID
    @param dept_type    学段: 1小学 2初中
    @return             {'user_id':用户ID, 'username':用户名, 'password':新密码}
        返回None表示帐号已存在
    """

    def foo(user):
        profile = com_user.get_profile(user.id)
        assert profile, 'user_id: %s' % user.id
        password = auth.decode_plain_password(profile.password)
        return {'user_id': user.id, 'username': user.username, 'password': password}

    # 不允许同名用户注册
    user = db.user.auth_user.select('id', 'username').get(phone=phone, real_name=real_name, type=user_type)
    if user:
        return foo(user)

    username = alloc_username(phone, user_type)
    user = db.user.auth_user.select('id', 'username').get(username=username)
    if user:
        return foo(user)

    nowt = int(time.time())
    # 沿用已有帐号的密码
    sql = """
    select p.password from auth_user u
    inner join auth_profile p on p.user_id=u.id
    where u.type=%s and u.phone='%s'
    limit 1
    """ % (user_type, phone)
    profile = db.user_slave.fetchone_dict(sql)
    if profile:
        password = auth.decode_plain_password(profile.password)
    else:
        password = "".join(random.sample('1234567890', 8))  # 新帐号随机生成6位密码
    # if user_type == 3:
    #     dept_type = 0
    with db.user as c:
        user_id = c.auth_user.create(
            ignore=True,
            username=username,
            password=auth.encode_password(password),
            type=user_type,
            real_name=real_name,
            last_login=0,
            date_joined=nowt,
            status=1,
            phone=phone,
            platform_id=platform_id,
            grade_id=0,
            sid=subject_id,
            dept_id=dept_type,
        )
        # duplicate
        if not user_id:
            user = db.user.select('id', 'username').get(username=username)
            assert user, '%s' % username
            return foo(user)
        # create auth_profile
        plain_password = auth.encode_plain_password(password)
        c.auth_profile.create(
            user_id=user_id,
            nickname='',
            portrait='',
            sex=1,
            password=plain_password,
        )

    # 如果本手机号已经是移动开通状态, 那么这个用户也插入一条开通主记录
    mslist = db.ketang_slave.mobile_subject.filter(phone_number=phone, platform_id=platform_id,
                                                   pay_type='cmcc').group_by('subject_id')[:]
    details = []
    for m in mslist:
        if nowt >= m.open_date and (m.cancel_date <= 0 or nowt < m.cancel_date):
            details.append({
                'user_id': user_id,
                'phone_number': phone,
                'subject_id': m.subject_id,
                'open_date': m.open_date,
                'cancel_date': m.cancel_date,
                'pay_type': m.pay_type,
                'platform_id': platform_id,
                'add_date': nowt,
            })
    if details:
        db.ketang.mobile_subject.bulk_create(details, ignore=True)

    return {'user_id': user_id, 'username': username, 'password': password}


def register_student(platform_id, phone, dept_type, code):
    """
    快速注册一个帐号, 生成随机密码, 名字留空.
    支持二次短信验证码开通
    ----------------------
    王晨光     2017-2-21
    ----------------------
    @param platform_id  平台ID
    @param phone        手机号
    @param dept_type    学段: 1小学 2初中
    @param code         二次短信验证码
    @return             {'user_id':用户ID, 'password':新密码}
    """
    r = register(platform_id, 1, phone, "", 0, dept_type)
    if not r:
        return

    return r


def sendpwd(request, phone, username, password, platform_id=1):
    """
    发送帐号密码短信
    ----------------------
    王晨光    2017-5-27
    ----------------------
    """
    if not isinstance(username, unicode):
        username = username.decode('utf-8')
    content = u"您的同步课堂账号是:{} 密码是：{},做作业(除数学知识点视频作业外)功能免费，请放心使用。客户端点此m.tbkt.cn下载安装。咨询电话：12556185".format(
        username, password
    )
    hub = tbktapi.Hub(request)
    hub.sms.post('/sms/send', {'phone': phone, 'content': content})


def get_third_info(user):
    """
    根据user 获取第三方信息
    :param user: 
    :return: 
    """
    third = db.user_slave.third_user.select('third_id').get(user_id=user.id, platform_id=6)
    if not third:
        return {}
    ord_province = user.get_mobile_order_region().select('province').order_by('-add_date').get(user_id=user.id)
    if not ord_province:
        return {}
    province = db.user_slave.third_common_provincecity.select('third_cityid').get(cityid=ord_province.province,
                                                                                  platform_id=6)
    if not province:
        return {}
    d = {
        'third_id': third.third_id,
        'province_id': province.third_cityid,
        'name': user.real_name
    }
    return d


def qg_open_subject(third_id, product_id, pay_type, success_url, fail_url):
    """
    开通接口
    :param third_id: 
    :param product_id: 
    :param success_url:
    :param fail_url: 
    :return: 
    """
    url = '/api/open/'
    data = dict(
        third_id=third_id,
        groupBillingId=product_id,
        pay_type=pay_type,
        successUrl=success_url,
        failUrl=fail_url
    )
    r = tbktapi.Hub().qg.post(url, data)
    return r.data


state_remark = {0: u'未订购', 1: u'包月中', 2: u'点播中', 3: u'试用推广中', 4: u'暂停', 5: u'销号', 6: u'过期'}

open_status = [1, 2, 3]

open_type = {1: u'月', 2: u'天'}

PRODUCT = {
    111: 2,  # 数学
    112: 5,  # 语文
    113: 9,  # 英语
    114: 4,  # 化学
    130: 3,  # 物理
    2001020: 2,  # 数学
    2001021: 5,  # 语文
    2001022: 9,  # 英语
    2001023: 4,  # 化学
    2001024: 3,  # 物理

}


def get_user_info(province_id, third_id, from_type, user):
    if not province_id or not third_id or not from_type:
        return {}

    hub = tbktapi.Hub()
    url = '/api/getopentotal/'
    data = dict(
        third_id=third_id,
        province_id=province_id,
        from_type=from_type,
        platform_id=6
    )
    r = hub.qg.post(url, data)
    if not r:
        return {}
    if r.respones == 'fail':
        return {}

    try:
        data = r.data.get('productInfos')
        if not data:
            r = hub.qg.post(url, data)
            data = r.data.get('productInfos')
        if not data:
            return {}
        data = map(Struct, data)

        out = Struct()
        out.third_id = third_id,
        out.province_id = province_id,
        out.list = []
        user_type = user.dept_id
        user_id = user.id
        for i in data:
            productId_tmp = int(i.productId)

            if productId_tmp in (2001023, 2001024, 114, 130):
                continue

            if int(user_type) == 2 and productId_tmp not in (111, 2001020):
                continue

            arg = Struct()
            arg.status = 1 if int(i.state) in open_status else 0  # 当前是否开通
            arg.group = []  # 开通资费信息
            arg.productId = productId_tmp
            arg.sid = PRODUCT.get(productId_tmp, 0)
            if int(i.state) != 3:
                arg.tiyan_day = 0
            else:
                arg.tiyan_day = qg_get_yiyan_days(i, user_id)

            group = map(Struct, i.groupList)
            for g in group:
                arg.subject_name = g.groupName  # 科目名称(第三方提供)
                arg.groupId = g.groupId  # 子组合ID
                billings = map(Struct, g.groupBillings)
                for bill in billings:
                    gup = Struct()
                    gup.product_id = bill.groupBillingId  # 资费id(套餐id，开通接口需要)
                    gup.day_num = bill.billingDay  # 开通时间
                    gup.open_type = open_type.get(int(bill.billingType))  # 开通类型 1： 包月  2：按天点播
                    gup.price = bill.price
                    arg.group.append(gup)
            out.list.append(arg)
        out.list.sort(lambda x, y: cmp(x["productId"], y["productId"]))
        out.third_id = third_id
        return out
    except Exception as e:
        print e
        return {}


def qg_get_yiyan_days(data, user_id):
    """
    用户体验剩余时间
    """
    produce_id = int(data.productId)
    sid = PRODUCT.get(produce_id)  # 学科id
    subject_status = db.ketang.mobile_subject.filter(user_id=user_id, subject_id=sid, platform_id=6).first()
    if not subject_status:
        return 0
    nowt = time.time()
    cancel_date = subject_status.cancel_date  # 结束时间

    if not cancel_date:
        return 0
    if cancel_date < nowt:
        return 0

    # 免费试用,和点播--正在体验
    logging.info(data)
    logging.info(data.state)
    if int(data.state) == 3:
        day_range = get_time_range(cancel_date)
        return int(day_range) + 1
    return 0


def get_time_range(ctime):
    now = time.time()
    daysec = 24 * 60 * 60
    return int((ctime - now) / daysec)


def get_qg_tiyan_day(user, subject_ids):
    if not user:
        return {}
    third = db.user_slave.third_user.select('third_id').get(user_id=user.id, platform_id=6)
    ord_province = user.get_mobile_order_region().select('province').order_by('-add_date').get(user_id=user.id)
    province = db.user_slave.third_common_provincecity.select('third_cityid').get(cityid=ord_province.province,
                                                                                  platform_id=6)
    if not third or not ord_province or not province:
        return {}

    hub = tbktapi.Hub()
    url = '/api/getopentotal/'
    data = dict(
        third_id=third.third_id,
        province_id=province.third_cityid,
        from_type=4,
        platform_id=6
    )
    r = hub.qg.post(url, data)
    if not r:
        return {}
    if r.respones == 'fail':
        return {}
    try:
        logging.info(r.data)
        data = r.data.get('productInfos', '')

        if not data:
            r = hub.qg.post(url, data)
            data = r.data.get('productInfos', '')
        if not data:
            return {}

        data = map(Struct, data)
        out = []
        for i in data:
            arg = Struct()
            produce_id = int(i.productId)
            sid = PRODUCT.get(produce_id, 0)
            if int(sid) != int(subject_ids):
                continue
            else:
                arg.sid = sid
                arg.status, arg.tiyan_day = get_qg_tiyan_range(i, user)
            out.append(arg)
        return out
    except Exception as e:
        logging.error('/api/getopentotal/ ERROR %s' % e)
    return []


def get_qg_tiyan_range(data, user_id):
    """
    获取用户的是否已经体验过或开通过， 以及 剩余时间 天数
      0， 0            # 未体验，剩余时间
     1， 30           # 正在体验，剩余时间
     2, 0             # 体验过或开通过
    """
    produce_id = int(data.productId)
    status = 1 if int(data.state) in (1, 2, 4, 5, 6) else 0  # 当前是否开通  不包含体验
    if status:  # 已经体验过
        return 2, 0
    sid = PRODUCT.get(produce_id)  # 学科id

    startTime = data.startTime or ''  # 开始时间
    endTime = data.endTime or ''  # 包月产品，无该字段

    if not startTime and not endTime:
        return 0, 0

    if int(data.state) == 3:  # 体验
        endTime = string2int(data.endTime)
        day_range = get_time_range(endTime)
        return 1, int(day_range) + 1

    sid = PRODUCT.get(produce_id)  # 学科id

    subject_status = db.ketang_slave.mobile_subject.filter(user_id=user_id, subject_id=sid, platform_id=6).first()
    if not subject_status:
        return 0, 0

    nowt = time.time()
    cancel_date = subject_status.cancel_date  # 结束时间
    open_date = subject_status.open_date  # 开始时间

    if not open_date:
        return 0, 0

    if cancel_date < nowt:
        return 2, 0

    # 免费试用,和点播--正在体验
    if int(data.state) == 3:
        day_range = get_time_range(cancel_date)
        return 1, int(day_range) + 1
    return 0, 0


def get_js_account(user):
    """
    获得江苏省本用户下所有帐号
    --------------------------------
    张帅男     2017-10-16
    --------------------------------
    @param user 用户
    @return [{"user_id":用户ID, "name":姓名, "role":"数学教师", "portrait":头像url, "unit_name":东风路小学403班}]
    """
    third_ids = db.user_slave.third_parent_stus.filter(third_parent_id=user.id, platform_id=user.platform_id).flat(
        "third_stu_id")[:]
    user_ids = db.user_slave.third_user.filter(third_id__in=third_ids, platform_id=user.platform_id).flat("user_id")[:]
    users = db.user_slave.auth_user.filter(id__in=user_ids).select('id', 'type', 'real_name', 'grade_id', 'sid')[:]
    accounts = com_users_info(user, users)
    return accounts


def com_users_info(user, users):
    if not users:
        return []
    user_ids = [u.id for u in users]
    profiles = db.user_slave.auth_profile.filter(user_id__in=user_ids).select('user_id', 'portrait')[:]
    profiled = {p.user_id: p for p in profiles}
    for u in users:
        p = profiled.get(u.id)
        u.portrait = p.portrait if p else ''
    subject_t = {2: '数学', 3: '物理', 4: '化学', 9: '英语', 5: '语文'}
    role_t = {1: '学生', 3: '老师'}
    # 查班级
    unit_groups = user.get_mobile_order_region().filter(
        user_id__in=user_ids, unit_class_id__gt=0, is_update=0
    ).select('user_id', 'unit_class_id', 'school_name')[:]
    unit_ids = [g.unit_class_id for g in unit_groups]
    units = db.slave.school_unit_class.filter(id__in=unit_ids).select('id', 'unit_name', 'grade_id')[:]
    unitd = {u.id: u for u in units}
    regiond = {}  # {user_id: [units]}
    user_grade_set = set()  # set((user_id, grade_id)) 一个年级只取一个班
    for ug in unit_groups:
        regs = regiond.get(ug.user_id) or []
        reg = unitd.get(ug.unit_class_id)
        if reg:
            k = (ug.user_id, reg.grade_id)
            if k not in user_grade_set:
                reg.school_name = ug.school_name
                regs.append(reg)
                user_grade_set.add(k)
        regiond[ug.user_id] = regs

    accounts = []
    for u in users:
        user_type = u.type if u else None
        regs = regiond.get(u.id) or [None]  # [None]保证至少有一条帐号数据
        for reg in regs:
            grade_id = reg.grade_id if reg else 0
            unit_name = reg.unit_name if reg else ''
            # 学生显示学校名
            if user.type == 1:
                school_name = reg.school_name if reg else ''
                unit_name = school_name + unit_name
            account = {'user_id': u.id, 'bind_id': u.id, 'name': u.real_name, 'type': user_type,
                       'subject_id': u.sid, 'grade_id': grade_id, 'unit_name': unit_name,
                       'role': subject_t.get(u.sid, '') + role_t.get(u.type, ''),
                       'portrait': com_user.get_portrait(u, u.type)
                       }
            accounts.append(account)
    return accounts


def string2int(ctime):
    """字符串转时间戳"""
    return int(time.mktime(time.strptime(ctime, '%Y-%m-%d%H:%M:%S')))


def get_borders(user_id):
    user_borders = db.default.user_border_detail.filter(user_id=user_id).select('border_id').flat('border_id')[:]
    if not user_borders:
        default_border = db.slave.border.select('id', 'border_url').get(remark=u'默认')
        give_default = db.slave.user_border_detail.get(user_id=user_id, border_id=default_border.id)
        if not give_default:
            db.slave.user_border_detail.create(user_id=user_id, border_id=default_border.id,
                                               add_time=int(time.time()))
    borders = db.slave.border.filter(status=1).select('id', 'border_url')[:]
    border_default = db.slave.border.get(remark=u'默认')

    for b in borders:
        b.is_able = 0
        b.border_url = get_absurl(b.border_url)
        # b.border_url = ""
        if b.id in user_borders:
            b.is_able = 1
        if b.id == border_default.id:
            b.is_able = 1
    borders = sorted(borders, key=lambda x: (-x["is_able"]))
    return borders


def change_border(user_id, border_id):
    if not (user_id and border_id):
        return False, u'缺少参数'
    border_default = db.slave.border.get(remark=u'默认')
    user_border = db.slave.user_border_detail.get(user_id=user_id, border_id=border_id)
    if not user_border:
        return False, u'暂未获得该边框'
    nowt = int(time.time())
    if border_id == border_default.id:
        db.default.user_border_detail.filter(user_id=user_id, status=1).update(status=0)
    else:
        if db.default.user_border_detail.get(user_id=user_id, border_id=border_id):
            db.default.user_border_detail.filter(user_id=user_id, status=1).update(status=0)
            db.default.user_border_detail.filter(border_id=border_id, user_id=user_id).update(add_time=nowt,
                                                                                              status=1)

    cache.user_profile.delete(user_id)
    cache.auth_profile.delete(user_id)
    return True, u''


def real_name_filter(real_name):
    """
    登录的时候，用户名筛选
      功能:判断用户姓名长度是否是2到5个字节,并且全部是中文
    :param user_name:用户姓名
    :return: 满足返回True,否则返回False
    """
    if u"语文" in real_name or u"数学" in real_name or u"英语" in real_name or u"物理" in real_name or u"化学" in real_name:
        return False
    if u"学生" == real_name[:2]:
        return False

    try:
        user_name_len = len(real_name)
        name_list = []
        if 1 < user_name_len < 6:
            for name_check in real_name:
                if u'\u4e00' <= name_check <= u'\u9fff':
                    name_list.append(1)
                else:
                    name_list.append(0)
        else:
            name_list.append(0)
        if 0 in name_list:
            return False
        return True
    except Exception as e:
        print e
        return False
