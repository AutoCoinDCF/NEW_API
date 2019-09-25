import time


class Mon_tool:
    def _2_group(self, idlist: list):
        res = []
        for f_id in idlist:
            for t_id in idlist[idlist.index(f_id) + 1:]:
                res.append([f_id, t_id])
        return res

    def get_timestamp(self, timeStamp):
        # 根据时间戳获取当天的时间戳
        timeStamp = timeStamp
        timeArray = time.localtime(timeStamp)
        otherStyleTime = time.strftime("%Y-%m-%d", timeArray)
        timeArray = time.strptime(otherStyleTime, "%Y-%m-%d")
        timeStamp = int(time.mktime(timeArray))
        return (timeStamp, timeStamp + 86399)
