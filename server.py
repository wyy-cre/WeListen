import os
import socket
import threading
from player import Player


def get_host_ip():
    s = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


def deal_command(p, command, conn, flag):
    global info
    """
    :param flag: 如果是用户输入的命令，flag为True，需要向对方发送命令，如果是接收到对方的命令，flag为False，不需要再发送命令
    """
    if command == "stop":
        if p.song_name == "":
            info = "请先输入要播放的歌曲"
            return info
        p.mixer.music.pause()
        if flag:
            conn.send(command.encode("utf-8"))
        info = f"{p.song_name} 已暂停\n"
    elif command == "start":
        if p.song_name == "":
            info = "请先输入要播放的歌曲"
            return info
        p.mixer.music.unpause()
        if flag:
            conn.send(command.encode("utf-8"))
        info = f"正在播放: {p.song_name}\n"
    elif command in os.listdir(p.root):
        if flag:
            conn.send(command.encode("utf-8"))
        p.song_name = command
        p.mixer.music.load(os.path.join(p.root, p.song_name))
        p.mixer.music.play()
        info = f"正在播放: {p.song_name}\n"
    else:
        if "无法识别命令" in info:
            info = info.partition(' | ')[-1]
        info = "无法识别命令: " + command + " | " + info


def receive(socket_server, conn, p):
    while True:
        print("\033[39m" + info)
        print("\n> ", end="")
        try:
            command = conn.recv(1024).decode("utf-8")
        except ConnectionAbortedError as e:
            return
        if command == 'exit':
            print("对方已断开连接，请输入 exit 结束程序")
            conn.close()
            socket_server.close()
            return
        deal_command(p, command, conn, False)


def input_command(socket_server, conn, p):
    # 打印操作信息
    os.system("chcp 65001")
    print("连接成功\n\033[36m命令：\n1. 输入音乐名字播放\n2. start: 开始\n3. stop: 暂停\n4. exit: 退出")
    # 等待用户输入命令
    while True:
        print("\033[39m" + info)
        command = input("> ")
        if command == 'exit':
            try:
                conn.send(command.encode("utf-8"))
            except OSError as e:
                pass
            conn.close()
            socket_server.close()
            break
        deal_command(p, command, conn, True)


def link():
    ip = get_host_ip()
    port = 8888  # 默认使用8888作为端口号
    print(f"当前服务端内网IP: {ip}")
    print(f"使用默认端口号: {port}")
    socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_server.bind((ip, port))
    socket_server.listen(1)
    print("等待连接...")
    conn, addr = socket_server.accept()
    return socket_server, conn


def main():
    # 连接
    socket_server, conn = link()
    # 创建播放器对象
    p = Player()
    # 输入命令的线程
    t_input = threading.Thread(target=input_command, args=(socket_server, conn, p))
    t_input.start()
    # 接收命令的线程
    t_recv = threading.Thread(target=receive, args=(socket_server, conn, p))
    t_recv.start()


if __name__ == "__main__":
    info = ""  # 用于显示信息的全局变量
    main()
