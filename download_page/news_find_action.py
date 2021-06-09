# -*- encoding: utf-8 -*-
'''
news_find_action.py
#Created on 2020/4/6 14:34
#@author:VincentZhao
'''
import traceback, queue, datetime
from bs4 import BeautifulSoup

from commons.action.base_producer_action import ProducerAction
from commons.action.base_consumer_action import ConsumerAction

from commons.action.producer import Producer
from commons.util.db_util import DBUtil
from commons.util.util import Util
from commons.util.request_util import RequestUtil
from commons.util.html_util import HtmlUtil
from commons.util.time_util import TimeUtil
from commons.util.log_util import LogUtil

from configs.config import _HAINIU_DB, _QUEUE_NEWS_FIND


# 定义发现新闻的ProducerAction
class NewsFindProducerAction(ProducerAction):

    def queue_items(self):
        # 读取hainiu_queue表的符合条件的记录，根据这个记录
        # 创建HainiuConsumerAction 对象列表，更新is_work=1，提交事务

        select_sql = """select id, action, params from hainiu_queue where type=%s and is_work=0 and fail_times < %s 
        limit 0,%s for update; """

        # 屏蔽ip的查询
        # select_sql = """
        # select id, action, params from hainiu_queue where type=%s and is_work=0 and fail_times < %s and fail_ip!=%s limit 0,%s for update;
        # """
        update_sql = """
        update hainiu_queue set is_work=1 where id in (%s);
        """

        # 创建DB_Util对象
        db_util = DBUtil(_HAINIU_DB)
        try:
            # 悲观锁查询符合条件的记录，并封装成对象列表
            sql_param = [1, _QUEUE_NEWS_FIND['MAX_FAIL_TIMES'], _QUEUE_NEWS_FIND['LIMIT_NUM']]
            # 屏蔽ip的查询参数
            # ip = Util().get_local_ip()
            # sql_param = [1, _QUEUE_NEWS_FIND['MAX_FAIL_TIMES'], ip, _QUEUE_NEWS_FIND['LIMIT_NUM']]
            # ({},{})
            res1 = db_util.read_dict(select_sql, sql_param)
            actions = []
            # 字符串列表
            ids = []
            for row in res1:
                id = row['id']
                ids.append(str(id))
                act = row['action']
                params = row['params']
                c_action = NewsFindConsumerAction(id, act, params)
                actions.append(c_action)

            # 更新记录的状态
            if len(ids) > 0:
                db_util.execute_no_commit(update_sql % ','.join(ids))

            # 提交事务
            db_util.commit()

        except Exception as msg:
            actions = []
            db_util.rollback()
            traceback.print_exc(msg)

        finally:
            db_util.close()

        return actions


