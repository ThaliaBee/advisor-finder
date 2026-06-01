import json
from openai import OpenAI
from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, MODEL
from tools import TOOLS, TOOL_MAP, read_personal_files

SYSTEM_PROMPT_TEMPLATE = """你是一个专业的保研/考研导师匹配助手，支持两种工作模式。

## 模式一：搜索推荐导师
当用户提供某学校某学院的师资介绍页面网址时：
1. 用 fetch_webpage 获取该页面，找出所有导师的个人主页链接
2. 逐一用 fetch_webpage 访问导师主页，了解其研究方向和代表论文
3. 结合下方用户个人情况，筛选 3~5 个最匹配的导师（最多8个）
4. 每位导师给出契合度评分（1~10分）和推荐理由
5. 用 save_file 将推荐结果保存到 "学校名称/推荐导师.md"，同时将内容输出到屏幕

## 模式二：整理导师详细资料
当用户要求整理某位具体导师的详细资料时：
1. 搜索并整理：联系方式、个人网站网址、招生要求
2. 用 search_web 搜索该导师在 Google Scholar 上近2年的论文，列出题目和一句话简介
3. 搜索网络上对该导师的评价（最多5条来源）
4. 整理导师的研究领域
5. 每项信息标注来源网址
6. 用 save_file 保存到 "学校名称/导师姓名/详细资料.md"，同时将内容输出到屏幕

## 防幻觉原则（必须严格遵守）
- 只推荐名字在你实际获取的页面文本中明确出现的导师，严禁凭记忆或训练数据补充任何人名
- 每位推荐导师必须有对应的 fetch_webpage 调用记录作为依据
- 如果页面加载失败或内容为空，如实告知用户，不要猜测或补充内容
- 学校名称使用全称，如"北京大学"而非"北大"
- 不确定的信息请注明"待核实"并标注来源

---
## 用户个人情况
{personal_info}
"""


class AdvisorAgent:
    def __init__(self):
        self.client = OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_BASE_URL
        )
        personal_info = read_personal_files()
        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(personal_info=personal_info)
        self.history = [{"role": "system", "content": system_prompt}]
        self._personal_loaded = "（personal_info 文件夹为空" not in personal_info

    def chat(self, user_message: str) -> str:
        self.history.append({"role": "user", "content": user_message})

        while True:
            response = self.client.chat.completions.create(
                model=MODEL,
                messages=self.history,
                tools=TOOLS,
                tool_choice="auto"
            )

            message = response.choices[0].message

            if message.tool_calls:
                self.history.append(message)
                for tool_call in message.tool_calls:
                    func_name = tool_call.function.name
                    func_args = json.loads(tool_call.function.arguments)

                    if func_name == "fetch_webpage":
                        print(f"  [访问网页] {func_args.get('url', '')}")
                    elif func_name == "search_web":
                        print(f"  [搜索] {func_args.get('query', '')}")
                    elif func_name == "save_file":
                        print(f"  [保存文件] {func_args.get('relative_path', '')}")

                    result = TOOL_MAP[func_name](**func_args)
                    self.history.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result
                    })
                continue

            reply = message.content
            self.history.append({"role": "assistant", "content": reply})
            return reply

    def reset(self):
        personal_info = read_personal_files()
        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(personal_info=personal_info)
        self.history = [{"role": "system", "content": system_prompt}]
        print("对话已重置，个人情况已重新读取。")
