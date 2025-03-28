import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import subprocess
import sys
import re
import os
from threading import Thread
import json
from pathlib import Path

# 全局变量
current_env = {"type": "system", "path": sys.executable, "name": "系统 Python"}
all_environments = []

def get_conda_environments():
    """获取所有conda环境"""
    environments = []
    try:
        # 尝试使用conda命令获取环境列表
        result = subprocess.check_output(['conda', 'env', 'list', '--json'], text=True)
        env_data = json.loads(result)
        
        for env_path in env_data.get('envs', []):
            env_name = os.path.basename(env_path)
            if env_name == '':  # base环境可能是根目录
                env_name = 'base'
            
            python_path = os.path.join(env_path, 'python.exe') if os.name == 'nt' else os.path.join(env_path, 'bin', 'python')
            if os.path.exists(python_path):
                environments.append({
                    "type": "conda",
                    "name": f"Conda: {env_name}",
                    "path": python_path
                })
    except (subprocess.SubprocessError, json.JSONDecodeError, FileNotFoundError):
        # 如果conda命令不可用或出错，跳过
        pass
    
    return environments

def get_venv_environments():
    """搜索常见的venv虚拟环境位置"""
    environments = []
    
    # 常见的虚拟环境位置
    venv_locations = [
        os.path.join(os.path.expanduser("~"), "venv"),
        os.path.join(os.path.expanduser("~"), ".virtualenvs"),
        os.path.join(os.path.expanduser("~"), "Envs"),
    ]
    
    # 添加当前目录和其父目录
    current_dir = os.getcwd()
    venv_locations.append(current_dir)
    venv_locations.append(os.path.dirname(current_dir))
    
    for location in venv_locations:
        if os.path.exists(location):
            # 搜索该位置下的所有目录
            for item in os.listdir(location):
                item_path = os.path.join(location, item)
                if os.path.isdir(item_path):
                    # 检查是否是虚拟环境（查找python或python.exe）
                    python_path = os.path.join(item_path, 'bin', 'python') if os.name != 'nt' else os.path.join(item_path, 'Scripts', 'python.exe')
                    if os.path.exists(python_path):
                        environments.append({
                            "type": "venv",
                            "name": f"Venv: {item}",
                            "path": python_path
                        })
    
    return environments

def refresh_environments():
    """刷新所有可用的Python环境"""
    global all_environments
    
    # 添加系统Python
    all_environments = [{
        "type": "system",
        "name": "系统 Python",
        "path": sys.executable
    }]
    
    # 添加conda环境
    all_environments.extend(get_conda_environments())
    
    # 添加venv环境
    all_environments.extend(get_venv_environments())
    
    # 更新环境选择下拉菜单
    env_combobox['values'] = [env["name"] for env in all_environments]
    
    # 默认选择当前环境
    env_combobox.current(0)
    
    return all_environments

def change_environment(event=None):
    """切换当前Python环境"""
    global current_env
    
    selected_index = env_combobox.current()
    if selected_index >= 0 and selected_index < len(all_environments):
        current_env = all_environments[selected_index]
        status_bar.config(text=f"当前环境: {current_env['name']} | {current_env['path']}")
        refresh_packages()

