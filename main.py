from agent import AdvisorAgent


HELP_TEXT = """
==========================================
          保研导师匹配助手
==========================================
  模式一：搜索推荐导师
    直接粘贴学院师资介绍页的网址即可

  模式二：整理导师详细资料
    说"帮我整理 [学校] [导师姓名] 的详细资料"

  准备工作：把简历/个人陈述放在 personal_info/ 文件夹
  输出结果：自动保存到 results/ 文件夹

  命令：重置 / 退出
==========================================
"""


def main():
    print(HELP_TEXT)
    agent = AdvisorAgent()

    if agent._personal_loaded:
        print("[OK] 已读取个人情况文件\n")
    else:
        print("[!] personal_info folder is empty. Add your resume for better recommendations.\n")

    while True:
        try:
            user_input = input("你：").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n再见！")
            break

        if not user_input:
            continue
        if user_input == "退出":
            print("再见！")
            break
        if user_input == "重置":
            agent.reset()
            continue

        print()
        reply = agent.chat(user_input)
        print(f"\n助手：{reply}\n")


if __name__ == "__main__":
    main()
