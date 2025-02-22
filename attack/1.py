import threading
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import logging

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='browser_thread.log'
)

def open_webpage(url, driver_path):
    try:
        # 创建 ChromeOptions 对象并开启无头模式
        chrome_options = Options()
        chrome_options.add_argument('--headless')

        # 配置 Chrome 浏览器驱动服务
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # 打开网页
        driver.get(url)
        logging.info(f"Successfully opened {url} in a new browser window.")

    except Exception as e:
        logging.error(f"An error occurred while opening {url}: {e}")
    finally:
        # 关闭浏览器
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    while True:
        # 要打开的网页 URL
        url = "http://pxs22b.sunzk.com/"
        # ChromeDriver 的路径
        driver_path = r'D:\LENOVO\Desktop\msedgedriver.exe'
        # 要打开的网页数量（线程数）
        num_threads = 12

        threads = []
        for _ in range(num_threads):
            # 创建线程
            thread = threading.Thread(target=open_webpage, args=(url, driver_path))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()