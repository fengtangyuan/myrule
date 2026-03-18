# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

代理规则管理项目，维护和转换各种代理规则格式（Loon YAML ↔ Clash LIST），并支持通过 IP 归属地自动分类域名。

## 目录结构

- **根目录**: 规则文件和转换脚本
  - `*.txt`: Loon YAML 格式规则
  - `*.list`: Clash LIST 格式规则
  - `domain-classify.py`: 域名查询工具（交互式/命令行）
  - `calsh-to-loon.py`: TXT → LIST 批量转换
  - `loon-to-clash.py`: LIST → YAML 批量转换
  - `get-*.py`: 从远程获取规则

- `binding/python/`: ip2region 查询客户端
- `maker/python/`: XDB 数据库生成工具
- `data/`: IP 数据文件

## 常用命令

### 域名查询与分类
```bash
# 交互模式
python domain-classify.py

# 命令行模式（AI 调用）
python domain-classify.py <domain> <format>
# format: 1=完整域名, 2=后缀匹配(+.domain)
# 例: python domain-classify.py www.baidu.com 1
```

### 规则格式转换
```bash
# TXT → LIST (处理所有文件)
python calsh-to-loon.py

# LIST → YAML (需要修改 input_file/output_file)
python loon-to-clash.py
```

### 从远程获取规则
```bash
python get-ai-rules.py
python get-google-rules.py
```

### IP 地理位置查询
```bash
# 交互模式
cd binding/python
python search_test.py --db=../../data/ip2region_v4.xdb

# 非交互模式（直接查询）
cd binding/python && echo -e "<IP>\nquit" | python search_test.py --db=../../data/ip2region_v4.xdb
# 例: cd binding/python && echo -e "70.36.96.43\nquit" | python search_test.py --db=../../data/ip2region_v4.xdb
# 输出: {region: 中国|香港特别行政区|0|0|CN, ioCount: 5, took: 0 μs}
```

## 规则文件格式

### Loon 格式 (TXT/YAML)
```yaml
payload:
- 'example.com'      # 精确域名
- '+.example.com'    # 域名后缀
```

### Clash 格式 (LIST)
```
DOMAIN,example.com        # 精确域名
DOMAIN-SUFFIX,example.com # 域名后缀
```

## ip2region 集成

使用 `vectorIndex` 缓存模式，需要通过 `sys.path.insert()` 添加模块路径：
```python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'binding', 'python'))
import ip2region.searcher as xdb
import ip2region.util as util
```

XDB 数据库位于 `data/ip2region_v4.xdb`。
