import sys
import subprocess
import json
import os
import time
import socket
from concurrent.futures import ThreadPoolExecutor
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLineEdit, QTableWidget, 
                            QTableWidgetItem, QLabel, QMessageBox, QHeaderView, 
                            QProgressBar, QComboBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer

# 添加单例锁机制来防止多实例启动
class SingleInstanceChecker:
    def __init__(self, port=12345):
        self.port = port
        self.sock = None
        
    def is_another_instance_running(self):
        """检查是否有另一个实例正在运行"""
        try:
            # 创建 TCP 套接字
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # 设置端口重用选项
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # 尝试绑定本地地址和端口
            self.sock.bind(('127.0.0.1', self.port))
            return False  # 绑定成功，说明没有其他实例在运行
        except socket.error:
            return True  # 绑定失败，说明端口被占用，有其他实例在运行
    
    def cleanup(self):
        """关闭套接字"""
        if self.sock:
            self.sock.close()

class PackageWorker(QThread):
    """用于后台执行pip操作的线程类"""
    finished = pyqtSignal(str, bool)
    progress = pyqtSignal(str)
    
    def __init__(self, operation, package_name=None, version=None):
        super().__init__()
        self.operation = operation
        self.package_name = package_name
        self.version = version
        
    def run(self):
        try:
            if self.operation == "list":
                # 获取基础列表信息
                output = subprocess.check_output(
                    [sys.executable, "-m", "pip", "list", "--format=json"],
                    universal_newlines=True
                )
                packages = json.loads(output)
                
                # 对每个包判断是否是第三方库
                for package in packages:
                    try:
                        # 获取包的安装位置信息
                        location_output = subprocess.check_output(
                            [sys.executable, "-c", f"import {package['name'].replace('-', '_')} as m; print(m.__file__)"],
                            universal_newlines=True,
                            stderr=subprocess.PIPE
                        ).strip()
                        
                        # 判断是否是第三方库（非标准库）
                        is_third_party = "site-packages" in location_output
                        package["is_third_party"] = is_third_party
                    except Exception:
                        # 如果无法导入，默认为第三方库
                        package["is_third_party"] = True
                
                self.finished.emit(json.dumps(packages), True)
            elif self.operation == "install":
                package = self.package_name
                if self.version:
                    package = f"{self.package_name}=={self.version}"
                    
                self.progress.emit(f"正在安装 {package}...")
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", package],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                self.finished.emit(f"成功安装 {package}", True)
            elif self.operation == "uninstall":
                self.progress.emit(f"正在卸载 {self.package_name}...")
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "uninstall", "-y", self.package_name],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                self.finished.emit(f"成功卸载 {self.package_name}", True)
            elif self.operation == "search":
                self.progress.emit(f"正在搜索 {self.package_name}...")
                output = subprocess.check_output(
                    [sys.executable, "-m", "pip", "search", self.package_name],
                    universal_newlines=True
                )
                self.finished.emit(output, True)
            elif self.operation == "upgrade":
                self.progress.emit(f"正在升级 {self.package_name}...")
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", "--upgrade", self.package_name],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                self.finished.emit(f"成功升级 {self.package_name}", True)
            elif self.operation == "show":
                output = subprocess.check_output(
                    [sys.executable, "-m", "pip", "show", self.package_name],
                    universal_newlines=True
                )
                self.finished.emit(output, True)
        except Exception as e:
            self.finished.emit(str(e), False)


class PackageCache:
    """缓存包信息以提高性能"""
    def __init__(self, ttl=300):  # 默认缓存5分钟
        self.cache = {}
        self.ttl = ttl
        
    def get(self, key):
        if key in self.cache:
            timestamp, value = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return value
        return None
    
    def set(self, key, value):
        self.cache[key] = (time.time(), value)
        
    def clear(self):
        self.cache.clear()


