# ideas — 零散想法与小实验的存放目录

## 定位

存放一次性小工具、技术实验、原型验证、随手写的脚本。
不是正式项目，不需要完美，但要能找回、能看懂。

## 命名规范

格式：`{类型}-{简述}`，全小写，连字符分隔。

类型前缀：
- `exp-` — 实验/探索（试一个库、验证一个想法）
- `tool-` — 小工具（能跑起来用的）
- `demo-` — 示例/demo（给别人看的、展示用的）
- `proto-` — 原型（可能会发展成正式项目）
- `tmp-` — 一次性临时用，用完可删

简述部分：2-4 个英文单词，说清楚做什么。不要用日期、不要用 test/test1/test2。

示例：
```
exp-markdown-to-slides    # 试一下 markdown 转幻灯片
tool-batch-rename         # 批量重命名文件的小工具
demo-webgl-particles      # WebGL 粒子效果 demo
proto-cli-todo            # 可能做成正式项目的 CLI todo
tmp-csv-parse             # 临时解析一个 csv
```

## 目录结构

每个小东西一个目录，内部结构随意，但建议：

- 有入口文件的放一个 README 或注释说明怎么跑
- 依赖了什么写清楚（`package.json`、`requirements.txt`、或 README 里一句话）
- 别把 node_modules / venv / __pycache__ 提交到 git（如果初始化了 git 的话）

## 清理机制

- `tmp-` 前缀的：用完即删，不要囤积
- 超过 3 个月没动过的 `exp-`：要么删、要么升级为 `proto-`
- 每次往里加新东西前，扫一眼有没有可以清理的

## 快速开始（给我自己的备忘）

新想法直接建目录开搞，不用犹豫：
```bash
# 1. 建目录
mkdir exp-想做的事

# 2. 进去开搞
cd exp-想做的事

# 3. 结束后如果值得留，加个 README；不值得留就 rm -rf
```

## Claude 在这个目录下的行为

- 帮用户起目录名时，遵守上述命名规范
- 不强制要求内部结构，但建议加 README 说明用途和运行方式
- 提醒用户定期清理 `tmp-` 和过期的 `exp-`
