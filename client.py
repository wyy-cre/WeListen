import os
import sys
import socket
import threading
from player import Player


def deal_command(p, command, socket_client, flag):
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
            socket_client.send(command.encode("utf-8"))
        info = f"{p.song_name} 已暂停\n"
    elif command == "start":
        if p.song_name == "":
            info = "请先输入要播放的歌曲"
            return info
        p.mixer.music.unpause()
        if flag:
            socket_client.send(command.encode("utf-8"))
        info = f"正在播放: {p.song_name}\n"
    elif command in os.listdir(p.root):
        if flag:
            socket_client.send(command.encode("utf-8"))
        p.song_name = command
        p.mixer.music.load(os.path.join(p.root, p.song_name))
        p.mixer.music.play()
        info = f"正在播放: {p.song_name}\n"
    else:
        if "无法识别命令" in info:
            info = info.partition(' | ')[-1]
        info = "无法识别命令: " + command + " | " + info


def receive(socket_client, p):
    while True:
        print("\033[39m" + info)
        print("\n> ", end="")
        try:
            command = socket_client.recv(1024).decode("utf-8")
        except ConnectionAbortedError as e:
            return
        if command == 'exit':
            print("对方已断开连接，请输入 exit 结束程序")
            socket_client.close()
            return
        deal_command(p, command, socket_client, False)


def input_command(socket_client, p):
    # 打印操作信息
    os.system("chcp 65001")
    print("连接成功\n\033[36m命令：\n1. 输入音乐名字播放\n2. start: 开始\n3. stop: 暂停\n4. exit: 退出")
    # 等待用户输入命令
    while True:
        print("\033[39m" + info)
        command = input("> ")
        if command == 'exit':
            try:
                socket_client.send(command.encode("utf-8"))
            except OSError as e:
                pass
            socket_client.close()
            return
        deal_command(p, command, socket_client, True)


def link():
    add_server = input("请输入服务器地址: ")
    port = int(input("请输入端口号: "))
    socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_client.connect((add_server, port))
    return socket_client


def main():
    # 连接
    socket_client = link()
    # 创建播放器对象
    p = Player()
    # 输入命令的线程
    t_input = threading.Thread(target=input_command, args=(socket_client, p))
    t_input.start()
    # 接收命令的线程
    t_recv = threading.Thread(target=receive, args=(socket_client, p))
    t_recv.start()


if __name__ == "__main__":
    info = ""  # 用于显示信息的全局变量
    main()
