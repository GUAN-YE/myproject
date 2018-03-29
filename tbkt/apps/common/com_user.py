# coding: utf-8
"""用户常用函数"""
import time
import hashlib
import base64
from libs.utils import ajax, db, Struct, auth, get_absurl
from .com_cache import cache

from django.conf import settings

STUDENT_CODES = {2: 'A', 3: 'B', 4: 'C', 9: 'D', 5: 'E'}
TEACHER_CODES = {2: 'J', 3: 'K', 4: 'L', 9: 'M', 5: 'N'}

REGIONMAP = {
    1: "mobile_order_region",  # 河南
    2: "mobile_order_region_jx",  # 江西
    3: "mobile_order_region_gx",  # 广西
    4: "mobile_order_region_js",  # 江苏
    5: "mobile_order_region_sx",  # 山西
    6: "mobile_order_region_qg"  # 北京(全国)
}


def need_login(f):
    """
    ajax强制登录修饰器

    王晨光     2016-10-11
    """

    def wrap(request, *args, **kw):
        user = request.user
        if not user:
            return ajax.jsonp_fail(request, error='no_user', message="请您先登录")
        else:
            return f(request, *args, **kw)

    return wrap


def need_teacher(f):
    """
    教师强制登录修饰器

    王晨光     2017-1-3
    """

    def wrap(request, *args, **kw):
        user = request.user
        if not user:
            return ajax.jsonp_fail(request, error='no_user', message="请您先登录")
        elif not user.is_teacher:
            return ajax.jsonp_fail(request, error='no_user', message="请用教师帐号登录")
        elif not user.units:
            return ajax.jsonp_fail(request, error='no_class', message="请先加入一个班级")
        else:
            return f(request, *args, **kw)

    return wrap


def app_login_check(user):
    """
    检查用户是否符合登录条件, 返回失败信息

    王晨光     2017-2-13
    """
    # 暂不支持的老师学科
    if user.type == 3 and user.subject_id == 92:
        return "暂不支持初中英语教师, 请登录网站使用!"
    if user.type == 3 and user.subject_id == 52:
        return "暂不支持初中语文教师, 请登录网站使用!"
    if user.type == 3 and user.sid == 3:
        return "暂不支持物理教师, 请登录网站使用!"
    if user.type == 3 and user.sid == 4:
        return "暂不支持化学教师, 请登录网站使用!"
    if user.status == 2:
        return "该账号暂未开通，请联系客服！"


def web_login_check(user):
    """
    检查用户是否符合登录条件, 返回失败信息

    王晨光     2017-7-20
    """
    if user.type == 3 and user.subject_id == 51:
        return "Web端暂不支持语文教师, 请登录APP使用!"
    if user.type == 3 and user.subject_id == 52:
        return "暂不支持初中语文教师登录"
    if user.status == 2:
        return "该账号暂未开通，请联系客服！"


def get_portrait(user, type, portrait=None):
    """
    功能说明:获取用户头像
    ------------------------------------------------------------------------
    修改人            修改时间                修改原因
    ------------------------------------------------------------------------
    杜祖永            2010-7-19
    """
    if portrait:
        return get_absurl(portrait)
    elif user and user.profile and user.profile.portrait.strip():
        return get_absurl(user.profile.portrait)
    else:
        if type == 1:
            return '%s/user_media/images/profile/default-student.png' % settings.FILE_MEDIA_URLROOT
        elif type == 2:
            return '%s/user_media/images/profile/default-parents.png' % settings.FILE_MEDIA_URLROOT
        elif type == 3:
            return '%s/user_media/images/profile/default-teacher.png' % settings.FILE_MEDIA_URLROOT
        elif type == 4:
            return '%s/user_media/images/profile/default-teacher.png' % settings.FILE_MEDIA_URLROOT


def pure_book(book_id):
    """
    根据ID单个教材/教辅数据
    ----------------------
    王晨光     2017-2-18
    ----------------------
    @param book_id
    @return {'id':教材教辅ID, 'subject_id':两位学科ID, 'name':默认书名, 'press_name':出版社名, 
            'version_name':版本名, 'volume':1上册2下册3全册}
    """
    book = cache.book.get(book_id)
    if book:
        return book

    sql = """
    select b.id, b.name, b.subject_id, b.grade_id, p.name press_name, v.name version_name, b.volume
    from zy_book b
    inner join zy_press p on p.id=b.press_id
    inner join zy_press_version v on v.id=b.version_id
    where b.id=%s
    """ % (book_id)
    book = db.ziyuan_slave.fetchone_dict(sql)
    cache.book.set(book_id, book)
    return book


