"""
youtube.py — 從 YouTube 影片取得字幕或音檔轉文字

優先順序：
1. 取得官方字幕（繁中 zh-TW → 簡中 zh-Hans → 英文 en）
2. 若無字幕，取得自動字幕（auto-generated）
3. 若皆無，回傳 None（ingest.py 可選擇跳過或用 Whisper）
"""
import subprocess
import json
import os
import tempfile
from pathlib import Path


def get_video_info(url: str) -> dict:
    """取得影片基本資訊（標題、頻道、時長、發佈日期）"""
    result = subprocess.run(
        [
            "yt-dlp",
            "--dump-json",
            "--no-download",
            url,
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


def get_transcript(url: str, tmp_dir: str) -> str | None:
    """
    嘗試下載字幕，回傳純文字字幕內容。
    優先使用人工字幕，其次自動字幕。
    """
    subtitle_langs = ["zh-TW", "zh-Hant", "zh-Hans", "zh", "en"]

    # 先嘗試人工字幕
    for lang in subtitle_langs:
        transcript = _download_subtitle(url, tmp_dir, lang, auto=False)
        if transcript:
            return transcript

    # 再嘗試自動字幕
    for lang in subtitle_langs:
        transcript = _download_subtitle(url, tmp_dir, lang, auto=True)
        if transcript:
            return transcript

    return None


def _download_subtitle(url: str, tmp_dir: str, lang: str, auto: bool) -> str | None:
    """下載特定語言字幕並轉為純文字，失敗則回傳 None"""
    flag = "--write-auto-subs" if auto else "--write-subs"
    result = subprocess.run(
        [
            "yt-dlp",
            flag,
            "--sub-langs", lang,
            "--sub-format", "vtt",
            "--skip-download",
            "--output", os.path.join(tmp_dir, "subtitle"),
            url,
        ],
        capture_output=True,
        text=True,
    )

    # 找到下載的 .vtt 檔
    vtt_files = list(Path(tmp_dir).glob("*.vtt"))
    if not vtt_files:
        return None

    raw = vtt_files[0].read_text(encoding="utf-8")
    return _vtt_to_text(raw)


def _vtt_to_text(vtt: str) -> str:
    """將 WebVTT 格式轉為純文字，去除時間碼和重複行"""
    lines = []
    seen = set()
    for line in vtt.splitlines():
        line = line.strip()
        # 跳過 WebVTT header、時間碼行、空行
        if (
            not line
            or line.startswith("WEBVTT")
            or line.startswith("NOTE")
            or "-->" in line
            or line.isdigit()
        ):
            continue
        # 去除 HTML 標籤（<c>, <00:00:00.000> 等）
        import re
        line = re.sub(r"<[^>]+>", "", line).strip()
        if line and line not in seen:
            seen.add(line)
            lines.append(line)

    return "\n".join(lines)
