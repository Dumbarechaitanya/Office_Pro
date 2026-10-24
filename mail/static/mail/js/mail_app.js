/**
 * Office Pro Webmail Suite JS Engine
 * Gmail and Outlook Grade Interactive Client
 */

(function () {
  'use strict';

  // State
  const state = {
    folder: 'inbox',
    label: '',
    filter: 'all',
    search: '',
    page: 1,
    pageSize: 35,
    selectedIds: new Set(),
    openedEmailId: null,
    emails: [],
    composerAttachments: [],
    isSending: false
  };

  function getCsrfToken() {
    const input = document.querySelector('[name=csrfmiddlewaretoken]');
    if (input) return input.value;
    const match = document.cookie.match(/csrftoken=([^;]+)/);
    return match ? match[1] : '';
  }

  // Toast Notification
  window.showMailToast = function (msg, isError = false) {
    const toast = document.getElementById('opMailToast');
    if (!toast) return;
    toast.textContent = msg;
    toast.style.background = isError ? '#ef4444' : '#0f172a';
    toast.style.display = 'flex';
    clearTimeout(toast._timeout);
    toast._timeout = setTimeout(() => {
      toast.style.display = 'none';
    }, 3500);
  };

  // -------------------------------------------------------------------------
  // 1. Loading & Rendering Thread List
  // -------------------------------------------------------------------------
  window.loadEmails = function () {
    const container = document.getElementById('opThreadListContainer');
    if (!container) return;

    container.innerHTML = '<div style="padding: 30px; text-align: center; color: #94a3b8;">Loading messages...</div>';

    let url = `/mail/api/emails/?folder=${encodeURIComponent(state.folder)}&page=${state.page}&page_size=${state.pageSize}`;
    if (state.label) url += `&label=${encodeURIComponent(state.label)}`;
    if (state.filter && state.filter !== 'all') url += `&filter=${encodeURIComponent(state.filter)}`;
    if (state.search) url += `&q=${encodeURIComponent(state.search)}`;

    fetch(url)
      .then(res => res.json())
      .then(data => {
        if (data.error) {
          container.innerHTML = `<div style="padding: 30px; text-align: center; color: #ef4444;">${data.error}</div>`;
          return;
        }

        state.emails = data.emails || [];
        updateFolderBadges(data.folder_counts || {});
        renderEmailList(state.emails, data.total_count || 0);

        // Update pagination text
        const countText = document.getElementById('opMailCountText');
        if (countText) {
          if (data.total_count === 0) {
            countText.textContent = '0 of 0';
          } else {
            const start = (state.page - 1) * state.pageSize + 1;
            const end = Math.min(start + state.emails.length - 1, data.total_count);
            countText.textContent = `${start}–${end} of ${data.total_count}`;
          }
        }
      })
      .catch(err => {
        container.innerHTML = `<div style="padding: 30px; text-align: center; color: #ef4444;">Failed to load messages.</div>`;
      });
  };

  function updateFolderBadges(counts) {
    const inboxBadge = document.getElementById('opFolderBadge_inbox');
    if (inboxBadge) {
      inboxBadge.textContent = counts.inbox_unread || '0';
      inboxBadge.style.display = counts.inbox_unread > 0 ? 'inline-block' : 'none';
      if (counts.inbox_unread > 0) inboxBadge.classList.add('badge-highlight');
      else inboxBadge.classList.remove('badge-highlight');
    }

    const starredBadge = document.getElementById('opFolderBadge_starred');
    if (starredBadge) {
      starredBadge.textContent = counts.starred_count || '0';
      starredBadge.style.display = counts.starred_count > 0 ? 'inline-block' : 'none';
    }

    const draftsBadge = document.getElementById('opFolderBadge_drafts');
    if (draftsBadge) {
      draftsBadge.textContent = counts.drafts_count || '0';
      draftsBadge.style.display = counts.drafts_count > 0 ? 'inline-block' : 'none';
    }

    const trashBadge = document.getElementById('opFolderBadge_trash');
    if (trashBadge) {
      trashBadge.textContent = counts.trash_count || '0';
      trashBadge.style.display = counts.trash_count > 0 ? 'inline-block' : 'none';
    }
  }

  function renderEmailList(emails, totalCount) {
    const container = document.getElementById('opThreadListContainer');
    if (!container) return;

    if (!emails || emails.length === 0) {
      container.innerHTML = `
        <div style="padding: 50px 20px; text-align: center; color: #94a3b8;">
          <div style="font-size: 38px; margin-bottom: 10px;">📭</div>
          <div style="font-size: 14.5px; font-weight: 600; color: #475569; margin-bottom: 4px;">No messages here</div>
          <div style="font-size: 12.5px;">Your ${state.folder} folder is clear.</div>
        </div>
      `;
      return;
    }

    let html = '';
    emails.forEach(m => {
      const isSelected = state.selectedIds.has(m.id);
      const isOpened = state.openedEmailId === m.id;
      const unreadCls = !m.is_read ? 'unread' : '';
      const selectedCls = isSelected ? 'selected' : '';
      const activeCls = isOpened ? 'active-open' : '';

      html += `
        <div class="op-email-card ${unreadCls} ${selectedCls} ${activeCls}" id="opEmailCard_${m.id}" onclick="openEmail(${m.id})">
          ${!m.is_read ? '<span class="op-card-unread-dot"></span>' : ''}
          
          <div class="op-card-avatar" style="background-color: ${m.avatar_color};">
            ${m.avatar_initial}
          </div>

          <div class="op-card-content">
            <div class="op-card-header">
              <span class="op-card-sender" title="${escapeHtml(m.email_from)}">${escapeHtml(m.sender_name)}</span>
              <span class="op-card-date">${m.date_formatted}</span>
            </div>

            <div class="op-card-subject" title="${escapeHtml(m.subject)}">
              ${escapeHtml(m.subject)}
            </div>

            <div class="op-card-snippet">
              ${escapeHtml(m.snippet)}
            </div>

            <div class="op-card-footer">
              <button type="button" class="op-star-btn ${m.is_starred ? 'starred' : ''}" onclick="toggleStar(${m.id}, event)" title="${m.is_starred ? 'Starred' : 'Not starred'}">
                ${m.is_starred ? '★' : '☆'}
              </button>

              <span class="op-tag-pill op-tag-${m.label || 'work'}">${m.label || 'work'}</span>

              ${m.has_attachments ? '<span style="font-size: 13px; color: #64748b;" title="Has attachment">📎</span>' : ''}

              ${m.res_name ? `
                <a href="${m.record_url || '#'}" class="op-erp-badge" onclick="event.stopPropagation();" title="Linked to ERP record">
                  📋 ${escapeHtml(m.res_name)}
                </a>
              ` : ''}

              <div style="margin-left: auto;" onclick="event.stopPropagation();">
                <input type="checkbox" class="op-card-check" ${isSelected ? 'checked' : ''} onchange="toggleEmailSelection(${m.id}, this.checked)">
              </div>
            </div>
          </div>
        </div>
      `;
    });

    container.innerHTML = html;
  }

  function escapeHtml(text) {
    if (!text) return '';
    const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
    return String(text).replace(/[&<>"']/g, m => map[m]);
  }

  // -------------------------------------------------------------------------
  // 2. Reading Pane (Email Details & Thread)
  // -------------------------------------------------------------------------
  window.openEmail = function (emailId) {
    state.openedEmailId = emailId;

    // Highlight active card
    document.querySelectorAll('.op-email-card').forEach(c => c.classList.remove('active-open'));
    const card = document.getElementById(`opEmailCard_${emailId}`);
    if (card) {
      card.classList.add('active-open');
      card.classList.remove('unread');
      const dot = card.querySelector('.op-card-unread-dot');
      if (dot) dot.remove();
    }

    const pane = document.getElementById('opReadingPane');
    if (!pane) return;

    pane.innerHTML = '<div style="padding: 40px; text-align: center; color: #94a3b8;">Loading email thread...</div>';

    fetch(`/mail/api/emails/${emailId}/`)
      .then(res => res.json())
      .then(email => {
        if (email.error) {
          pane.innerHTML = `<div style="padding: 40px; text-align: center; color: #ef4444;">${email.error}</div>`;
          return;
        }

        renderReadingPane(email);
      })
      .catch(err => {
        pane.innerHTML = `<div style="padding: 40px; text-align: center; color: #ef4444;">Failed to load email thread.</div>`;
      });
  };

  function renderReadingPane(email) {
    const pane = document.getElementById('opReadingPane');
    if (!pane) return;

    let attachmentsHtml = '';
    if (email.attachments && email.attachments.length > 0) {
      attachmentsHtml = `
        <div class="op-attachments-deck">
          <div class="op-attachments-title">
            <span>📎 Attachments (${email.attachments.length})</span>
          </div>
          <div class="op-attachments-grid">
            ${email.attachments.map(att => `
              <a href="${att.url}" target="_blank" class="op-attachment-card" download>
                <div class="op-att-icon">${att.icon || '📄'}</div>
                <div class="op-att-info">
                  <div class="op-att-name" title="${escapeHtml(att.name)}">${escapeHtml(att.name)}</div>
                  <div class="op-att-size">${att.size} • Download</div>
                </div>
              </a>
            `).join('')}
          </div>
        </div>
      `;
    }

    let erpBannerHtml = '';
    if (email.res_name && email.record_url) {
      erpBannerHtml = `
        <div class="op-erp-link-banner">
          <div class="op-erp-banner-left">
            <span>🔗 Linked ERP Document:</span>
            <strong style="color: #0f172a;">${escapeHtml(email.res_name)}</strong>
            <span style="font-size: 11px; background: #e0f2fe; padding: 2px 6px; border-radius: 4px;">${email.res_model || 'Document'}</span>
          </div>
          <a href="${email.record_url}" class="op-erp-banner-btn" target="_blank">Open Record ↗</a>
        </div>
      `;
    }

    let threadMessagesHtml = '';
    if (email.thread && email.thread.length > 1) {
      threadMessagesHtml = `
        <div style="padding: 10px 20px; font-size: 12.5px; font-weight: 700; color: #64748b; border-bottom: 1px solid #e2e8f0; background: #f8fafc;">
          Conversation History (${email.thread.length} messages)
        </div>
        ${email.thread.map((t, idx) => `
          <div style="padding: 16px 20px; border-bottom: 1px solid #f1f5f9; ${t.id === email.id ? 'background: #ffffff;' : 'background: #fbfcfe; opacity: 0.9;'}">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
              <div style="display: flex; align-items: center; gap: 8px;">
                <span class="op-card-avatar" style="width: 28px; height: 28px; font-size: 12px; background-color: ${t.avatar_color};">${t.avatar_initial}</span>
                <strong style="font-size: 13.5px;">${escapeHtml(t.sender_name)}</strong>
                <span style="font-size: 12px; color: #64748b;">&lt;${escapeHtml(t.sender_email)}&gt;</span>
              </div>
              <span style="font-size: 11.5px; color: #94a3b8;">${t.date_full}</span>
            </div>
            <div class="op-msg-body-content" style="padding: 6px 0 0 36px; font-size: 13.5px;">
              ${t.body_html || t.body_text}
            </div>
          </div>
        `).join('')}
      `;
    }

    pane.innerHTML = `
      <!-- Reading Toolbar -->
      <div class="op-reading-header-toolbar">
        <div class="op-actions-group">
          <button type="button" class="op-icon-btn" onclick="openComposer('reply', { to: '${escapeHtml(email.email_from)}', subject: 'Re: ${escapeHtml(email.subject)}', parentId: ${email.id} })" title="Reply">↩ Reply</button>
          <button type="button" class="op-icon-btn" onclick="openComposer('forward', { subject: 'Fwd: ${escapeHtml(email.subject)}', bodyHtml: '${escapeHtml(email.body_html)}' })" title="Forward">↪ Forward</button>
          <button type="button" class="op-icon-btn" onclick="singleAction(${email.id}, 'archive')" title="Archive">📦 Archive</button>
          <button type="button" class="op-icon-btn" onclick="singleAction(${email.id}, 'trash')" title="Delete">🗑️ Delete</button>
          <button type="button" class="op-icon-btn" onclick="singleAction(${email.id}, 'mark_unread')" title="Mark Unread">📬 Mark Unread</button>
        </div>

        <div class="op-actions-group">
          <button type="button" class="op-star-btn ${email.is_starred ? 'starred' : ''}" onclick="toggleStar(${email.id}, event)" title="${email.is_starred ? 'Starred' : 'Not starred'}" style="font-size: 18px;">
            ${email.is_starred ? '★' : '☆'}
          </button>
          <button type="button" class="op-icon-btn" onclick="window.print()" title="Print">🖨️</button>
          <button type="button" class="op-icon-btn" onclick="closeReadingPane()" title="Close pane">&times;</button>
        </div>
      </div>

      <!-- Subject Line -->
      <div class="op-reading-subject-row">
        <h2 class="op-reading-subject-title">${escapeHtml(email.subject)}</h2>
        <span class="op-tag-pill op-tag-${email.label || 'work'}">${email.label || 'work'}</span>
      </div>

      <!-- Sender details -->
      <div class="op-msg-sender-block">
        <div class="op-card-avatar" style="width: 44px; height: 44px; font-size: 16px; background-color: ${email.avatar_color};">
          ${email.avatar_initial}
        </div>
        <div class="op-msg-sender-details">
          <div class="op-sender-name-row">
            <span class="op-sender-display-name">${escapeHtml(email.sender_name)}</span>
            <span class="op-sender-email-text">&lt;${escapeHtml(email.sender_email)}&gt;</span>
            <span class="op-tls-badge" title="Encrypted via TLS SMTP Relay">🔒 TLS Verified</span>
          </div>
          <div class="op-msg-recipient-line">
            To: ${escapeHtml(email.email_to)} ${email.email_cc ? `• Cc: ${escapeHtml(email.email_cc)}` : ''}
          </div>
        </div>
        <div class="op-msg-date-line">
          ${email.date_full}
        </div>
      </div>

      <!-- ERP Link Banner if linked -->
      ${erpBannerHtml}

      <!-- Conversation Thread or Single Message Body -->
      ${threadMessagesHtml ? threadMessagesHtml : `
        <div class="op-msg-body-content">
          ${email.body_html || email.body_text}
        </div>
      `}

      <!-- Attachments Deck -->
      ${attachmentsHtml}

      <!-- Quick Inline Reply Box -->
      <div class="op-inline-reply-box">
        <div class="op-reply-header">
          <span>Reply to <strong>${escapeHtml(email.sender_name)}</strong></span>
          <button type="button" class="op-field-extra-btn" onclick="openComposer('reply', { to: '${escapeHtml(email.email_from)}', subject: 'Re: ${escapeHtml(email.subject)}', parentId: ${email.id} })">Pop-out composer ↗</button>
        </div>
        <textarea id="opInlineReplyBody" class="op-reply-textarea" placeholder="Type a quick reply here (Ctrl+Enter to send)..."></textarea>
        <div class="op-reply-footer">
          <div style="font-size: 12px; color: #94a3b8;">Press Ctrl+Enter to send</div>
          <button type="button" class="op-btn-reply-send" onclick="sendInlineReply(${email.id})">Send Reply</button>
        </div>
      </div>
    `;

    // Keyboard shortcut for inline reply
    const textarea = document.getElementById('opInlineReplyBody');
    if (textarea) {
      textarea.addEventListener('keydown', e => {
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
          sendInlineReply(email.id);
        }
      });
    }
  }

  window.closeReadingPane = function () {
    state.openedEmailId = null;
    document.querySelectorAll('.op-email-card').forEach(c => c.classList.remove('active-open'));
    const pane = document.getElementById('opReadingPane');
    if (pane) {
      pane.innerHTML = `
        <div class="op-reading-empty-state">
          <div class="op-empty-icon">📨</div>
          <h3 style="font-size: 16px; margin-bottom: 6px; color: #475569;">Select an item to read</h3>
          <p style="font-size: 13px; margin: 0;">Nothing is selected. Click on a thread on the left.</p>
        </div>
      `;
    }
  };

  // -------------------------------------------------------------------------
  // 3. Email Actions (Star, Archive, Trash, Batch)
  // -------------------------------------------------------------------------
  window.toggleStar = function (emailId, event) {
    if (event) event.stopPropagation();

    fetch(`/mail/api/star/${emailId}/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': getCsrfToken() }
    })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          const card = document.getElementById(`opEmailCard_${emailId}`);
          if (card) {
            const btn = card.querySelector('.op-star-btn');
            if (btn) {
              if (data.is_starred) {
                btn.classList.add('starred');
                btn.textContent = '★';
              } else {
                btn.classList.remove('starred');
                btn.textContent = '☆';
              }
            }
          }
          if (state.openedEmailId === emailId) {
            const readingBtn = document.querySelector('.op-reading-header-toolbar .op-star-btn');
            if (readingBtn) {
              if (data.is_starred) {
                readingBtn.classList.add('starred');
                readingBtn.textContent = '★';
              } else {
                readingBtn.classList.remove('starred');
                readingBtn.textContent = '☆';
              }
            }
          }
        }
      });
  };

  window.singleAction = function (emailId, action) {
    executeBatchAction(action, '', [emailId]);
  };

  window.toggleSelectAll = function (checked) {
    state.selectedIds.clear();
    const checkboxes = document.querySelectorAll('.op-card-check');
    checkboxes.forEach(cb => {
      cb.checked = checked;
    });

    if (checked) {
      state.emails.forEach(m => state.selectedIds.add(m.id));
      document.querySelectorAll('.op-email-card').forEach(c => c.classList.add('selected'));
    } else {
      document.querySelectorAll('.op-email-card').forEach(c => c.classList.remove('selected'));
    }

    updateSelectionToolbar();
  };

  window.toggleEmailSelection = function (emailId, checked) {
    if (checked) {
      state.selectedIds.add(emailId);
      const card = document.getElementById(`opEmailCard_${emailId}`);
      if (card) card.classList.add('selected');
    } else {
      state.selectedIds.delete(emailId);
      const card = document.getElementById(`opEmailCard_${emailId}`);
      if (card) card.classList.remove('selected');
    }
    updateSelectionToolbar();
  };

  function updateSelectionToolbar() {
    const bulkBar = document.getElementById('opBulkActionsBar');
    const normalBar = document.getElementById('opNormalActionsBar');
    const countLabel = document.getElementById('opSelectedCountLabel');

    if (state.selectedIds.size > 0) {
      if (bulkBar) bulkBar.style.display = 'flex';
      if (normalBar) normalBar.style.display = 'none';
      if (countLabel) countLabel.textContent = `${state.selectedIds.size} selected`;
    } else {
      if (bulkBar) bulkBar.style.display = 'none';
      if (normalBar) normalBar.style.display = 'flex';
    }
  }

  window.executeBatchAction = function (action, label = '', explicitIds = null) {
    const ids = explicitIds || Array.from(state.selectedIds);
    if (!ids || ids.length === 0) {
      showMailToast('No messages selected', true);
      return;
    }

    fetch('/mail/api/batch-action/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken()
      },
      body: JSON.stringify({
        action: action,
        email_ids: ids,
        label: label
      })
    })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          showMailToast(`Action completed (${data.affected_count} messages)`);
          state.selectedIds.clear();
          updateSelectionToolbar();
          loadEmails();
          if (ids.includes(state.openedEmailId)) {
            closeReadingPane();
          }
        } else {
          showMailToast(data.error || 'Action failed', true);
        }
      })
      .catch(err => {
        showMailToast('Failed to perform action', true);
      });
  };

  // -------------------------------------------------------------------------
  // 4. Folder & Filter Switching
  // -------------------------------------------------------------------------
  window.selectFolder = function (folder) {
    state.folder = folder;
    state.label = '';
    state.page = 1;
    state.selectedIds.clear();

    document.querySelectorAll('.op-mail-folder-item').forEach(el => el.classList.remove('active'));
    const target = document.getElementById(`opFolderItem_${folder}`);
    if (target) target.classList.add('active');

    const folderTitle = document.getElementById('opCurrentFolderTitle');
    if (folderTitle) folderTitle.textContent = folder.charAt(0).toUpperCase() + folder.slice(1);

    closeReadingPane();
    loadEmails();
  };

  window.selectLabel = function (label) {
    state.label = label;
    state.page = 1;
    state.selectedIds.clear();

    document.querySelectorAll('.op-mail-folder-item').forEach(el => el.classList.remove('active'));
    const target = document.getElementById(`opLabelItem_${label}`);
    if (target) target.classList.add('active');

    const folderTitle = document.getElementById('opCurrentFolderTitle');
    if (folderTitle) folderTitle.textContent = 'Label: ' + label.charAt(0).toUpperCase() + label.slice(1);

    closeReadingPane();
    loadEmails();
  };

  window.setFilterChip = function (type) {
    state.filter = type;
    document.querySelectorAll('.op-filter-chip').forEach(btn => btn.classList.remove('active'));
    const target = document.getElementById(`opChip_${type}`);
    if (target) target.classList.add('active');
    loadEmails();
  };

  window.handleMailSearch = function (query) {
    state.search = query.trim();
    state.page = 1;
    loadEmails();
  };

  // -------------------------------------------------------------------------
  // 5. Floating Composer Modal (Gmail / Outlook style)
  // -------------------------------------------------------------------------
  window.openComposer = function (mode = 'new', prefill = {}) {
    const dock = document.getElementById('opMailComposerModal');
    if (!dock) return;

    dock.style.display = 'flex';
    dock.classList.remove('minimized');

    const titleEl = document.getElementById('opComposerTitle');
    const toInput = document.getElementById('opComposerTo');
    const ccInput = document.getElementById('opComposerCc');
    const bccInput = document.getElementById('opComposerBcc');
    const subjectInput = document.getElementById('opComposerSubject');
    const editor = document.getElementById('opComposerEditor');
    const parentIdInput = document.getElementById('opComposerParentId');

    state.composerAttachments = [];
    renderComposerAttachments();

    if (mode === 'new') {
      if (titleEl) titleEl.textContent = 'New Message';
      if (toInput) toInput.value = prefill.to || '';
      if (ccInput) ccInput.value = '';
      if (bccInput) bccInput.value = '';
      if (subjectInput) subjectInput.value = prefill.subject || '';
      if (editor) editor.innerHTML = '';
      if (parentIdInput) parentIdInput.value = '';
    } else if (mode === 'reply') {
      if (titleEl) titleEl.textContent = 'Reply Message';
      if (toInput) toInput.value = prefill.to || '';
      if (subjectInput) subjectInput.value = prefill.subject || '';
      if (parentIdInput) parentIdInput.value = prefill.parentId || '';
      if (editor) editor.innerHTML = '<br><br><br>';
    } else if (mode === 'forward') {
      if (titleEl) titleEl.textContent = 'Forward Message';
      if (toInput) toInput.value = '';
      if (subjectInput) subjectInput.value = prefill.subject || '';
      if (editor) editor.innerHTML = `<br><br>---------- Forwarded message ---------<br>${prefill.bodyHtml || ''}`;
    }

    if (editor) editor.focus();
  };

  window.closeComposer = function () {
    const dock = document.getElementById('opMailComposerModal');
    if (dock) dock.style.display = 'none';
  };

  window.minimizeComposer = function () {
    const dock = document.getElementById('opMailComposerModal');
    if (dock) dock.classList.toggle('minimized');
  };

  window.maximizeComposer = function () {
    const dock = document.getElementById('opMailComposerModal');
    if (dock) dock.classList.toggle('maximized');
  };

  window.toggleCcBcc = function (field) {
    const row = document.getElementById(`opComposerRow_${field}`);
    if (row) {
      row.style.display = row.style.display === 'none' ? 'flex' : 'none';
    }
  };

  window.formatEditor = function (command, val = null) {
    document.execCommand(command, false, val);
    const editor = document.getElementById('opComposerEditor');
    if (editor) editor.focus();
  };

  window.handleAttachmentPicker = function (event) {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    for (let i = 0; i < files.length; i++) {
      const formData = new FormData();
      formData.append('file', files[i]);

      fetch('/mail/api/upload-attachment/', {
        method: 'POST',
        headers: { 'X-CSRFToken': getCsrfToken() },
        body: formData
      })
        .then(res => res.json())
        .then(att => {
          if (att.id) {
            state.composerAttachments.push(att);
            renderComposerAttachments();
          }
        });
    }
  };

  function renderComposerAttachments() {
    const container = document.getElementById('opComposerAttachmentsList');
    if (!container) return;

    if (state.composerAttachments.length === 0) {
      container.innerHTML = '';
      container.style.display = 'none';
      return;
    }

    container.style.display = 'flex';
    container.innerHTML = state.composerAttachments.map((att, idx) => `
      <div class="op-composer-att-chip">
        <span>${att.icon || '📄'}</span>
        <span>${escapeHtml(att.name)} (${att.size})</span>
        <button type="button" class="op-att-remove-btn" onclick="removeComposerAttachment(${idx})">&times;</button>
      </div>
    `).join('');
  }

  window.removeComposerAttachment = function (idx) {
    state.composerAttachments.splice(idx, 1);
    renderComposerAttachments();
  };

  window.sendMail = function (isDraft = false) {
    if (state.isSending) return;

    const to = (document.getElementById('opComposerTo')?.value || '').trim();
    const cc = (document.getElementById('opComposerCc')?.value || '').trim();
    const bcc = (document.getElementById('opComposerBcc')?.value || '').trim();
    const subject = (document.getElementById('opComposerSubject')?.value || '').trim();
    const editor = document.getElementById('opComposerEditor');
    const bodyHtml = editor ? editor.innerHTML : '';
    const bodyText = editor ? editor.innerText : '';
    const label = document.getElementById('opComposerLabel')?.value || 'work';
    const resModel = document.getElementById('opComposerResModel')?.value || '';
    const resId = document.getElementById('opComposerResId')?.value || 0;
    const resName = document.getElementById('opComposerResName')?.value || '';
    const mailServerId = document.getElementById('opComposerMailServer')?.value || null;

    if (!to && !isDraft) {
      showMailToast('Please specify at least one recipient (To)', true);
      document.getElementById('opComposerTo')?.focus();
      return;
    }

    state.isSending = true;
    showMailToast(isDraft ? 'Saving draft...' : 'Sending message...');

    const payload = {
      email_to: to,
      email_cc: cc,
      email_bcc: bcc,
      subject: subject,
      body_html: bodyHtml,
      body_text: bodyText,
      is_draft: isDraft,
      label: label,
      res_model: resModel,
      res_id: resId,
      res_name: resName,
      mail_server_id: mailServerId,
      attachment_ids: state.composerAttachments.map(a => a.id)
    };

    fetch('/mail/api/compose/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken()
      },
      body: JSON.stringify(payload)
    })
      .then(res => res.json())
      .then(data => {
        state.isSending = false;
        if (data.success) {
          showMailToast(isDraft ? 'Draft saved.' : 'Message sent.');
          closeComposer();
          loadEmails();
        } else {
          showMailToast(data.error || 'Failed to send message', true);
        }
      })
      .catch(err => {
        state.isSending = false;
        showMailToast('Failed to send message', true);
      });
  };

  window.sendInlineReply = function (parentId) {
    const textarea = document.getElementById('opInlineReplyBody');
    if (!textarea) return;
    const text = textarea.value.trim();
    if (!text) {
      showMailToast('Please type a reply message first', true);
      textarea.focus();
      return;
    }

    showMailToast('Sending reply...');

    fetch(`/mail/api/reply/${parentId}/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken()
      },
      body: JSON.stringify({
        body_text: text,
        body_html: `<p>${escapeHtml(text).replace(/\n/g, '<br>')}</p>`
      })
    })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          showMailToast('Reply sent successfully.');
          textarea.value = '';
          openEmail(parentId);
        } else {
          showMailToast(data.error || 'Failed to send reply', true);
        }
      })
      .catch(err => {
        showMailToast('Failed to send reply', true);
      });
  };

  // -------------------------------------------------------------------------
  // 6. Global Keyboard Shortcuts
  // -------------------------------------------------------------------------
  document.addEventListener('keydown', function (e) {
    const activeTag = document.activeElement.tagName.toLowerCase();
    const isEditing = activeTag === 'input' || activeTag === 'textarea' || document.activeElement.isContentEditable;

    if (isEditing) {
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        const composer = document.getElementById('opMailComposerModal');
        if (composer && composer.style.display !== 'none' && !composer.classList.contains('minimized')) {
          sendMail(false);
        }
      }
      return;
    }

    if (e.key === 'c' || e.key === 'C') {
      e.preventDefault();
      openComposer('new');
    } else if (e.key === 'Delete' || e.key === '#') {
      if (state.openedEmailId) {
        singleAction(state.openedEmailId, 'trash');
      } else if (state.selectedIds.size > 0) {
        executeBatchAction('trash');
      }
    } else if (e.key === 'e' || e.key === 'E') {
      if (state.openedEmailId) {
        singleAction(state.openedEmailId, 'archive');
      } else if (state.selectedIds.size > 0) {
        executeBatchAction('archive');
      }
    } else if (e.key === 's' || e.key === 'S') {
      if (state.openedEmailId) {
        toggleStar(state.openedEmailId);
      }
    } else if (e.key === 'Escape') {
      closeComposer();
      if (state.openedEmailId) closeReadingPane();
    }
  });

  // Auto-init on page load
  document.addEventListener('DOMContentLoaded', function () {
    const initialFolder = window.initialMailFolder || 'inbox';
    selectFolder(initialFolder);
  });
})();
