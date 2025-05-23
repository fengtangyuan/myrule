import yaml


def parse_yaml_classical_to_domain(input_file, output_file):
    """
    将 Clash 的 YAML 格式 Classical 规则转换为 YAML 格式 Domain 规则。
    删除 `DOMAIN-KEYWORD` 类型规则，并对域名前后加单引号。
    :param input_file: 输入的 YAML 格式 Classical 规则文件路径。
    :param output_file: 输出的 YAML 格式 Domain 规则文件路径。
    """
    try:
        # 读取输入的 YAML 文件
        with open(input_file, "r", encoding="utf-8") as infile:
            classical_rules = yaml.safe_load(infile)

        # 检查是否包含规则项
        if "payload" not in classical_rules:
            print("输入的 YAML 文件中没有规则项 (rules)!")
            return

        domain_list = []
        for rule in classical_rules["payload"]:
            if rule.startswith("DOMAIN-SUFFIX,"):
                domain = rule.split(",", 1)[1]
                domain_list.append(f"+.{domain}")
            elif rule.startswith("DOMAIN,"):
                domain = rule.split(",", 1)[1]
                domain_list.append(f"{domain}")
            elif rule.startswith("DOMAIN-KEYWORD,"):
                # 跳过 DOMAIN-KEYWORD 类型规则
                continue
            else:
                # 跳过其他类型规则，例如 IP-CIDR
                continue

        # 生成新的 YAML 数据
        yaml_data = {"payload": domain_list}

        # 写入输出的 YAML 文件
        with open(output_file, "w", encoding="utf-8") as outfile:
            yaml.dump(
                yaml_data,
                outfile,
                allow_unicode=True,
                default_flow_style=False,
                default_style="'",
            )

        print(f"转换完成！新的 YAML 文件已保存到 {output_file}")

    except FileNotFoundError:
        print(f"文件 {input_file} 未找到！")
    except Exception as e:
        print(f"发生错误：{e}")


# 示例用法
input_path = "classical.yaml"
output_path = "domain.yaml"
parse_yaml_classical_to_domain(input_path, output_path)
