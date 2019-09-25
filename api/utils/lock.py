import os
import time


class LOCK():
    def __init__(self):
        self.file = "./api/utils/lock.txt"

    def monitor(self):
        if os.path.exists(self.file):
            while True:
                time.sleep(5)
                if not os.path.exists(self.file):
                    os.popen('touch {}'.format(self.file)).readlines()
                    print("终于排队排到我了~")
                    break
        else:
            # 文件不存在，创建文件，并执行任务。
            os.popen('touch ./api/utils/lock.txt').readlines()
            print("我抢到了！！！ 文件锁 任务模拟sleep 20s")

    def remove_lock(self):
        print("删了删了~")
        os.remove(self.file)
