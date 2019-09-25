from pprint import pprint

import paramiko


class SSH():
    def __init__(self, ip, username, password):
        self.ip = ip
        self.username = username
        self.password = password

    def ssh2(self, cmd):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self.ip, 22, self.username, self.password, timeout=5)
            for m in cmd:
                stdin, stdout, stderr = ssh.exec_command(m)
                stdin.write("Y")
                out = stdout.readlines()
                # 以下两行注释用来执行所有命令和脚本的输出，本程序不用所以注释
                # for o in out:
                #     print(o)
            print("-------远程操作文件报错信息------")
            pprint(stderr.readlines())
            print('%s\t服务器登录执行命令成功\n' % (self.ip))
            # time.sleep(20)
            ssh.close()
        except:
            print('%s\t服务器登录异常，请检查\n' % (self.ip))
        return out


if __name__ == '__main__':
    # cmd = ['rm -rf ...']
    cmd = [
        '''
        clickhouse client --multiquery --query="
        use EEDGraphSingular_v16;
        show tables;
        "
        '''
    ]
    ip = '10.60.1.142'
    username = 'sqlgraph'
    password = 'sqlgraph'
    s = SSH(ip, username, password)
    print("Begin....")
    try:
        ssh_list_95 = s.ssh2(cmd)
        print('----------ssh_list_95-----------')
        print(ssh_list_95)
    except:
        print("-----------------raise----------------")
        raise
    # cp: 直接读取远程文件命令cat，如：f = self.ssh_140.ssh2(['cat /root/upload_task/{}.json'.format(_id)])
