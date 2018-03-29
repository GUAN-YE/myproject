# coding: utf-8
import math
import time
import datetime
from libs.utils import Struct, ajax, db, get_absurl, from_unixtime

# 礼品商城金豆APPID
APPID = 7


def get_order_dict(gift_ids):
    """批量查询订购数 {gift_id: 订购数}"""
    if not gift_ids:
        return {}
    gift_ids_s = ','.join(str(i) for i in gift_ids)
    sql = """
    select gift_id, count(*) n FROM score_gift_order 
    where gift_id in (%s) and status in (0,1) and app_id=%s
    group by gift_id
    """ % (gift_ids_s, APPID)
    rows = db.slave.fetchall(sql)
    return {r[0]: r[1] for r in rows}


def get_gifts(sort, category_id):
    """
    所有商品的列表
    -----------------------
    王晨光     2016-12-06
    -----------------------
    :param sort: 排序方式(0默认按时间 1按兑换量从高到低 2按兑换量从低到高 3按价格从高到低 4按价格从低到高)
            category_id  分类 id
    :return: [礼品列表]
    """
    # 优化 新加分类
    # tm= db.slave.score_gift.select("id", "name", "img_url", "score", "gift_detail").filter(app_id=APPID, status=1, category_id=category_id)
    if category_id:
        gifts = db.slave.score_gift.select("id", "name", "img_url", "score", "category_id", "available_date").filter(
            app_id=APPID,
            status=1,
            category_id=category_id).order_by('-id')[:]
    else:
        gifts = db.slave.score_gift.select("id", "name", "img_url", "score", "category_id", "available_date").filter(
            app_id=APPID,
            status=1).order_by('-id')[:]
    gift_ids = [g.id for g in gifts]
    order_dict = get_order_dict(gift_ids)
    for gift in gifts:
        gift.img_url = get_absurl(gift.img_url)
        # 兑换量
        gift.norder = order_dict.get(gift.id) or 0
        # 判断是否为新礼品，7天以内算新品
        gift.is_new = 0
        if int(time.time()) - gift.available_date <= 3600 * 24 * 7:
            gift.is_new = 1

    # 排序
    if sort == 1:
        gifts.sort(key=lambda x: (-x.is_new, -x.norder))
    elif sort == 2:
        gifts.sort(key=lambda x: (-x.is_new, x.norder))
    elif sort == 3:
        gifts.sort(key=lambda x: (-x.is_new, x.norder))
    elif sort == 4:
        gifts.sort(key=lambda x: (-x.is_new, x.voucher, x.point))
    else:
        gifts.sort(key=lambda x: -x.is_new)

    return gifts


def get_gift(id):
    """
    单个商品详情
    -----------------------
    王晨光     2016-12-06
    -----------------------
    :param id: 礼品ID
    :return: {id:礼品ID, }
    """
    if not id:
        return
    gift = db.slave.score_gift.get(id=id)
    if not gift:
        return
    data = Struct()
    data.id = gift.id
    data.name = gift.name
    data.category_id = gift.category_id
    data.status = gift.status
    data.num = gift.num
    data.img_url = get_absurl(gift.img_url)
    data.score = gift.score
    data.gift_detail = gift.gift_detail
    return data


def create_order_number():
    """
    功能说明：             生成订单号(公共变量c)
    -----------------------------------------------
    修改人                    修改时间
    -----------------------------------------------
    王晨光                   2015-11-2
    """
    order = db.slave.score_gift_order.filter(app_id=APPID).last()
    no = order.order_number if order else ''
    no_time = no[:14]
    no_salt = no[14:]
    now = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    new = ''
    if now > no_time:
        new = now + '001'
    else:
        new = no_time + "%03d" % (int(no_salt) + 1)
    return new


