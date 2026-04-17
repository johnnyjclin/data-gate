"""
youtube.py — 從 YouTube 影片取得字幕與影片資訊

使用 youtube-transcript-api（不需要 cookie / yt-dlp）直接呼叫 YouTube 內部 transcript API。
影片基本資訊（標題、頻道）透過 YouTube oEmbed 端點取得（無需驗證）。
"""
import re
import requests
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound


_LANG_PRIORITY = ["zh-TW", "zh-Hant", "zh-Hans", "zh", "en"]


def _extract_video_id(url: str) -> str:
    match = re.search(r"[?&]v=([a-zA-Z0-9_-]{11})", url)
    if match:
        return match.group(1)
    match = re.search(r"youtu\.be/([a-zA-Z0-9_-]{11})", url)
    if match:
        return match.group(1)
    raise ValueError(f"無法從 URL 取得 video ID：{url}")


def get_video_info(url: str) -> dict:
    """透過 oEmbed API 取得影片標題與頻道名稱（不需驗證）"""
    video_id = _extract_video_id(url)
    oembed_url = (
        f"https://www.youtube.com/oembed"
        f"?url=https://www.youtube.com/watch?v={video_id}&format=json"
    )
    resp = requests.get(oembed_url, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    return {
        "id": video_id,
        "title": data.get("title", "Untitled"),
        "channel": data.get("author_name", "Unknown"),
        "uploader": data.get("author_name", "Unknown"),
        "duration": 0,
        "upload_date": "",
    }


def get_transcript(url: str, tmp_dir: str = None) -> str | None:
    """
    取得字幕文字。優先使用人工字幕，其次自動字幕。
    直接呼叫 YouTube transcript API，不需要 yt-dlp 或 cookie。
    """
    video_id = _extract_video_id(url)
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        # 先找人工字幕
        for lang in _LANG_PRIORITY:
            try:
                t = transcript_list.find_manually_created_transcript([lang])
                return _format_segments(t.fetch())
            except NoTranscriptFound:
                continue

        # 再找自動字幕
        for lang in _LANG_PRIORITY:
            try:
                t = transcript_list.find_generated_transcript([lang])
                return _format_segments(t.fetch())
            except NoTranscriptFound:
                continue

        # last resort：取任何可用字幕
        try:
            t = next(iter(transcript_list))
            return _format_segments(t.fetch())
        except StopIteration:
            pass

    except TranscriptsDisabled:
        print("⚠️  此影片已停用字幕")
    except Exception as e:
        print(f"⚠️  取得字幕失敗：{e}")

    return None


def _format_segments(segments) -> str:
    """將 transcript segments 轉為去重複的純文字"""
    seen: set[str] = set()
    lines = []
    for seg in segments:
        text = seg["text"].strip().replace("\n", " ") if isinstance(seg, dict) else seg.text.strip().replace("\n", " ")
        if text and text not in seen:
            seen.add(text)
            lines.append(text)
    return "\n".join(lines)
