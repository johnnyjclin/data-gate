輪詢所有訂閱頻道的 RSS feed，自動解析新影片。

## 使用方式

直接執行：
```bash
python pipeline/rss_poller.py
```

## 說明

- 讀取 `data/channels.json` 中的所有頻道
- 拉取 RSS feed，比對 `docs/channels/{slug}/` 下已有的影片 ID
- 每個頻道最多處理 5 支新影片
- 每支新影片自動執行完整 ingest pipeline
- 已存在的影片自動跳過

## 前置條件

需先用 `/project:subscribe` 訂閱至少一個頻道。
如果 `data/channels.json` 的 `channels` 陣列為空，告知用戶先訂閱頻道。
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
