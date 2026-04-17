# 提交影片 / 訂閱頻道

透過此頁面提交 YouTube 影片或訂閱頻道，系統會自動解析並上架至知識庫。

<div class="dg-wrap">

<div class="dg-token-bar">
  <span class="dg-token-label">🔑 GitHub Token</span>
  <input type="password" id="dg-token" class="dg-input dg-input-token" placeholder="ghp_xxxxxxxxxxxx（儲存於瀏覽器本機）">
  <button class="dg-btn dg-btn-save" onclick="dgSaveToken()">儲存</button>
  <span id="dg-token-status" class="dg-token-status"></span>
</div>

<div class="dg-hint">
  需要 <strong>Classic PAT</strong>，勾選 <code>workflow</code> scope。Fine-grained token 不支援觸發 Actions。<br>
  <a href="https://github.com/settings/tokens/new?scopes=workflow&description=DataGate+Token" target="_blank">點此建立 Classic PAT（已預選 workflow）→</a>
</div>

<div class="dg-tabs">
  <button class="dg-tab dg-tab-active" id="tab-btn-url" onclick="dgSwitchTab('url')">🎬 提交影片 URL</button>
  <button class="dg-tab" id="tab-btn-channel" onclick="dgSwitchTab('channel')">📡 訂閱頻道</button>
</div>

<!-- 提交影片 -->
<div class="dg-panel" id="dg-panel-url">
  <div class="dg-form-group">
    <label class="dg-label">YouTube 影片網址 <span class="dg-required">*</span></label>
    <input type="text" id="dg-url" class="dg-input" placeholder="https://www.youtube.com/watch?v=VIDEO_ID">
  </div>
  <div class="dg-form-group">
    <label class="dg-label">頻道 slug <span class="dg-optional">（選填，自動偵測）</span></label>
    <input type="text" id="dg-channel-slug" class="dg-input" placeholder="e.g. xrex">
  </div>
  <button class="dg-btn dg-btn-primary" onclick="dgSubmitURL()">🚀 開始解析</button>
</div>

<!-- 訂閱頻道 -->
<div class="dg-panel dg-panel-hidden" id="dg-panel-channel">
  <div class="dg-form-group">
    <label class="dg-label">頻道名稱 <span class="dg-required">*</span></label>
    <input type="text" id="dg-ch-name" class="dg-input" placeholder="e.g. XREX">
  </div>
  <div class="dg-form-group">
    <label class="dg-label">頻道 Slug <span class="dg-required">*</span></label>
    <input type="text" id="dg-ch-slug" class="dg-input" placeholder="英數小寫，e.g. xrex">
  </div>
  <div class="dg-form-group">
    <label class="dg-label">YouTube Channel ID <span class="dg-required">*</span></label>
    <input type="text" id="dg-ch-id" class="dg-input" placeholder="UCxxxxxxxxxxxxxxxxxxxx">
    <div class="dg-hint-inline">在 YouTube 頻道頁面 → 點選「更多」→「分享頻道」→「複製頻道 ID」</div>
  </div>
  <div class="dg-form-group">
    <label class="dg-label">頻道描述 <span class="dg-optional">（選填）</span></label>
    <input type="text" id="dg-ch-desc" class="dg-input" placeholder="一句話描述此頻道">
  </div>
  <button class="dg-btn dg-btn-primary" onclick="dgAddChannel()">📡 訂閱並監聽新片</button>
</div>

<!-- Status -->
<div id="dg-status" class="dg-status dg-status-hidden"></div>

</div>

