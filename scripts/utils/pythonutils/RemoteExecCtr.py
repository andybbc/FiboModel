import sys
import paramiko

# web服务器
host = "172.16.209.173"
port = 22
username = 'apps'
password = 'apps'


def ssh(cmd_str):
    sshClient = paramiko.SSHClient()
    sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # 指定当对方主机没有本机公钥的情况时应该怎么办，AutoAddPolicy表示自动在对方主机保存下本机的秘钥
    sshClient.connect(host, port, username, password)  # SSH端口默认22，可改
    stdin, stdout, stderr = sshClient.exec_command(cmd_str)  # 这三个得到的都是类文件对象
    outmsg, errmsg = stdout.read(), stderr.read()  # 读一次之后，stdout和stderr里就没有内容了，所以一定要用变量把它们带的信息给保存下来，否则read一次之后就没有了
    # outmsg = str(outmsg)
    # print(outmsg.replace("\\n","\\r\\n"))
    print(outmsg.decode())
    if errmsg != b'':
        print("--错误输出--")
        print(errmsg.decode())
    # 判断返回值
    channel = stdout.channel
    status = channel.recv_exit_status()
    print(type(status))
    print(status)
    if status != 0:
        print("远程命令执行报错")
        exit(99)


def scp_put(local_file, remote_file):
    sshClient = paramiko.SSHClient()
    sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    sshClient.connect(host, port, username, password)
    stdin, stdout, stderr = sshClient.exec_command('date')
    outmsg, errmsg = stdout.read(), stderr.read()
    print(outmsg.decode())
    if errmsg != b'':
        print(errmsg.decode())
        print("远程命令报错")
        exit(99)

    sftp = paramiko.SFTPClient.from_transport(sshClient.get_transport())
    sftp = sshClient.open_sftp()
    sftp.put(local_file, remote_file)
    sshClient.close()


def scp_get(remote_file, local_file):
    sshClient = paramiko.SSHClient()
    sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    sshClient.connect(host, port, username, password)
    stdin, stdout, stderr = sshClient.exec_command('date')
    outmsg, errmsg = stdout.read(), stderr.read()
    print(outmsg.decode())
    if errmsg != b'':
        print(errmsg.decode())
        print("远程命令报错")
        exit(99)

    sftp = paramiko.SFTPClient.from_transport(sshClient.get_transport())
    sftp = sshClient.open_sftp()
    sftp.get(remote_file, local_file)
    sshClient.close()

if __name__ == '__main__':
    # sys.argv = ['', 'ssh','ls', '-ls']
    exec_type = sys.argv[1]

    ####
    # exec_type = 'ssh'
    # sys.argv = ['ssh', '','ls', '-ls']
    ####
    # exec_type = 'scp_put'
    # sys.argv = ['ssh', '', 'RemoteExecCtr.py', '/home/apps/test/a/aa.txt']
    ####
    # exec_type = 'scp_get'
    # sys.argv = ['ssh', '', '/home/apps/test/a/aa.txt', 'a.txt']

    if exec_type == "ssh":
        cmd_str = " ".join(sys.argv[2:])
        ssh(cmd_str)
    elif exec_type == "scp_put":
        local_file = sys.argv[2]
        remote_file = sys.argv[3]
        scp_put(local_file, remote_file)
    elif exec_type == "scp_get":
        remote_file = sys.argv[2]
        local_file = sys.argv[3]
        scp_get(remote_file, local_file)

