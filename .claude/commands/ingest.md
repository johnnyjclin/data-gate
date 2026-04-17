解析 YouTube 影片，將字幕整理為結構化 Markdown 並存入知識庫。

## 使用方式

用戶會提供 YouTube 影片 URL（有時可能含有多餘空格或引號），執行以下步驟：

1. 清理 URL（去除首尾空白、引號、反斜線）
2. 執行指令：
   ```bash
   python pipeline/ingest.py --url "<URL>"
   ```
3. 如果用戶有指定頻道 slug，加上 `--channel <slug>`

## 常見問題

- **找不到字幕**：影片可能未開啟字幕，告知用戶跳過
- **LLM 呼叫失敗**：確認 `.env` 中 `GITHUB_TOKEN` 已設定
- **URL 格式錯誤**：只接受 `youtube.com/watch?v=` 或 `youtu.be/` 格式，不接受頻道首頁
