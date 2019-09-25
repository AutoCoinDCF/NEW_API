import pexpect


class Transfer(object):
    def __init__(self, ip, user, passwd,):
        self.ip = ip
        self.user = user
        self.passwd = passwd

    def file_transfer(self, dst_path, filename, to_local=False):
        print("远程传输开始...")
        passwd_key = '.*assword.*'
        if not to_local:
            cmdline = 'scp %s %s@%s:%s' % (filename, self.user, self.ip, dst_path)
        else:
            cmdline = 'scp %s@%s:%s %s' % (self.user, self.ip, filename, dst_path)
        try:
            child = pexpect.spawn(cmdline)
            child.sendline('yes')
            #child.expect_exact(passwd_key, timeout=None)
            child.expect(passwd_key, timeout=None)
            child.sendline(self.passwd)
            child.expect(pexpect.EOF, timeout=None)
            print("Transfer Work Finish!")
        except:
            raise


if __name__ == "__main__":
    triger = Transfer('10.60.1.142', 'sqlgraph', 'sqlgraph')
    # triger.file_transfer('/home/sqlgraph/ssd/search_script', '/home/ssd/git_lab_102/v_0610/QBInterface/set_relation.csv')
    triger.file_transfer('/home/ssd/git_lab_102/v_0610/QBInterface', '/home/sqlgraph/ssd/search_script/create_eed_graph2_v2.sh', True)
