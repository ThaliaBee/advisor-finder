import os
import re
import atexit
from duckduckgo_search import DDGS
from playwright.sync_api import sync_playwright, Browser, BrowserContext

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "results")
PERSONAL_DIR = os.path.join(BASE_DIR, "personal_info")

# 模块级浏览器单例：启动一次，整个程序复用，退出时自动关闭
_pw = None
_browser: Browser = None
_context: BrowserContext = None


def _get_browser_context() -> BrowserContext:
    global _pw, _browser, _context
    if _context is None:
        _pw = sync_playwright().start()
        _browser = _pw.chromium.launch(headless=True)
        _context = _browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            ),
            ignore_https_errors=True,
        )
        atexit.register(_close_browser)
    return _context


def _close_browser():
    global _pw, _browser, _context
    try:
        if _context:
            _context.close()
        if _browser:
            _browser.close()
        if _pw:
            _pw.stop()
    except Exception:
        pass


def read_personal_files() -> str:
    """启动时读取个人情况文件夹（内部使用，不暴露给模型）"""
    if not os.path.exists(PERSONAL_DIR):
        os.makedirs(PERSONAL_DIR)
        return "（personal_info 文件夹为空，请放入简历或个人陈述文件）"

    texts = []
    for filename in os.listdir(PERSONAL_DIR):
        filepath = os.path.join(PERSONAL_DIR, filename)
        try:
            if filename.endswith((".txt", ".md")):
                with open(filepath, "r", encoding="utf-8") as f:
                    texts.append(f"【{filename}】\n{f.read()}")
            elif filename.endswith(".pdf"):
                from pypdf import PdfReader
                reader = PdfReader(filepath)
                content = "\n".join(page.extract_text() or "" for page in reader.pages)
                texts.append(f"【{filename}】\n{content}")
            elif filename.endswith(".docx"):
                from docx import Document
                doc = Document(filepath)
                content = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
                texts.append(f"【{filename}】\n{content}")
        except Exception as e:
            texts.append(f"【{filename}】读取失败：{e}")

    if not texts:
        return "（personal_info 文件夹为空，请放入简历或个人陈述文件）"
    return "\n\n".join(texts)


def search_web(query: str, max_results: int = 6) -> str:
    """搜索互联网，获取导师信息、论文、评价等"""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        if not results:
            return "没有找到相关结果。"
        output = []
        for i, r in enumerate(results, 1):
            output.append(f"[{i}] {r['title']}\n链接：{r['href']}\n{r['body']}")
        return "\n\n".join(output)
    except Exception as e:
        return f"搜索出错：{e}"


def fetch_webpage(url: str) -> str:
    """
    用真实浏览器获取网页内容和链接，支持 JavaScript 渲染的页面。
    返回页面文本和链接列表，同时标注名字验证用的原始文本。
    """
    try:
        ctx = _get_browser_context()
        page = ctx.new_page()
        try:
            page.goto(url, timeout=20000, wait_until="domcontentloaded")
            page.wait_for_timeout(1500)  # 等待 JS 渲染完成

            # 提取正文文本
            raw_text = page.inner_text("body")
            lines = [l.strip() for l in raw_text.splitlines() if len(l.strip()) > 8]
            text = "\n".join(lines)
            if len(text) > 6000:
                text = text[:6000] + "\n\n[...页面内容过长，已截断]"

            # 提取链接
            link_elements = page.eval_on_selector_all(
                "a[href]",
                "els => els.map(a => ({text: a.innerText.trim(), href: a.href}))"
            )
            links = [
                f"{el['text']}: {el['href']}"
                for el in link_elements
                if el.get("text") and el.get("href", "").startswith("http")
            ]
            links_text = "\n".join(links[:50]) if links else "（未找到链接）"

        finally:
            page.close()

        return (
            f"=== 页面文本（可用于验证人名是否真实存在）===\n{text}\n\n"
            f"=== 页面链接（前50条）===\n{links_text}"
        )
    except Exception as e:
        return f"获取网页失败：{e}"


def save_file(relative_path: str, content: str) -> str:
    """
    保存内容到推荐结果目录，同时生成 .md 和 .txt 两个版本。
    relative_path 示例：'北京大学/推荐导师.md' 或 '北京大学/张三/详细资料.md'
    """
    full_path = os.path.join(OUTPUT_DIR, relative_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

    txt_content = re.sub(r"#{1,6}\s*", "", content)
    txt_content = re.sub(r"\*{1,2}(.+?)\*{1,2}", r"\1", txt_content)
    txt_content = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", txt_content)
    txt_content = re.sub(r"`(.+?)`", r"\1", txt_content)
    txt_path = os.path.splitext(full_path)[0] + ".txt"
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(txt_content)

    return f"已保存：\n  格式版：{full_path}\n  纯文本：{txt_path}"


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "用关键词搜索互联网，适合查找导师论文、网络评价、招生信息等",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "搜索关键词"},
                    "max_results": {"type": "integer", "description": "返回结果数，默认6", "default": 6}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_webpage",
            "description": (
                "用真实浏览器获取网页内容和链接，支持 JS 渲染页面。"
                "获取到内容后，只推荐名字在页面文本中明确出现的导师，不得凭记忆补充。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "要访问的完整网址"}
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "save_file",
            "description": "将内容保存为 Markdown 文件，同时生成纯文本版本",
            "parameters": {
                "type": "object",
                "properties": {
                    "relative_path": {"type": "string", "description": "文件路径，如 '北京大学/推荐导师.md'"},
                    "content": {"type": "string", "description": "文件内容（Markdown 格式）"}
                },
                "required": ["relative_path", "content"]
            }
        }
    }
]

TOOL_MAP = {
    "search_web": search_web,
    "fetch_webpage": fetch_webpage,
    "save_file": save_file,
}
