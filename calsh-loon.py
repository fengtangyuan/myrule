#!/usr/bin/env python3
import yaml


def main(file_name):
    output_file = file_name.replace(".txt", ".list")
    with open(file_name, "r", encoding="utf-8") as fin, open(
        output_file, "w", encoding="utf-8"
    ) as fout:
        lines = fin.readlines()
        # 跳过第一行
        for line in lines[1:]:
            line = line.strip()
            if not line or not line.startswith("- "):
                continue
            domain = line[2:].strip().strip("'").strip('"')
            if domain.startswith("+."):
                fout.write(f"DOMAIN-SUFFIX,{domain[2:]}\n")
            else:
                fout.write(f"DOMAIN,{domain}\n")


if __name__ == "__main__":
    list = ["mydirect.txt", "myproxy.txt"]
    for item in list:
        main(item)
