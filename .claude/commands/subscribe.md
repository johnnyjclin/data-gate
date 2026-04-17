訂閱 YouTube 頻道，將其加入 RSS 自動追蹤清單。

## 使用方式

用戶提供頻道 URL 或頻道名稱，執行以下步驟：

1. 接受以下格式：
   - `https://www.youtube.com/@ChannelHandle`
   - `https://www.youtube.com/channel/UCxxxxx`
   - 或純頻道名稱（會自動加上 `https://www.youtube.com/@`）
2. 執行：
   ```bash
   python pipeline/add_channel.py --url "<頻道 URL>"
   ```
3. 成功後執行：
   ```bash
   git add data/ docs/ && git commit -m "subscribe: <頻道名稱>"
   ```

## 說明

- 訂閱後頻道資訊會寫入 `data/channels.json`
- 執行 `/project:poll` 可立即抓取該頻道的最新影片
- 每個頻道會在 `docs/channels/<slug>/` 建立專屬目錄
