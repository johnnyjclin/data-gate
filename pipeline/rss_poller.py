"""
rss_poller.py — 檢查所有訂閱頻道 RSS，自動 ingest 新影片

執行方式：
  python pipeline/rss_poller.py          # 手動或由 Claude 觸發

流程：
  1. 讀取 data/channels.json 中所有頻道
  2. 拉取各頻道 RSS feed
  3. 比對 docs/channels/{slug}/ 下已有的影片 ID，找出新集數
  4. 呼叫 ingest pipeline 處理新集數
  5. 更新 channels.json 的 last_video_id 與 last_checked
"""
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import feedparser
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).parent.parent
CHANNELS_FILE = ROOT / "data" / "channels.json"
DOCS_DIR = ROOT / "docs" / "channels"


def load_channels() -> dict:
    return json.loads(CHANNELS_FILE.read_text(encoding="utf-8"))


def save_channels(data: dict):
    CHANNELS_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def extract_video_id(entry) -> str | None:
    """從 RSS entry 提取 YouTube video ID"""
    # YouTube RSS 格式：yt:video:VIDEO_ID
    vid = entry.get("yt_videoid") or entry.get("id", "")
    if ":" in vid:
        return vid.split(":")[-1]
    return vid or None


def get_new_entries(feed_url: str, last_video_id: str | None) -> list[dict]:
    """回傳 RSS 中比 last_video_id 更新的影片，最多 5 部（避免第一次爆量）"""
    feed = feedparser.parse(feed_url)
    entries = feed.entries

    if not entries:
        return []

    if last_video_id is None:
        # 首次執行：只取最新一部
        return entries[:1]

    new_entries = []
    for entry in entries:
        vid = extract_video_id(entry)
        if vid == last_video_id:
            break
        new_entries.append(entry)

    return new_entries[:5]  # 最多一次處理 5 部


def ingest_video(url: str, channel_slug: str) -> bool:
    """呼叫 ingest.py 處理單支影片，回傳是否成功"""
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "pipeline" / "ingest.py"),
            "--url", url,
            "--channel", channel_slug,
        ],
        capture_output=False,  # 直接輸出到 stdout，方便 Actions log 查看
    )
    return result.returncode == 0


def main():
    data = load_channels()
    channels = data.get("channels", [])

    if not channels:
        print("沒有已登錄的頻道，請先執行 add_channel.py")
        return

    total_new = 0

    for channel in channels:
        slug = channel["slug"]
        name = channel["name"]
        rss_url = channel["rss_url"]
        last_video_id = channel.get("last_video_id")

        print(f"\n📡 檢查頻道：{name} ({slug})")
        print(f"   RSS：{rss_url}")

        new_entries = get_new_entries(rss_url, last_video_id)

        if not new_entries:
            print("   ✅ 無新影片")
            channel["last_checked"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            continue

        print(f"   🆕 發現 {len(new_entries)} 部新影片")

        for entry in reversed(new_entries):  # 從舊到新處理
            video_id = extract_video_id(entry)
            title = entry.get("title", video_id)
            url = f"https://www.youtube.com/watch?v={video_id}"

            # 檢查是否已存在（跳過重複）
            existing_path = DOCS_DIR / slug / f"{video_id}.md"
            if existing_path.exists():
                print(f"   ⏭ 已存在，跳過：{video_id}")
                channel["last_video_id"] = video_id
                continue

            print(f"\n   ▶ 處理：{title}")
            success = ingest_video(url, slug)

            if success:
                channel["last_video_id"] = video_id
                total_new += 1
            else:
                print(f"   ⚠️  ingest 失敗，跳過：{title}")

        channel["last_checked"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    save_channels(data)
    print(f"\n🎉 RSS 輪詢完成，共處理 {total_new} 部新影片")


if __name__ == "__main__":
    main()
