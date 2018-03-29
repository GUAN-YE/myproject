# coding: utf-8
import datetime
from libs.utils import db, num_to_ch, thread_pool
from apps.common.com_cache import cache


def get_gradelist(subject_id, type, grade_id, book_id=0):
    """
    选年级教材列表
    ---------------------
    王晨光     2017-1-4
    ---------------------
    :param subject_id: 学科ID
    :param type: 1教材 2教辅
    :param grade_id: 年级ID
    :param book_id: 设置教材要对应年级
    :return: [{id:BOOKID, name:书名, press_name:出版社, version:版本, volume:上下册}]
    """
    if type == 1:
        order_by = "order by press_name,p.id, volume"
    else:
        order_by = "order by name,press_name, volume"
    book_related = ''
    if type == 2 and subject_id in (21, 22) and book_id:
        book_related = 'and b.book_id =%s' % book_id

    sql = """
    select b.id, b.name, b.subject_id, b.grade_id, p.name press_name, p.id press_id, 
        v.name version_name, b.volume, b.book_type
    from zy_book b
    inner join zy_press p on p.id=b.press_id
    inner join zy_press_version v on v.id=b.version_id
    where b.subject_id=%s and b.grade_id=%s and b.book_type=%s and b.is_active=1 %s
    %s
    """ % (subject_id, grade_id, type, book_related,order_by)
    books = db.ziyuan_slave.fetchall_dict(sql)
    for b in books:
        b.volume_name = {1: u'上册', 2: u'下册', 3: u'全册'}.get(b.volume, u'')
        b.grade_name = num_to_ch(b.grade_id) + u'年级'
        if b.book_type == 1:
            b.name = b.grade_name + b.volume_name
    return books


def get_sources(book_id):
    """
    教材相关练习册列表
    ----------------------
    王晨光     2017-2-15
    ----------------------
    :param book_id: 教材ID
    :return: [{id:练习册ID, name:书名, press_name:出版社, version:版本, volume:上下册}]
    """
    sql = """
    select b.id, b.name, b.subject_id, b.grade_id, p.name press_name, v.name version_name, b.volume
    from zy_book b 
    inner join zy_press p on p.id=b.press_id
    inner join zy_press_version v on v.id=b.version_id
    where b.book_id=%s and b.is_active=1 and b.book_type=2
    order by b.press_id, b.volume, b.sequence
    """ % (book_id)
    return db.ziyuan_slave.fetchall_dict(sql)


def setbook(user_id, book_id):
    """
    设置用户教材
    ---------------------
    王晨光     2017-1-4
    ---------------------
    :param book_id: 教材/教辅ID
    """
    thread_pool.call(_set_book, user_id, book_id)


def _set_book(user_id, book_id):
    book = db.ziyuan_slave.zy_book.select('id', 'book_type', 'subject_id').get(id=book_id)
    if not book:
        return

    is_work_book = 1 if book.book_type == 2 else 0
    ubook = db.slave.user_book.get(user_id=user_id, subject_id=book.subject_id, is_work_book=is_work_book)
    if ubook:
        db.default.user_book.filter(id=ubook.id).update(book_id=book_id)
    else:
        db.default.user_book.create(
            book_id=book_id,
            subject_id=book.subject_id,
            user_id=user_id,
            add_time=datetime.datetime.now(),
            is_work_book=is_work_book
        )
    cache.userbook.set((user_id, book.subject_id, is_work_book), book_id)