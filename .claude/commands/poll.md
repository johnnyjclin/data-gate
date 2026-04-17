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
  git add data/ && git commit -m "poll: update last_video_id"
  ```

## 前置條件

需先用 `/project:subscribe` 訂閱至少一個頻道。
如果 `data/channels.json` 的 `channels` 陣列為空，告知用戶先訂閱頻道。

## 設定自動定時執行（macOS LaunchAgent）

如果用戶想設定自動每 6 小時執行，依以下步驟操作：

1. 複製 plist 到 LaunchAgents：
   ```bash
   cp scripts/com.datagate.poller.plist ~/Library/LaunchAgents/
   ```

2. 編輯 plist，把路徑換成實際專案路徑：
   ```bash
   sed -i '' "s|/Users/YOUR_USERNAME/Documents/DataGate|$PWD|g" \
     ~/Library/LaunchAgents/com.datagate.poller.plist
   ```

3. 載入並啟用：
   ```bash
   launchctl load ~/Library/LaunchAgents/com.datagate.poller.plist
   ```

4. 查看 log：
   ```bash
   tail -f /tmp/datagate-poller.log
   ```

停止排程：
```bash
launchctl unload ~/Library/LaunchAgents/com.datagate.poller.plist
```
