#!/usr/bin/env python3
"""
域名查询工具 - 查询域名 IP 归属地并写入规则文件
"""

import dns.resolver
import sys
import os
import io

# 添加 ip2region 模块路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'binding', 'python'))
import ip2region.searcher as xdb
import ip2region.util as util


def create_ip_searcher(db_path):
    """创建 IP 查询器"""
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"XDB 数据库不存在: {db_path}")

    handle = io.open(db_path, "rb")
    try:
        util.verify(handle)
        header = util.load_header(handle)
        version = util.version_from_header(header)
        if version is None:
            handle.close()
            raise Exception("无法从头部获取 IP 版本")

        v_index = util.load_vector_index(handle)
        searcher = xdb.new_with_vector_index(version, db_path, v_index)
        return searcher
    except Exception as e:
        handle.close()
        raise


def query_dns(domain):
    """查询域名的 A 记录，返回 IP 列表"""
    try:
        answers = dns.resolver.resolve(domain, 'A')
        return [rdata.address for rdata in answers]
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.Timeout, Exception):
        return None


def check_ip_country(searcher, ip_str):
    """检查 IP 的归属国家"""
    try:
        ip_bytes = util.parse_ip(ip_str)
        region = searcher.search(ip_bytes)
        if region:
            parts = region.split('|')
            return parts[0]
    except Exception:
        pass
    return None


def get_output_filename(is_cn):
    """根据归属地获取输出文件名"""
    return "mydirect-cn.txt" if is_cn else "mydirect-uncn.txt"


def append_to_yaml(file_path, domain):
    """追加域名到 YAML 文件"""
    # 检查是否已存在
    domain_clean = domain.strip().strip("'").strip('"')
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if f"'{domain_clean}'" in content or f'"{domain_clean}"' in content:
                return  # 已存在，跳过

    # 追加新域名到文件末尾
    if not os.path.exists(file_path):
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("payload:\n")
            f.write(f"  - '{domain}'\n")
    else:
        with open(file_path, 'rb+') as f:
            f.seek(0, 2)  # 移动到文件末尾
            # 检查最后一个字符是否是换行符
            f.seek(-1, 2)
            last_char = f.read(1)
            if last_char not in (b'\n', b'\r'):
                f.write(b'\n')
            f.write(f"  - '{domain}'\n".encode('utf-8'))


def append_to_main_file(domain):
    """同时追加到 mydirect.txt 总文件"""
    main_file = "mydirect.txt"
    if not os.path.exists(main_file):
        with open(main_file, 'w', encoding='utf-8') as f:
            f.write("payload:\n")
            f.write(f"  - '{domain}'\n")
        return

    # 检查是否已存在
    with open(main_file, 'r', encoding='utf-8') as f:
        content = f.read()
        # 检查域名是否已存在（去除引号和空格后比较）
        domain_clean = domain.strip().strip("'").strip('"')
        if f"'{domain_clean}'" in content or f'"{domain_clean}"' in content:
            return  # 已存在，跳过

    # 追加新域名，确保先有换行符
    with open(main_file, 'rb+') as f:
        f.seek(0, 2)  # 移动到文件末尾
        # 检查最后一个字符是否是换行符
        f.seek(-1, 2)
        last_char = f.read(1)
        if last_char not in (b'\n', b'\r'):
            # 文件末尾没有换行，先添加换行
            f.write(b'\n')
        f.write(f"  - '{domain}'\n".encode('utf-8'))


def convert_to_list(txt_file):
    """将 TXT 文件转换为 LIST 格式"""
    output_file = txt_file.replace(".txt", ".list")
    try:
        with open(txt_file, "r", encoding="utf-8") as fin, \
             open(output_file, "w", encoding="utf-8") as fout:
            lines = fin.readlines()
            for line in lines:
                line = line.strip()
                if not line or line == "payload:":
                    continue
                if not line.startswith("- "):
                    continue
                domain = line[2:].strip().strip("'").strip('"')
                if domain.startswith("+."):
                    fout.write(f"DOMAIN-SUFFIX,{domain[2:]}\n")
                else:
                    fout.write(f"DOMAIN,{domain}\n")
    except Exception as e:
        print(f"警告: 转换失败: {e}")


def query_domain_info(domain, searcher):
    """查询域名信息，返回 (归属地, IP)"""
    ips = query_dns(domain)
    if not ips:
        return None, None

    ip = ips[0]
    country = check_ip_country(searcher, ip)
    return country, ip


