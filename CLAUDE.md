# DataGate — Claude Code 操作指南

DataGate 是一個本地知識庫工具，將 YouTube 影片字幕透過 LLM 整理為結構化 Markdown 文章，並用 MkDocs 在本地瀏覽。

## 環境設定

```bash
pip install -r requirements.txt
cp .env.example .env   # 填入 GITHUB_TOKEN
```

`.env` 需要：
```
GITHUB_TOKEN=ghp_xxxx   # GitHub Models API（免費 GPT-4o）
LLM_MODEL=gpt-4o-mini
```

## 可用指令

### 解析單支影片
```bash
python pipeline/ingest.py --url "https://www.youtube.com/watch?v=VIDEO_ID"
python pipeline/ingest.py --url "..." --channel my-channel   # 指定頻道 slug
python pipeline/ingest.py --url "..." --dry-run              # 預覽不寫檔
```

### 訂閱頻道（RSS 自動追蹤）
```bash
python pipeline/add_channel.py --url "https://www.youtube.com/@ChannelName"
```

### 手動 RSS 輪詢（抓所有訂閱頻道的新影片）
```bash
python pipeline/rss_poller.py
```

### 本地預覽網站
```bash
mkdocs serve
# 瀏覽 http://127.0.0.1:8000
```

## 專案結構

```
pipeline/
  ingest.py        # 主入口：URL → 字幕 → LLM → Markdown
  youtube.py       # youtube-transcript-api 取字幕 + oEmbed 取影片資訊
  llm.py           # GitHub Models GPT-4o 整理逐字稿
  add_channel.py   # 註冊頻道 + 建立 channels.json 記錄
  rss_poller.py    # 輪詢所有頻道 RSS，自動 ingest 新影片
docs/
  channels/        # 每個頻道一個資料夾，內含各集 .md
data/
  channels.json    # 訂閱頻道清單
```

## 注意事項

- 影片需有字幕（人工或自動生成），否則會跳過
- `GITHUB_TOKEN` 每日免費額度 150 次 LLM 呼叫
- 解析後執行 `git add . && git commit -m "add: ..."` 儲存

## Claude Code Slash Commands

使用 `/project:ingest`、`/project:subscribe`、`/project:poll`、`/project:serve` 快速執行操作。
