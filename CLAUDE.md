# DataGate — Claude Code 操作指南

DataGate 是一個本地知識庫工具，將 YouTube 影片字幕透過 LLM 整理為結構化 Markdown 文章，並用 MkDocs 在本地瀏覽。

生成的文章只存本機（`docs/channels/` 已加入 `.gitignore`），不會上傳 Git。

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

### 解析單支影片（ingest）
```bash
python pipeline/ingest.py --url "https://www.youtube.com/watch?v=VIDEO_ID"
python pipeline/ingest.py --url "..." --channel my-channel   # 指定頻道 slug
python pipeline/ingest.py --url "..." --dry-run              # 預覽不寫檔
```
- 影片已存在時自動跳過

### 訂閱頻道（subscribe）
```bash
python pipeline/add_channel.py --url "https://www.youtube.com/@ChannelName"
python pipeline/add_channel.py --url "https://www.youtube.com/feeds/videos.xml?channel_id=UCxxx"
python pipeline/add_channel.py --url "..." --slug custom-slug --name "自訂名稱"
```
- 支援 YouTube 頻道 URL 或 RSS feed URL
- 自動偵測頻道名稱與 channel ID

### 手動 RSS 輪詢（poll）
```bash
python pipeline/rss_poller.py
```
- 比對 docs/channels/ 下已有的影片 ID，只抓新影片

### 本地預覽網站
```bash
mkdocs serve
# 瀏覽 http://127.0.0.1:8000
```

## 專案結構

```
pipeline/
  ingest.py        # 主入口：URL → 字幕 → LLM → Markdown
  youtube.py       # yt-dlp 下載字幕 + 取影片資訊
  llm.py           # GitHub Models GPT-4o 整理逐字稿
  add_channel.py   # 訂閱頻道 + 建立 RSS 追蹤
  rss_poller.py    # 輪詢所有頻道 RSS，自動 ingest 新影片
docs/
  channels/        # 每個頻道一個資料夾，內含各集 .md（本地不上傳）
data/
  channels.json    # 訂閱頻道清單
```

## 注意事項

- docs/channels/ 下的內容只存本機，不上傳 Git
- 影片需有字幕（人工或自動生成），否則跳過
- GITHUB_TOKEN 每日免費額度 150 次 LLM 呼叫
- 重複影片自動偵測跳過
