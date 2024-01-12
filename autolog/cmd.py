import datetime
import socket
import multiprocessing

import select


class CMDManage:
    server_socket: socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 创建TCP socket
    inputs: list = []
    outputs: list = []
    exceptional: list = []
    last_activity = {}
    timeout_ms: int = 1000

    def __init__(self):
        self.server_socket.setblocking(False)  # 设置为非阻塞模式

    def recive_server(self):
        try:
            server_address = ('localhost', 8080)
            self.server_socket.bind(server_address)  # 绑定到指定的IP地址和端口号
            self.server_socket.listen(5)  # 开始监听连接
            print("Server is listening on {}:{}...".format(*server_address))

            while True:
                readable, writable, exceptional = select.select([self.server_socket], self.outputs, self.exceptional)

                for sock in readable:
                    if sock == self.server_socket:
                        client_sock, address = self.server_socket.accept()
                        print("New connection from {}".format(address))
                        self.inputs.append(client_sock)
                    else:
                        # 使用 datetime.datetime.now().microsecond 获取微秒级别的时间戳，并转为毫秒级别
                        current_timestamp = int(datetime.datetime.now().microsecond / 1000)
                        last_active_time = self.last_activity.get(sock, None)
                        if last_active_time and current_timestamp - last_active_time > self.timeout_ms:
                            print("Client timed out! Closing connection...")
                            self.inputs.remove(sock)
                            sock.close()
                        else:
                            data = sock.recv(1024).decode()
                            if not data:
                                print("Connection closed by the client")
                                self.inputs.remove(sock)
                                sock.close()
                            else:
                                print("Received message:", data)
                                self.last_activity[sock] = current_timestamp

        except KeyboardInterrupt:
            print("无法建立通信服务{}:{}...".format(*server_address))
            pass

    def close_all_client(self):
        for sock in self.inputs:
            sock.close()
        self.inputs.clear()

    def get_client_number(self):
        return len(self.inputs)
