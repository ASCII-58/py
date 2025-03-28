import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import subprocess
import sys
import re
from threading import Thread

def get_installed_packages():
    """获取所有已安装的包及其版本"""
    try:
        result = subprocess.check_output([sys.executable, '-m', 'pip', 'list'], text=True)
        packages = []
        for line in result.split('\n')[2:]:  # 跳过标题行
            if line.strip():
                parts = line.split()
                if len(parts) >= 2:
                    packages.append((parts[0], parts[1]))  # (包名, 版本)
        return packages
    except Exception as e:
        messagebox.showerror("错误", f"无法获取已安装的包: {str(e)}")
        return []

def install_package():
    """安装新包"""
    package_name = simpledialog.askstring("安装包", "请输入要安装的包名:")
    if not package_name:
        return
    
    progress_window = tk.Toplevel(root)
    progress_window.title("安装中")
    progress_window.geometry("300x100")
    progress_label = tk.Label(progress_window, text=f"正在安装 {package_name}...")
    progress_label.pack(pady=20)
    
    def run_install():
        try:
            result = subprocess.check_output(
                [sys.executable, '-m', 'pip', 'install', package_name],
                stderr=subprocess.STDOUT,
                text=True
            )
            progress_window.destroy()
            messagebox.showinfo("成功", f"{package_name} 安装成功!")
            refresh_packages()
        except subprocess.CalledProcessError as e:
            progress_window.destroy()
            messagebox.showerror("错误", f"安装失败: {e.output}")
    
    Thread(target=run_install).start()

def update_package():
    """更新选中的包"""
    selected = treeview.selection()
    if not selected:
        messagebox.showwarning("警告", "请先选择一个包")
        return
    
    package_name = treeview.item(selected[0])['values'][0]
    
    progress_window = tk.Toplevel(root)
    progress_window.title("更新中")
    progress_window.geometry("300x100")
    progress_label = tk.Label(progress_window, text=f"正在更新 {package_name}...")
    progress_label.pack(pady=20)
    
    def run_update():
        try:
            result = subprocess.check_output(
                [sys.executable, '-m', 'pip', 'install', '--upgrade', package_name],
                stderr=subprocess.STDOUT,
                text=True
            )
            progress_window.destroy()
            messagebox.showinfo("成功", f"{package_name} 更新成功!")
            refresh_packages()
        except subprocess.CalledProcessError as e:
            progress_window.destroy()
            messagebox.showerror("错误", f"更新失败: {e.output}")
    
    Thread(target=run_update).start()

def uninstall_package():
    """卸载选中的包"""
    selected = treeview.selection()
    if not selected:
        messagebox.showwarning("警告", "请先选择一个包")
        return
    
    package_name = treeview.item(selected[0])['values'][0]
    if not messagebox.askyesno("确认", f"确定要卸载 {package_name} 吗?"):
        return
    
    progress_window = tk.Toplevel(root)
    progress_window.title("卸载中")
    progress_window.geometry("300x100")
    progress_label = tk.Label(progress_window, text=f"正在卸载 {package_name}...")
    progress_label.pack(pady=20)
    
    def run_uninstall():
        try:
            result = subprocess.check_output(
                [sys.executable, '-m', 'pip', 'uninstall', '-y', package_name],
                stderr=subprocess.STDOUT,
                text=True
            )
            progress_window.destroy()
            messagebox.showinfo("成功", f"{package_name} 卸载成功!")
            refresh_packages()
        except subprocess.CalledProcessError as e:
            progress_window.destroy()
            messagebox.showerror("错误", f"卸载失败: {e.output}")
    
    Thread(target=run_uninstall).start()

def search_packages():
    """搜索包"""
    search_term = search_entry.get().lower()
    treeview.delete(*treeview.get_children())
    
    for package in all_packages:
        if search_term in package[0].lower():
            treeview.insert('', 'end', values=package)

def refresh_packages():
    """刷新包列表"""
    global all_packages
    all_packages = get_installed_packages()
    treeview.delete(*treeview.get_children())
    
    for package in all_packages:
        treeview.insert('', 'end', values=package)

def show_package_details():
    """显示选中包的详细信息"""
    selected = treeview.selection()
    if not selected:
        return
    
    package_name = treeview.item(selected[0])['values'][0]
    
    try:
        result = subprocess.check_output(
            [sys.executable, '-m', 'pip', 'show', package_name],
            text=True
        )
        
        detail_window = tk.Toplevel(root)
        detail_window.title(f"{package_name} 详情")
        detail_window.geometry("500x400")
        
        text_area = tk.Text(detail_window, wrap=tk.WORD)
        text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_area.insert(tk.END, result)
        text_area.config(state=tk.DISABLED)
        
    except subprocess.CalledProcessError as e:
        messagebox.showerror("错误", f"无法获取包详情: {str(e)}")

# 创建主窗口
root = tk.Tk()
root.title("Python 包管理器")
root.geometry("800x600")

# 创建顶部工具栏框架
toolbar_frame = tk.Frame(root)
toolbar_frame.pack(fill=tk.X, padx=10, pady=10)

# 创建搜索栏
search_label = tk.Label(toolbar_frame, text="搜索:")
search_label.pack(side=tk.LEFT, padx=5)

search_entry = tk.Entry(toolbar_frame, width=30)
search_entry.pack(side=tk.LEFT, padx=5)
search_entry.bind("<KeyRelease>", lambda e: search_packages())

# 创建按钮
refresh_button = tk.Button(toolbar_frame, text="刷新", command=refresh_packages)
refresh_button.pack(side=tk.RIGHT, padx=5)

uninstall_button = tk.Button(toolbar_frame, text="卸载", command=uninstall_package)
uninstall_button.pack(side=tk.RIGHT, padx=5)

update_button = tk.Button(toolbar_frame, text="更新", command=update_package)
update_button.pack(side=tk.RIGHT, padx=5)

install_button = tk.Button(toolbar_frame, text="安装", command=install_package)
install_button.pack(side=tk.RIGHT, padx=5)

# 创建表格
columns = ("包名", "版本")
treeview = ttk.Treeview(root, columns=columns, show='headings')

# 设置列标题
for col in columns:
    treeview.heading(col, text=col)
    treeview.column(col, width=100)

# 设置列宽
treeview.column("包名", width=300)
treeview.column("版本", width=100)

# 绑定双击事件显示详情
treeview.bind("<Double-1>", lambda e: show_package_details())

# 添加滚动条
scrollbar = ttk.Scrollbar(root, orient=tk.VERTICAL, command=treeview.yview)
treeview.configure(yscroll=scrollbar.set)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
treeview.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# 状态栏
status_bar = tk.Label(root, text="就绪", bd=1, relief=tk.SUNKEN, anchor=tk.W)
status_bar.pack(side=tk.BOTTOM, fill=tk.X)

# 加载包列表
all_packages = []
refresh_packages()

# 启动主循环
root.mainloop()
