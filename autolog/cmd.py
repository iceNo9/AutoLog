import concurrent.futures
import datetime
import json
import queue
import socket
import threading
import time

import select

import msg_queue
from common import Protocol


class Cmd:
    server_socket: socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 创建TCP socket
    inputs: list = []
    outputs: list = []
    exceptional: list = []
    last_activity = {}
    timeout_ms: int = 500
    last_inputs_len: int = 0

    def __init__(self, rv_queue: queue.Queue):
        # self.server_socket.setblocking(False)  # 设置为非阻塞模式
        self._queue = rv_queue

    def receive_message(self):
        while True:
            message = self._queue.get()  # 从队列中获取消息
            try:
                parsed_message = json.loads(message)  # 将JSON格式的消息解析为Python字典
                # print(f"Processing message: {parsed_message}")
                if parsed_message["receiver"] == "cmd":  # 检查接收方的信息是否匹配
                    # 如果匹配，处理消息或执行其他操作
                    if parsed_message["head"] == Protocol.CMD_CLOSE_ALL_CLIENT.value:
                        close_message = 'close'
                        for sock in self.inputs:
                            sock.sendall(close_message.encode())
                    else:
                        print("cmd Message received by matching receiver,but illgal{}".format(parsed_message["receiver"]))

                    self._queue.task_done()
                    # print("cmd Message received by matching receiver")
                else:
                    # 如果不匹配，将消息重新入列
                    self._queue.put(message)
                    # print("Message requeued due to mismatching receiver")
            except json.JSONDecodeError:
                print("Error parsing JSON message")
                self._queue.put(message)  # 如果解析失败，将消息重新入列

    def _handle_client(self, client_socket):
        while True:
            current_timestamp = int(datetime.datetime.now().microsecond / 1000)
            last_active_time = self.last_activity.get(client_socket, None)
            if last_active_time and current_timestamp - last_active_time > self.timeout_ms:
                print("Client timed out! Closing connection...")
                self.inputs.remove(client_socket)
                client_socket.close()
                break
            else:
                request = client_socket.recv(1024)  # 读取客户端请求
                print(f"Received request from {client_socket.getpeername()}: {request.decode()}")
                if not request:
                    print("Connection closed by the client")
                    self.inputs.remove(client_socket)
                    client_socket.close()
                    break
                else:
                    # print("Received message:", request)
                    self.last_activity[client_socket] = current_timestamp

            # response = "Hello, client!"  # 构建响应内容
            # client_socket.send(response.encode())  # 发送响应给客户端
            # client_socket.close()  # 关闭客户端套接字

    def recive_server(self):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            try:
                server_address = ('localhost', 8080)
                self.server_socket.bind(server_address)  # 绑定到指定的IP地址和端口号
                self.server_socket.listen(5)  # 开始监听连接
                # print("Server is listening on {}:{}...".format(*server_address))
                executor.submit(self.server_socket.listen)

                while True:
                    client_socket, client_address = self.server_socket.accept()  # 接受客户端连接请求
                    print("New connection from {}".format(client_address))
                    # 将客户端套接字传递给线程池中的一个线程进行处理
                    executor.submit(self._handle_client, client_socket)
                    self.inputs.append(client_socket)

            except KeyboardInterrupt:
                print("无法建立通信服务{}:{}...".format(*server_address))
                pass

    def send_message(self):
        cur_inputs_len = len(self.inputs)
        if self.last_inputs_len != cur_inputs_len and cur_inputs_len == 0:
            msg_queue.send_message(self._queue, "cmd", "fo", Protocol.CMD_NO_CONNECT.value)

        self.last_inputs_len = cur_inputs_len


def start(rv_queue):
    obj_cmd = Cmd(rv_queue)

    th_rv_msg = threading.Thread(target=obj_cmd.receive_message)
    th_server = threading.Thread(target=obj_cmd.recive_server)

    th_rv_msg.start()
    th_server.start()

    while True:
        obj_cmd.send_message()



