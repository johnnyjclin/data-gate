# DataGate

> 將 YouTube 影音內容自動轉化為結構化 Markdown 知識庫，透過 Claude 操作，本地 MkDocs 瀏覽。

---

## 這是什麼？

DataGate 是一個本地知識庫工具。你丟一個 YouTube 影片連結，它會：

1. 用 **yt-dlp** 自動下載字幕（支援中文、英文，人工或自動字幕）
2. 用 **GPT-4o** 整理成結構化 Markdown（摘要、重點、逐字稿）
3. 寫入本地 `docs/channels/` 目錄
4. 透過 **MkDocs** 在本機瀏覽知識庫

所有生成的 Markdown 文章只存在本機（`docs/channels/` 已加入 `.gitignore`），**不會上傳至 Git**。

**Pipeline：**
```
YouTube URL
  → yt-dlp 下載字幕
  → GPT-4o 結構化整理
  → Markdown 寫入 docs/channels/
  → mkdocs serve 本地瀏覽
```

---

## 快速開始

### 1. 安裝

```bash
git clone https://github.com/johnnyjclin/data-gate.git
cd data-gate
pip install -r requirements.txt
```

### 2. 設定 API Token

```bash
cp .env.example .env
```

編輯 `.env`，填入你的 GitHub Personal Access Token（用於呼叫 GitHub Models GPT-4o）：

```env
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
LLM_MODEL=gpt-4o-mini
```

> 取得 Token：GitHub → Settings → Developer settings → Personal access tokens

### 3. 確認 yt-dlp 已安裝

```bash
brew install yt-dlp   # macOS
# 或 pip install yt-dlp
```

---

## 使用方式（Claude 操作）

所有操作以 Claude 為主。在 Claude Code 中使用 slash commands：

| Command | 功能 |
|---|---|
| `/project:ingest` | 解析單支 YouTube 影片 |
| `/project:subscribe` | 訂閱 YouTube 頻道（RSS）|
| `/project:poll` | 拉取所有訂閱頻道新影片 |
| `/project:serve` | 啟動本地預覽網站 |

### 範例對話

```
解析這支影片 https://www.youtube.com/watch?v=VIDEO_ID

訂閱這個頻道 https://www.youtube.com/@ChannelName

執行 poll 抓最新影片

啟動 mkdocs 預覽
```

---

## 手動指令

### 解析單支影片（ingest）

```bash
python pipeline/ingest.py --url "https://www.youtube.com/watch?v=VIDEO_ID"
python pipeline/ingest.py --url "..." --channel my-channel  # 指定頻道 slug
python pipeline/ingest.py --url "..." --dry-run              # 預覽不寫檔
```

- 自動下載字幕（優先人工字幕，其次自動字幕）
- 用 GPT-4o 整理為結構化 Markdown
- 存入 `docs/channels/{slug}/{video_id}.md`
- **如果該影片已存在，自動跳過**

### 訂閱頻道（subscribe）

```bash
python pipeline/add_channel.py --url "https://www.youtube.com/@ChannelName"
python pipeline/add_channel.py --url "https://www.youtube.com/feeds/videos.xml?channel_id=UCxxx"
python pipeline/add_channel.py --url "..." --slug custom-slug --name "自訂名稱"
```

- 支援 YouTube 頻道 URL 或直接輸入 RSS feed URL
- 自動偵測頻道名稱、建立 RSS 追蹤
- 將頻道資訊寫入 `data/channels.json`
- 建立 `docs/channels/{slug}/` 目錄

### RSS 輪詢（poll）

```bash
python pipeline/rss_poller.py
```

- 讀取 `data/channels.json` 中所有訂閱頻道
- 拉取 RSS feed，比對已有影片 ID
- 新影片自動執行 ingest pipeline
- 每個頻道每次最多處理 5 支新影片
- 已存在的影片自動跳過

### 本地預覽網站

```bash
mkdocs serve
# 瀏覽 http://127.0.0.1:8000
```

---

## 專案結構

```
DataGate/
├── pipeline/
│   ├── ingest.py          # 主入口：URL → 字幕 → LLM → Markdown
│   ├── youtube.py         # yt-dlp 下載字幕 + 取影片資訊
│   ├── llm.py             # GitHub Models GPT-4o 結構化整理
│   ├── add_channel.py     # 訂閱頻道 + 建立 RSS 追蹤
│   └── rss_poller.py      # 輪詢所有頻道 RSS，自動 ingest
├── docs/
│   ├── index.md           # MkDocs 網站首頁
│   └── channels/          # 本地生成，不上傳 Git
│       └── {slug}/
│           ├── index.md   # 頻道首頁（集數列表）
│           └── {video_id}.md
├── data/
│   └── channels.json      # 訂閱頻道清單
├── .claude/
│   └── commands/          # Claude Code slash commands
├── scripts/
│   ├── poll.sh            # RSS 輪詢包裝腳本（選用）
│   └── com.datagate.poller.plist  # macOS 定時排程（選用）
├── mkdocs.yml             # MkDocs Material 設定
├── CLAUDE.md              # Claude Code 操作指南
└── requirements.txt
```

---

## 每篇文章的格式

每支影片自動生成包含以下段落的 Markdown：

| 段落 | 內容 |
|------|------|
| **摘要** | 2-4 句話的核心內容 |
| **重點整理** | 5-10 個條列式核心觀念 |
| **詳細筆記** | 依主題分段、有小標題 |
| **關鍵詞** | 自動提取作為 tags |
| **完整逐字稿** | 保留原始內容 |

---

## 注意事項

- `docs/channels/` 為本地生成內容，已加入 `.gitignore`，**不會上傳 Git**
- 影片需有字幕（人工或自動生成），否則跳過
- `GITHUB_TOKEN` 每日免費額度 150 次 LLM 呼叫
- 重複影片自動偵測跳過，不會重複處理

---

## 費用

| 項目 | 費用 |
|------|------|
| GitHub Models GPT-4o | 免費（150 req/day） |
| yt-dlp 字幕 | 免費 |
| MkDocs 本地瀏覽 | 免費 |
| **總計** | **$0** |

---

## Roadmap

### Phase 1 — 本地知識庫 ✅（目前）
- [x] YouTube URL → Markdown pipeline
- [x] yt-dlp 字幕擷取（中英文優先）
- [x] GitHub Models GPT-4o 結構化整理
- [x] MkDocs Material 本地知識庫（全文搜尋、標籤）
- [x] RSS 頻道訂閱與自動輪詢
- [x] 重複影片自動跳過
- [x] Claude Code slash commands 整合

### Phase 2 — 內容強化
- [ ] Whisper API fallback（無字幕影片 → 語音轉文字）
- [ ] 支援音檔直接輸入（Podcast MP3）
- [ ] 多語言字幕自動翻譯
- [ ] 更精細的 tag 分類與搜尋
- [ ] 批次匯入（一次處理多支影片）

### Phase 3 — AI Agent 生態
- [ ] MCP Server：AI Agent 可直接查詢知識庫
- [ ] 向量搜尋（RAG）：語意搜尋跨頻道知識
- [ ] 跨頻道知識交叉比較與趨勢分析
- [ ] Export 功能（Markdown / PDF 匯出）
- [ ] Web UI：本地網頁介面提交 URL

---

## 授權

MIT License