def get_user(user_id):
    """
    从auth_uesr表读取数据, 顺便添加一些常用属性
    失败返回None

    王晨光     2016-12-22 
    """
    user = cache.auth_user.get(user_id)
    if not user:
        user = db.user_slave.auth_user.get(id=user_id) or {}
        cache.auth_user.set(user_id, user)
    return User(user) or None


def get_profile(user_id):
    """
    从auth_profile读取数据
    失败返回None

    王晨光     2017-6-8
    """
    profile = cache.auth_profile.get(user_id)
    if profile:
        return profile
    profile = db.user_slave.auth_profile.get(user_id=user_id)
    if profile:
        # 加入头像边框
        sql = """select border_url from user_border_detail  u join border b on u.border_id=b.id where u.user_id=%s and u.status=1""" % user_id
        user_border = db.slave.fetchone_dict(sql)
        border = ""
        if user_border:
            border = user_border.border_url
        profile.border = border
        cache.auth_profile.set(user_id, profile)
        return profile


def get_users(user_ids):
    """
    获取多条User数据
    返回 {user_id: auth_user数据}

    王晨光     2017-6-8
    """
    if not user_ids:
        return {}
    users = cache.auth_user.get_many(user_ids)
    wild_ids = [i for i in user_ids if i not in users]
    if wild_ids:
        wilds = db.user_slave.auth_user.filter(id__in=wild_ids)[:]
        wildd = {u.id: u for u in wilds}
        if wildd:
            users.update(wildd)
            cache.auth_user.set_many(wildd)
    return {user_id: User(u) for user_id, u in users.iteritems()}


