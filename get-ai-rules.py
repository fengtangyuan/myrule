# 使用request获取ai规则并设置请求头
import requests

hearders = {"User-Agent": "Loon/91 CFNetwork/3860.200.71 Darwin/20.5.0"}


def get_ai_rules(url):
    try:
        response = requests.get(url, headers=hearders)
        response.raise_for_status()  # 检查请求是否成功
        ai_rules = response.text
        return ai_rules
    except requests.exceptions.RequestException as e:
        print(f"请求AI规则时出错: {e}")
        return None


def save_ai_rules_to_file(rules, filename):
    try:
        with open(filename, "w", encoding="utf-8") as file:
            file.write(rules)
        print(f"AI规则已成功保存到{filename}文件中。")
    except IOError as e:
        print(f"保存AI规则时出错: {e}")


if __name__ == "__main__":
    url = "https://kelee.one/Tool/Loon/Lsr/AI.lsr"  # 替换为实际的AI规则URL
    rules = get_ai_rules(url)
    # 将获取到的规则保存到本地文件，并可自定义文件名
    if rules:
        save_ai_rules_to_file(rules, "AI.list")
