/* ==========================================================================
   Office Pro ERP - Top Bar Popovers & Activities Controller
   ========================================================================== */

(function () {
  'use strict';

  // Global state cache
  window.opMailState = {
    activeConvTab: 'inbox',
    activeActFilter: 'all',
    conversationsData: null,
    activitiesData: null,
    activityTypes: [],
    usersList: [],
    currentUserId: null,
  };

  // Helper to get CSRF token
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  const csrftoken = getCookie('csrftoken') || '';

  // -------------------------------------------------------------------------
  // Initialization & Event Listeners
  // -------------------------------------------------------------------------
  document.addEventListener('DOMContentLoaded', function () {
    initTopbarPopovers();

    // Defer non-critical background polling by 1.5s so user navigation & asset loading is unhindered
    setTimeout(loadTopbarCounters, 1500);

    // Poll counters every 90 seconds while tab is active
    setInterval(function() {
      if (document.visibilityState === 'visible') {
        loadTopbarCounters();
      }
    }, 90000);
  });


  function initTopbarPopovers() {
    const convBtn = document.getElementById('opConversationsBtn');
    const actBtn = document.getElementById('opActivitiesBtn');
    const convDropdown = document.getElementById('opConversationsDropdown');
    const actDropdown = document.getElementById('opActivitiesDropdown');
    const profileDropdown = document.getElementById('profileDropdown');

    if (convBtn && convDropdown) {
      convBtn.addEventListener('click', function (e) {
        e.stopPropagation();
        const isOpen = convDropdown.classList.contains('show');
        closeAllPopovers();
        if (!isOpen) {
          convDropdown.classList.add('show');
          convBtn.classList.add('active');
          loadConversations();
        }
      });
    }

    if (actBtn && actDropdown) {
      actBtn.addEventListener('click', function (e) {
        e.stopPropagation();
        const isOpen = actDropdown.classList.contains('show');
        closeAllPopovers();
        if (!isOpen) {
          actDropdown.classList.add('show');
          actBtn.classList.add('active');
          loadActivities(window.opMailState.activeActFilter);
        }
      });
    }

    // Close on clicking outside
    document.addEventListener('click', function (e) {
      if (convDropdown && !convDropdown.contains(e.target) && convBtn && !convBtn.contains(e.target)) {
        convDropdown.classList.remove('show');
        if (convBtn) convBtn.classList.remove('active');
      }
      if (actDropdown && !actDropdown.contains(e.target) && actBtn && !actBtn.contains(e.target)) {
        actDropdown.classList.remove('show');
        if (actBtn) actBtn.classList.remove('active');
      }
    });

    // Prevent popover clicks from bubbling to document
    if (convDropdown) convDropdown.addEventListener('click', function (e) { e.stopPropagation(); });
    if (actDropdown) actDropdown.addEventListener('click', function (e) { e.stopPropagation(); });
  }

  function closeAllPopovers() {
    document.querySelectorAll('.topbar-popover.show').forEach(p => p.classList.remove('show'));
    document.querySelectorAll('.topbar-icon-btn.active').forEach(b => b.classList.remove('active'));
    const profileDropdown = document.getElementById('profileDropdown');
    if (profileDropdown) profileDropdown.classList.remove('show');
    const switcherDropdown = document.getElementById('switcherUserDropdown');
    if (switcherDropdown) switcherDropdown.classList.remove('show');
  }

  // -------------------------------------------------------------------------
  // Fetch Topbar Counters (Badges) via ultra-lightweight endpoint (<15ms)
  // -------------------------------------------------------------------------
  window.loadTopbarCounters = function () {
    fetch('/mail/counters/')
      .then(r => r.json())
      .then(data => {
        if (data.status === 'success') {
          updateConversationsBadge(data.unread_count || 0);
          updateActivitiesBadge(data.total_pending || 0, data.overdue_count || 0);
          updateActivityChips(data);
        }
      })
      .catch(err => console.debug('Counters load err:', err));
  };


  function updateConversationsBadge(count) {
    const badge = document.getElementById('opConversationsBadge');
    if (!badge) return;
    if (count > 0) {
      badge.textContent = count > 99 ? '99+' : count;
      badge.className = 'topbar-badge badge-purple';
      badge.style.display = 'flex';
    } else {
      badge.style.display = 'none';
    }
  }

  function updateActivitiesBadge(total, overdue) {
    const badge = document.getElementById('opActivitiesBadge');
    if (!badge) return;
    if (total > 0) {
      badge.textContent = total > 99 ? '99+' : total;
      badge.className = overdue > 0 ? 'topbar-badge' : 'topbar-badge badge-amber';
      badge.style.display = 'flex';
    } else {
      badge.style.display = 'none';
    }
  }

  function updateActivityChips(data) {
    const chipAll = document.getElementById('opActChipAll');
    const chipOverdue = document.getElementById('opActChipOverdue');
    const chipToday = document.getElementById('opActChipToday');
    const chipPlanned = document.getElementById('opActChipPlanned');

    if (chipAll) chipAll.textContent = data.total_pending || 0;
    if (chipOverdue) chipOverdue.textContent = data.overdue_count || 0;
    if (chipToday) chipToday.textContent = data.today_count || 0;
    if (chipPlanned) chipPlanned.textContent = data.planned_count || 0;
  }

  // -------------------------------------------------------------------------
  // Conversations Popover Rendering & Actions
  // -------------------------------------------------------------------------
  window.loadConversations = function () {
    const listEl = document.getElementById('opConversationsList');
    if (!listEl) return;

    fetch('/mail/conversations/')
      .then(r => r.json())
      .then(data => {
        if (data.status === 'success') {
          window.opMailState.conversationsData = data;
          window.opMailState.usersList = data.users || [];
          updateConversationsBadge(data.unread_count || 0);
          populateRecipientSelect(data.users || []);
          renderConversationsTab(window.opMailState.activeConvTab);

        }
      })
      .catch(err => {
        if (listEl) listEl.innerHTML = `<div class="op-popover-empty">Failed to load conversations.</div>`;
      });
  };

  window.switchConvTab = function (tabName) {
    window.opMailState.activeConvTab = tabName;
    document.querySelectorAll('.op-popover-tab').forEach(t => {
      t.classList.toggle('active', t.dataset.tab === tabName);
    });
    renderConversationsTab(tabName);
  };

  function renderConversationsTab(tabName) {
    const listEl = document.getElementById('opConversationsList');
    if (!listEl || !window.opMailState.conversationsData) return;

    const data = window.opMailState.conversationsData;
    const searchVal = (document.getElementById('opConvSearchInput')?.value || '').toLowerCase().trim();

    if (tabName === 'inbox') {
      let items = data.inbox || [];
      if (searchVal) {
        items = items.filter(m =>
          (m.author_name && m.author_name.toLowerCase().includes(searchVal)) ||
          (m.body && m.body.toLowerCase().includes(searchVal)) ||
          (m.subject && m.subject.toLowerCase().includes(searchVal))
        );
      }
      if (!items.length) {
        listEl.innerHTML = `<div class="op-popover-empty">&#128236; No messages in your inbox.</div>`;
        return;
      }
      listEl.innerHTML = items.map(m => `
        <div class="op-msg-item ${!m.is_read ? 'unread' : ''}" onclick="markMessageRead(${m.id})">
          <div class="op-msg-avatar avatar-user">${escapeHtml(m.author_avatar || 'U')}</div>
          <div class="op-msg-content">
            <div class="op-msg-header">
              <span class="op-msg-author">${escapeHtml(m.author_name || 'User')}</span>
              <span class="op-msg-time">${escapeHtml(m.created_at_human || m.created_at)}</span>
            </div>
            ${m.subject ? `<div style="font-size: 12px; font-weight: 600; color: #1e293b;">${escapeHtml(m.subject)}</div>` : ''}
            <div class="op-msg-snippet">${escapeHtml(m.body || '')}</div>
          </div>
        </div>
      `).join('');
    } else if (tabName === 'chatter') {
      let items = data.chatter_stream || [];
      if (searchVal) {
        items = items.filter(m =>
          (m.author_name && m.author_name.toLowerCase().includes(searchVal)) ||
          (m.body && m.body.toLowerCase().includes(searchVal)) ||
          (m.model_name && m.model_name.toLowerCase().includes(searchVal))
        );
      }
      if (!items.length) {
        listEl.innerHTML = `<div class="op-popover-empty">&#128221; No recent record chatter notes.</div>`;
        return;
      }
      listEl.innerHTML = items.map(m => `
        <div class="op-msg-item" onclick="if ('${m.record_url}' !== '#') window.location.href='${m.record_url}'">
          <div class="op-msg-avatar ${m.message_type === 'note' ? 'avatar-note' : ''}">${escapeHtml(m.author_avatar || 'S')}</div>
          <div class="op-msg-content">
            <div class="op-msg-header">
              <span class="op-msg-author">${escapeHtml(m.author_name || 'System')}</span>
              <span class="op-msg-time">${escapeHtml(m.created_at_human || m.created_at)}</span>
            </div>
            <div class="op-msg-target">
              &#128193; ${escapeHtml(m.model_name)} #${m.record_id} &rarr;
            </div>
            <div class="op-msg-snippet">${escapeHtml(m.body || '')}</div>
          </div>
        </div>
      `).join('');
    } else if (tabName === 'direct') {
      let users = data.users || [];
      if (searchVal) {
        users = users.filter(u =>
          (u.username && u.username.toLowerCase().includes(searchVal)) ||
          (u.name && u.name.toLowerCase().includes(searchVal)) ||
          (u.email && u.email.toLowerCase().includes(searchVal))
        );
      }
      if (!users.length) {
        listEl.innerHTML = `<div class="op-popover-empty">&#128101; No other users registered.</div>`;
        return;
      }
      listEl.innerHTML = users.map(u => `
        <div class="op-user-card" onclick="startDirectChat(${u.id}, '${escapeHtml(u.username)}')">
          <div class="op-user-info">
            <div class="op-msg-avatar avatar-user">${escapeHtml(u.avatar || 'U')}</div>
            <div>
              <div class="op-user-name">${escapeHtml(u.name || u.username)}</div>
              <div class="op-user-email">${escapeHtml(u.email || '')} &bull; ${escapeHtml(u.role || 'User')}</div>
            </div>
          </div>
          <button type="button" class="op-popover-header-btn">&#9998; Chat</button>
        </div>
      `).join('');
    }
  }

  window.filterConversations = function (val) {
    renderConversationsTab(window.opMailState.activeConvTab);
  };

  window.toggleConversationsComposer = function (show) {
    const box = document.getElementById('opConvComposerBox');
    if (!box) return;
    if (show === undefined) {
      box.style.display = box.style.display === 'none' ? 'flex' : 'none';
    } else {
      box.style.display = show ? 'flex' : 'none';
    }
    if (box.style.display === 'flex') {
      const textarea = document.getElementById('opConvBody');
      if (textarea) textarea.focus();
    }
  };

  function populateRecipientSelect(users) {
    const sel = document.getElementById('opConvRecipientSelect');
    if (!sel) return;
    const currentVal = sel.value;
    sel.innerHTML = `<option value="">Select colleague...</option>` +
      users.map(u => `<option value="${u.id}">${escapeHtml(u.name || u.username)} (${escapeHtml(u.email)})</option>`).join('');
    if (currentVal) sel.value = currentVal;
  }

  window.startDirectChat = function (userId, username) {
    toggleConversationsComposer(true);
    const sel = document.getElementById('opConvRecipientSelect');
    if (sel) sel.value = userId;
    const textarea = document.getElementById('opConvBody');
    if (textarea) {
      textarea.placeholder = `Write message to ${username}...`;
      textarea.focus();
    }
  };

  window.sendDirectMessage = function () {
    const sel = document.getElementById('opConvRecipientSelect');
    const bodyEl = document.getElementById('opConvBody');
    const recipientId = sel ? sel.value : '';
    const body = bodyEl ? bodyEl.value.trim() : '';

    if (!recipientId) {
      alert('Please select a recipient.');
      return;
    }
    if (!body) {
      alert('Please enter a message body.');
      return;
    }

    const formData = new FormData();
    formData.append('recipient_id', recipientId);
    formData.append('body', body);

    fetch('/mail/direct-message/send/', {
      method: 'POST',
      body: formData,
      headers: { 'X-CSRFToken': csrftoken }
    })
      .then(r => r.json())
      .then(data => {
        if (data.status === 'success') {
          if (bodyEl) bodyEl.value = '';
          toggleConversationsComposer(false);
          loadConversations();
          switchConvTab('inbox');
        } else {
          alert('Error sending message: ' + (data.message || 'Unknown'));
        }
      })
      .catch(err => alert('Network error sending message.'));
  };

  window.markMessageRead = function (msgId) {
    fetch(`/mail/messages/${msgId}/mark-read/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': csrftoken }
    })
      .then(r => r.json())
      .then(data => {
        if (data.status === 'success') {
          updateConversationsBadge(data.unread_count || 0);
          if (window.opMailState.conversationsData && window.opMailState.conversationsData.inbox) {
            const item = window.opMailState.conversationsData.inbox.find(m => m.id === msgId);
            if (item) item.is_read = true;
          }
          renderConversationsTab(window.opMailState.activeConvTab);
        }
      });
  };

  window.markAllMessagesRead = function () {
    fetch('/mail/messages/mark-all-read/', {
      method: 'POST',
      headers: { 'X-CSRFToken': csrftoken }
    })
      .then(r => r.json())
      .then(data => {
        if (data.status === 'success') {
          updateConversationsBadge(0);
          if (window.opMailState.conversationsData && window.opMailState.conversationsData.inbox) {
            window.opMailState.conversationsData.inbox.forEach(m => m.is_read = true);
          }
          renderConversationsTab(window.opMailState.activeConvTab);
        }
      });
  };

  // -------------------------------------------------------------------------
  // Activities Popover Rendering & Actions
  // -------------------------------------------------------------------------
  window.loadActivities = function (filter) {
    const listEl = document.getElementById('opActivitiesList');
    if (!listEl) return;

    filter = filter || window.opMailState.activeActFilter || 'all';

    fetch(`/mail/activities/?filter=${filter}`)
      .then(r => r.json())
      .then(data => {
        if (data.status === 'success') {
          window.opMailState.activitiesData = data;
          updateActivitiesBadge(data.total_pending || 0, data.overdue_count || 0);
          updateActivityChips(data);
          renderActivitiesList(data.activities || []);
        }
      })
      .catch(err => {
        if (listEl) listEl.innerHTML = `<div class="op-popover-empty">Failed to load activities.</div>`;
      });
  };

  window.switchActivityFilter = function (filterName) {
    window.opMailState.activeActFilter = filterName;
    document.querySelectorAll('.op-chip-filter').forEach(c => {
      c.classList.toggle('active', c.dataset.filter === filterName);
    });
    loadActivities(filterName);
  };

  function renderActivitiesList(activities) {
    const listEl = document.getElementById('opActivitiesList');
    if (!listEl) return;

    if (!activities.length) {
      listEl.innerHTML = `<div class="op-popover-empty">&#9989; No scheduled activities found for this filter.</div>`;
      return;
    }

    listEl.innerHTML = activities.map(act => `
      <div class="op-act-item" id="opActItem_${act.id}">
        <div class="op-act-top">
          <span class="op-act-type-chip">${escapeHtml(act.type_icon)} ${escapeHtml(act.type_name)}</span>
          <span class="op-act-due-badge ${act.due_badge_class}">${escapeHtml(act.due_text)}</span>
        </div>
        <div class="op-act-summary">${escapeHtml(act.summary)}</div>
        ${act.res_model && act.res_model !== 'general' ? `
          <a href="${act.record_url}" class="op-act-record-link">&#128193; ${escapeHtml(act.res_name)} &nearr;</a>
        ` : ''}
        ${act.note ? `<div class="op-act-note">${escapeHtml(act.note)}</div>` : ''}
        ${act.feedback ? `<div class="op-act-note" style="color: #059669;"><strong>Feedback:</strong> ${escapeHtml(act.feedback)}</div>` : ''}
        
        <div class="op-act-footer">
          <span class="op-act-assignee">Assigned to: <strong>${escapeHtml(act.assigned_to)}</strong></span>
          <div class="op-act-actions">
            ${act.state === 'planned' ? `
              <button type="button" class="op-act-btn op-act-btn-done" onclick="openActivityDoneModal(${act.id}, '${escapeHtml(act.summary)}')">&#10003; Done</button>
              <button type="button" class="op-act-btn op-act-btn-cancel" onclick="cancelActivity(${act.id})">&#10005; Cancel</button>
            ` : `
              <span style="font-size: 11px; font-weight: 600; color: #059669;">&#9989; Completed</span>
            `}
          </div>
        </div>
      </div>
    `).join('');
  }

  // -------------------------------------------------------------------------
  // Schedule Activity Modal Functions
  // -------------------------------------------------------------------------
  function loadActivityTypes() {
    fetch('/mail/activities/types/')
      .then(r => r.json())
      .then(data => {
        if (data.status === 'success') {
          window.opMailState.activityTypes = data.activity_types || [];
          populateActivityTypeSelect();
        }
      });
  }

  function populateActivityTypeSelect() {
    const sel = document.getElementById('opActTypeSelect');
    if (!sel || !window.opMailState.activityTypes) return;
    sel.innerHTML = window.opMailState.activityTypes.map(t =>
      `<option value="${t.id}" data-days="${t.default_next_days}">${escapeHtml(t.icon)} ${escapeHtml(t.name)}</option>`
    ).join('');
  }

  function populateAssigneeSelect() {
    const sel = document.getElementById('opActAssigneeSelect');
    if (!sel || !window.opMailState.usersList) return;
    const users = window.opMailState.usersList;
    sel.innerHTML = users.map(u =>
      `<option value="${u.id}">${escapeHtml(u.name || u.username)}</option>`
    ).join('');
  }

  window.openScheduleActivityModal = function (modelName, recordId, recordName) {
    const modal = document.getElementById('opScheduleActivityModal');
    if (!modal) return;

    closeAllPopovers();
    modal.style.display = 'flex';

    if (!window.opMailState.activityTypes || !window.opMailState.activityTypes.length) {
      loadActivityTypes();
    } else {
      populateActivityTypeSelect();
    }
    populateAssigneeSelect();


    // Default target model/id/name
    document.getElementById('opActResModel').value = modelName || 'general';
    document.getElementById('opActResId').value = recordId || 0;
    document.getElementById('opActResName').value = recordName || '';

    const targetDisplay = document.getElementById('opActTargetDisplay');
    if (targetDisplay) {
      targetDisplay.value = (modelName && modelName !== 'general') ? `${modelName} #${recordId} (${recordName || 'Record'})` : 'General ERP Task';
    }

    // Reset summary and note
    document.getElementById('opActSummary').value = '';
    document.getElementById('opActNote').value = '';

    // Set default due date
    const typeSel = document.getElementById('opActTypeSelect');
    if (typeSel && typeSel.options[0]) {
      const days = parseInt(typeSel.options[0].dataset.days || 0, 10);
      setQuickDueDate(days);
    } else {
      setQuickDueDate(0);
    }
  };

  window.closeScheduleActivityModal = function () {
    const modal = document.getElementById('opScheduleActivityModal');
    if (modal) modal.style.display = 'none';
  };

  window.handleActivityTypeChange = function (sel) {
    const opt = sel.options[sel.selectedIndex];
    if (opt) {
      const days = parseInt(opt.dataset.days || 0, 10);
      setQuickDueDate(days);
    }
  };

  window.setQuickDueDate = function (daysFromNow) {
    const d = new Date();
    d.setDate(d.getDate() + daysFromNow);
    const dateStr = d.toISOString().split('T')[0];
    const input = document.getElementById('opActDateDeadline');
    if (input) input.value = dateStr;
  };

  window.handleScheduleActivitySubmit = function (e) {
    e.preventDefault();
    const form = document.getElementById('opScheduleActivityForm');
    const formData = new FormData(form);

    fetch('/mail/activities/create/', {
      method: 'POST',
      body: formData,
      headers: { 'X-CSRFToken': csrftoken }
    })
      .then(r => r.json())
      .then(data => {
        if (data.status === 'success') {
          closeScheduleActivityModal();
          loadTopbarCounters();
          loadActivities(window.opMailState.activeActFilter);
          // If on a record page with a chatter feed, refresh chatter or reload
          const chatterFeed = document.getElementById('chatterFeed');
          if (chatterFeed && formData.get('res_model') !== 'general') {
            // Quick reload or append
            window.location.reload();
          }
        } else {
          alert('Failed to schedule activity: ' + (data.message || 'Unknown'));
        }
      })
      .catch(err => alert('Network error scheduling activity.'));
  };

  // -------------------------------------------------------------------------
  // Complete Activity / Done Feedback Modal
  // -------------------------------------------------------------------------
  window.openActivityDoneModal = function (activityId, summary) {
    const modal = document.getElementById('opActivityDoneModal');
    if (!modal) return;
    modal.style.display = 'flex';
    document.getElementById('opDoneActId').value = activityId;
    document.getElementById('opDoneActTitle').textContent = `Action: "${summary}"`;
    document.getElementById('opDoneFeedback').value = '';
    document.getElementById('opDoneFeedback').focus();
  };

  window.closeActivityDoneModal = function () {
    const modal = document.getElementById('opActivityDoneModal');
    if (modal) modal.style.display = 'none';
  };

  window.handleActivityDoneSubmit = function (e) {
    e.preventDefault();
    const actId = document.getElementById('opDoneActId').value;
    const feedback = document.getElementById('opDoneFeedback').value.trim();

    const formData = new FormData();
    formData.append('feedback', feedback);

    fetch(`/mail/activities/${actId}/done/`, {
      method: 'POST',
      body: formData,
      headers: { 'X-CSRFToken': csrftoken }
    })
      .then(r => r.json())
      .then(data => {
        if (data.status === 'success') {
          closeActivityDoneModal();
          loadTopbarCounters();
          loadActivities(window.opMailState.activeActFilter);
        } else {
          alert('Failed to complete activity: ' + (data.message || 'Unknown'));
        }
      })
      .catch(err => alert('Network error completing activity.'));
  };

  window.cancelActivity = function (actId) {
    if (!confirm('Are you sure you want to cancel this activity?')) return;

    fetch(`/mail/activities/${actId}/cancel/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': csrftoken }
    })
      .then(r => r.json())
      .then(data => {
        if (data.status === 'success') {
          loadTopbarCounters();
          loadActivities(window.opMailState.activeActFilter);
        } else {
          alert('Failed to cancel activity: ' + (data.message || 'Unknown'));
        }
      })
      .catch(err => alert('Network error cancelling activity.'));
  };

  // String escaper
  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

})();
