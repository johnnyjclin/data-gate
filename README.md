# DataGate

> 將 YouTube 影音內容自動轉化為結構化 Markdown 知識庫，部署在 GitHub Pages，供人與 AI Agent 存取。

---

## 這是什麼？

你丟一個 YouTube 影片連結，DataGate 會：

1. 自動取得字幕（支援中文、英文）
2. 用 GPT-4o 整理成結構化 Markdown（摘要、重點、逐字稿）
3. 寫入 Git repo，GitHub Pages 自動更新網站
4. 透過 RSS 定時監聽頻道，有新影片自動處理

**Pipeline 示意：**
```
YouTube URL
  → yt-dlp 取字幕
  → GPT-4o 結構化整理
  → Markdown 寫入 docs/
  → git push → GitHub Pages 自動更新
```

---

## 快速開始

### 1. 安裝

```bash
git clone https://github.com/johnnyjclin/data-gate.git
cd datagate
pip install -r requirements.txt
```

### 2. 設定 API Token

```bash
cp .env.example .env
```

編輯 `.env`，填入你的 GitHub Personal Access Token：

```env
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
```

> 取得 Token：GitHub → Settings → Developer settings → Personal access tokens → 勾選 `read:user` 即可

### 3. 跑第一支影片

```bash
python pipeline/ingest.py --url 'https://www.youtube.com/watch?v=VIDEO_ID'
```

加上 `--dry-run` 可預覽輸出，不寫入檔案：

```bash
python pipeline/ingest.py --url 'https://www.youtube.com/watch?v=VIDEO_ID' --dry-run
```

指定頻道 slug（選填，不指定會自動從頻道名稱產生）：

```bash
python pipeline/ingest.py --url 'https://...' --channel xrex
```

### 4. 訂閱頻道 RSS（自動追蹤新片）

```bash
# 用 YouTube Channel ID
python pipeline/add_channel.py --slug xrex --name "XREX" --youtube-channel-id UCxxxxxxxxxx

# 或直接提供 RSS URL
python pipeline/add_channel.py --slug xrex --name "XREX" --rss "https://www.youtube.com/feeds/videos.xml?channel_id=UCxxxxxxxxxx"
```

之後 GitHub Actions 每 6 小時會自動拉新片。

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
