# coding: utf-8
import datetime
from libs.utils import ajax, ajax_try
from apps.common import com_user
import common


@ajax_try([])
def p_list(request):
    """
    @api {get} /gift/list [金豆商城]商品列表
    @apiGroup gift
    @apiParamExample {json} 请求示例
        {"sort":排序方式(0默认按时间 1按兑换量从高到低 2按兑换量从低到高 3按价格从高到低 4按价格从低到高)
        "category_id": 1     # 0全部， 其他是分类搜索
        }
    @apiSuccessExample {json} 成功返回
        {
            "message": "",
            "next": "",
            "data": [
                {
                    "norder": 0, # 兑换量
                    "score": 0, # 价格
                    "img_url": "http://file.tbkt.cn/upload_media/score/gift/2016/03/03/20160303170022249985.png",
                    "id": 202,
                    "name": "探险者户外34人全自动液压帐篷 牛津布防雨双人2人双层野外露营帐篷套装 三用套餐一"
                    "category_id": 1                        # 分类
                },
            ],
            "response": "ok",
            "error": ""
        }
    """
    # 排序方式(0默认按时间 1按兑换量从高到低 2按兑换量从低到高 3按价格从高到低 4按价格从低到高)
    args = request.QUERY.casts(sort=int, category_id=int)
    sort = args.sort or 1
    category_id = int(args.category_id or 0)  # 分类id
    gifts = common.get_gifts(sort, category_id)
    return ajax.jsonp_ok(request, gifts)


@ajax_try({})
def p_detail(request):
    """
    @api {get} /gift/detail [金豆商城]商品详情
    @apiGroup gift
    @apiParamExample {json} 请求示例
        {"id":礼品ID}
    @apiSuccessExample {json} 成功返回
        {
            "message": "",
            "next": "",
            "data": {
                "status": 1,
                "name": "小熊（bear）电热饭盒 加热保温饭盒 双层真空DFHS2116",
                "num": 9977, # 库存
                "score": 1,  # 价格
                "category_id": 2, # 分类 14是话费
                "img_url": "http://file.tbkt.cn/upload_media/score/gift/2016/03/03/20160303164135334193.png",
                "gift_detail": "5张图片和详解"
                "id": 173
            },
            "response": "ok",
            "error": ""
        }
    """
    # 排序方式(0默认按时间 1按兑换量从高到低 2按兑换量从低到高 3按价格从高到低 4按价格从低到高)
    args = request.QUERY.casts(id=int)
    gift_id = args.id or 0
    gift = common.get_gift(gift_id) or {}
    return ajax.jsonp_ok(request, gift)


@ajax_try({})
@com_user.need_login
def p_buy(request):
    """
    @api {post} /gift/buy [金豆商城]订购接口
    @apiGroup gift
    @apiParamExample {json} 请求示例
        {"id":礼品ID, "n":数量, "link_user":联系人, "link_phone":联系电话, "link_address":联系地址, "link_count":行政编码}
    @apiSuccessExample {json} 成功返回
        {
            "message": "",
            "next": "",
            "data": {
                "orderno": "20161207084407001" # 订单号
                "cost": 100,  # 本次扣除金豆
                "score": 662   # 剩余金豆 
            },
            "response": "ok",
            "error": ""
        }
    @apiSuccessExample {json} 失败返回
        {
            "message": "积分不足",
            "next": "",
            "data": "",
            "response": "fail",
            "error": "no_score"
        }
    """
    args = request.QUERY.casts(id=int, n=int,
                               link_user=unicode, link_phone=str,
                               link_address=unicode, link_count=str)
    id = args.id or 0
    n = args.n or 1
    n = max(1, n)
    # 新增用户订单收货地址
    link_user = args.link_user or ''
    link_phone = args.link_phone or ''
    link_address = args.link_address or ''
    link_count = args.link_count or ''

    now = datetime.datetime.now()

    gift = common.get_gift(id)
    if not gift:
        return ajax.jsonp_fail(request, 'no_gift', message='商品不存在')

    user = request.user
    return common.buy(request, user, gift, n, link_user, link_phone, link_address, link_count)


@ajax_try({})
@com_user.need_login
def p_scores(request):
    """
    @api {get} /gift/scores [金豆商城]用户积分详情
    @apiGroup gift
    @apiParamExample {json} 请求示例
        {"way":明细分类(1收入 2支出 0全部), "p":页号, "psize":每页几条}
    @apiSuccessExample {json} 成功返回
    {
        "message": "",
        "next": "",
        "data": {
            "balance": 1162, # 余额
            "details": [
                {
                    "item_no": "tea_voucher",
                    "title": "支出100金豆",
                    "remark": "积分商城兑换礼品,订单号20170218160135002",
                    "add_date": "2016-12-07 08:44:07",
                    "score": 100,
                    "way": 1, # 明细分类(1收入 2支出)
                    "id": 6110933 # 明细ID
                },
            ],
            "pageno": 1, # 当前页号
            "pagecount": 20 # 总页数
        },
        "response": "ok",
        "error": ""
    }
    """
    args = request.QUERY.casts(way=int, p=int, psize=int)
    way = args.way or 0
    pageno = args.p or 1
    pageno = max(1, pageno)
    pagesz = args.psize or 10
    user_id = request.user_id
    details = common.get_user_details(user_id, way, pageno, pagesz=pagesz)
    return ajax.jsonp_ok(request, details)