def buy(request, user, gift, n, link_user, link_phone, link_address, link_count):
    """
    订购商品
    -----------------------
    王晨光     2016-12-06
    -----------------------
    :param user: 用户
    :param gift: 商品
    :param n: 个数
    :param link_user: 联系人
    :param link_phone: 联系电话
    :param link_address: 联系地址
    :param link_count: 地市编码
    :return: {
        'orderno': 订单号,
        'cost': 消费积分,
        'score': 剩余积分,
    }
    """
    # 总分
    need_score = n * gift.score
    # 库存
    if gift.num < n:
        return ajax.jsonp_fail(request, 'no_stock', message='库存不足')

    # 事务
    with db.default as c:
        # 扣分
        us = c.score_user.get(app_id=APPID, user_id=user.id)
        u_score = us.score if us else 0
        if u_score < need_score:
            return ajax.jsonp_fail(request, 'no_score', message='积分不足')
        u_score = u_score - need_score
        if not us:
            us_id = c.score_user.create(
                app_id=APPID,
                user_id=user.id,
                score=u_score,
            )
        else:
            c.score_user.filter(id=us.id).update(score=u_score)
        c.score_gift.filter(id=gift.id).update(num=gift.num - n)

        # 生成订单
        no = create_order_number()
        now = int(time.time())
        order_id = c.score_gift_order.create(
            app_id=APPID,
            order_number=no,
            user_id=user.id,
            gift_id=gift.id,
            num=n,
            score=gift.score,
            status=0,
            link_user=link_user if link_user else user.real_name,
            link_phone=link_phone if link_phone else user.phone_number,
            link_address=link_address,
            link_count=link_count,
            add_date=now,
            update_date=now,
        )

        # 生成兑换记录
        c.score_user_detail.create(
            app_id=APPID,
            user_id=user.id,
            item_no='tea_voucher',
            score=need_score,
            cycle_num=1,
            remark=u"积分商城兑换礼品,订单号%s" % no,
            add_date=now
        )

        # # 分类总数量减少--- 不需要这个字段了
        # sql = """
        #     update score_gift_category set total_number = total_number-%s WHERE id = %s
        #     """ % (n, gift.category_id)
        # c.execute(sql)

        data = {
            'orderno': no,
            'cost': need_score,
            'score': u_score,
        }
        return ajax.jsonp_ok(request, data)


def get_user_details(user_id, way, pageno, pagesz=10):
    """
    获取用户积分明细
    -----------------------
    王晨光     2016-12-07
    -----------------------
    :param user_id: 用户ID
    :param way: 明细分类(1收入 2支出 0全部)
    :param pageno: 页号
    :param pagesz: 每页条数
    :return: {balance:余额, pagecount:总页数, details:[detail]}
    """
    us = db.slave.score_user.get(app_id=APPID, user_id=user_id)
    balance = us.score if us else 0

    details = db.slave.score_user_detail.filter(app_id=APPID, user_id=user_id)
    if way == 1:
        details = details.filter(item_no='tea_voucher_bak')
    elif way == 2:
        details = details.filter(item_no='tea_voucher')

    n = details.count()
    pagecount = int(math.ceil(1.0 * n / pagesz))
    details = details.order_by('-id')[(pageno - 1) * pagesz:pageno * pagesz]
    rows = []
    for d in details:
        item_no = d.item_no
        score = d.score
        theway = 0  # 0收入 1支出
        if item_no == 'tea_voucher':
            title = u"支出%s金豆" % score
            theway = 1
        elif item_no == 'tea_voucher_bak':
            title = u"收入%s金豆" % score
        row = Struct()
        row.id = d.id
        row.item_no = d.item_no
        row.way = theway
        row.title = title
        row.score = score
        row.remark = d.remark
        row.add_date = from_unixtime(d.add_date).strftime('%Y-%m-%d %H:%M')
        rows.append(row)
    out = {
        'balance': balance,
        'pageno': pageno,
        'pagecount': pagecount,
        'details': rows
    }
    return out


def get_user_orders(user_id, pageno, pagesz):
    """
    获取用户订单明细
    -----------------------
    王晨光     2016-12-07
    -----------------------
    :param user_id: 用户ID
    :param pageno: 页号
    :param pagesz: 每页条数
    :return: {pagecount:总页数, orders:[订单列表]}
    """
    orders = db.slave.score_gift_order.filter(app_id=APPID, user_id=user_id)
    n = orders.count()
    pagecount = int(math.ceil(1.0 * n / pagesz))
    orders = orders.order_by('-id')[(pageno - 1) * pagesz:pageno * pagesz]
    gift_ids = [o.gift_id for o in orders]
    gifts = db.slave.score_gift.filter(id__in=gift_ids)
    giftdict = {g.id: g for g in gifts}
    rows = []
    for o in orders:
        gift = giftdict.get(o.gift_id)
        r = Struct()
        r.id = o.id
        r.order_number = o.order_number
        r.gift_id = gift.id if gift else 0
        r.gift_name = gift.name if gift else u''
        r.gift_img = get_absurl(gift.img_url) if gift else ''
        r.num = o.num
        r.score = o.score
        r.status = o.status
        r.add_time = from_unixtime(o.add_date).strftime('%Y-%m-%d %H:%M')
        r.update_time = from_unixtime(o.update_date).strftime('%Y-%m-%d %H:%M')
        r.express = o.express
        rows.append(r)
    data = {
        'pagecount': pagecount,
        'orders': rows
    }
    return data


