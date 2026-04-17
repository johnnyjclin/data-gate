# DataGate

> 將 YouTube 影音內容自動轉化為結構化 Markdown 知識庫，透過 Claude Code 操作，本地 MkDocs 瀏覽。

---

## 這是什麼？

你丟一個 YouTube 影片連結，DataGate 會：

1. 用 **yt-dlp** 自動取得字幕（支援中文、英文）
2. 用 **GPT-4o** 整理成結構化 Markdown（摘要、重點、逐字稿）
3. 寫入本地 `docs/channels/` 目錄
4. 透過 **MkDocs** 在本機瀏覽知識庫
5. RSS 定時輪詢頻道，有新片自動處理

**Pipeline：**
```
YouTube URL
  → yt-dlp 取字幕
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

> 取得 Token：GitHub → Settings → Developer settings → Personal access tokens (classic)

---

## 用 Claude Code 操作

在 Claude Code 中使用以下 slash commands：

| Command | 功能 |
|---|---|
| `/project:ingest` | 解析單支 YouTube 影片 |
| `/project:subscribe` | 訂閱 YouTube 頻道（RSS）|
| `/project:poll` | 手動拉取所有頻道新影片 |
| `/project:serve` | 啟動本地預覽網站 |

**範例對話：**
```
解析這支影片 https://www.youtube.com/watch?v=VIDEO_ID
```
Claude Code 會自動執行 `python pipeline/ingest.py --url ...`

---

## 指令操作（手動）

### 解析單支影片
```bash
python pipeline/ingest.py --url "https://www.youtube.com/watch?v=VIDEO_ID"
python pipeline/ingest.py --url "..." --channel my-channel  # 指定頻道 slug
python pipeline/ingest.py --url "..." --dry-run              # 預覽不寫檔
```

### 訂閱頻道
```bash
python pipeline/add_channel.py --url "https://www.youtube.com/@ChannelName"
```

### 手動 RSS 輪詢
```bash
python pipeline/rss_poller.py
```

### 本地預覽網站
```bash
mkdocs serve
# 瀏覽 http://127.0.0.1:8000
```

---

## RSS 自動輪詢（本機排程）

設定 macOS LaunchAgent 讓 RSS 輪詢每 6 小時自動執行：

```bash
# 複製 plist 到 LaunchAgents
cp scripts/com.datagate.poller.plist ~/Library/LaunchAgents/

# 編輯 plist，將路徑替換為你的實際路徑
nano ~/Library/LaunchAgents/com.datagate.poller.plist

# 載入並啟動
launchctl load ~/Library/LaunchAgents/com.datagate.poller.plist
```

停止排程：
```bash
launchctl unload ~/Library/LaunchAgents/com.datagate.poller.plist
```

---

## 專案結構

```
pipeline/
  ingest.py        # 主入口：URL → 字幕 → LLM → Markdown
  youtube.py       # yt-dlp 取字幕 + 影片資訊
  llm.py           # GitHub Models GPT-4o 整理逐字稿
  add_channel.py   # 註冊頻道 + 建立 channels.json 記錄
  rss_poller.py    # 輪詢所有頻道 RSS，自動 ingest 新影片
scripts/
  poll.sh                      # RSS 輪詢包裝腳本
  com.datagate.poller.plist    # macOS LaunchAgent 範本
docs/
  channels/        # 本地生成，不上傳 git
data/
  channels.json    # 訂閱頻道清單
.claude/
  commands/        # Claude Code slash commands
CLAUDE.md          # Claude Code 操作說明
```

---

## 注意事項

- `docs/channels/` 為本地生成內容，已加入 `.gitignore`，不會上傳 Git
- `GITHUB_TOKEN` 每日免費額度 150 次 LLM 呼叫
- 影片需有字幕（人工或自動生成），否則跳過


### 5. 本地預覽網站

```bash
pip install mkdocs-material
mkdocs serve
# 開啟 http://localhost:8000
```

### 6. 部署到 GitHub Pages

```bash
git add .
git commit -m "init: first articles"
git push
```

Push 後 GitHub Actions 自動 build 並部署：`https://your-username.github.io/datagate/`

---

## 專案結構

```
datagate/
├── pipeline/
│   ├── ingest.py          # 主入口：URL → Markdown
│   ├── youtube.py         # yt-dlp 字幕擷取
│   ├── llm.py             # GitHub Models GPT-4o 結構化
│   ├── add_channel.py     # 登錄頻道 + 設定 RSS 監聽
│   └── rss_poller.py      # Cron Job：定時拉新片
├── docs/
│   ├── index.md           # 網站首頁
│   └── channels/
│       └── {slug}/
│           ├── index.md   # 頻道首頁（集數列表）
│           └── {video_id}.md  # 單集完整內容
├── data/
│   └── channels.json      # 已登錄頻道與 RSS 設定
├── .github/workflows/
│   ├── deploy.yml         # Push main → 自動建站
│   └── rss_poller.yml     # 每 6 小時自動拉新片
├── mkdocs.yml             # MkDocs Material 設定
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

## GitHub Actions 設定

需要在 repo 的 **Settings → Secrets and variables → Actions** 加入：

| Secret 名稱 | 說明 |
|-------------|------|
| `GH_MODELS_TOKEN` | GitHub Personal Access Token（用於 GPT-4o API） |

`GITHUB_TOKEN` 是 Actions 內建的，不需要另外設定（用於 `git push` 和部署）。

---

## 費用

| 項目 | 費用 |
|------|------|
| GitHub Pages | 免費 |
| GitHub Actions | 免費（每月 2000 分鐘） |
| GitHub Models GPT-4o | 免費（150 req/day，每天 reset） |
| yt-dlp 字幕 | 免費 |
| **總計** | **$0** |

> 若影片沒有字幕才需要 Whisper API（$0.006/分鐘）。大多數有字幕的影片完全免費。

---

## Roadmap

### Phase 1 — MVP ✅（目前）
- [x] YouTube URL → Markdown pipeline
- [x] yt-dlp 字幕擷取（中英文優先）
- [x] GitHub Models GPT-4o 結構化整理
- [x] MkDocs Material 網站（全文搜尋、標籤）
- [x] GitHub Pages 自動部署
- [x] RSS Poller（GitHub Actions Cron，每 6 小時）
- [x] 頻道 White Label 路徑（`/channels/{slug}/`）

### Phase 2 — 開放平台
- [ ] Web UI：使用者可直接在網頁提交 YouTube URL
- [ ] Whisper API fallback（無字幕影片支援）
- [ ] 自訂域名 White Label（CNAME，`knowledge.xrex.io`）
- [ ] Export 功能（整包 Markdown 下載）
- [ ] PDF 文件 parsing
- [ ] 多語言字幕自動翻譯

### Phase 3 — AI Agent 生態
- [ ] MCP Server（Cloudflare Workers）：AI Agent 可直接查詢知識庫
- [ ] x402 付費 API：KOL 知識庫可選擇收費存取
- [ ] 向量搜尋（RAG）：語意搜尋跨頻道知識
- [ ] 跨頻道知識交叉搜尋與比較
- [ ] 市場調查：分析多頻道內容趨勢

---

## 授權

MIT License — 自由使用、修改、部署，歡迎 fork 自建。
