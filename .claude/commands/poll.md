輪詢所有訂閱頻道的 RSS feed，自動解析新影片。

## 使用方式

直接執行：
```bash
python pipeline/rss_poller.py
```

## 說明

- 會讀取 `data/channels.json` 中的所有頻道
- 比對 `last_video_id` 找出新影片（每個頻道最多處理 5 支）
- 每支新影片自動執行完整 ingest pipeline
- 完成後執行：
  ```bash
  git add docs/ data/ && git commit -m "poll: auto-ingest new videos"
  ```

## 前置條件

需先用 `/project:subscribe` 訂閱至少一個頻道。
如果 `data/channels.json` 的 `channels` 陣列為空，告知用戶先訂閱頻道。
