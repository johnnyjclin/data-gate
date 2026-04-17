"""
add_channel.py — 登錄新頻道到知識庫，設定 RSS 監聽

用法：
  python pipeline/add_channel.py --slug xrex --name "XREX" --rss "https://www.youtube.com/feeds/videos.xml?channel_id=UCxxx"
  python pipeline/add_channel.py --slug xrex --name "XREX" --youtube-channel-id UCxxx
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent.parent
CHANNELS_FILE = ROOT / "data" / "channels.json"
DOCS_DIR = ROOT / "docs" / "channels"


def youtube_rss_from_channel_id(channel_id: str) -> str:
    return f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"


def load_channels() -> dict:
    if CHANNELS_FILE.exists():
        return json.loads(CHANNELS_FILE.read_text(encoding="utf-8"))
    return {"channels": []}


def save_channels(data: dict):
    CHANNELS_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def create_channel_index(slug: str, name: str, description: str):
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


def main():
    parser = argparse.ArgumentParser(description="登錄新頻道")
    parser.add_argument("--slug", required=True, help="頻道代號（英數小寫，e.g. xrex）")
    parser.add_argument("--name", required=True, help="頻道顯示名稱")
    parser.add_argument("--rss", default=None, help="RSS feed URL")
    parser.add_argument("--youtube-channel-id", default=None, help="YouTube Channel ID (UCxxx)")
    parser.add_argument("--description", default="", help="頻道描述")
    args = parser.parse_args()

    rss_url = args.rss
    if not rss_url and args.youtube_channel_id:
        rss_url = youtube_rss_from_channel_id(args.youtube_channel_id)
    if not rss_url:
        print("❌ 請提供 --rss 或 --youtube-channel-id")
        sys.exit(1)

    data = load_channels()

    # 檢查是否已存在
    for ch in data["channels"]:
        if ch["slug"] == args.slug:
            print(f"⚠️  頻道 '{args.slug}' 已存在，更新 RSS URL")
            ch["rss_url"] = rss_url
            ch["name"] = args.name
            save_channels(data)
            print(f"✅ 已更新：{args.slug}")
            return

    new_channel = {
        "slug": args.slug,
        "name": args.name,
        "rss_url": rss_url,
        "description": args.description,
        "added_at": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "last_checked": None,
        "last_video_id": None,
    }
    data["channels"].append(new_channel)
    save_channels(data)

    create_channel_index(args.slug, args.name, args.description)

    print(f"\n🎉 頻道已登錄：{args.name} ({args.slug})")
    print(f"   RSS：{rss_url}")
    print(f"\n   下一步（手動 seed 既有影片）：")
    print(f"   python pipeline/ingest.py --url <youtube_url> --channel {args.slug}")


if __name__ == "__main__":
    main()
