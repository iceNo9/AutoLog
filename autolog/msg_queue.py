import json
import queue

msgQueue = queue.Queue(maxsize=32)


# 定义发送消息的函数
def send_message(rv_sender_info, rv_receiver_info, rv_head, rv_content=[0]):
    message = {
        "sender": rv_sender_info,
        "receiver": rv_receiver_info,
        "head": rv_head,
        "content": rv_content
    }
    try:
        msgQueue.put(json.dumps(message))  # 将消息转换为JSON格式并添加到队列中
        # print(f"Message {message} put into queue successfully.")
    except Exception as e:  # 如果发生异常，捕获并打印异常信息
        print(f"Error putting message into queue: {e}")
    print(f"Message added to queue by {rv_sender_info}: {json.dumps(message)}")
