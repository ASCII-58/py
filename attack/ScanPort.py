import socket
import random
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from tqdm import tqdm  # 引入tqdm库

# 创建logger实例
logger = logging.getLogger('PortScanner')
logger.setLevel(logging.INFO)

# 清除可能存在的处理器
if logger.handlers:
    logger.handlers.clear()

# 配置日志处理器，指定UTF-8编码
handler = logging.FileHandler('1.log', encoding='utf-8')
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

def scan_port(target, port):
    """扫描单个端口"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1.5)
    result = {"port": port, "status": "closed"}
    
    try:
        conn_result = sock.connect_ex((target, port))
        if conn_result == 0:
            result["status"] = "open"
    except socket.gaierror:
        result["status"] = "error"
        logger.error(f"主机名解析失败: {target}")
    except Exception as e:
        result["status"] = "error"
        logger.error(f"扫描端口 {port} 时出错: {str(e)}")
    finally:
        sock.close()
    return result

def main():
    target = "xhub.top"
    ports = list(range(1, 65536))
    random.shuffle(ports)
    total_ports = len(ports)

    logger.info(f"开始扫描目标: {target}")
    logger.info(f"计划扫描端口数量: {total_ports}")
    start_time = datetime.now()
    
    open_ports = []  # 添加列表来存储开放端口
    
    with ThreadPoolExecutor(max_workers=600) as executor:
        # 提交所有扫描任务
        future_to_port = {
            executor.submit(scan_port, target, port): port 
            for port in ports
        }
        
        # 处理完成的任务
        scan_count = 0  # 添加计数器
        with tqdm(total=total_ports, desc="扫描进度", unit="端口") as pbar:  # 使用tqdm显示进度条
            for future in as_completed(future_to_port):
                result = future.result()
                port = result["port"]
                status = result["status"]
                
                if status == "open":
                    open_ports.append(port)  # 记录开放端口
                
                scan_count += 1  # 增加计数
                pbar.update(1)  # 更新进度条
    
    end_time = datetime.now()
    duration = end_time - start_time
    
    # 记录扫描结果摘要
    logger.info(f"扫描完成，耗时: {duration}")
    
    # 记录开放端口
    if open_ports:
        logger.info(f"开放端口: {open_ports}")
    else:
        logger.info("没有发现开放端口")

if __name__ == "__main__":
    
        main()
