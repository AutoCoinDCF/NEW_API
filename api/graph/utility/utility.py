""" some utility functions"""
# import paramiko
import datetime
from defaultlist import defaultlist
from collections import defaultdict, Iterable


def create_response_dict(code: int, message: str = "", nodes: list = None, links: list = None) -> dict:
    """
    use code, nodes and links to chrate a response dict
    :param code: response code, 0 is success
    :param nodes: nodes
    :param links: links
    :return: the response dict
    """
    return {
        "code": code,
        "message": message,
        "data": [{
            "nodes": nodes if nodes else [],
            "links": links if links else [],
        }] if code == 0 else defaultlist(lambda: defaultdict(list))
    }


class NestedHelper(object):
    def __init__(self, obj: object):
        self.obj = obj

    def deep_get(self, multi_index: tuple):
        if isinstance(multi_index, str) or not isinstance(multi_index, Iterable):
            return self.obj[multi_index]
        else:
            item = self.obj
            for index in multi_index:
                item = item[index]
            return item

    def flatten2dict(self, enum_start=1, empty_to_none=True):
        def flatten2dict(obj, enum_start=1, empty_to_none=True):
            if isinstance(obj, str) or not isinstance(obj, Iterable):
                return obj
            elif empty_to_none and isinstance(obj, Iterable) and not obj:
                return None
            else:
                new_dict = dict()
                iterator = obj.items() if isinstance(obj, dict) else enumerate(obj, start=enum_start)
                for k, v in iterator:
                    flat = flatten2dict(v, enum_start)
                    if isinstance(flat, dict):
                        for subk, subv in flat.items():
                            new_dict["%s.%s" % (k, subk)] = subv
                    else:  # atom type
                        new_dict[str(k)] = flat
                return new_dict

        return flatten2dict(self.obj, enum_start, empty_to_none)

    def deep_drop_empty(self):
        def deep_drop_empty(obj):
            if isinstance(obj, str) or not isinstance(obj, Iterable):
                return obj
            elif isinstance(obj, dict):
                return {k: deep_drop_empty(v) for k, v in obj.items() if deep_drop_empty(v)}
            elif isinstance(obj, list):
                return [deep_drop_empty(v) for v in obj if deep_drop_empty(v)]
            elif isinstance(obj, set):
                return set(deep_drop_empty(v) for v in obj if deep_drop_empty(v))
            else:
                return obj

        return deep_drop_empty(self.obj)