<style>
.dg-wrap {
  max-width: 640px;
  margin: 1.5rem 0;
  font-family: inherit;
}
.dg-token-bar {
  display: flex;
  align-items: center;
  gap: .6rem;
  flex-wrap: wrap;
  margin-bottom: .4rem;
}
.dg-token-label { font-weight: 600; white-space: nowrap; }
.dg-input {
  width: 100%;
  padding: .5rem .75rem;
  border: 1px solid var(--md-default-fg-color--lightest, #ddd);
  border-radius: 6px;
  background: var(--md-default-bg-color, #fff);
  color: var(--md-default-fg-color, #333);
  font-size: .9rem;
  box-sizing: border-box;
}
.dg-input-token { width: 260px; flex: 1; min-width: 160px; }
.dg-input:focus { outline: 2px solid #5c6bc0; border-color: transparent; }
.dg-token-status { font-size: .85rem; }
.dg-hint {
  font-size: .82rem;
  color: var(--md-default-fg-color--light, #666);
  margin-bottom: 1.2rem;
}
.dg-hint a { color: #5c6bc0; }
.dg-tabs {
  display: flex;
  gap: .5rem;
  border-bottom: 2px solid var(--md-default-fg-color--lightest, #ddd);
  margin-bottom: 1.2rem;
}
.dg-tab {
  padding: .5rem 1.1rem;
  border: none;
  background: transparent;
  cursor: pointer;
  font-size: .92rem;
  color: var(--md-default-fg-color--light, #666);
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  border-radius: 4px 4px 0 0;
  transition: all .15s;
}
.dg-tab:hover { color: #5c6bc0; }
.dg-tab-active {
  color: #5c6bc0 !important;
  border-bottom-color: #5c6bc0 !important;
  font-weight: 600;
}
.dg-panel { display: flex; flex-direction: column; gap: 1rem; }
.dg-panel-hidden { display: none !important; }
.dg-form-group { display: flex; flex-direction: column; gap: .3rem; }
.dg-label { font-size: .9rem; font-weight: 500; }
.dg-required { color: #e53935; font-size: .8rem; }
.dg-optional { color: var(--md-default-fg-color--light, #888); font-size: .8rem; font-weight: 400; }
.dg-hint-inline { font-size: .8rem; color: var(--md-default-fg-color--light, #888); margin-top: .2rem; }
.dg-btn {
  padding: .55rem 1.4rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: .92rem;
  font-weight: 600;
  transition: opacity .15s;
}
.dg-btn:hover { opacity: .85; }
.dg-btn:disabled { opacity: .5; cursor: not-allowed; }
.dg-btn-primary {
  background: #5c6bc0;
  color: #fff;
  align-self: flex-start;
  margin-top: .3rem;
}
.dg-btn-save {
  background: #43a047;
  color: #fff;
  padding: .48rem 1rem;
  white-space: nowrap;
}
.dg-status {
  margin-top: 1.2rem;
  padding: .8rem 1rem;
  border-radius: 6px;
  font-size: .9rem;
  line-height: 1.5;
}
.dg-status-hidden { display: none; }
.dg-status-success { background: #e8f5e9; color: #2e7d32; border: 1px solid #a5d6a7; }
.dg-status-error   { background: #fce4ec; color: #c62828; border: 1px solid #ef9a9a; }
.dg-status-loading { background: #e3f2fd; color: #1565c0; border: 1px solid #90caf9; }
</style>

<script>
const DG_REPO_OWNER = 'johnnyjclin';
const DG_REPO_NAME  = 'data-gate';
const DG_TOKEN_KEY  = 'dg_github_token';

// 初始化：讀取已存的 token
(function() {
  const t = localStorage.getItem(DG_TOKEN_KEY);
  if (t) {
    document.getElementById('dg-token').value = t;
    document.getElementById('dg-token-status').textContent = '✅ 已載入';
  }
})();

function dgSaveToken() {
  const t = document.getElementById('dg-token').value.trim();
  if (!t) {
    document.getElementById('dg-token-status').textContent = '❌ 請輸入 Token';
    return;
  }
  localStorage.setItem(DG_TOKEN_KEY, t);
  document.getElementById('dg-token-status').textContent = '✅ 已儲存';
  setTimeout(() => {
    document.getElementById('dg-token-status').textContent = '';
  }, 2000);
}

function dgSwitchTab(tab) {
  document.getElementById('dg-panel-url').classList.add('dg-panel-hidden');
  document.getElementById('dg-panel-channel').classList.add('dg-panel-hidden');
  document.getElementById('tab-btn-url').classList.remove('dg-tab-active');
  document.getElementById('tab-btn-channel').classList.remove('dg-tab-active');
  document.getElementById('dg-panel-' + tab).classList.remove('dg-panel-hidden');
  document.getElementById('tab-btn-' + tab).classList.add('dg-tab-active');
  dgHideStatus();
}

function dgShowStatus(msg, type) {
  const el = document.getElementById('dg-status');
  el.className = 'dg-status dg-status-' + type;
  el.innerHTML = msg;
}
function dgHideStatus() {
  document.getElementById('dg-status').className = 'dg-status dg-status-hidden';
}

function dgGetToken() {
  return localStorage.getItem(DG_TOKEN_KEY) || document.getElementById('dg-token').value.trim();
}

async function dgDispatch(workflow, inputs) {
  const token = dgGetToken();
  if (!token) {
    dgShowStatus('❌ 請先填入並儲存 GitHub Token', 'error');
    return;
  }
  dgShowStatus('⏳ 提交中...', 'loading');
  try {
    const res = await fetch(
      `https://api.github.com/repos/${DG_REPO_OWNER}/${DG_REPO_NAME}/actions/workflows/${workflow}/dispatches`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Accept': 'application/vnd.github+json',
          'Content-Type': 'application/json',
          'X-GitHub-Api-Version': '2022-11-28',
        },
        body: JSON.stringify({ ref: 'main', inputs }),
      }
    );
    if (res.status === 204) {
      dgShowStatus(
        `✅ 已送出！GitHub Actions 正在處理中，約 3-5 分鐘後網站自動更新。<br>
         <a href="https://github.com/${DG_REPO_OWNER}/${DG_REPO_NAME}/actions" target="_blank">查看執行進度 →</a>`,
        'success'
      );
    } else {
      const body = await res.json().catch(() => ({}));
      const detail = body.message || '未知錯誤';
      let hint = '';
      if (res.status === 401) {
        hint = '→ Token 無效或已過期，請重新設定';
      } else if (res.status === 403) {
        hint = '→ Token 缺少 <code>workflow</code> 權限，或此 repo 未開啟 Actions';
      } else if (res.status === 404) {
        hint = '→ Repo 或 workflow 檔案找不到，確認 repo 名稱正確';
      } else if (res.status === 422) {
        hint = '→ workflow_dispatch 設定問題，確認 workflow 已存在於 main branch';
      }
      dgShowStatus(`❌ HTTP ${res.status}：<code>${detail}</code><br><small>${hint}</small>`, 'error');
    }
  } catch (e) {
    dgShowStatus(`❌ 網路錯誤：${e.message}`, 'error');
  }
}

function dgSubmitURL() {
  const url = document.getElementById('dg-url').value.trim();
  const channel = document.getElementById('dg-channel-slug').value.trim();
  if (!url) {
    dgShowStatus('❌ 請輸入 YouTube 影片網址', 'error');
    return;
  }
  if (!url.includes('youtube.com/watch') && !url.includes('youtu.be/')) {
    dgShowStatus('❌ 請輸入有效的 YouTube 影片網址（非頻道首頁）', 'error');
    return;
  }
  dgDispatch('ingest_on_demand.yml', { url, channel });
}

function dgAddChannel() {
  const name = document.getElementById('dg-ch-name').value.trim();
  const slug = document.getElementById('dg-ch-slug').value.trim();
  const channel_id = document.getElementById('dg-ch-id').value.trim();
  const description = document.getElementById('dg-ch-desc').value.trim();
  if (!name || !slug || !channel_id) {
    dgShowStatus('❌ 請填寫頻道名稱、Slug 與 Channel ID', 'error');
    return;
  }
  if (!channel_id.startsWith('UC')) {
    dgShowStatus('❌ Channel ID 格式不正確，應以 UC 開頭', 'error');
    return;
  }
  dgDispatch('add_channel_on_demand.yml', { slug, name, channel_id, description });
}
</script>