def get_installed_packages():
    """获取所选环境中所有已安装的包及其版本"""
    try:
        result = subprocess.check_output([current_env["path"], '-m', 'pip', 'list'], text=True)
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
    """在选中的环境中安装新包"""
    package_name = simpledialog.askstring("安装包", "请输入要安装的包名:")
    if not package_name:
        return
    
    progress_window = tk.Toplevel(root)
    progress_window.title("安装中")
    progress_window.geometry("300x100")
    progress_label = tk.Label(progress_window, text=f"正在 {current_env['name']} 中安装 {package_name}...")
    progress_label.pack(pady=20)
    
    def run_install():
        try:
            result = subprocess.check_output(
                [current_env["path"], '-m', 'pip', 'install', package_name],
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
    """在选中的环境中更新选中的包"""
    selected = treeview.selection()
    if not selected:
        messagebox.showwarning("警告", "请先选择一个包")
        return
    
    package_name = treeview.item(selected[0])['values'][0]
    
    progress_window = tk.Toplevel(root)
    progress_window.title("更新中")
    progress_window.geometry("300x100")
    progress_label = tk.Label(progress_window, text=f"正在 {current_env['name']} 中更新 {package_name}...")
    progress_label.pack(pady=20)
    
    def run_update():
        try:
            result = subprocess.check_output(
                [current_env["path"], '-m', 'pip', 'install', '--upgrade', package_name],
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
    """在选中的环境中卸载选中的包"""
    selected = treeview.selection()
    if not selected:
        messagebox.showwarning("警告", "请先选择一个包")
        return
    
    package_name = treeview.item(selected[0])['values'][0]
    if not messagebox.askyesno("确认", f"确定要从 {current_env['name']} 卸载 {package_name} 吗?"):
        return
    
    progress_window = tk.Toplevel(root)
    progress_window.title("卸载中")
    progress_window.geometry("300x100")
    progress_label = tk.Label(progress_window, text=f"正在卸载 {package_name}...")
    progress_label.pack(pady=20)
    
    def run_uninstall():
        try:
            result = subprocess.check_output(
                [current_env["path"], '-m', 'pip', 'uninstall', '-y', package_name],
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
    """刷新当前环境的包列表"""
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
            [current_env["path"], '-m', 'pip', 'show', package_name],
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

def show_env_info():
    """显示当前环境的详细信息"""
    try:
        # 获取Python版本
        version_cmd = f'"{current_env["path"]}" --version'
        version_result = subprocess.check_output(version_cmd, shell=True, text=True).strip()
        
        # 获取pip版本
        pip_version_cmd = f'"{current_env["path"]}" -m pip --version'
        pip_version_result = subprocess.check_output(pip_version_cmd, shell=True, text=True).strip()
        
        # 获取安装包数量
        package_count = len(all_packages)
        
        # 显示信息窗口
        info_window = tk.Toplevel(root)
        info_window.title(f"环境信息: {current_env['name']}")
        info_window.geometry("500x300")
        
        info_frame = tk.Frame(info_window, padx=20, pady=20)
        info_frame.pack(fill=tk.BOTH, expand=True)
        
        # 环境名称
        tk.Label(info_frame, text="环境名称:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", pady=5)
        tk.Label(info_frame, text=current_env['name']).grid(row=0, column=1, sticky="w", pady=5)
        
        # 环境类型
        tk.Label(info_frame, text="环境类型:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="w", pady=5)
        tk.Label(info_frame, text=current_env['type']).grid(row=1, column=1, sticky="w", pady=5)
        
        # Python路径
        tk.Label(info_frame, text="Python路径:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky="w", pady=5)
        path_label = tk.Label(info_frame, text=current_env['path'])
        path_label.grid(row=2, column=1, sticky="w", pady=5)
        
        # Python版本
        tk.Label(info_frame, text="Python版本:", font=("Arial", 10, "bold")).grid(row=3, column=0, sticky="w", pady=5)
        tk.Label(info_frame, text=version_result).grid(row=3, column=1, sticky="w", pady=5)
        
        # Pip版本
        tk.Label(info_frame, text="Pip版本:", font=("Arial", 10, "bold")).grid(row=4, column=0, sticky="w", pady=5)
        tk.Label(info_frame, text=pip_version_result).grid(row=4, column=1, sticky="w", pady=5)
        
        # 包数量
        tk.Label(info_frame, text="已安装包数量:", font=("Arial", 10, "bold")).grid(row=5, column=0, sticky="w", pady=5)
        tk.Label(info_frame, text=str(package_count)).grid(row=5, column=1, sticky="w", pady=5)
        
    except Exception as e:
        messagebox.showerror("错误", f"无法获取环境信息: {str(e)}")

# 创建主窗口
root = tk.Tk()
root.title("Python 包管理器")
root.geometry("800x600")

# 创建顶部工具栏框架
toolbar_frame = tk.Frame(root)
toolbar_frame.pack(fill=tk.X, padx=10, pady=10)

# 创建环境选择下拉菜单
env_label = tk.Label(toolbar_frame, text="环境:")
env_label.pack(side=tk.LEFT, padx=5)

env_combobox = ttk.Combobox(toolbar_frame, width=25, state="readonly")
env_combobox.pack(side=tk.LEFT, padx=5)
env_combobox.bind("<<ComboboxSelected>>", change_environment)

# 环境信息按钮
env_info_button = tk.Button(toolbar_frame, text="环境信息", command=show_env_info)
env_info_button.pack(side=tk.LEFT, padx=5)

# 创建搜索栏
search_label = tk.Label(toolbar_frame, text="搜索:")
search_label.pack(side=tk.LEFT, padx=5)

search_entry = tk.Entry(toolbar_frame, width=20)
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

# 加载环境列表
all_environments = refresh_environments()

# 加载包列表
all_packages = []
refresh_packages()

# 更新状态栏显示当前环境
status_bar.config(text=f"当前环境: {current_env['name']} | {current_env['path']}")

# 启动主循环
root.mainloop()
