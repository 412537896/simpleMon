#!/usr/bin/python
#-*- coding:utf-8 -*-
 
import socket, select, logging, errno
import os, sys, json

def cmdRunner(input):
    import commands
    cmd_ret = commands.getstatusoutput(input)
    return json.dumps({'ret':cmd_ret[0], 'out':cmd_ret[1]}, separators=(',', ':'))

class _State:
    def __init__(self):
        self.state = "read"
        self.have_read = 0
        self.need_read = 10
        self.have_write = 0
        self.need_write = 0
        self.data = ""

__all__ = ['nbNet','sendData']

class nbNet:

    def __init__(self, host, port, logic):
        self.host = host
        self.port = port
        self.logic = logic
        self.sm = {
            "read":self.aread,
            "write":self.awrite,
            "process":self.aprocess,
            "closing":self.aclose,
        }

    def run(self):

        try:
            self.listen_fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        except socket.error, msg:
            print("create socket failed")

        try:
            self.listen_fd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except socket.error, msg:
            print("setsocketopt SO_REUSEADDR failed")
     
        try:
            self.listen_fd.bind((self.host, self.port))
        except socket.error, msg:
            print("bind failed")

        try:
            self.listen_fd.listen(10)
        except socket.error, msg:
            print(msg)

        try:
            self.epoll_fd = select.epoll()
            # 向 epoll 句柄中注册 新来socket链接，监听可读事件
            self.epoll_fd.register(self.listen_fd.fileno(), select.EPOLLET | select.EPOLLIN )
        except select.error, msg:
            print(msg)

        self.STATE = {}

        while True:
            print self.STATE
            # epoll 进行 fd 扫描的地方 -- 未指定超时时间[毫秒]则为阻塞等待
            epoll_list = self.epoll_fd.poll()
            for fd, events in epoll_list:
                if select.EPOLLHUP & events:
                    print 'EPOLLHUP'
                    self.STATE[fd][2].state = "closing"
                elif select.EPOLLERR & events:
                    print 'EPOLLERR'
                    self.STATE[fd][2].state = "closing"
                self.state_machine(fd)
    def state_machine(self, fd):
        if fd == self.listen_fd.fileno():
            print "state_machine fd %s accept" % fd
            # fd与初始监听的fd一致,新创建一个连接
            conn, addr = self.listen_fd.accept()
            # 设置为非阻塞
            conn.setblocking(0)
            self.STATE[conn.fileno()] = [conn, addr, _State()]
            # 将新的链接注册在epoll句柄中，监听可读事件
            self.epoll_fd.register(conn.fileno(), select.EPOLLET | select.EPOLLIN )
        else:
            # 否则为历史已存在的fd，调用对应的状态方法
            print "state_machine fd %s %s" % (fd,self.STATE[fd][2].state) 
            stat = self.STATE[fd][2].state
            self.sm[stat](fd)
    def aread(self, fd):
        try:
            # 接收当前fd的可读事件中的数据
            one_read = self.STATE[fd][0].recv(self.STATE[fd][2].need_read)
            if len(one_read) == 0:
                # 接收错误改变状态为关闭
                self.STATE[fd][2].state = "closing"
                self.state_machine(fd)
                return
            # 将历史接收的数据叠加
            self.STATE[fd][2].data += one_read
            self.STATE[fd][2].have_read += len(one_read)
            self.STATE[fd][2].need_read -= len(one_read)
            # 接收协议的10个字符
            if self.STATE[fd][2].have_read == 10:
                # 通过10个字符得知下次应该具体接收多少字节,存入状态字典中
                self.STATE[fd][2].need_read += int(self.STATE[fd][2].data)
                self.STATE[fd][2].data = ''
                # 调用状态机重新处理
                self.state_machine(fd)
            elif self.STATE[fd][2].need_read == 0:
                # 当接全部收完毕,改变状态,去执行具体服务
                self.STATE[fd][2].state = 'process'
                self.state_machine(fd)
        except socket.error, msg:
            self.STATE[fd][2].state = "closing"
            print(msg)
            self.state_machine(fd)
            return

    def aprocess(self, fd):
        # 执行具体执行方法 cmdRunner 得到符合传输协议的返回结果
        response = self.logic(self.STATE[fd][2].data)
        self.STATE[fd][2].data = "%010d%s"%(len(response), response)
        self.STATE[fd][2].need_write = len(self.STATE[fd][2].data)
        # 改变为写的状态
        self.STATE[fd][2].state = 'write'
        # 改变监听事件为写
        self.epoll_fd.modify(fd, select.EPOLLET | select.EPOLLOUT)
        self.state_machine(fd)

    def awrite(self, fd):
        try:
            last_have_send = self.STATE[fd][2].have_write
            # 发送返回给客户端的数据
            have_send = self.STATE[fd][0].send(self.STATE[fd][2].data[last_have_send:])
            self.STATE[fd][2].have_write += have_send
            self.STATE[fd][2].need_write -= have_send
            if self.STATE[fd][2].need_write == 0 and self.STATE[fd][2].have_write != 0:
                # 发送完成,重新初始化状态,并将监听写事件改回读事件
                self.STATE[fd][2] = _State()
                self.epoll_fd.modify(fd, select.EPOLLET | select.EPOLLIN)
        except socket.error, msg:
            self.STATE[fd][2].state = "closing"
            self.state_machine(fd)
            print(msg)
            return

    def aclose(self, fd):
        try:
            print 'Error: %s:%d' %(self.STATE[fd][1][0] ,self.STATE[fd][1][1])
            # 取消fd的事件监听
            self.epoll_fd.unregister(fd)
            # 关闭异常链接
            self.STATE[fd][0].close()
            # 删除fd的状态信息
            self.STATE.pop(fd)
        except:
            print 'Close the abnormal'

def sendData(sock_l, host, port, data):
    retry = 0
    while retry < 3:
        try:
            if sock_l[0] == None:
                sock_l[0] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock_l[0].connect((host, port))
                print "connecting"
            d = data
            sock_l[0].sendall("%010d%s"%(len(d), d))
            print "%010d%s"%(len(d), d)
            count = sock_l[0].recv(10)
            if not count:
                raise Exception("recv error", "recv error")
            count = int(count)
            buf = sock_l[0].recv(count)
            print buf
            if buf[:2] == "OK":
                retry = 0
                break
        except:
            sock_l[0].close()
            sock_l[0] = None
            retry += 1

if __name__ == "__main__":
    HOST = '0.0.0.0'
    PORT = 50005
    nb = nbNet(HOST, PORT, cmdRunner)
    nb.run()

