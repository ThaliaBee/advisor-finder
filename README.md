# advisor-finder

> 基于 DeepSeek API 的保研/考研导师匹配智能体

输入你的研究方向和目标学校的院系页面，自动帮你找到匹配的导师并整理详细资料。

---

## 功能

**模式一：搜索推荐导师**
粘贴学院师资介绍页的网址，Agent 会自动浏览页面、分析每位导师的研究方向，结合你的个人情况给出推荐列表和契合度评分，保存为 Markdown 文件。

**模式二：整理导师详细资料**
指定某位导师，自动收集其联系方式、个人主页、招生要求、近两年论文、网络评价等，整理成结构化文档，每项信息标注来源。

---

## 使用前准备

1. **Python 3.11**：[下载地址](https://www.python.org/downloads/)，安装时勾选 `Add Python to PATH`
2. **DeepSeek API Key**：在 [platform.deepseek.com](https://platform.deepseek.com) 注册获取（充值几块钱即可）

---

## 快速开始

**第一步：下载项目**

点击页面右上角绿色 `Code` 按钮 → `Download ZIP`，解压到任意位置。

**第二步：运行配置脚本**

双击 `setup.bat`，脚本会自动创建虚拟环境并安装所有依赖。

**第三步：填入 API Key**

用记事本打开 `.env` 文件，将内容改为：
```
DEEPSEEK_API_KEY=你的API_Key
```

> ⚠️ **安全提示**：`.env` 文件含有你的 API Key，请勿分享给他人，不要上传到 GitHub/Gitee 或任何公开平台。API Key 泄露会导致他人盗用你的余额。

**第四步：放入个人资料（推荐）**

将简历、个人陈述等文件（`.txt` / `.docx` / `.pdf` 格式）放入 `personal_info/` 文件夹，Agent 会据此给出更精准的匹配。

> ⚠️ **隐私提示**：文件内容会被发送至 DeepSeek API 进行分析。放入前请删除手机号、身份证号、家庭住址等敏感信息，只保留研究方向、项目经历、教育背景等与导师匹配相关的内容。

**第五步：启动程序**

双击 `start.bat` 即可启动程序。

---

## 使用示例

```
你：https://cs.pku.edu.cn/szdw/（北大计算机学院师资页）

[访问网页] https://cs.pku.edu.cn/szdw/
[搜索] 北京大学计算机学院导师研究方向

助手：根据你的研究方向，为你推荐以下导师...
（同时保存到 results/北京大学/推荐导师.md）
```

```
你：帮我整理北京大学张三老师的详细资料

[搜索] 北京大学 张三 Google Scholar

助手：已整理完成...
（保存到 results/北京大学/张三/详细资料.md）
```

---

## 项目结构

```
advisor-finder/
├── personal_info/   # 放入你的简历、个人陈述（不会上传到仓库）
├── results/         # 自动生成的导师推荐文件（不会上传到仓库）
├── .env             # API Key 配置（不会上传到仓库）
├── config.py        # 配置读取
├── tools.py         # 工具：网页抓取、搜索、文件保存
├── agent.py         # Agent 核心逻辑
├── main.py          # 对话入口
├── setup.bat        # 一键配置环境
├── start.bat        # 一键启动
├── uninstall.bat    # 一键卸载
└── requirements.txt
```

---

## 技术说明

- 使用 DeepSeek API（兼容 OpenAI SDK）
- 基于 Function Calling 实现工具调用
- 使用 Playwright 真实浏览器抓取网页，支持 JavaScript 渲染页面
- 工具包括：DuckDuckGo 搜索、网页抓取、本地文件读写
- 多轮对话，带完整上下文记忆

---

## 查看生成的文件

程序会在 `results/` 文件夹下同时生成两个版本：
- `.md` 文件：格式美观，推荐用 [Typora](https://typora.io)（免费）打开
- `.txt` 文件：纯文本，用记事本直接打开即可

---

## 注意事项

- **API Key**：`.env` 文件不要发给任何人，泄露后请立即在 platform.deepseek.com 重置 Key
- **个人信息**：放入 `personal_info/` 的文件内容会发送给 DeepSeek AI，请提前删除手机号、身份证号、家庭住址等敏感内容
- 网页抓取结果依赖目标网站的可访问性，部分高校网站可能需要校内网才能访问
