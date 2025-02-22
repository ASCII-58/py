import logging
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from concurrent.futures import ThreadPoolExecutor
import threading

# 创建线程安全的日志处理
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [Thread-%(thread)d] - %(levelname)s - %(message)s',
    filename='0.log',
    filemode='a'
)

def auto(thread_id):
    try:
        logging.info(f"Thread {thread_id}: Starting automation")
        edge_options = Options()
        edge_options.add_argument('--headless')

        service = Service(r'D:\LENOVO\Desktop\msedgedriver.exe')
        driver = webdriver.Edge(service=service, options=edge_options)

        driver.get('http://pxs22b.sunzk.com/')
        logging.info(f"Thread {thread_id}: Page opened")

        # ...existing code...

    except Exception as e:
        logging.error(f"Thread {thread_id}: An error occurred: {e}")
    finally:
        if 'driver' in locals():
            driver.quit()
            logging.info(f"Thread {thread_id}: Browser closed")

def run_multiple_threads(thread_count=4):
    with ThreadPoolExecutor(max_workers=thread_count) as executor:
        while True:
            futures = [executor.submit(auto, i) for i in range(thread_count)]
            # 等待所有线程完成当前循环
            for future in futures:
                future.result()

if __name__ == "__main__":
    try:
        # 设置要运行的线程数
        THREAD_COUNT = 8
        logging.info(f"Starting automation with {THREAD_COUNT} threads")
        run_multiple_threads(THREAD_COUNT)
    except KeyboardInterrupt:
        logging.info("Program terminated by user")
    except Exception as e:
        logging.error(f"Main program error: {e}")