# 定义发现新闻的ConsumerAction
class NewsFindConsumerAction(ConsumerAction):

    def __init__(self, id, act, params):
        super(self.__class__, self).__init__()
        self.id = id
        self.url = act
        self.params = params

        self.logger = LogUtil().get_logger('news_find_ca', 'news_find_ca')

    def action(self):
        print('id:%d, act:%s, params:%s' % (self.id, self.url, self.params))

        # 1) ----爬取种子url 获取 种子页的所有a 链接----
        request_util = RequestUtil()
        html_util = HtmlUtil()
        util = Util()
        time_util = TimeUtil()

        db_util = DBUtil(_HAINIU_DB)

        # action 操作成功失败的标记
        success_flag = True

        # 装内链接
        inner_list = []
        # 装外链接
        exter_list = []

        # 获取种子url的md5
        md5 = util.get_md5(self.url)

        # 获取创建时间
        create_time = time_util.get_timestamp()

        # 获取创建天
        create_day = time_util.now_day()
        # 获取创建小时
        create_hour = time_util.now_hour()

        # 获取更新时间
        update_time = create_time

        try:
            # 通过phandomjs 请求url，返回网页，包括网页的ajax请求
            html = request_util.http_get_phandomjs(self.url)

            # 可以从HTML或XML文件中提取数据的Python第三方库
            soup = BeautifulSoup(html, 'lxml')
            # a链接dom对象列表
            a_docs = soup.find_all("a")

            # 判断爬取的种子url页面是空的
            if len(a_docs) == 0:
                raise Exception("无效的种子url")

            aset = set()
            # 获取domain
            domain = html_util.get_url_domain(self.url)
            # 获取host
            host = html_util.get_url_host(self.url)

            # 2)----遍历 所有a链接， 分出内外链，分别放入内链list、外链list----
            for a in a_docs:
                # 获取a标签的href
                a_href = html_util.get_format_url(self.url, a, host)
                # 获取a标签的内容
                a_title = a.get_text().strip()
                if a_href == '' or a_title == '':
                    continue

                if aset.__contains__(a_href):
                    continue
                aset.add(a_href)
                # 获取a标签的host
                a_host = html_util.get_url_host(a_href)

                # 获取a标签href链接url的md5
                a_md5 = util.get_md5(a_href)

                # 获取a标签所对应的xpath
                a_xpath = html_util.get_dom_parent_xpath_js_new(a)

                # 封装一行数据的元组
                t = (self.url, md5, self.params, domain, host, a_href, a_md5,
                     a_host, a_xpath, a_title, create_time, create_day, create_hour,
                     update_time)
                # url,md5,param,domain,host,a_url,a_md5,a_host,a_xpath,a_title,create_time,
                # create_day,create_hour,update_time
                # 判断内外链
                if a_href.__contains__(domain):
                    inner_list.append(t)
                else:
                    exter_list.append(t)

            # 3)----把内链list、外链list的数据批量插入数据表----
            sql = """
            insert into <table>
    (url,md5,param,domain,host,a_url,a_md5,a_host,a_xpath,a_title,create_time,create_day,create_hour,update_time) values
    (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) on DUPLICATE KEY UPDATE update_time=values(update_time);
            """

            # 设置字符集是utf8mb4
            db_util.execute_no_commit("set NAMES utf8mb4;")

            if len(inner_list) > 0:
                # 执行插入内链表
                inner_sql = sql.replace('<table>', 'hainiu_web_seed_internally')
                db_util.executemany_no_commit(inner_sql, inner_list)
            if len(exter_list) > 0:
                # 执行插入外链表
                exter_sql = sql.replace('<table>', 'hainiu_web_seed_externally')
                db_util.executemany_no_commit(exter_sql, exter_list)

            db_util.commit()
        except Exception as msg:
            success_flag = False
            db_util.rollback()
            self.logger.exception(msg)

        finally:
            db_util.close()
            # 关闭phandomjs
            request_util.close_phandomjs()

        return self.result(success_flag, self.id, md5, len(inner_list), len(exter_list))

    def success_action(self, values):
        del_sql = 'delete from hainiu_queue where id=%s';

        update_sql = """
        update hainiu_web_seed
        set last_crawl_time=%s,
            last_crawl_internally=%s,
            last_crawl_externally=%s where md5=%s;
        """

        db_util = DBUtil(_HAINIU_DB)
        try:
            # 1）记录种子url最后爬取成功数， （用来校验最后的爬取是否成功）；
            md5 = values[1]
            last_crawl_internally = values[2]
            last_crawl_externally = values[3]
            update_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sql_params = [update_time, last_crawl_internally, last_crawl_externally, md5]
            db_util.execute_no_commit(update_sql, sql_params)

            # 2）在hainiu_queue 表中删除已经爬取成功的url；
            sql_params = [self.id]
            db_util.execute_no_commit(del_sql, sql_params)

            db_util.commit()
        except Exception as msg:
            db_util.rollback()
            self.logger.exception(msg)
        finally:
            db_util.close()

    def fail_action(self, values):
        update_sql1 = """
        update hainiu_queue set fail_ip=%s, fail_times=fail_times+1 where id=%s;
        """

        update_sql2 = """
        update hainiu_queue set is_work = 0 where id=%s;
        """

        update_sql3 = """
        update hainiu_web_seed set fail_times=fail_times+1, fail_ip=%s where md5=%s;
        """

        db_util = DBUtil(_HAINIU_DB)
        try:
            # 1) 更新失败次数和ip
            ip = Util().get_local_ip()
            sql_param = [ip, self.id]
            db_util.execute_no_commit(update_sql1, sql_param)

            # 2) 当这个记录以及达到当前机器的最大重试次数，就需要把
            #   记录的is_work 设置成0，目的是为了再次重试。
            if self.current_retry_num == _QUEUE_NEWS_FIND['C_RETRY_TIMES'] - 1:
                sql_param = [self.id]
                db_util.execute_no_commit(update_sql2, sql_param)

            # 3）更新种子表的失败次数、失败ip；队列表的数据不删除，有可能是因为目标网站把ip给封了， 在某个时间，写个脚本，把失败的队列数据改状态和失败次数和失败ip，重新爬取试试。
            md5 = values[1]
            sql_param = [ip, md5]
            db_util.execute_no_commit(update_sql3, sql_param)

            db_util.commit()
        except Exception as msg:
            db_util.rollback()
            traceback.print_exc(msg)
        finally:
            db_util.close()


# 测试
if __name__ == '__main__':
    # 创建队列
    queue = queue.Queue()
    # 创建生产动作对象
    p_action = NewsFindProducerAction()
    # 初始化生产者线程
    producer = Producer(queue,
                        _QUEUE_NEWS_FIND['NAME'],
                        p_action,
                        _QUEUE_NEWS_FIND['P_SLEEP_TIME'],
                        _QUEUE_NEWS_FIND['C_MAX_NUM'],
                        _QUEUE_NEWS_FIND['C_MAX_SLEEP_TIME'],
                        _QUEUE_NEWS_FIND['C_RETRY_TIMES']
                        )

    producer.start_work()

    # ----------单线程测试-----------
    # p_action = NewsFindProducerAction()
    # 
    # queue = Queue.Queue()
    # 
    # c_actions = p_action.queue_items()
    # for c_action in c_actions:
    #     c_action.action()
