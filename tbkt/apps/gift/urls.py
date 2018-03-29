# coding: utf-8
from django.conf.urls import include, url, patterns

# 礼品商城
urlpatterns = patterns('apps.gift.views',
                       (r'^list$', 'p_list'),
                       (r'^detail$', 'p_detail'),
                       (r'^buy$', 'p_buy'),
                       (r'^scores$', 'p_scores'),
                       (r'^orders$', 'p_orders'),
                       (r'^assort$', 'p_assord'),  # 分类筛选

                       (r'^remind$', 'p_remind'),  # 更新礼品时，用户弹窗提示
                       (r'^wish/list$', 'p_wish_list'),  # 愿望墙
                       (r'^wish/submit$', 'p_wish_submit'),  # 愿望墙提交
                       (r'^wish/vote$', 'p_wish_vote'),  # 愿望墙投票
                       )
