# DataGate 知識庫

> 將 YouTube / Podcast 影音內容自動轉化為結構化 Markdown 知識庫

---

## 什麼是 DataGate？

DataGate 將散落在 YouTube 頻道的影音內容，自動解析成可搜尋、可瀏覽的知識文件。

每支影片都包含：

- **摘要**：2-4 句話的核心內容
- **重點整理**：條列式關鍵觀念
- **詳細筆記**：依主題分段整理
- **完整逐字稿**：保留原始內容

## 頻道列表

瀏覽 [頻道列表](channels/index.md) 查看所有已收錄的頻道。

## 提交影片

```bash
git clone https://github.com/your-github-username/datagate
cd datagate
pip install -r requirements.txt
cp .env.example .env   # 填入 GITHUB_TOKEN

python pipeline/ingest.py --url "https://youtube.com/watch?v=xxx"
```

---

*由 [DataGate](https://github.com/your-github-username/datagate) 自動生成 · 開源於 MIT License*