class User:
    """同步课堂用户类, 取代django的User模型
    
    用法:
    user = User(用户表字典数据)
    if user: ...
    """

    def __init__(self, auser):
        """
        @param auser auth_user表数据
        """
        self.auser = auser or {}
        for k, v in self.auser.iteritems():
            setattr(self, k, v)
        self.aprofile = None  # auth_profile表数据

    def __len__(self):
        if hasattr(self, 'id'):
            return 1
        return 0

    @property
    def profile(self):
        """
        获取用户附加信息
        """
        if self.aprofile is not None:
            return self.aprofile
        self.aprofile = get_profile(self.id)
        return self.aprofile

    def set_password(self, password):
        """
        修改密码, 同时修改所有关联帐号的密码
        @param password 新密码
        @return [users]
        """
        hash = auth.encode_password(password)
        plain_password = auth.encode_plain_password(password)
        username_prefix = self.phone_number + ('js' if self.type == 3 else 'xs')
        with db.user as c:
            users = c.auth_user.filter(username__startswith=username_prefix, type=self.type)[:]
            if users:
                user_ids = [u.id for u in users]
                c.auth_user.filter(id__in=user_ids).update(password=hash)
                c.auth_profile.filter(user_id__in=user_ids).update(password=plain_password)
            self.auser.password = hash
            self.password = hash
            if self.aprofile:
                self.aprofile.password = plain_password

            # 更新缓存
            for user in users:
                user.password = hash
                cache.auth_user.set(user.id, user)
                if self.aprofile:
                    cache.auth_profile.set(user.id, self.aprofile)
                else:
                    cache.auth_profile.delete(user.id)

            return users

    def check_password(self, password):
        return auth.verify_password(password, self.password)

    def set_name(self, name):
        """
        更新用户姓名
        """
        db.user.auth_user.filter(id=self.id).update(real_name=name)

        self.auser.real_name = name
        self.real_name = name
        cache.auth_user.set(self.id, self.auser)

    def set_sex(self, sex):
        """
        更新性别
        """
        db.user.auth_profile.filter(user_id=self.id).update(sex=sex)
        profile = self.profile
        profile.sex = sex
        cache.auth_profile.set(self.id, profile)

    def set_portrait(self, path):
        """
        更新用户头像
        @param path      头像相对地址
        @return 头像绝对地址
        """
        if not path:
            return ''
        db.user.auth_profile.filter(user_id=self.id).update(portrait=path)

        if self.aprofile:
            self.aprofile.portrait = path
            cache.auth_profile.set(self.id, self.aprofile)
        else:
            cache.auth_profile.delete(self.id)

        return get_absurl(path)

    def set_grade(self, grade_id):
        """
        更新老师用户当前年级
        @param grade_id 新年级
        """
        if grade_id != self.grade_id:
            db.user.auth_user.filter(id=self.id).update(grade_id=grade_id)
            self.grade_id = self.auser.grade_id = grade_id
            cache.auth_user.set(self.id, self.auser)
            cache.user_profile.delete(self.id)

    def get_mobile_order_region(self, is_slave=True):
        # is_slave 是否读取从库数据
        if is_slave:
            dt = db.ketang_slave
        else:
            dt = db.ketang

        region_map = {
            2: dt.mobile_order_region_jx,  # 江西
            3: dt.mobile_order_region_gx,  # 广西
            4: dt.mobile_order_region_js,  # 江苏
            5: dt.mobile_order_region_sx,  # 山西
            6: dt.mobile_order_region_qg  # 北京(全国)
        }
        return region_map.get(self.platform_id, dt.mobile_order_region)

    @property
    def portrait(self):
        "获取头像url"
        return get_portrait(self, self.type)

    @property
    def border(self):
        "获取头像边框"
        if self.profile:
            return get_absurl(self.profile.border)
        return ""

    @property
    def is_teacher(self):
        return self.type == 3

    @property
    def is_student(self):
        return self.type == 1

    @property
    def phone_number(self):
        return self.phone

    @property
    def sex(self):
        profile = self.profile
        return profile.sex if profile else 1

    @property
    def plain_password(self):
        profile = self.profile
        if profile:
            return auth.decode_plain_password(profile.password)

    @property
    def all_units(self):
        """
        获取用户所有班级(包括跨年级)

        王晨光            2016-10-10
        """
        # if hasattr(self, '_units'):
        #     return self._units

        units = cache.user_units.get(self.id)
        if units:
            self._units = units
            return units

        # 查用户-班级关系
        unit_ids = (self.get_mobile_order_region(is_slave=False).filter(user_id=self.id, unit_class_id__gt=0,
                                                                        is_update=0)
                    .select('unit_class_id').order_by('-add_date').flat('unit_class_id'))[:]
        # print self.get_mobile_order_region()
        # print unit_ids,self.id
        if unit_ids:
            # 学生只去一个班级
            if self.type == 1:
                unit_ids = unit_ids[0:1]
            sql = """
            select u.id, u.unit_name name, u.type, u.school_id, s.name school_name, u.grade_id, u.class_id, 
                   u.id unit_class_id,
                   s.county
            from school_unit_class u
            inner join school s on s.id=u.school_id
            where u.id in (%s)
            order by u.grade_id, u.class_id
            """ % (','.join(str(i) for i in unit_ids))
            units = db.slave.fetchall_dict(sql)
            # 补充班级名
            for u in units:
                if not u.city:
                    u.city = u.county[:4] + '00'
                if not u.name:
                    u.name = u'%d%02d班' % (u.grade_id, u.class_id)

        else:
            units = []
        self._units = units
        cache.user_units.set(self.id, units)
        return self._units

    @property
    def grades(self):
        """
        老师: 所在的年级列表

        王晨光            2016-10-10
        """
        if hasattr(self, '_grades'):
            return self._grades
        units = self.all_units
        grades = [u.grade_id for u in units]
        grades = list(set(grades))
        grades.sort()
        self._grades = grades
        return grades

    @property
    def units(self):
        """
        老师: 返回当前年级的班级列表
        学生: 返回他的班级列表

        王晨光            2016-10-10
        """
        units = self.all_units
        # print units,"units"
        if self.type != 3:
            return units
        grades = self.grades
        # 默认选最小年级
        if grades and self.grade_id not in grades:
            self.grade_id = grades[0]
            db.user.auth_user.filter(id=self.id).update(grade_id=self.grade_id)
            self.auser.grade_id = self.grade_id
            cache.auth_user.set(self.id, self.auser)
        units = [u for u in units if u.grade_id == self.grade_id]
        return units

    @property
    def unit(self):
        """
        学生: 返回学生当前班级

        王晨光            2016-10-10
        """
        units = self.units
        return units[0] if units else None

    @property
    def dept_type(self):
        """
        当前所在部门类型: 0空 1小学 2初中

        王晨光            2016-10-10
        """
        units = self.units
        dtype = units[0].type if units else 1
        if dtype and dtype != self.dept_id:
            dtype = max(1, int(dtype))
            db.user.auth_user.filter(id=self.id).update(dept_id=dtype)
            self.auser.dept_id = dtype
            self.dept_id = dtype
            cache.auth_user.set(self.id, self.auser)
        return self.dept_id

    @property
    def province(self):
        if hasattr(self, '_platform'):
            platform = self._platform
        else:
            platform = db.user_slave.platform.get(id=self.platform_id)
            self._platform = platform
        if platform:
            return platform.province

    @property
    def city(self):
        units = self.units
        return units[0].city if units else ''

    @property
    def county(self):
        units = self.units
        return units[0].county if units else ''

    @property
    def school_id(self):
        "property: school_id"
        units = self.units
        return units[0].school_id if units else 0

    @property
    def school_name(self):
        "property: school_name"
        units = self.units
        return units[0].school_name if units else ''

    @property
    def subject_id(self):
        """
        老师当前两位数学科ID

        王晨光            2016-10-10
        """
        if not self.is_teacher:
            return 0
        dept_type = self.dept_type
        sid = self.sid
        return sid * 10 + dept_type

    @property
    def subject_name(self):
        """
        老师当前学科名称

        王晨光            2016-10-10
        """
        sid = self.sid
        return {2: u"数学", 3: u"物理", 4: u"化学", 9: u"英语"}.get(sid, u'')

    @property
    def subject_en(self):
        """
        获取老师当前学科的英文名

        王晨光            2016-10-10
        """
        subject_id = self.subject_id
        d = {21: 'math', 22: 'math2', 91: 'english', 92: 'english2'}
        return d.get(subject_id, '')

    def get_book(self, subject_id):
        """
        用户当前某一科教材

        王晨光            2016-10-10

        :param subject_id: 两位数学科ID
        """
        book_id = cache.userbook.get((self.id, subject_id, 0))
        if book_id is None:
            ubook = db.slave.user_book.get(user_id=self.id, subject_id=subject_id, is_work_book=0)
            if ubook:
                book_id = ubook.book_id
                cache.userbook.set((self.id, subject_id, 0), book_id)
        if book_id:
            return pure_book(book_id)

    def get_pbook(self, subject_id):
        """
        用户当前某一科教辅

        王晨光            2016-10-10

        :param subject_id: 两位数学科ID
        """
        book_id = cache.userbook.get((self.id, subject_id, 1))
        if book_id is None:
            ubook = db.slave.user_book.get(user_id=self.id, subject_id=subject_id, is_work_book=1)
            if ubook:
                book_id = ubook.book_id
                cache.userbook.set((self.id, subject_id, 1), book_id)
        if book_id:
            return pure_book(book_id)

    @property
    def book(self):
        """
        老师当前教材

        王晨光            2016-10-10
        """
        if hasattr(self, '_book'):
            return self._book
        subject_id = self.subject_id
        self._book = self.get_book(subject_id)
        return self._book

    @property
    def pbook(self):
        """
        老师当前练习册

        王晨光            2016-10-10
        """
        if hasattr(self, '_pbook'):
            return self._pbook
        subject_id = self.subject_id
        self._pbook = self.get_pbook(subject_id)
        return self._pbook

    def mobile_subject(self, sid):
        """
        返回用户某一科的最新开通信息(mobile_subject表)

        王晨光            2017-5-9

        :param sid: 一位数学科码
        :returns: None or {open_date, cancel_date, status}
        """
        if sid not in STUDENT_CODES:
            return
        if not hasattr(self, '_mobile_subjects'):
            self._mobile_subjects = {}
        if sid in self._mobile_subjects:
            return self._mobile_subjects[sid]
        ms = db.ketang_slave.mobile_subject.filter(user_id=self.id, subject_id=sid).select(
            'open_date', 'cancel_date').last()
        self._mobile_subjects[sid] = ms
        return ms

    def openstatus(self, sid):
        """
        返回用户某一科开通情况

        王晨光            2016-10-10

        :param sid: 一位数学科码
        :returns: 开通状态 0没开1开通 (试用也算开通)
        """
        ms = self.mobile_subject(sid)
        if ms:
            nowt = int(time.time())
            if nowt >= ms.open_date and (ms.cancel_date <= 0 or nowt < ms.cancel_date):
                return 1
        return 0


def authenticate(username, password):
    """
    验证用户名密码 
    成功返回(User, None)
    失败返回(None, user)
    """
    user_id = cache.username_id.get(username)
    if user_id:
        user = cache.auth_user.get(user_id)
    else:
        user = None
    if not user:
        user = db.user_slave.auth_user.get(username=username)
        if user:
            cache.auth_user.set(user.id, user)
            cache.username_id.set(username, user.id)
    if not user:
        return None, None
    encoded = user.password or ''
    if not auth.verify_password(password, encoded):
        return None, user
    return User(user), user
