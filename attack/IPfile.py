from ipwhois import IPWhois
import json
from concurrent.futures import ThreadPoolExecutor

def query_ip_info(ip_address):
    try:
        obj = IPWhois(ip_address)
        results = obj.lookup_rdap(depth=1)
        return {
            "IP": ip_address,
            "ASN": results.get("asn"),
            "ASN Description": results.get("asn_description"),
            "Country": results.get("network", {}).get("country"),
            "ISP": results.get("network", {}).get("name"),
            "CIDR": results.get("network", {}).get("cidr"),
            "Start Date": results.get("network", {}).get("start_date"),
            "Description": results.get("network", {}).get("description"),
        }
    except Exception as e:
        return {"IP": ip_address, "Error": str(e)}

def main():
    input_file = "access.log"
    output_file = "IPInfo.json"

    # 读取 IP 地址
    with open(input_file, "r") as f:
        ip_addresses = [line.strip().split()[0] for line in f if line.strip()]

    # 使用多线程查询 IP 信息
    results = []
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(query_ip_info, ip) for ip in ip_addresses]
        for future in futures:
            result = future.result()
            print(result)  # 打印结果
            results.append(result)

    # 将结果保存到 JSON 文件
    with open(output_file, "w") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

    print(f"查询结果已保存到 {output_file}")

if __name__ == "__main__":
    main()
