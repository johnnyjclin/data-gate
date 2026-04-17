"""
add_channel.py — 訂閱 YouTube 頻道，加入 RSS 追蹤清單

用法：
  python pipeline/add_channel.py --url "https://www.youtube.com/@ChannelName"
  python pipeline/add_channel.py --url "https://www.youtube.com/feeds/videos.xml?channel_id=UCxxx"
  python pipeline/add_channel.py --url "..." --slug custom-slug --name "自訂名稱"
"""
import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import feedparser

ROOT = Path(__file__).parent.parent
CHANNELS_FILE = ROOT / "data" / "channels.json"
DOCS_DIR = ROOT / "docs" / "channels"


def load_channels() -> dict:
    if CHANNELS_FILE.exists():
        return json.loads(CHANNELS_FILE.read_text(encoding="utf-8"))
    return {"channels": []}


def save_channels(data: dict):
    CHANNELS_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def is_rss_url(url: str) -> bool:
    """判斷是否為 YouTube RSS feed URL"""
    return "feeds/videos.xml" in url


def resolve_from_rss(url: str) -> dict:
    """從 RSS feed URL 解析頻道資訊"""
    feed = feedparser.parse(url)
    name = feed.feed.get("title", "Unknown")
    match = re.search(r"channel_id=([^&]+)", url)
    channel_id = match.group(1) if match else None
    return {"channel_id": channel_id, "name": name, "rss_url": url}


def resolve_from_channel_url(url: str) -> dict:
    """從 YouTube 頻道頁面 URL 取得頻道資訊（使用 yt-dlp）"""
    result = subprocess.run(
        [
            "yt-dlp",
            "--print", "channel_id",
            "--print", "channel",
            "--playlist-items", "1",
            "--no-download",
            url,
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"yt-dlp 無法解析頻道：{url}\n{result.stderr[:500]}"
        )

    lines = result.stdout.strip().split("\n")
    if len(lines) < 2:
        raise RuntimeError(f"無法從 URL 取得頻道資訊：{url}")

    channel_id = lines[0].strip()
    name = lines[1].strip()
    rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    return {"channel_id": channel_id, "name": name, "rss_url": rss_url}


def make_slug(name: str) -> str:
    """從頻道名稱產生 slug"""
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def create_channel_index(slug: str, name: str, description: str = ""):
    """建立頻道的 docs/channels/{slug}/index.md"""
    channel_dir = DOCS_DIR / slug
    channel_dir.mkdir(parents=True, exist_ok=True)
    index_path = channel_dir / "index.md"
    if not index_path.exists():
        index_path.write_text(
            f"# {name} 知識庫\n\n{description}\n\n## 所有集數\n\n",
            encoding="utf-8",
        )
        print(f"✅ 建立頻道首頁：{index_path.relative_to(ROOT)}")


def update_channels_index(slug: str, name: str):
    """更新 docs/channels/index.md 頻道列表"""
    index_path = DOCS_DIR / "index.md"
    if not index_path.exists():
        return

    content = index_path.read_text(encoding="utf-8")
    entry = f"- [{name}]({slug}/index.md)\n"

    if slug not in content:
        content = content.rstrip() + "\n" + entry
        index_path.write_text(content, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="訂閱 YouTube 頻道")
    parser.add_argument("--url", required=True, help="YouTube 頻道 URL 或 RSS feed URL")
    parser.add_argument("--slug", default=None, help="頻道代號（選填，自動偵測）")
    parser.add_argument("--name", default=None, help="頻道顯示名稱（選填，自動偵測）")
    parser.add_argument("--description", default="", help="頻道描述（選填）")
    args = parser.parse_args()

    url = args.url.strip()

    # 解析頻道資訊
    print(f"🔍 解析頻道：{url}")
    if is_rss_url(url):
        info = resolve_from_rss(url)
    else:
        info = resolve_from_channel_url(url)

    rss_url = info["rss_url"]
    name = args.name or info["name"]
    slug = args.slug or make_slug(name)

    data = load_channels()

    # 檢查是否已存在
    for ch in data["channels"]:
        if ch["slug"] == slug:
            print(f"⚠️  頻道 '{slug}' 已存在，更新 RSS URL")
            ch["rss_url"] = rss_url
            ch["name"] = name
            save_channels(data)
            print(f"✅ 已更新：{slug}")
            return

    new_channel = {
        "slug": slug,
        "name": name,
        "rss_url": rss_url,
        "description": args.description,
        "added_at": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "last_checked": None,
        "last_video_id": None,
    }
    data["channels"].append(new_channel)
    save_channels(data)

    create_channel_index(slug, name, args.description)
    update_channels_index(slug, name)

    print(f"\n🎉 頻道已訂閱：{name} ({slug})")
    print(f"   RSS：{rss_url}")
    print(f"\n   下一步：執行 poll 拉取最新影片")


if __name__ == "__main__":
    main()