class Match_list:

    def filter_group(self, list_r):
        list_c = list_r.copy()
        list_h = []
        for id in list_r:
            if ''.join(id) not in list_h:
                list_h.append(''.join(id))
            else:
                list_c.remove(id)
        return list_c

    def group_id(self, todo_list):
        # 倒序查找，先最多的组合，直到为2
        list_r = []

        def chance(todo_list):
            if len(todo_list) == 2:
                list_r.append(todo_list)
                return list_r
            elif todo_list not in list_r:
                list_r.append(todo_list)
                for x in range(len(todo_list)):
                    chance(todo_list[:x] + todo_list[x + 1:])

        chance(todo_list)
        return self.filter_group(list_r)

    def statistics(self, nodes, st_type):
        _statistics = []
        type_list = list(set([record.get(st_type) for record in nodes]))

        def num_ids(type):
            num = 0
            ids = []
            for i in nodes:
                if i.get(st_type) == type:
                    num += 1
                    ids.append(i.get("id"))
            return num, ids

        def each_st():
            for _type in type_list:
                each = {}
                each["type"] = _type
                each["num"] = num_ids(_type)[0]
                each["ids"] = num_ids(_type)[1]
                _statistics.append(each)

        each_st()
        return _statistics

    def links_nodes_filter(self, links_nodes):
        id_list = []
        links_nodes_list = []
        for _each in links_nodes:
            if _each["id"] not in id_list:
                id_list.append(_each["id"])
                links_nodes_list.append(_each)
        return links_nodes_list

    def links_filter(self, links_nodes):
        _list = []
        links_nodes_list = []
        links_nodes_end = []
        for _each in links_nodes:
            if _each["from"] + _each["to"] not in _list:
                _list.append(_each["from"] + _each["to"])
                links_nodes_list.append(_each)
        for _each in links_nodes_list:
            if [x["from"] for x in links_nodes_list].count(_each["from"]) > 1:
                links_nodes_end.append(_each)
        return links_nodes_end

    def links_to_end(self, nodes, links_end):
        links_end_nodes = []
        nodes_end = []
        for link in links_end:
            links_end_nodes.append(link["from"])
            links_end_nodes.append(link["to"])
        for node in nodes:
            if node["id"] in links_end_nodes:
                nodes_end.append(node)
        return nodes_end

    def recursion_combination_links(self, combination_links_end, start_node, end_node, typeLabels,
                                    combination_links_node_check):
        traverse_start = []
        traverse_body = []
        traverse_end = []
        traverse_all = []
        for each_link in combination_links_end:
            if each_link[0] in start_node:
                traverse_start.append(each_link)
            else:
                traverse_body.append(each_link)
        traverse_body.append("NO")

        def check_node(node):
            return combination_links_node_check.get("to_meta_type")[combination_links_node_check.get("to").index(node)]

        def recursion_combination(start, body):
            if not traverse_end:
                traverse_end.append(start)
            if body == "NO":
                global exit_label
                exit_label = 1
            else:
                len_tra = len(traverse_end)
                if body[0] == traverse_end[len_tra - 1][-1]:
                    traverse_end.append(body)
                    global label
                    label = 1

        for _start in traverse_start:
            global exit_label
            exit_label = 0
            traverse_end.clear()
            while 1:
                if exit_label == 1:
                    if traverse_end[-1][-1] not in end_node:
                        traverse_end.clear()
                    if len(traverse_end) == 2 and check_node(traverse_end[0][1]) not in typeLabels:
                        traverse_end.clear()
                    break
                global label
                label = 0
                for _body in traverse_body:
                    if not label:
                        recursion_combination(_start, _body)
                    else:
                        break
            traverse_all.extend(traverse_end)
        return traverse_all

    def filling_time_count(self, times: list) -> dict:
        '''
        Add the missing time period to the timeline
        '''
        filling_time = {
            "code": 0,
            "data": {
                "time": []
            }
        }

        def middle_time(time: list) -> list:
            middle = [time[0], time[1], time[2] + 1]
            _month1 = [1, 3, 5, 7, 8, 10]
            _month2 = [4, 6, 9, 11]
            if middle[-1] == 31 and middle[-2] in _month2:
                middle_end = [middle[0], middle[1] + 1, 1]
            elif middle[-1] == 32 and middle[-2] in _month1:
                middle_end = [middle[0], middle[1] + 1, 1]
            elif middle[-1] == 32 and middle[-2] == 12:
                middle_end = [middle[0] + 1, 1, 1]
            elif middle[-1] == 30 and middle[-2] == 2 and middle[0] % 4 == 0 and middle[0] % 100 != 0:
                middle_end = [middle[0], middle[1] + 1, 1]
            elif middle[-1] == 29 and middle[-2] == 2 and middle[0] % 4 == 0 and middle[0] % 100 == 0:
                middle_end = [middle[0], middle[1] + 1, 1]
            elif middle[-1] == 29 and middle[-2] == 2 and middle[0] % 4 != 0:
                middle_end = [middle[0], middle[1] + 1, 1]

            else:
                middle_end = middle.copy()
            return middle_end

        for x in range(len(times)):
            # Add by string
            if x != len(times) - 1:
                start = times[x].split("-")
                end = times[x + 1].split("-")
                if not filling_time["data"]["time"]:
                    filling_time["data"]["time"].append([int(i) for i in start])
                    # filling_time["data"]["count"].append(counts[x])
                if int("".join(end)) - int("".join(start)) >= 1:
                    while 1:
                        if filling_time["data"]["time"][-1] == [int(i) for i in end]:
                            filling_time["data"]["time"].pop()
                            # filling_time["data"]["count"].pop()
                            filling_time["data"]["time"].append([int(i) for i in end])
                            # filling_time["data"]["count"].append(counts[x + 1])
                            break
                        else:
                            filling_time["data"]["time"].append(middle_time(filling_time["data"]["time"][-1]))
                            # filling_time["data"]["count"].append("null")
            else:
                filling_time["data"]["time"].append([int(x) for x in times[-1].split("-")])
                # filling_time["data"]["count"].append(counts[-1])

        time_end = []
        time_end2 = []
        for x in filling_time["data"]["time"]:
            time_end.append([str(y) for y in x])

        for i in time_end:
            k = []
            for j in i:
                if len(j) == 1:
                    k.append("0" + j)
                else:
                    k.append(j)

            time_end2.append("-".join(k))

        filling_time["data"]["time"] = time_end2
        if len(filling_time["data"]["time"]) > 1 and filling_time["data"]["time"][-1] == filling_time["data"]["time"][-2]:
            filling_time["data"]["time"].pop()
            # filling_time["data"]["count"].pop()
        return filling_time

    # def ssh_conn(self, list_file_content=[], add=True, vertex=True):
    #     '''基于SSH用于连接远程服务器并执行相关操作。'''
    #
    #     # 创建ssh对象
    #     ssh = paramiko.SSHClient()
    #
    #     # 允许连接不在know_hosts文件中的主机
    #     ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #
    #     # 连接服务器
    #     ssh.connect(hostname='10.60.1.142', port=22, username='sqlgraph', password='sqlgraph')
    #
    #     if add:
    #         # echo后边用单引号包围要添加的内容
    #         for _record in list_file_content:
    #             try:
    #                 if vertex:
    #                     ssh.exec_command("echo '%s'>>/home/sqlgraph/ssd/community.csv" % _record)
    #                 else:
    #                     print('55555555555555555555')
    #                     s = _record[0] + ',' + _record[1]
    #                     print(s)
    #                     ssh.exec_command("echo '%s'>>/home/sqlgraph/ssd/community.csv" % s)
    #             except Exception as error:
    #                 print('------------error-------------')
    #                 print(error)
    #     else:
    #         ssh.exec_command("rm -rf /home/sqlgraph/ssd/community.csv")
    #         ssh.exec_command("touch /home/sqlgraph/ssd/community.csv")
    #
    #     ssh.close()