POINT_APP_ID = 8


def get_gift_assord():
    """
    功能说明：                金豆商城， 分类筛选
    -----------------------------------------------
    修改人                    修改时间
    -----------------------------------------------
    张帅男                    2017-10-21
    """
    data = db.slave.score_gift_category.select("id", "name").filter(app_id=POINT_APP_ID, del_state=0)[:]
    if not data:
        return {}

    sql = """
            SELECT category_id, SUM(num) num FROM score_gift WHERE app_id = 7 AND `status` = 1 GROUP BY category_id;
        """
    cate_nums = db.slave.fetchall_dict(sql)
    cate_dict = {}
    for cate_n in cate_nums:
        cate_dict[cate_n.category_id] = cate_n.num
    for d in data:
        d.total_number = cate_dict.get(d.id, 0)
    return data


def get_user_remind(user_id):
    """新礼品上线，用户弹窗记录"""
    newest_gift = db.slave.score_gift.select('available_date').filter(app_id=7, status=1).order_by(
        '-available_date').first()
    if not newest_gift or newest_gift.available_date == 0:
        return 0
    remind = db.slave.score_gift_remind.select('id', 'available_date').get(user_id=user_id)
    if not remind:
        db.default.score_gift_remind.create(user_id=user_id, available_date=newest_gift.available_date)
        return 1
    if remind.available_date < newest_gift.available_date:
        db.slave.score_gift_remind.filter(user_id=user_id).update(user_id=user_id,
                                                                  available_date=newest_gift.available_date)
        return 1
    return 0


def get_wish_list(user_id, p, page_size):
    """愿望墙列表"""
    start = (p - 1) * page_size
    end = p * page_size
    # 30天的愿望不显示,    # 审核通过两个小时内的愿望不显示
    nowt = int(time.time())
    begin_time = nowt - 24 * 3600 * 30
    end_time = nowt - 3600 * 2
    wish = db.slave.score_gift_wish.select('wish', 'votes', 'id').filter(status=1,
                                                                         update_time__range=[begin_time,
                                                                                             end_time]).order_by(
        '-votes', 'id')[start:end]
    wish_ids = [r.id for r in wish]
    user_vote = []
    if wish_ids:
        user_vote = db.slave.score_gift_wish_vote.select('wish_id').filter(
            user_id=user_id,
            status=1,
            wish_id__in=wish_ids).flat('wish_id')
    for k, w in enumerate(wish):
        w.rank = (p - 1) * page_size + 1 + k
        w.is_vote = 0
        if w.id in user_vote:
            w.is_vote = 1

    # 愿望总数
    count = db.slave.score_gift_wish.filter(status=1, update_time__range=[begin_time, end_time]).count()
    pages = count / page_size + 1
    return wish, pages


def get_today_user_wish(user_id):
    today = datetime.datetime.today()
    ling = datetime.datetime(today.year, today.month, today.day, 0, 0, 0)
    ling = int(time.mktime(ling.timetuple()))
    wish = db.default.score_gift_wish.select('wish', 'status').get(add_time__gte=ling, user_id=user_id)
    return wish


def save_wish(wish, user_id):
    if not wish or not user_id:
        return
    nowt = int(time.time())
    db.default.score_gift_wish.create(user_id=user_id, wish=wish, add_time=nowt,update_time=nowt, votes=0, status=0)


def vote_wish(wish_id, user_id, vote_type):
    if not (wish_id and user_id and vote_type):
        return False
    status = 1
    if vote_type == -1:
        status = 0
    nowt = int(time.time())
    with db.default as db_gift:
        user_vote = db_gift.score_gift_wish_vote.get(wish_id=wish_id, user_id=user_id)
        if not user_vote:
            db_gift.score_gift_wish_vote.create(user_id=user_id, status=status, wish_id=wish_id, update_time=nowt)
        else:
            if user_vote.status == status:
                return False
            db_gift.score_gift_wish_vote.filter(user_id=user_id, wish_id=wish_id).update(update_time=nowt,
                                                                                         status=status)

        sql = """update score_gift_wish set votes=votes +%s where id=%s """ % (vote_type, wish_id)
        db_gift.execute(sql)
    return True
