"""
ingest.py — 主入口：接收 YouTube URL，執行完整 parsing pipeline

用法：
  python pipeline/ingest.py --url "https://youtube.com/watch?v=xxx"
  python pipeline/ingest.py --url "https://youtube.com/watch?v=xxx" --channel xrex
  python pipeline/ingest.py --url "https://youtube.com/watch?v=xxx" --channel xrex --dry-run
"""
import argparse
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

# 載入 .env
load_dotenv()

# 確保 pipeline/ 在 import 路徑
sys.path.insert(0, str(Path(__file__).parent))

from youtube import get_video_info, get_transcript
from llm import transcript_to_markdown

# 專案根目錄
ROOT = Path(__file__).parent.parent
DOCS_DIR = ROOT / "docs" / "channels"
DATA_DIR = ROOT / "data"
CHANNELS_FILE = DATA_DIR / "channels.json"


def load_channels() -> dict:
    if CHANNELS_FILE.exists():
        return json.loads(CHANNELS_FILE.read_text())
    return {"channels": []}


def get_channel_slug(channel_name: str, explicit_slug: str | None) -> str:
    """決定頻道 slug：優先使用指定值，否則用頻道名稱轉小寫"""
    if explicit_slug:
        return explicit_slug.lower().replace(" ", "-")
    # 嘗試從已知頻道比對
    data = load_channels()
    for ch in data["channels"]:
        if ch["name"].lower() == channel_name.lower():
            return ch["slug"]
    # fallback：直接用頻道名稱
    return channel_name.lower().replace(" ", "-").replace("/", "-")


def seconds_to_hms(seconds: int) -> str:
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    if h:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def build_frontmatter(
    title: str,
    channel: str,
    slug: str,
    url: str,
    published: str,
    duration: str,
    video_id: str,
    tags: list[str],
) -> str:
    tags_yaml = "\n".join(f"  - {t}" for t in tags) if tags else "  []"
    return f"""---
title: "{title.replace('"', "'")}"
channel: "{channel}"
channel_slug: "{slug}"
source: "{url}"
video_id: "{video_id}"
published: {published}
duration: "{duration}"
parsed_at: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}
tags:
{tags_yaml}
---

"""


def save_markdown(slug: str, video_id: str, content: str, dry_run: bool) -> Path:
    channel_dir = DOCS_DIR / slug
    channel_dir.mkdir(parents=True, exist_ok=True)
    output_path = channel_dir / f"{video_id}.md"

    if dry_run:
        print(f"\n[dry-run] 將寫入：{output_path}")
        print("=" * 60)
        print(content[:2000])
        print("... (truncated)")
        return output_path

    output_path.write_text(content, encoding="utf-8")
    print(f"✅ 已儲存：{output_path}")
    return output_path


def update_channel_index(slug: str, title: str, video_id: str, published: str, summary: str):
    """更新頻道的 index.md，將新集數加入列表"""
    channel_dir = DOCS_DIR / slug
    index_path = channel_dir / "index.md"

    entry = f"- [{title}]({video_id}.md) `{published}`\n"

    if not index_path.exists():
        index_path.write_text(
            f"# {slug.upper()} 知識庫\n\n## 所有集數\n\n{entry}",
            encoding="utf-8",
        )
    else:
        content = index_path.read_text(encoding="utf-8")
        if video_id not in content:
            # 插到「## 所有集數」區塊後的第一行
            content = content.replace("## 所有集數\n\n", f"## 所有集數\n\n{entry}")
            index_path.write_text(content, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="DataGate ingest pipeline")
    parser.add_argument("--url", required=True, help="YouTube 影片網址")
    parser.add_argument("--channel", default=None, help="頻道 slug（選填，自動偵測）")
    parser.add_argument("--dry-run", action="store_true", help="預覽輸出，不寫入檔案")
    args = parser.parse_args()

    # 清理 URL：移除 shell escape 殘留的反斜線
    url = args.url.replace("\\", "")

    # 驗證是影片 URL（不接受頻道首頁）
    import re
    if not re.search(r"[?&]v=([a-zA-Z0-9_-]{11})", url) and "youtu.be/" not in url:
        print(f"❌ 不是有效的影片 URL：{url}")
        print("   請傳入單支影片網址，例如：")
        print("   python pipeline/ingest.py --url 'https://www.youtube.com/watch?v=VIDEO_ID'")
        sys.exit(1)

    print(f"🔍 取得影片資訊：{url}")
    info = get_video_info(url)

    video_id = info.get("id", "unknown")
    title = info.get("title", "Untitled")
    channel_name = info.get("channel", info.get("uploader", "Unknown"))
    duration_sec = info.get("duration", 0)
    duration = seconds_to_hms(int(duration_sec))
    upload_date = info.get("upload_date", "")  # YYYYMMDD
    published = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:]}" if len(upload_date) == 8 else datetime.now().strftime("%Y-%m-%d")

    slug = get_channel_slug(channel_name, args.channel)

    print(f"📺 影片：{title}")
    print(f"📡 頻道：{channel_name} (slug: {slug})")
    print(f"⏱  時長：{duration}")

    with tempfile.TemporaryDirectory() as tmp_dir:
        print("📝 嘗試取得字幕...")
        transcript = get_transcript(url, tmp_dir)

    if not transcript:
        print("⚠️  找不到字幕，跳過此影片（可手動加 Whisper 支援）")
        sys.exit(1)

    print(f"✅ 取得字幕（{len(transcript)} 字）")
    print("🤖 LLM 整理中...")

    body, tags = transcript_to_markdown(
        title=title,
        channel=channel_name,
        duration=duration,
        published=published,
        url=url,
        transcript=transcript,
    )

    frontmatter = build_frontmatter(
        title=title,
        channel=channel_name,
        slug=slug,
        url=url,
        published=published,
        duration=duration,
        video_id=video_id,
        tags=tags,
    )

    full_content = frontmatter + body

    output_path = save_markdown(slug, video_id, full_content, args.dry_run)

    if not args.dry_run:
        update_channel_index(slug, title, video_id, published, "")
        print(f"\n🎉 完成！")
        print(f"   檔案：{output_path.relative_to(ROOT)}")
        print(f"   標籤：{', '.join(tags)}")
        print(f"\n   下一步：git add . && git commit -m 'add: {title}' && git push")


if __name__ == "__main__":
    main()