def get_root_domain(domain):
    """提取主域名（去除 www 等常见子域名）"""
    domain = domain.lstrip('+.')
    parts = domain.split('.')
    if len(parts) >= 2:
        # 去除 www, m 等常见子域名
        common_subdomains = {'www', 'm', 'mobile', 'app'}
        if parts[0].lower() in common_subdomains:
            return '.'.join(parts[1:])
    return domain


def format_domain_rule(domain, use_suffix):
    """格式化域名规则"""
    domain_clean = domain.lstrip('+.')
    if use_suffix:
        # 后缀匹配使用主域名
        root = get_root_domain(domain_clean)
        return f"+.{root}"
    # 完整域名保持原样
    return domain_clean


def process_domain(domain, searcher, use_suffix=False):
    """处理单个域名并写入文件"""
    query_domain = domain.lstrip('+.')
    print(f"正在查询 {query_domain} ...")

    country, ip = query_domain_info(query_domain, searcher)

    if not ip:
        print(f"❌ DNS 查询失败，无法解析域名")
        return False

    is_cn = country and '中国' in country

    print(f"   IP: {ip}")
    print(f"   归属地: {country or '未知'}")
    print(f"   类型: {'🇨🇳 CN' if is_cn else '🌍 非CN'}")

    rule = format_domain_rule(domain, use_suffix)
    output_file = get_output_filename(is_cn)

    # 写入分类文件
    append_to_yaml(output_file, rule)
    convert_to_list(output_file)

    # 同时追加到总文件
    append_to_main_file(rule)
    convert_to_list("mydirect.txt")

    print(f"✅ 已写入: {output_file} + mydirect.txt -> {rule}")
    return True


def main():
    db_path = "data/ip2region_v4.xdb"

    # 解析命令行参数
    args = sys.argv[1:]

    # 初始化 IP 查询器
    try:
        searcher = create_ip_searcher(db_path)
    except FileNotFoundError:
        print(f"错误: XDB 数据库不存在: {db_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"错误: 初始化失败: {e}", file=sys.stderr)
        sys.exit(1)

    # 命令行模式: python domain-classify.py <domain> <format>
    # format: 1=完整域名, 2=后缀匹配
    if len(args) >= 1:
        domain = args[0]
        use_suffix = (len(args) >= 2 and args[1] == '2')
        success = process_domain(domain, searcher, use_suffix)
        searcher.close()
        sys.exit(0 if success else 1)

    # 交互模式
    print("=" * 50)
    print("域名查询工具")
    print("输入域名查询归属地，选择写入规则文件")
    print("输入 'q' 或 'quit' 退出")
    print("=" * 50)

    while True:
        try:
            domain = input("\n请输入域名: ").strip()

            if domain.lower() in ('q', 'quit', 'exit'):
                break

            if not domain:
                continue

            # 去除已有的 +. 前缀用于查询
            query_domain = domain.lstrip('+.')

            print(f"正在查询 {query_domain} ...")

            country, ip = query_domain_info(query_domain, searcher)

            if not ip:
                print(f"❌ DNS 查询失败，无法解析域名")
                continue

            is_cn = country and '中国' in country

            print(f"   IP: {ip}")
            print(f"   归属地: {country or '未知'}")
            print(f"   类型: {'🇨🇳 CN' if is_cn else '🌍 非CN'}")

            # 选择写入格式
            print("\n选择写入格式:")
            print("  1 - 完整域名")
            print("  2 - 后缀匹配 (+.domain)")
            print("  0 - 跳过")

            choice = input("请选择 [1/2/0]: ").strip()

            if choice == '0':
                print("已跳过")
                continue

            use_suffix = (choice == '2')
            rule = format_domain_rule(domain, use_suffix)
            output_file = get_output_filename(is_cn)

            # 写入分类文件
            append_to_yaml(output_file, rule)
            convert_to_list(output_file)

            # 同时追加到总文件
            append_to_main_file(rule)
            convert_to_list("mydirect.txt")

            print(f"✅ 已写入: {output_file} + mydirect.txt -> {rule}")

        except KeyboardInterrupt:
            print("\n\n退出程序")
            break
        except Exception as e:
            print(f"❌ 错误: {e}")

    # 关闭查询器
    searcher.close()
    print("\n再见!")


if __name__ == "__main__":
    main()
