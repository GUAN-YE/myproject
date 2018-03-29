# coding: utf-8
"""教材常用模块"""
from libs.utils import db


def get_press(id):
    """
    返回出版社
    {"id":1, "name":"人教版", "sequence":9, "isactive":1}
    """
    return db.ziyuan_slave.zy_press.get(id=id)


def get_small_name(book):
    """
    返回书名
    例如: 一年级(上册)
    -------------------------
    王晨光     2016-12-23
    -------------------------
    @param book: zy_book表数据
    """
    grade_name = [u'一', u'二', u'三', u'四', u'五', u'六', u'七', u'八', u'九', u"十", u"十一", u"十二"][book.grade_id - 1]
    volume_name = {1:u'上册', 2:u'下册', 3:u'全册'}.get(book.volume) or u''
    return u'%s年级(%s)' % (grade_name, volume_name)


def get_name(book):
    """
    返回书名
    例如: 人教版一年级(上册)
    -------------------------
    王晨光     2016-12-23
    -------------------------
    @param book: zy_book表数据
    """
    press = get_press(book.press_id)
    return u'%s%s' % (press.name, get_small_name(book))
