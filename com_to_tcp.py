# -*- coding: utf-8 -*-
import time
import socket
import binascii
import threading
from cushy_serial import CushySerial


ip = ''
port = 0
com = ''
baud = 0
parity = ''
DEBUG = False


def ListStringToHex(data_):
    HexStr = str(binascii.b2a_hex(bytearray(data_)))
    return HexStr[2:-1]


def creation_socket(ip_, port_):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server = (ip_, port_)
    try:
        s.connect(server)
        return s
    except socket.error:
        print("连接出错.")
        return False


def socket_recv(s):
    global ser
    while True:
        try:
            data = s.recv(1024)
            if len(data) > 0:
                try:
                    data = ListStringToHex(data)
                    ser.send(bytes.fromhex(data.replace(" ", "")))
                    if DEBUG:
                        print('串口发送:', data)
                except Exception as e:
                    print("err-socket_recv-2:", e)
                    print('串口数据发送失败.')
        except Exception as e:
            print("err-socket_recv-1:", e)
            time.sleep(0.5)


def creation_thread_TCP_recv(recv, s):
    recv_t = threading.Thread(target=recv, args=(s,))
    recv_t.setDaemon(True)
    recv_t.start()


def openSerial(c, b, p):
    global sock
    try:
        ser_ = CushySerial(c, b, 8, p, 1)
        print('打开串口.')

        @ser_.on_message()
        def handle_serial_message(msg: bytes):
            sock.send(msg)
            if DEBUG:
                print('TCP发送:', ListStringToHex(msg))

        return ser_
    except Exception as e:
        print("err-openSerial:", e)
        print("操作串口失败.")
        return


def CMD_Input():
    global ip, port, com, baud, parity, DEBUG
    while True:
        try:
            ip = str(input("请输入TCP地址，例如192.168.8.88或www.baidu.com:"))
            port = int(input("请输入TCP端口号:"))
            com = str(input("请输入要打开的COM口，例如COM8:")).upper()
            baud = int(input("请输入COM口波特率，例如115200:"))
            parity = str(input("请输入校验位，例如偶校验-E、奇校验-O、无校验-N:")).upper()
            temp = str(input("是否显示报文，1-显示，其他值-不显示:"))
            if temp == '1':
                DEBUG = True
            else:
                DEBUG = False
            break
        except Exception as e:
            print("输入有误.", e)


if __name__ == "__main__":
    CMD_Input()
    sock = creation_socket(ip, port)
    creation_thread_TCP_recv(socket_recv, sock)
    ser = openSerial(com, baud, parity)