@ajax_try({})
@com_user.need_login
def p_orders(request):
    """
    @api {get} /gift/orders [金豆商城]用户订单详情
    @apiGroup gift
    @apiParamExample {json} 请求示例
        {"p":页号, "psize":每页几条}
    @apiSuccessExample {json} 成功返回
    {
        "message": "",
        "next": "",
        "data": {
            "orders": [
                {
                    "id": 4577 # 订单ID
                    "status": 0, # 0未发货, 1已发货, 2已取消
                    "add_time": "2017-02-18 16:01", # 订购时间
                    "update_time": "2016-09-05 15:42",  # 发货时间
                    "gift_id": 367, # 商品ID
                    "gift_img": "http://file.tbkt.cn/upload_media/score/gift/2016/06/08/20160608140932235338.jpg",
                    "gift_name": "厨房必备切菜神器",
                    "num": 1, # 兑换数量
                    "score": 59, # 兑换单价
                    "order_number": "20160801181131001", # 订单号
                    "express": "", # 快递单号
                },
            ],
            "pagecount": 8 # 总页数
        },
        "response": "ok",
        "error": ""
    }
    """
    args = request.QUERY.casts(p=int, psize=int)
    pageno = args.p or 1
    pageno = max(1, pageno)
    pagesz = args.psize or 10
    user_id = request.user_id
    orders = common.get_user_orders(user_id, pageno, pagesz=pagesz)
    return ajax.jsonp_ok(request, orders)


def p_assord(request):
    """
    @api {get} /gift/assort [金豆商城]分类筛选
    @apiGroup gift
    @apiSuccessExample {json} 成功返回
    {
        "message": "",
        "next": "",
        "data": [
            {
                "id": 15,
                "total_number": 10,
                "name": "体育用品"
            },
            {
                "id": 16,
                "total_number": 20,
                "name": "电器"
            }
        ],
        "response": "ok",
        "error": ""
    }
    """
    """
    功能说明：                金豆商城， 分类筛选
    -----------------------------------------------
    修改人                    修改时间
    -----------------------------------------------
    张帅男                    2017-10-21
    """
    data = common.get_gift_assord()
    return ajax.jsonp_ok(request, data)


@ajax_try({})
@com_user.need_teacher
def p_remind(request):
    """
    @api {get} /gift/remind [金豆商城]新商品是否弹窗
    @apiGroup gift
    @apiSuccessExample {json} 成功返回
    {
        "message": "",
        "next": "",
        "data": {
            is_new:1 ：有新礼品，需要弹窗，0： 无新商品，或已经提示过
        },
        "response": "ok",
        "error": ""
    }
    """
    user_id = request.user_id
    is_new = common.get_user_remind(user_id)
    return ajax.jsonp_ok(request, {'is_new': is_new})


@ajax_try({})
@com_user.need_teacher
def p_wish_list(request):
    """
    @api {get} /gift/wish/list [金豆商城] 愿望墙列表
    @apiGroup gift
    @apiParamExample {json} 请求示例
    {"p":页号}
    @apiSuccessExample {json} 成功返回
    {
        "message": "",
        "next": "",
        "data":
            wish_list:[
                id:123 愿望id
                wish:'****',
                votes:125,

            ],
            count:10
        "response": "ok",
        "error": ""
    }
    """
    user_id = request.user_id
    args = request.QUERY.casts(p=int)
    p = args.p or 1
    page_size = 9
    today_wish = common.get_today_user_wish(user_id)
    has_wish = 0
    if today_wish:
        has_wish = 1
    wish_list, pages = common.get_wish_list(user_id, p, page_size)
    data = {"wish_list": wish_list, "count": pages, "has_wish": has_wish}
    return ajax.jsonp_ok(request, data)


@ajax_try({})
@com_user.need_teacher
def p_wish_submit(request):
    """
    @api {get} /gift/wish/submit [金豆商城] 愿望墙愿望提交
    @apiGroup gift
    @apiParamExample {json} 请求示例
    {"wish":"呵呵"  愿望内容}
    @apiSuccessExample {json} 成功返回
    {
        "message": "",
        "next": "",
        "data": []
        "response": "ok",
        "error": ""
    }
    """
    user_id = request.user_id
    args = request.QUERY.casts(wish=unicode)
    wish = args.wish.strip()
    if not wish:
        return ajax.jsonp_fail(request, error=u'愿望内容不能为空')
    if len(wish) > 120:
        return ajax.jsonp_fail(request, error=u'愿望内容过长')
    today_wish = common.get_today_user_wish(user_id)
    if today_wish:
        return ajax.jsonp_fail(request, error=u'今天已发布过愿望')
    common.save_wish(wish, user_id)
    return ajax.jsonp_ok(request)


@ajax_try({})
@com_user.need_teacher
def p_wish_vote(request):
    """
    @api {get} /gift/wish/vote [金豆商城] 愿望墙愿望投票
    @apiGroup gift
    @apiParamExample {json} 请求示例
    {
        "type":1  :投票，-1：撤销投票
        "wish_id:  124   愿望id
    }
    @apiSuccessExample {json} 成功返回
    {
        "message": "",
        "next": "",
        "data": {}
        "response": "ok",
        "error": ""
    }
    """
    args = request.QUERY.casts(type=int, wish_id=int)
    vote_type = args.type
    wish_id = args.wish_id
    if not vote_type or not wish_id or vote_type not in [-1, 1]:
        return ajax.jsonp_fail(request, error=u'参数错误')
    user_id = request.user_id
    status = common.vote_wish(wish_id, user_id, vote_type)
    if not status:
        return ajax.jsonp_fail(request, error=u'投票失败，请重试')
    return ajax.jsonp_ok(request)
