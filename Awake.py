import sys
import time
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout,
                             QHBoxLayout, QWidget, QLabel, QMenuBar, QStatusBar,
                             QAction, QMessageBox, QSystemTrayIcon, QStyle)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont, QIcon
import pyautogui
import win32gui
import win32con

class AwakeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.always_on_top = True
        self.initUI()
        self.initTimer()

    def initUI(self):
        # 设置窗口
        self.setWindowTitle('Awake - 屏幕常亮工具')
        self.setFixedSize(500,250)
        self.setGeometry(300, 300, 500, 250)

        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 创建菜单栏
        self.createMenuBar()

        # 创建状态栏
        self.statusBar().showMessage('就绪')

        # 创建右侧状态标签
        self.right_status_label = QLabel('间隔：1分钟')
        self.right_status_label.setAlignment(Qt.AlignRight)
        self.right_status_label.setStyleSheet("color: gray;")
        self.statusBar().addPermanentWidget(self.right_status_label)

        # 窗口置顶状态
        if self.always_on_top:
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
            self.right_status_label.setText('窗口已置顶 | 间隔：1分钟')

        # 创建主布局
        layout = QVBoxLayout(central_widget)

        # 创建时间显示标签
        self.time_label = QLabel('点击开始保持您的屏幕常亮!', self)
        font = QFont("Microsoft YaHei Light", 16, QFont.Bold)
        self.time_label.setFont(font)
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setStyleSheet("padding: 20px;")
        layout.addWidget(self.time_label)

        # 创建按钮布局
        button_layout = QHBoxLayout()

        # 创建开始/重新开始按钮
        self.start_btn = QPushButton('开始', self)
        self.start_btn.setStyleSheet('font-size: 14px; padding: 8px;')
        self.start_btn.clicked.connect(self.startTimer)
        button_layout.addWidget(self.start_btn)

        # 创建暂停/继续按钮
        self.pause_btn = QPushButton('暂停', self)
        self.pause_btn.setStyleSheet('font-size: 14px; padding: 8px;')
        self.pause_btn.setEnabled(False)
        self.pause_btn.clicked.connect(self.pauseTimer)
        button_layout.addWidget(self.pause_btn)

        # 添加按钮布局到主布局
        layout.addLayout(button_layout)

        # 计时器状态变量
        self.is_running = False
        self.is_paused = False
        self.elapsed_seconds = 0


        # 设置窗口图标
        self.setWindowIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))

    def createMenuBar(self):
        # 创建菜单栏
        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu('文件')

        # 开始动作
        start_action = QAction('开始', self)
        start_action.setShortcut('Ctrl+S')
        start_action.setStatusTip('启动屏幕常亮功能')
        start_action.hovered.connect(lambda: self.statusBar().showMessage('启动屏幕常亮功能'))
        start_action.triggered.connect(self.startTimer)
        file_menu.addAction(start_action)

        # 暂停动作
        pause_action = QAction('暂停', self)
        pause_action.setShortcut('Ctrl+P')
        pause_action.setStatusTip('暂停屏幕常亮功能')
        pause_action.hovered.connect(lambda: self.statusBar().showMessage('暂停屏幕常亮功能'))
        pause_action.triggered.connect(self.pauseTimer)
        file_menu.addAction(pause_action)

        # 分隔线
        file_menu.addSeparator()

        # 退出动作
        exit_action = QAction('退出', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('退出应用程序')
        exit_action.hovered.connect(lambda: self.statusBar().showMessage('退出应用程序'))
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # 视图菜单
        view_menu = menubar.addMenu('视图')

        # 置顶动作
        self.always_on_top_action = QAction('窗口置顶', self)
        self.always_on_top_action.setCheckable(True)
        self.always_on_top_action.setChecked(self.always_on_top)
        self.always_on_top_action.setShortcut('Ctrl+T')
        self.always_on_top_action.setStatusTip('将窗口设置为始终在最前面')
        self.always_on_top_action.hovered.connect(lambda: self.statusBar().showMessage('将窗口设置为始终在最前面'))
        self.always_on_top_action.triggered.connect(self.toggleAlwaysOnTop)
        view_menu.addAction(self.always_on_top_action)

        # 设置菜单
        settings_menu = menubar.addMenu('设置')

        # 间隔时间设置
        interval_menu = settings_menu.addMenu('防休眠间隔')

        # 30秒间隔
        # interval_30s = QAction('30秒', self)
        # interval_30s.setStatusTip('设置防休眠间隔为30秒')
        # interval_30s.hovered.connect(lambda: self.statusBar().showMessage('设置防休眠间隔为30秒'))
        # interval_30s.triggered.connect(lambda: self.setInterval(30000))
        # interval_menu.addAction(interval_30s)

        # 1分钟间隔
        interval_1m = QAction('1分钟', self)
        interval_1m.setStatusTip('设置防休眠间隔为1分钟')
        interval_1m.hovered.connect(lambda: self.statusBar().showMessage('设置防休眠间隔为1分钟'))
        interval_1m.triggered.connect(lambda: self.setInterval(60000))
        interval_menu.addAction(interval_1m)

        # 2分钟间隔
        interval_2m = QAction('2分钟', self)
        interval_2m.setStatusTip('设置防休眠间隔为2分钟')
        interval_2m.hovered.connect(lambda: self.statusBar().showMessage('设置防休眠间隔为2分钟'))
        interval_2m.triggered.connect(lambda: self.setInterval(120000))
        interval_menu.addAction(interval_2m)

        # 5分钟间隔
        interval_5m = QAction('5分钟', self)
        interval_5m.setStatusTip('设置防休眠间隔为5分钟')
        interval_5m.hovered.connect(lambda: self.statusBar().showMessage('设置防休眠间隔为5分钟'))
        interval_5m.triggered.connect(lambda: self.setInterval(300000))
        interval_menu.addAction(interval_5m)

        # 帮助菜单
        help_menu = menubar.addMenu('帮助')

        # 关于动作
        about_action = QAction('关于', self)
        about_action.setStatusTip('显示程序信息')
        about_action.hovered.connect(lambda: self.statusBar().showMessage('显示程序信息'))
        about_action.triggered.connect(self.showAbout)
        help_menu.addAction(about_action)

        # 使用说明动作
        usage_action = QAction('使用说明', self)
        usage_action.setStatusTip('查看程序使用说明')
        usage_action.hovered.connect(lambda: self.statusBar().showMessage('查看程序使用说明'))
        usage_action.triggered.connect(self.showUsage)
        help_menu.addAction(usage_action)

    def initTimer(self):
        # 创建定时器
        self.timer = QTimer(self)
        self.timer.setInterval(1000)  # 1秒间隔
        self.timer.timeout.connect(self.updateTime)

        # 创建模拟点击定时器
        self.click_interval = 60000  # 默认60秒间隔
        self.click_timer = QTimer(self)
        self.click_timer.setInterval(self.click_interval)
        self.click_timer.timeout.connect(self.simulateClick)

    def setInterval(self, interval):
        # 设置防休眠间隔
        self.click_interval = interval
        self.click_timer.setInterval(interval)
        seconds = interval%60000//1000
        minutes = interval // 60000
        if self.always_on_top:
            self.right_status_label.setText(f'窗口已置顶 | 间隔已设置为: {minutes}分钟')
        else:
            self.right_status_label.setText(f'间隔已设置为: {minutes}分钟')
        if not seconds:
            self.statusBar().showMessage(f'防休眠间隔已设置为{minutes}分钟')
        else:
            self.statusBar().showMessage(f'防休眠间隔已设置为{minutes}分钟{seconds}秒')

    def startTimer(self):
        if not self.is_running:
            # 首次开始计时
            self.is_running = True
            self.is_paused = False
            self.elapsed_seconds = 0
            self.start_btn.setText('重新开始')
            self.pause_btn.setEnabled(True)
            self.timer.start()
            self.click_timer.start()
            self.updateDisplay()
            self.statusBar().showMessage('屏幕常亮已启动')
        else:
            # 重新开始计时
            self.is_paused = False
            self.elapsed_seconds = 0
            self.pause_btn.setText('暂停')
            self.updateDisplay()
            if not self.timer.isActive():
                self.timer.start()
                self.click_timer.start()
            self.statusBar().showMessage('屏幕常亮已重新开始')

    def pauseTimer(self):
        if self.is_running:
            if not self.is_paused:
                # 暂停计时
                self.is_paused = True
                self.timer.stop()
                self.click_timer.stop()
                self.pause_btn.setText('继续')
                self.statusBar().showMessage('屏幕常亮已暂停')
                self.time_label.setText('屏幕常亮已暂停')
                # self.toggleAlwaysOnTop()
            else:
                # 继续计时
                self.is_paused = False
                self.pause_btn.setText('暂停')
                self.timer.start()
                self.click_timer.start()
                self.updateDisplay()
                self.statusBar().showMessage('屏幕常亮已继续')
                # self.toggleAlwaysOnTop()

    def updateTime(self):
        # 更新已用时间（秒）
        self.elapsed_seconds += 1
        self.updateDisplay()

    def updateDisplay(self):
        # 将秒数转换为可读格式
        awake_days = self.elapsed_seconds // 86400
        awake_hours = (self.elapsed_seconds // 3600) % 24
        awake_minutes = (self.elapsed_seconds % 3600) // 60
        awake_seconds = self.elapsed_seconds % 60

        if awake_days:
            awake_time = f"{awake_days}天{awake_hours}小时{awake_minutes}分钟{awake_seconds}秒"
        elif awake_hours:
            awake_time = f"{awake_hours}小时{awake_minutes}分钟{awake_seconds}秒"
        elif awake_minutes:
            awake_time = f"{awake_minutes}分钟{awake_seconds}秒"
        else:
            awake_time = f"{awake_seconds}秒"

        time_str = f"您的屏幕已保持常亮 {awake_time}"
        self.time_label.setText(time_str)
    def toggleAlwaysOnTop(self):
            # 切换窗口置顶状态
            self.always_on_top = not self.always_on_top

            # 保存当前窗口位置和大小
            geometry = self.geometry()

            if self.always_on_top:
                # 设置窗口置顶
                self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
                self.statusBar().showMessage('窗口已置顶')
                status_value = self.right_status_label.text().split("|")[-1]
                self.right_status_label.setText(f'窗口已置顶 | {status_value}')
            else:
                # 取消窗口置顶
                self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
                self.right_status_label.setText(f'窗口已取消置顶 | {self.right_status_label.text().split("|")[-1]}')

            # 重新显示窗口以使设置生效
            self.setGeometry(geometry)
            self.show()
    def simulateClick(self):
        # 模拟点击以防止屏幕休眠
        try:
            current_window = win32gui.FindWindow(None, 'Awake - 屏幕常亮工具')
            left, top, right, bottom = win32gui.GetWindowRect(current_window)
            x, y = (left + right) // 2, (top + bottom) // 2
            # 移动鼠标到窗口中心但不点击，避免干扰用户
            pyautogui.moveTo(x, y, duration=0.1)

            # 模拟按下和释放一个键（例如Shift键）来防止屏幕休眠
            pyautogui.keyDown('shift')
            pyautogui.keyUp('shift')

            # 更新状态栏信息
            minutes = self.click_interval // 60000
            self.statusBar().showMessage(f'已执行防休眠操作 ({minutes}分钟间隔) - {time.strftime("%H:%M:%S")}')
        except Exception as e:
            self.statusBar().showMessage(f'防休眠操作失败: {str(e)}')

    def showAbout(self):
        # 显示关于对话框
        QMessageBox.about(self, "关于 Awake",
                         "Awake - 屏幕常亮工具\n\n"
                         "版本: 1.1\n"
                         "功能: 防止计算机进入休眠状态，保持屏幕常亮\n\n"
                         "新增功能:\n"
                         "- 窗口置顶功能 (Ctrl+T)\n"
                         "- 可调节防休眠间隔\n"
                         "- 状态栏显示更多信息\n\n"
                         "使用方法:\n"
                         "1. 点击'开始'按钮启动防休眠功能\n"
                         "2. 点击'暂停'按钮暂时停止防休眠功能\n"
                         "3. 在'视图'菜单中可设置窗口置顶\n"
                         "4. 在'设置'菜单中可调整防休眠间隔\n\n"
                         "注意: 此工具不会影响系统电源设置，只是模拟用户活动")

    def showUsage(self):
        # 显示使用说明对话框
        QMessageBox.information(self, "使用说明",
                              "Awake 使用说明:\n\n"
                              "1. 点击'开始'按钮启动防休眠功能\n"
                              "2. 程序会自动模拟用户活动，防止系统进入休眠\n"
                              "3. 点击'暂停'按钮可以临时停止防休眠功能\n"
                              "4. 在'视图'菜单中可以设置窗口置顶（默认）\n"
                              "5. 在'设置'菜单中可以调整防休眠操作的间隔时间\n\n"
                              "快捷键:\n"
                              "Ctrl+S - 开始/重新开始\n"
                              "Ctrl+P - 暂停/继续\n"
                              "Ctrl+T - 切换窗口置顶\n"
                              "Ctrl+Q - 退出程序")

    def closeEvent(self, event):
        # 确保在关闭窗口时停止所有定时器
        self.timer.stop()
        self.click_timer.stop()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = AwakeApp()
    ex.show()
    sys.exit(app.exec_())