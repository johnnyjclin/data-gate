訂閱 YouTube 頻道，將其加入 RSS 自動追蹤清單。

## 使用方式

用戶提供頻道 URL 或 RSS feed URL，執行以下步驟：

1. 接受以下格式：
   - `https://www.youtube.com/@ChannelHandle`（頻道頁面）
   - `https://www.youtube.com/channel/UCxxxxx`（頻道頁面）
   - `https://www.youtube.com/feeds/videos.xml?channel_id=UCxxx`（RSS feed）
2. 執行：
   ```bash
   python pipeline/add_channel.py --url "<URL>"
   ```
3. 如果用戶有指定 slug 或名稱，加上 `--slug <slug>` 或 `--name "名稱"`

## 說明

- 自動偵測頻道名稱與 channel ID
- 頻道資訊寫入 `data/channels.json`
- 建立 `docs/channels/<slug>/` 目錄
- 執行 `/project:poll` 可立即抓取該頻道的最新影片
