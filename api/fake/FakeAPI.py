""" fake api to return fake data """
import os
import time
import datetime
import uuid
import requests
import operator
import time
# import threading
from threading import Thread

from functools import reduce
from api.Mongo import DbOpsFactory
import api.Mongo.config_mapping as MAPPING
from scripts.__V2.sqlgraph_v2.create_csv_from_mongo_v2 import Test
from api.Mongo.schema import document_schema, entity_schema
from api.utils.transfer import Transfer
from api.utils.creat_chart import SSH
# from api.fake.task_record import task
from api.es.set_and_project import SetProject
from api.utils.lock import LOCK
from multiprocessing import Process, Manager

import api.configs.dynamic_config as dy_config
from api.log.QBLog import QBLog

logger = QBLog({
    'LOG_LEVEL': dy_config.LOG_LEVEL
})


class FakeApplication(object):
    """ fake api to return fake data """

    def __init__(self):
        self.db = DbOpsFactory.get_dbops_instance('mongo',
                                                  host='10.60.1.140',
                                                  port=6080,
                                                  usr="root",
                                                  pwd="111111"
                                                  )
        self.transfer = Transfer('10.60.1.142', 'sqlgraph', 'sqlgraph')
        self.ssh = SSH('10.60.1.142', 'sqlgraph', 'sqlgraph')
        self.set = SetProject()
        self.lock = LOCK()

    def event2time_count(self, EventIds: list) -> dict:
        data = {
            "code": 0,
            "data": {
                "time": [
                    "2018-01-02",
                    "2018-01-03",
                    "2018-01-04",
                    "2018-02-02",
                    "2018-02-03",
                    "2018-02-04"
                ],
                "count": [
                    1,
                    2,
                    1,
                    1,
                    2,
                    1
                ]
            }
        }
        return data

    def searchTask(self, status: str, source: str, page: int, pageSize: int):
        res = {"code": 0}
        data = self.db.search_task(status=status, source=source, page=page, pageSize=pageSize)
        res["data"] = data
        return res

    # 解析原始内容为mongo指定字段并返回
    def analysis_from_search(self, query):
        if "url" not in query:
            query["url"] = ""
        res = requests.post("http://10.60.1.101:8335/corenlu_api",
                            data={"id": query["_id"], "title": query["title"],
                                  "url": query["url"], "content": query["content"]}).json()["document"]
        res["_id"] = query["_id"]
        res["channel"] = 1
        res["site_name"] = ""
        res["publish_time"] = "{}".format(int(time.time()))
        return res

    # 通过快照url抽取详情文章
    def extraction(self, urls: list, ids: list, return_list=[]):
        results = []
        try:
            for index in range(len(urls)):
                result = {}
                res = requests.post("http://221.0.111.140:8052/npce", data={"url": urls[index]}).json()
                result["_id"] = ids[index]
                result["title"] = res["doc"]["title"]
                result["url"] = urls[index]
                result["content"] = res["doc"]["content"]
                results.append(result)
                print('---------------------result-------------------')
                print(result)
                return_list.extend(results)
            return results
        except Exception as error:
            logger.error("文档详情抽取报错： {0}".format(error, urls[0]))
            return None
        # except:
        #     print('------------被卡住的url-------------')
        #     print(urls[0])
        #     raise

    def indexDataSet(self, name: str, des: str, source: str, ids: list, titles: list, urls: list):
        uu_id = "_".join(str(uuid.uuid1()).split("-"))
        print('-----------该任务的id为{}------------'.format(uu_id))
        create_time = int(time.time())
        res_data = {"code": 0, "create_time": create_time}

        # 写入任务表
        task = {
            "task_id": uu_id,
            "task_name": name,
            "task_des": des,
            "source": source,
            "create_time": create_time,
            "status": "下载中",
            "set_id": "",
            "content": [{
                'content_id': content_id,
                'title': titles[ids.index(content_id)],
                'content_status': "暂未下载",
                'content_file': "html"
            } for content_id in ids]
        }
        self.db.insert_task_state(table_id='task_record', body=task)
        extraction_result = self.extraction(urls, ids)
        if not extraction_result:
            self.db.drop_task_record_table(uu_id)
            return {"code": -1, "message": "文档详情抽取报错"}

        f = open("./api/fake/fake_data/{}.json".format(uu_id), "w")
        for doc in extraction_result:
            self.db.update_task_state(table_id='task_record', uu_id=uu_id, content_id=doc["_id"],
                                      type_key="content.$.content_status", type_val="文档下载中")

            analysis = self.analysis_from_search(doc)
            analysis["task_id"] = uu_id
            f.write("{}\n".format(analysis))
            # 将文档详情数据加载到mongo
            self.db.creat_and_index_to_mongo(body=analysis)
            self.db.update_task_state(table_id='task_record', uu_id=uu_id, content_id=doc["_id"],
                                      type_key="content.$.content_status", type_val="文档已下载")
        f.close()

        self.db.update_task_state_task(table_id='task_record', uu_id=uu_id, type_key="status", type_val="加载中")
        for doc in extraction_result:
            self.db.update_task_state(table_id='task_record', uu_id=uu_id, content_id=doc["_id"],
                                      type_key="content.$.content_status", type_val="文档加载中")


        try:
            # sqlgraph不能同时建图，在此建图前加锁，建图完成后解锁
            self.lock.monitor()

            # 将数据加载到图中
            test = Test(uu_id)
            test.run()

            # 将点边文件传到142
            try:
                # 这里的路径不是本文件的路径,是从项目根路径去找
                self.transfer.file_transfer('/home/sqlgraph/ssd/search_script/csv',
                                            './api/fake/fake_data/{}/set_document_{}.csv'.format(uu_id, uu_id))
                self.transfer.file_transfer('/home/sqlgraph/ssd/search_script/csv',
                                            './api/fake/fake_data/{}/set_relation_{}.csv'.format(uu_id, uu_id))
                self.transfer.file_transfer('/home/sqlgraph/ssd/search_script/row_doc',
                                            './api/fake/fake_data/{}.json'.format(uu_id))
                # 将项目本地中间文件删除
                os.popen('rm -rf ./api/fake/fake_data/{}*'.format(uu_id)).readlines()
            except:
                raise

            # 构建建图脚本
            # 注:当前建图时的点表边表没有过多的数据处理,如's转换文'',之后有可能因为数据格式等问题报错
            with open("./api/fake/install.sh", "r") as f:
                _res = f.read()

            cmd = [
                '''
                clickhouse client --multiquery --query="
                use EEDGraphSingular_v16;
                show tables;
                "
                '''
            ]
            need_edge = ''
            tables = self.ssh.ssh2(cmd)
            for relate in tables:
                if "set_relation" in relate:
                    need_edge += relate.replace('\tE\n', '') + ","
            need_edge += "set_relation_{}".format(uu_id)
            with open("./api/fake/install_v2.sh", "w") as I:
                I.write(_res.replace("task_id", uu_id).replace("need_edge", need_edge).replace("random", "_".join(str(uuid.uuid1()).split("-"))))

            # 将建图脚本传到142
            # 这里的路径不是本文件的路径,是从项目根路径去找
            self.transfer.file_transfer('/home/sqlgraph/ssd/search_script', './api/fake/install_v2.sh')

            # 将本地的v2版建图脚本删除
            os.popen('rm -rf ./api/fake/install_v2.sh').readlines()

            # 远程执行建图脚本
            print("建图开始!")
            self.ssh.ssh2(['sh /home/sqlgraph/ssd/search_script/install_v2.sh'])
            print("建图完成!")
        finally:
            # 解锁建图空间
            self.lock.remove_lock()

        # 任务task加载完成
        self.db.update_task_state_task(table_id='task_record', uu_id=uu_id, type_key="status", type_val="已加载")
        for doc in extraction_result:
            self.db.update_task_state(table_id='task_record', uu_id=uu_id, content_id=doc["_id"],
                                      type_key="content.$.content_status", type_val="文档已加载")
        # 创建集合
        data = {
            "name": name,
            "des": des,
            "nodeIds": [{
                "type": "document",
                "ids": ids
            }],
            "modify_time": "2019-7-30",
            "create_time": "2019-7-30",
            "modify_user": "user",
            "create_user": "user",
            "type": "human"
        }

        set_res = self.set.insert_index_set_data(data)
        type_val = set_res["data"]["id"]
        self.db.update_task_state_task(table_id='task_record', uu_id=uu_id, type_key="set_id", type_val=type_val)

        res_data["uu_id"] = uu_id
        return res_data

    def to_do_task(self, task_ids: list, dispose_type: str):
        if dispose_type == "uninstall":
            try:
                # 抢进程锁
                self.lock.monitor()
                for task_id in task_ids:
                    self.db.update_task_state_task(table_id='task_record', uu_id=task_id, type_key="status",
                                                   type_val="卸载中")
                    self.db.update_task_state_to_do(table_id='task_record', uu_id=task_id, end="文档卸载中")
                    # 处理建图脚本

                    with open("./api/fake/uninstall.sh", "r") as f:
                        _res = f.read()

                    cmd = [
                        '''
                        clickhouse client --multiquery --query="
                        use EEDGraphSingular_v16;
                        show tables;
                        "
                        '''
                    ]
                    need_edge = ''
                    tables = self.ssh.ssh2(cmd)
                    for relate in tables:
                        if "set_relation" in relate and task_id not in relate:
                            need_edge += "," + relate.replace('\tE\n', '')

                    with open("./api/fake/uninstall_v2.sh", "w") as I:
                        I.write(_res.replace("task_id", task_id).replace("need_edge", need_edge).replace("random", "_".join(str(uuid.uuid1()).split("-"))))

                    # 将建图脚本传到142
                    # 这里的路径不是本文件的路径,是从项目根路径去找
                    self.transfer.file_transfer('/home/sqlgraph/ssd/search_script', './api/fake/uninstall_v2.sh')

                    # 将本地的v2版建图脚本删除
                    os.popen('rm -rf ./api/fake/uninstall_v2.sh').readlines()

                    # 远程执行建图脚本， 并删除服务器相关文件
                    print("建图开始!")
                    self.ssh.ssh2(['sh /home/sqlgraph/ssd/search_script/uninstall_v2.sh'])
                    print("建图完成!")

                    self.db.update_task_state_task(table_id='task_record', uu_id=task_id, type_key="status",
                                                   type_val="已卸载")
                    self.db.update_task_state_to_do(table_id='task_record', uu_id=task_id, end="文档已卸载")
            finally:
                # 解锁建图空间
                self.lock.remove_lock()

        elif dispose_type == "del":
            self.to_do_task(task_ids=task_ids, dispose_type="uninstall")
            for task_id in task_ids:
                self.db.update_task_state_task(table_id='task_record', uu_id=task_id, type_key="status", type_val="删除中")
                self.db.update_task_state_to_do(table_id='task_record', uu_id=task_id, end="文档删除中")
                # 如需提速，考虑将删除做成定时任务，接口中先不执行删除(测试删除远程文件速度极快)
                self.ssh.ssh2(['rm -rf /home/sqlgraph/ssd/search_script/csv/set_document_{}.csv'.format(task_id),
                               'rm -rf /home/sqlgraph/ssd/search_script/csv/set_relation_{}.csv'.format(task_id),
                               'rm -rf /home/sqlgraph/ssd/search_script/row_doc/{}.json'.format(task_id)
                               ])
                self.db.update_task_state_task(table_id='task_record', uu_id=task_id, type_key="status", type_val="已删除")
                self.db.update_task_state_to_do(table_id='task_record', uu_id=task_id, end="文档已删除")

                # 删集合
                _set_id = self.db.drop_task_set_id_table(task_id)
                self.set.deleteSetorProject(label="set", idlist=[_set_id], type="set")
                # 删mongo表删记录
                self.db.drop_task_table(task_id)
                # 删任务
                self.db.drop_task_record_table(task_id)

        elif dispose_type == "install":
            try:
                # 抢进程锁
                self.lock.monitor()
                for uu_id in task_ids:
                    self.db.update_task_state_task(table_id='task_record', uu_id=uu_id, type_key="status",type_val="加载中")
                    self.db.update_task_state_to_do(table_id='task_record', uu_id=uu_id, end="文档加载中")

                    # 构建建图脚本
                    with open("./api/fake/install.sh", "r") as f:
                        _res = f.read()

                    cmd = [
                        '''
                        clickhouse client --multiquery --query="
                        use EEDGraphSingular_v16;
                        show tables;
                        "
                        '''
                    ]
                    need_edge = ''
                    tables = self.ssh.ssh2(cmd)
                    for relate in tables:
                        if "set_relation" in relate:
                            need_edge += relate.replace('\tE\n', '') + ","
                    need_edge += "set_relation_{}".format(uu_id)

                    with open("./api/fake/install_v2.sh", "w") as I:
                        I.write(_res.replace("task_id", uu_id).replace("need_edge", need_edge).replace("random", "_".join(str(uuid.uuid1()).split("-"))))

                    # 将建图脚本传到142
                    # 这里的路径不是本文件的路径,是从项目根路径去找
                    self.transfer.file_transfer('/home/sqlgraph/ssd/search_script', './api/fake/install_v2.sh')

                    # 将本地的v2版建图脚本删除
                    os.popen('rm -rf ./api/fake/install_v2.sh').readlines()

                    # 远程执行建图脚本
                    print("建图开始!")
                    self.ssh.ssh2(['sh /home/sqlgraph/ssd/search_script/install_v2.sh'])
                    print("建图完成!")

                    self.db.update_task_state_task(table_id='task_record', uu_id=uu_id, type_key="status", type_val="已加载")
                    self.db.update_task_state_to_do(table_id='task_record', uu_id=uu_id, end="文档已加载")
            finally:
                # 解锁建图空间
                self.lock.remove_lock()
        return {"code": 0}

    def upload_task(self, content: list, name: str, des: str, source: str):
        uu_id = "_".join(str(uuid.uuid1()).split("-"))
        print('-----------该任务的id为{}------------'.format(uu_id))
        create_time = int(time.time())
        res_data = {"code": 0, "create_time": create_time}

        # 写入任务表
        task = {
            "task_id": uu_id,
            "task_name": name,
            "task_des": des,
            "source": source,
            "create_time": create_time,
            "status": "上传中",
            "set_id": "",
            "content": [{
                'content_id': con["_id"],
                'title': con["title"],
                'content_status': "暂未上传",
                'content_file': "html"
            } for con in content]
        }
        self.db.insert_task_state(table_id='task_record', body=task)

        f = open("./api/fake/fake_data/{}.json".format(uu_id), "w")
        for doc in content:
            self.db.update_task_state(table_id='task_record', uu_id=uu_id, content_id=doc["_id"],
                                      type_key="content.$.content_status", type_val="文档上传中")

            analysis = self.analysis_from_search(doc)
            analysis["task_id"] = uu_id
            f.write("{}\n".format(analysis))
            # 将文档详情数据加载到mongo
            self.db.creat_and_index_to_mongo(body=analysis)
            self.db.update_task_state(table_id='task_record', uu_id=uu_id, content_id=doc["_id"],
                                      type_key="content.$.content_status", type_val="文档已上传")
        f.close()

        self.db.update_task_state_task(table_id='task_record', uu_id=uu_id, type_key="status", type_val="加载中")
        for doc in content:
            self.db.update_task_state(table_id='task_record', uu_id=uu_id, content_id=doc["_id"],
                                      type_key="content.$.content_status", type_val="文档加载中")

        # 以下跟元搜索的接口的任务一模一样##############################################################################
        try:
            # sqlgraph不能同时建图，在此建图前加锁，建图完成后解锁
            self.lock.monitor()

            # 将数据加载到图中
            test = Test(uu_id)
            test.run()

            # 将点边文件传到142
            try:
                # 这里的路径不是本文件的路径,是从项目根路径去找
                self.transfer.file_transfer('/home/sqlgraph/ssd/search_script/csv',
                                            './api/fake/fake_data/{}/set_document_{}.csv'.format(uu_id, uu_id))
                self.transfer.file_transfer('/home/sqlgraph/ssd/search_script/csv',
                                            './api/fake/fake_data/{}/set_relation_{}.csv'.format(uu_id, uu_id))
                self.transfer.file_transfer('/home/sqlgraph/ssd/search_script/row_doc',
                                            './api/fake/fake_data/{}.json'.format(uu_id))
                # 将项目本地中间文件删除
                os.popen('rm -rf ./api/fake/fake_data/{}*'.format(uu_id)).readlines()
            except:
                raise

            # 构建建图脚本
            # 注:当前建图时的点表边表没有过多的数据处理,如's转换文'',之后有可能因为数据格式等问题报错
            with open("./api/fake/install.sh", "r") as f:
                _res = f.read()

            cmd = [
                '''
                clickhouse client --multiquery --query="
                use EEDGraphSingular_v16;
                show tables;
                "
                '''
            ]
            need_edge = ''
            tables = self.ssh.ssh2(cmd)
            for relate in tables:
                if "set_relation" in relate:
                    need_edge += relate.replace('\tE\n', '') + ","
            need_edge += "set_relation_{}".format(uu_id)
            with open("./api/fake/install_v2.sh", "w") as I:
                I.write(_res.replace("task_id", uu_id).replace("need_edge", need_edge).replace("random", "_".join(
                    str(uuid.uuid1()).split("-"))))

            # 将建图脚本传到142
            # 这里的路径不是本文件的路径,是从项目根路径去找
            self.transfer.file_transfer('/home/sqlgraph/ssd/search_script', './api/fake/install_v2.sh')

            # 将本地的v2版建图脚本删除
            os.popen('rm -rf ./api/fake/install_v2.sh').readlines()

            # 远程执行建图脚本
            print("建图开始!")
            self.ssh.ssh2(['sh /home/sqlgraph/ssd/search_script/install_v2.sh'])
            print("建图完成!")
        finally:
            # 解锁建图空间
            self.lock.remove_lock()

        # 以下改了点参数#################################################################################
        # 任务task加载完成
        self.db.update_task_state_task(table_id='task_record', uu_id=uu_id, type_key="status", type_val="已加载")
        for doc in content:
            self.db.update_task_state(table_id='task_record', uu_id=uu_id, content_id=doc["_id"],
                                      type_key="content.$.content_status", type_val="文档已加载")
        # 创建集合
        data = {
            "name": name,
            "des": des,
            "nodeIds": [{
                "type": "document",
                "ids": [_con["_id"] for _con in content]
            }],
            "modify_time": "2019-7-30",
            "create_time": "2019-7-30",
            "modify_user": "user",
            "create_user": "user",
            "type": "human"
        }

        set_res = self.set.insert_index_set_data(data)
        type_val = set_res["data"]["id"]
        self.db.update_task_state_task(table_id='task_record', uu_id=uu_id, type_key="set_id", type_val=type_val)

        res_data["uu_id"] = uu_id
        return res_data

    def dataSearch(self, keyword, website, requestNumber) -> dict:
        result = {"code": 0, "search_id": "_".join(str(uuid.uuid1()).split("-")), "data": []}
        url = f"http://10.60.1.102:9190/golaxy/metasearch/web/v1?keyword={keyword}&website={website}&requestNumber={requestNumber}"
        res = requests.get(url).json()
        for rec in res["webMetasearchResults"]:
            rec["id"] = "_".join(str(uuid.uuid1()).split("-"))
            rec["se"] = rec.pop("searchWebsites")
            rec["description"] = rec.pop("abstract")
            rec["publish_time"] = rec.pop("publishTime")
            result["data"].append(rec)
        return result

    def search_attr(self, ids: list, ses: list):
        result = {"code": 0, "data": []}
        res, data, tmp_all = {}, {}, {}
        fieldName_frist = {'firstLevelId': "ObjectsType", 'firstLevelName': "对象类型", "subStatisticsAttr": []}
        fieldName_sec = {'firstLevelId': "DocumentAttr", 'firstLevelName': "文档属性", "subStatisticsAttr": []}

        res["secondLevelId"] = "document"
        res["secondLevelName"] = "文档类型"
        res["specificStaticsAttr"] = []

        tmp_all["thirdLevelId"] = "_".join(str(uuid.uuid1()).split("-"))
        tmp_all["thirdLevelName"] = "全部"
        tmp_all["count"] = len(ids)
        tmp_all["idlist"] = ids
        tmp_all["per"] = 100
        res["specificStaticsAttr"].append(tmp_all)
        fieldName_frist["subStatisticsAttr"].append(res)
        result["data"].append(fieldName_frist)

        content = {}
        data["secondLevelId"] = "se"
        data["secondLevelName"] = "搜索引擎"
        data["specificStaticsAttr"] = []
        data["typecount"] = len(ses)
        for se in ses:
            for media in se:
                if media not in content:
                    content[media] = {}
                    content[media]["thirdLevelId"] = "_".join(str(uuid.uuid1()).split("-"))
                    content[media]["thirdLevelName"] = media
                    content[media]["idlist"] = [ids[ses.index(se)]]
                else:
                    content[media]["idlist"].append(ids[ses.index(se)])
        for record in list(content.values()):
            record["count"] = len(record["idlist"])
            record["per"] = int(record['count'] / len(ids) * 100) if ids else 0
            data["specificStaticsAttr"].append(record)

        fieldName_sec["subStatisticsAttr"].append(data)
        result["data"].append(fieldName_sec)
        return result

    # 多进程版
    def attr_pretreatment(self, data):
        jobs = []
        manager = Manager()
        return_list = manager.list()

        # 解析原始数据
        for rec in data["data"]:
            p = Process(target=self.extraction, args=([rec["url"]], [rec["id"]], return_list))
            # print('-------------------p--------------------')
            # print(p)
            jobs.append(p)
            p.start()
        for p in jobs:
            # p.join(timeout=10)
            p.join()

        # print("-------------return_list-------------")
        # print(return_list)

        logger.info("元搜索内容抽取/解析/入库完毕～")

        # 将原始数据进行解析并存入mongo(子进程不能继承父进程的mongo的游标，故不使用)
        for doc in return_list:
            analysis = self.analysis_from_search(doc)
            analysis["search_id"] = data["search_id"]
            analysis["search_time"] = "{}".format(int(time.time()))
            print('----------------analysis------------------')
            print(analysis)

            # 将文档详情数据加载到mongo
            self.db.search_index_to_mongo(body=analysis)

        return

    def AttrStatistics(self, docIds: list = [], doc_e_e_d=False):
        _res_result = []
        sub_types = ["site_name", "topic"]
        def select_entity_by_doc_eve(result: list):
            entity_ids = list(set(reduce(operator.add, list(result.values()))))
            entity_info = self.db.find_entity_info_by_entity_list(entity_ids)
            for _each in list(entity_info.values()):
                for _sec in _each:
                    _sec["idlist"] = []
                    for _event_id in result:
                        if _sec[entity_schema.get("Entity_id")] in result[_event_id]:
                            _sec["idlist"].append(_event_id)
            return entity_info

        if len(docIds) != 0 and not doc_e_e_d:
            _id = document_schema.get("_id")
            _res_result = self.db.find_subdoc_by_doc_sub_type_from_docSearch(docIds, sub_types)
            data = {}
            for _rec in _res_result:
                for _sub in _rec:
                    if _sub in sub_types:
                        if _sub not in data:
                            data[_sub] = {}
                        if _rec[_sub].lower() in data[_sub]:
                            data[_sub][_rec[_sub].lower()].append(_rec[_id])
                        else:
                            data[_sub][_rec[_sub].lower()] = []
                            data[_sub][_rec[_sub].lower()].append(_rec[_id])
            return data

        if doc_e_e_d:
            if len(docIds) == 0:
                return []
            else:
                _res_result = self.db.find_entity_list_by_doc_id_from_docSearch(docIds)
                return select_entity_by_doc_eve(_res_result)

    def TypeAttr(self, docIds):
        result_all = []
        _len = len(docIds)

        result = {'firstLevelId': "DocumentAttr", 'firstLevelName': "文档属性", "subStatisticsAttr": []}

        ASTS = self.AttrStatistics(docIds=docIds)
        if ASTS:
            for sub_type in ASTS:
                result_second = {}
                s_type = "_".join(sub_type.split(" "))
                result_second["secondLevelId"] = "_".join(str(uuid.uuid1()).split("-"))
                result_second["secondLevelName"] = MAPPING.chinese["document"][s_type] if s_type in MAPPING.chinese[
                    "document"] else s_type
                result_second["specificStaticsAttr"] = []
                for subsub_type in ASTS[sub_type]:
                    result_third = {}
                    result_third["thirdLevelId"] = "_".join(str(uuid.uuid1()).split("-"))
                    result_third["thirdLevelName"] = MAPPING.chinese['type'][
                        subsub_type.lower()] if subsub_type.lower() in \
                                                MAPPING.chinese[
                                                    'type'] else subsub_type
                    result_third["idlist"] = ASTS[sub_type][subsub_type]
                    result_third["count"] = len(result_third["idlist"])
                    result_third["per"] = int(result_third['count'] / _len * 100)
                    result_second["specificStaticsAttr"].append((result_third))
                    result_second["specificStaticsAttr"] = sorted(result_second["specificStaticsAttr"],
                                                                  key=lambda x: x["count"],
                                                                  reverse=True)
                result_second["typecount"] = len(result_second["specificStaticsAttr"])
                result["subStatisticsAttr"].append(result_second)

            Entity_name, Chinese_name = entity_schema.get("Entity_name"), entity_schema.get("Chinese_name")

            def select_entity_list(ids):
                # 统计需求写死，待之后需求变化写入配置文件
                for sub_type in ["human", "organization", "administrative", "geographic_entity"]:
                    if sub_type in ids:
                        tmp = {}
                        tmp["secondLevelId"] = sub_type
                        tmp["secondLevelName"] = MAPPING.chinese["entity"][sub_type]

                        tmp["specificStaticsAttr"] = []
                        for _third in ids[sub_type]:
                            stmp = {}
                            stmp["thirdLevelId"] = "_".join(_third[Entity_name].split(" "))
                            stmp["thirdLevelName"] = _third[Chinese_name] if _third[Chinese_name] != '' else \
                                stmp["thirdLevelId"]
                            stmp["idlist"] = _third["idlist"]
                            stmp["count"] = len(stmp["idlist"])
                            stmp["per"] = int(stmp["count"] / _len * 100)
                            tmp["specificStaticsAttr"].append(stmp)
                        tmp["typecount"] = len(tmp["specificStaticsAttr"])
                        tmp["specificStaticsAttr"] = sorted(tmp["specificStaticsAttr"], key=lambda x: x["count"],
                                                            reverse=True)
                        result["subStatisticsAttr"].append(tmp)
                result_all.append(result)

            doc_entity_ids = self.AttrStatistics(docIds=docIds, doc_e_e_d=True)
            select_entity_list(ids=doc_entity_ids)
        return result_all[:3]

    def se_attr(self, search_id: str, ids: list):
        result = {"code": 0, "data": []}
        _len = len(ids)
        fieldName_frist = {'firstLevelId': "ObjectsType", 'firstLevelName': "对象类型", "subStatisticsAttr": []}
        res = {}
        res["secondLevelId"] = "document"
        res["secondLevelName"] = "文档类型"
        res["specificStaticsAttr"] = []
        tmp_all = {}
        _all = self.db.find_doc_from_doc_search(search_id, ids)
        if _all:
            tmp_all["thirdLevelId"] = "_".join(str(uuid.uuid1()).split("-"))
            tmp_all["thirdLevelName"] = "全部"
            tmp_all["count"] = len(_all)
            tmp_all["idlist"] = [re["_id"] for re in _all]
            tmp_all["per"] = int(tmp_all['count'] / _len * 100) if _len else 0
            res["specificStaticsAttr"].append(tmp_all)
        fieldName_frist["subStatisticsAttr"].append(res)

        result['data'].append(fieldName_frist)
        result['data'].extend(self.TypeAttr(ids))

        return result
