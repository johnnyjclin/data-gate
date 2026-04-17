"""
llm.py — 使用 GitHub Models GPT-4o 將字幕轉為結構化 Markdown

使用 GitHub Models API（免費，用 GitHub Token 驗證）：
  endpoint: https://models.inference.ai.azure.com
  model:    gpt-4o
"""
import os
from openai import OpenAI


def get_client() -> OpenAI:
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise EnvironmentError("請設定 GITHUB_TOKEN 環境變數")
    return OpenAI(
        base_url="https://models.inference.ai.azure.com",
        api_key=token,
    )


SYSTEM_PROMPT = """你是一位專業的知識整理助手。
你的工作是將 YouTube 影片的逐字稿整理成結構清晰的 Markdown 知識文件。
請用繁體中文輸出（原文若為英文則翻譯或雙語並列）。"""

USER_PROMPT_TEMPLATE = """以下是影片資訊與逐字稿，請整理成 Markdown 文件。

## 影片資訊
- 標題：{title}
- 頻道：{channel}
- 時長：{duration}
- 發佈日期：{published}
- 來源：{url}

## 逐字稿
{transcript}

---

請輸出以下格式的 Markdown（不要輸出任何 frontmatter，我會另外加）：

# {title}

## 摘要
（2-4 句話總結本集核心內容）

## 重點整理
（用條列式整理 5-10 個核心觀念或論點，每點一句話）

## 詳細筆記
（依主題分段，每段有小標題，條列重要內容）

## 關鍵詞
（列出 5-10 個關鍵字或專有名詞，用逗號分隔）

## 完整逐字稿
（保留原始逐字稿，加上段落分隔，不需要時間碼）
"""


def transcript_to_markdown(
    title: str,
    channel: str,
    duration: str,
    published: str,
    url: str,
    transcript: str,
    model: str | None = None,
) -> tuple[str, list[str]]:
    """
    將逐字稿轉為結構化 Markdown 主體內容。
    回傳 (markdown_body, tags_list)
    """
    client = get_client()
    used_model = model or os.environ.get("LLM_MODEL", "gpt-4o")

    prompt = USER_PROMPT_TEMPLATE.format(
        title=title,
        channel=channel,
        duration=duration,
        published=published,
        url=url,
        transcript=transcript[:12000],  # 避免超過 token 限制
    )

    response = client.chat.completions.create(
        model=used_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
        max_tokens=4096,
    )

    body = response.choices[0].message.content.strip()

    # 從「關鍵詞」段落提取 tags
    tags = _extract_tags(body)

    return body, tags


def _extract_tags(markdown: str) -> list[str]:
    """從 Markdown 內容中提取關鍵詞作為 tags"""
    import re
    match = re.search(r"##\s*關鍵詞\s*\n(.+)", markdown)
    if not match:
        return []
    raw = match.group(1).strip()
    # 支援逗號或頓號分隔
    tags = [t.strip().strip("、").strip() for t in re.split(r"[,，、]", raw) if t.strip()]
    return tags[:10]