class PyLibManager(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.cache = PackageCache()
        self.executor = ThreadPoolExecutor(max_workers=3)
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Python库管理器')
        self.setGeometry(100, 100, 800, 600)
        
        # 主布局
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        
        # 搜索区域
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('输入库名称...')
        search_button = QPushButton('搜索')
        search_button.clicked.connect(self.search_package)
        refresh_button = QPushButton('刷新')
        refresh_button.clicked.connect(self.refresh_packages)
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)
        search_layout.addWidget(refresh_button)
        
        main_layout.addLayout(search_layout)
        
        # 库列表
        self.packages_table = QTableWidget()
        self.packages_table.setColumnCount(4)  # 增加一列用于显示是否为第三方库
        self.packages_table.setHorizontalHeaderLabels(['包名', '版本', '类型', '操作'])
        self.packages_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.packages_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.packages_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.packages_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.packages_table.verticalHeader().setVisible(False)
        self.packages_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        main_layout.addWidget(self.packages_table)
        
        # 状态栏和进度条
        status_layout = QHBoxLayout()
        self.status_label = QLabel('就绪')
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.progress_bar)
        
        main_layout.addLayout(status_layout)
        
        # 操作区域
        operation_layout = QHBoxLayout()
        
        self.package_name = QLineEdit()
        self.package_name.setPlaceholderText('库名称')
        self.package_version = QLineEdit()
        self.package_version.setPlaceholderText('版本（可选）')
        
        install_button = QPushButton('安装')
        install_button.clicked.connect(self.install_package)
        
        operation_layout.addWidget(self.package_name)
        operation_layout.addWidget(self.package_version)
        operation_layout.addWidget(install_button)
        
        main_layout.addLayout(operation_layout)
        
        self.setCentralWidget(central_widget)
        
        # 初始加载已安装的包
        self.refresh_packages()
        
    def refresh_packages(self):
        self.status_label.setText('正在加载已安装的库...')
        self.progress_bar.setVisible(True)
        
        # 使用缓存提高性能
        cached_packages = self.cache.get('installed_packages')
        if cached_packages:
            self.update_package_list(cached_packages)
            self.status_label.setText('已从缓存加载')
            self.progress_bar.setVisible(False)
            return
            
        self.worker = PackageWorker("list")
        self.worker.finished.connect(self.handle_list_finished)
        self.worker.progress.connect(self.update_status)
        self.worker.start()
    
    def handle_list_finished(self, output, success):
        if success:
            try:
                packages = json.loads(output)
                self.cache.set('installed_packages', packages)
                self.update_package_list(packages)
                self.status_label.setText('库列表已刷新')
            except Exception as e:
                self.status_label.setText(f'错误: {str(e)}')
        else:
            self.status_label.setText(f'错误: {output}')
        self.progress_bar.setVisible(False)
    
    def update_package_list(self, packages):
        self.packages_table.setRowCount(0)
        
        for i, pkg in enumerate(packages):
            self.packages_table.insertRow(i)
            
            name_item = QTableWidgetItem(pkg['name'])
            version_item = QTableWidgetItem(pkg['version'])
            
            # 添加第三方库标识
            is_third_party = pkg.get('is_third_party', True)  # 默认为第三方库
            type_item = QTableWidgetItem("第三方库" if is_third_party else "标准库")
            
            self.packages_table.setItem(i, 0, name_item)
            self.packages_table.setItem(i, 1, version_item)
            self.packages_table.setItem(i, 2, type_item)
            
            # 创建操作按钮
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            
            upgrade_btn = QPushButton('更新')
            upgrade_btn.clicked.connect(lambda _, pkg_name=pkg['name']: self.upgrade_package(pkg_name))
            
            uninstall_btn = QPushButton('卸载')
            uninstall_btn.clicked.connect(lambda _, pkg_name=pkg['name']: self.uninstall_package(pkg_name))
            
            info_btn = QPushButton('信息')
            info_btn.clicked.connect(lambda _, pkg_name=pkg['name']: self.show_package_info(pkg_name))
            
            actions_layout.addWidget(upgrade_btn)
            actions_layout.addWidget(uninstall_btn)
            actions_layout.addWidget(info_btn)
            
            self.packages_table.setCellWidget(i, 3, actions_widget)  # 操作列调整为第4列(索引3)
    
    def install_package(self):
        package_name = self.package_name.text().strip()
        version = self.package_version.text().strip()
        
        if not package_name:
            QMessageBox.warning(self, '警告', '请输入库名称')
            return
            
        self.status_label.setText(f'正在安装 {package_name}...')
        self.progress_bar.setVisible(True)
        
        self.worker = PackageWorker("install", package_name, version)
        self.worker.finished.connect(self.handle_operation_finished)
        self.worker.progress.connect(self.update_status)
        self.worker.start()
    
    def uninstall_package(self, package_name):
        reply = QMessageBox.question(
            self, '确认卸载',
            f'确定要卸载 {package_name} 吗?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.status_label.setText(f'正在卸载 {package_name}...')
            self.progress_bar.setVisible(True)
            
            self.worker = PackageWorker("uninstall", package_name)
            self.worker.finished.connect(self.handle_operation_finished)
            self.worker.progress.connect(self.update_status)
            self.worker.start()
    
    def upgrade_package(self, package_name):
        self.status_label.setText(f'正在升级 {package_name}...')
        self.progress_bar.setVisible(True)
        
        self.worker = PackageWorker("upgrade", package_name)
        self.worker.finished.connect(self.handle_operation_finished)
        self.worker.progress.connect(self.update_status)
        self.worker.start()
    
    def search_package(self):
        query = self.search_input.text().strip()
        if not query:
            self.refresh_packages()
            return
            
        filtered_rows = []
        for row in range(self.packages_table.rowCount()):
            name_item = self.packages_table.item(row, 0)
            if name_item and query.lower() in name_item.text().lower():
                filtered_rows.append(row)
                
        for row in range(self.packages_table.rowCount()):
            self.packages_table.setRowHidden(row, row not in filtered_rows)
    
    def show_package_info(self, package_name):
        self.status_label.setText(f'获取 {package_name} 的信息...')
        
        cached_info = self.cache.get(f'info_{package_name}')
        if cached_info:
            self.show_info_dialog(package_name, cached_info)
            self.status_label.setText('就绪')
            return
            
        self.worker = PackageWorker("show", package_name)
        self.worker.finished.connect(lambda output, success: self.handle_info_finished(output, success, package_name))
        self.worker.start()
    
    def handle_info_finished(self, output, success, package_name):
        if success:
            self.cache.set(f'info_{package_name}', output)
            self.show_info_dialog(package_name, output)
        else:
            QMessageBox.warning(self, '错误', f'获取包信息失败: {output}')
        self.status_label.setText('就绪')
    
    def show_info_dialog(self, package_name, info):
        msg_box = QMessageBox()
        msg_box.setWindowTitle(f'{package_name} 信息')
        msg_box.setText(info)
        msg_box.setDetailedText(info)
        msg_box.exec_()
    
    def handle_operation_finished(self, message, success):
        self.progress_bar.setVisible(False)
        
        if success:
            self.status_label.setText(message)
            # 刷新包列表
            self.cache.clear()  # 清除缓存，确保数据是最新的
            self.refresh_packages()
            
            # 清空输入框
            self.package_name.clear()
            self.package_version.clear()
        else:
            QMessageBox.warning(self, '错误', message)
            self.status_label.setText('操作失败')
    
    def update_status(self, message):
        self.status_label.setText(message)
    
    def closeEvent(self, event):
        """处理窗口关闭事件"""
        # 确保在关闭窗口时清理线程池资源
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)
        event.accept()

# 修改主函数部分，添加单例检查逻辑
if __name__ == '__main__':
    # 检查是否已有实例运行
    checker = SingleInstanceChecker()
    
    if checker.is_another_instance_running():
        # 已有实例运行，显示消息并退出
        app = QApplication(sys.argv)
        QMessageBox.warning(None, '警告', '程序已经在运行中！')
        sys.exit(0)
    else:
        # 这是第一个实例，正常启动
        # 确保 PyQt 的 QApplication 只创建一次
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)
            
        try:
            manager = PyLibManager()
            manager.show()
            exit_code = app.exec_()
        finally:
            # 确保在退出时释放资源
            checker.cleanup()
            
        sys.exit(exit_code)
