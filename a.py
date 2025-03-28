from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import time
import os
import sys
import platform

def auto_login():
    try:
        # 打印诊断信息
        print(f"Python 版本: {sys.version}")
        print(f"操作系统: {platform.system()} {platform.version()}")
        print(f"Selenium 版本: {webdriver.__version__}")
        
        # 设置Edge选项
        edge_options = webdriver.EdgeOptions()
        # 添加一些可能解决问题的选项
        edge_options.add_argument("--no-sandbox")
        edge_options.add_argument("--disable-dev-shm-usage")
        
        print("正在设置Edge驱动...")
        
        # 使用webdriver_manager自动下载和管理驱动
        os.environ['WDM_LOCAL'] = '1'  # 启用本地缓存
        os.environ['WDM_LOG_LEVEL'] = '0'  # 详细日志输出
        cache_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "webdriver_cache")
        os.makedirs(cache_path, exist_ok=True)
        
        print(f"缓存路径: {cache_path}")
        print("尝试安装Edge驱动...")
        
        try:
            driver_path = EdgeChromiumDriverManager(path=cache_path).install()
            print(f"驱动路径: {driver_path}")
            service = Service(driver_path)
        except Exception as driver_error:
            print(f"驱动管理器错误: {driver_error}")
            print("尝试使用备选方法初始化...")
            # 如果自动安装失败，尝试不使用webdriver_manager
            service = Service()
            
        # 初始化Edge浏览器
        print("正在初始化Edge浏览器...")
        driver = webdriver.Edge(service=service, options=edge_options)
        
        print("Edge驱动设置成功，开始自动化操作...")
        
        # 打开网页 (这里使用示例URL，需要替换为实际URL)
        driver.get("http://example.com/login")
        
        # 等待页面加载完成
        time.sleep(2)
        
        # 找到用户名输入框并输入"a"
        username_input = driver.find_element(By.ID, "user")
        username_input.clear()
        username_input.send_keys("a")
        
        # 找到密码输入框
        password_input = driver.find_element(By.ID, "password")
        
        # 确保密码框可编辑
        driver.execute_script("arguments[0].removeAttribute('readonly');", password_input)
        
        # 清空并输入密码
        password_input.clear()
        password_input.send_keys("psd")
        
        # 找到登录按钮并点击
        # 方法1：通过按钮文本内容查找
        login_button = driver.find_element(By.XPATH, "//button[contains(text(), '登录')]")
        login_button.click()
        
        # 等待登录过程完成
        time.sleep(3)
        
        print("登录操作完成")
        
    except Exception as e:
        print(f"发生错误: {e}")
        print(f"错误类型: {type(e).__name__}")
        print("请尝试以下解决方案:")
        print("1. 确保已安装Edge浏览器")
        print("2. 检查是否有管理员权限")
        print("3. 检查网络连接")
        print("4. 尝试手动下载Edge驱动")
        print("   - 访问: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/")
        print("   - 下载与您Edge版本匹配的驱动")
        print("   - 将驱动放在脚本同目录，并尝试以下代码替换:")
        print("     service = Service('msedgedriver.exe')")
        print("     driver = webdriver.Edge(service=service, options=edge_options)")
        print("5. 尝试使用Firefox作为替代方案")
    
    finally:
        # 关闭浏览器
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    # 安装依赖提示
    print("请确保已安装所需依赖:")
    print("pip install selenium webdriver-manager")
    print("\n开始执行自动化脚本...")
    
    auto_login()
