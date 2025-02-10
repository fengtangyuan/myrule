#!/usr/bin/env python3
from hmac import new
import yaml

def main(file_name):
    # 读取 YAML 文件
    with open(file_name, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    # 获取 payload 列表
    payload_list = data.get("payload", [])
    newfile_name = file_name.replace(".txt", "-ss.txt")
    # 打开输出文件，逐行写入处理后的域名
    with open(newfile_name, "w", encoding="utf-8") as f:
        for item in payload_list:
            # 如果字符串以 '+' 开头，则去掉它
            if item.startswith('+'):
                item = item[1:]
            f.write(item + "\n")

if __name__ == "__main__":
    list = ["mydirect.txt", "myemby.txt", "myother.txt", "myproxy.txt"]
    for item in list:
        main(item)
