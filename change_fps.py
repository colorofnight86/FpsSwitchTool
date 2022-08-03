# -*- coding: utf-8 -*-
# @Time    : 2022/7/20 14:45
# @Author  : ColorOfNight
# @Email   : 852477089@qq.com
# @File    : change_fps.py
# @Software: PyCharm

from threading import Thread
from pynput import keyboard
import os
import sys
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QAction, QSystemTrayIcon, qApp
import win10toast
import images

f60 = keyboard.Key.f10
f144 = keyboard.Key.f11

toaster = win10toast.ToastNotifier()


class mainWindow(QMainWindow):
    def __init__(self):
        super(mainWindow, self).__init__()
        self.setWindowIcon(QIcon(":/icon.ico"))


def quit():
    qApp.quit()


class TrayIcon(QSystemTrayIcon):
    def __init__(self, MainWindow, parent=None):
        super(TrayIcon, self).__init__(parent)
        self.fps = None
        self.listen_thread = None
        self.listen = False
        self.ui = MainWindow
        self.createMenu()
        self.init_icon()

    def createMenu(self):
        # 设置图标
        self.setIcon(QIcon(":/144.png"))
        self.icon = self.MessageIcon()

        self.menu = QMenu()
        self.showAction = QAction("显示刷新率", self, triggered=self.show_fps)
        # self.listenAction = QAction("启用快捷键", self, triggered=self.listen_key)
        self.quitAction = QAction("退出", self, triggered=quit)

        self.menu.addAction(self.showAction)
        # self.menu.addAction(self.listenAction)
        self.menu.addAction(self.quitAction)
        self.setContextMenu(self.menu)

        # 把鼠标点击图标的信号和槽连接
        self.activated.connect(self.onIconClicked)

    def init_icon(self):
        r = os.popen('setres m0:0')
        self.fps = int(r.readline().split(' ')[-2][1:])
        if self.fps == 60:
            self.setIcon(QIcon(":/60.png"))
        else:
            self.setIcon(QIcon(":/144.png"))

    def listen_key(self):
        if self.listen_thread is None:
            self.listen_thread = Thread(target=press_thread, daemon=self.ui)
        self.listen = not self.listen
        if self.listen:
            print("开始监听")
            self.listenAction.setIcon(QIcon("image/yes.png"))
            self.listen_thread.start()
        else:
            print("停止监听")
            self.listenAction.setIcon(QIcon())
            # self.listen_thread.join()

        # listen_thread = Thread(target=press_thread)

    def show_fps(self):
        self.showMessage("当前刷新率为" + str(self.fps), "点击退出", self.icon, msecs=1000)

    def showMsg(self, title, message):
        self.showMessage(title, message, self.icon, msecs=100)

    def show_window(self):
        # 若是最小化，则先正常显示窗口，再变为活动窗口（暂时显示在最前面）
        self.ui.showNormal()
        self.ui.activateWindow()

    # 鼠标点击icon传递的信号会带有一个整形的值，1是表示右键单击，2是双击，3是单击左键，4是用鼠标中键点击
    def onIconClicked(self, reason):
        if reason == 4:
            if self.ui.isMinimized() or not self.ui.isVisible():
                # 若是最小化，则先正常显示窗口，再变为活动窗口（暂时显示在最前面）
                self.ui.showNormal()
                self.ui.activateWindow()
                self.ui.setWindowFlags(Qt.Window)
                self.ui.show()
            else:
                # 若不是最小化，则最小化
                self.ui.showMinimized()
                self.ui.setWindowFlags(Qt.SplashScreen)
                self.ui.show()
        if reason == 2:
            self.change_fps()

    def change_fps(self):
        if self.fps == 60:
            r = os.popen('setres f144 n')
        else:
            r = os.popen('setres f60 n')
        result = r.readlines()
        target_fps = int(result[1].split(' ')[-1].split('\n')[0][1:])
        success = result[-1][0:1] != 'E'
        r.close()
        self.showMsg("刷新率切换至" + str(target_fps), "成功" if success else "失败")
        if success:
            self.setIcon(QIcon(":/" + str(target_fps) + ".png"))
            self.fps = target_fps


def press(key):
    if key == f60:
        r = os.popen('setres f60 n')
        r.close()
        send("刷新率切换", "切换至60fps")
    if key == f144:
        r = os.popen('setres f144 n')
        r.close()
        send("刷新率切换", "切换至144fps")
    # if key==keyboard.KeyCode(char='z'):
    #     print('yes')
    print(str(key))


def send(title, message):
    toaster.show_toast(title, message, "icon.ico", 2)


# 定义键盘监听线程
def press_thread():
    with keyboard.Listener(on_press=press) as lsn:
        lsn.join()
        print("listen")


# thread1 = Thread(target=press_thread())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = mainWindow()
    main_window.showMinimized()
    main_window.setWindowFlags(Qt.SplashScreen)
    tray = TrayIcon(main_window)
    tray.show()
    sys.exit(app.exec_())
