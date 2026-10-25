/**
 * Office Pro - Universal Kanban Drag and Drop & Board Controls Module
 * Handles:
 * 1. Drag and drop record cards between grouped columns (departments, statuses, etc.) with optimistic UI updates.
 * 2. Column folding and unfolding with ~48px width, vertical label, count badge, and localStorage persistence.
 * 3. Column gear (⚙) options dropdown menu.
 * 4. Inline "＋ Add Column" panel for dynamic creation of stages/departments without page reload.
 *
 * Proprietary and Confidential - Copyright (c) 2026 Dumbare Chaitanya.
 */

(function () {
  'use strict';

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

  function showToast(message, type = 'success') {
    let toastContainer = document.getElementById('opKanbanToastContainer');
    if (!toastContainer) {
      toastContainer = document.createElement('div');
      toastContainer.id = 'opKanbanToastContainer';
      toastContainer.style.cssText = 'position: fixed; bottom: 24px; right: 24px; z-index: 99999; display: flex; flex-direction: column; gap: 8px; pointer-events: none;';
      document.body.appendChild(toastContainer);
    }

    const toast = document.createElement('div');
    const isSuccess = type === 'success';
    toast.style.cssText = `
      padding: 10px 16px;
      border-radius: 6px;
      font-size: 13px;
      font-weight: 600;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      box-shadow: 0 4px 12px rgba(0,0,0,0.12);
      display: flex;
      align-items: center;
      gap: 8px;
      pointer-events: auto;
      transition: opacity 0.25s, transform 0.25s;
      transform: translateY(10px);
      opacity: 0;
      background: ${isSuccess ? '#0f172a' : '#ef4444'};
      color: #ffffff;
      border-left: 4px solid ${isSuccess ? '#10b981' : '#b91c1c'};
    `;
    toast.innerHTML = `<span>${isSuccess ? '✓' : '⚠️'}</span><span>${message}</span>`;
    toastContainer.appendChild(toast);

    requestAnimationFrame(() => {
      toast.style.transform = 'translateY(0)';
      toast.style.opacity = '1';
    });

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(10px)';
      setTimeout(() => toast.remove(), 250);
    }, 3200);
  }

  function updateColumnCount(columnEl, delta) {
    if (!columnEl) return;
    const countEl = columnEl.querySelector('.op-column-count, .op-kanban-column-header span:nth-child(2)');
    const foldedBadge = columnEl.querySelector('.op-column-folded-badge');
    let newCount = 0;

    if (countEl) {
      const match = countEl.textContent.match(/\d+/);
      if (match) {
        const currentCount = parseInt(match[0], 10);
        newCount = Math.max(0, currentCount + delta);
        countEl.textContent = `(${newCount})`;
      }
    }
    if (foldedBadge) {
      foldedBadge.textContent = `(${newCount})`;
    }
  }

  function ensurePlaceholder(dropZone) {
    if (!dropZone) return;
    const hasCards = dropZone.querySelector('.emp-kanban-panel-card, .leave-kanban-card, [data-kanban-card]');
    let ph = dropZone.querySelector('.op-empty-column-placeholder');
    if (!hasCards && !ph) {
      ph = document.createElement('div');
      ph.className = 'op-empty-column-placeholder';
      ph.style.cssText = 'border: 2px dashed #cbd5e1; border-radius: 8px; padding: 32px 16px; text-align: center; color: #94a3b8; font-size: 13px; font-weight: 500; background: #f8fafc; pointer-events: none; margin-top: 4px;';
      ph.textContent = 'Drop cards here';
      dropZone.appendChild(ph);
    }
  }

  function removePlaceholder(dropZone) {
    if (!dropZone) return;
    const ph = dropZone.querySelector('.op-empty-column-placeholder');
    if (ph) ph.remove();
  }

  // --- Fold / Storage Utilities ---
  function getColumnStorageKey(col) {
    const board = col.closest('.op-kanban-board');
    const modelKey = board?.getAttribute('data-model') || 'kanban';
    const groupField = col.getAttribute('data-group-field') || board?.getAttribute('data-group-by') || 'col';
    const groupVal = col.getAttribute('data-group-value') || col.getAttribute('data-group-label') || '';
    return `op_kanban_folded_${modelKey}_${groupField}_${groupVal}`;
  }

  function foldKanbanColumn(btn) {
    const col = btn.closest('.op-kanban-column');
    if (!col) return;
    col.classList.add('op-column-folded');
    const menu = col.querySelector('.op-column-menu');
    if (menu) menu.style.display = 'none';
    try {
      const key = getColumnStorageKey(col);
      localStorage.setItem(key, '1');
    } catch (e) {}
  }

  function unfoldKanbanColumn(col) {
    if (!col) return;
    col.classList.remove('op-column-folded');
    try {
      const key = getColumnStorageKey(col);
      localStorage.removeItem(key);
    } catch (e) {}
  }

  function toggleColumnMenu(event, btn) {
    if (event) {
      event.stopPropagation();
      event.preventDefault();
    }
    const container = btn.closest('.op-column-header-actions') || btn.parentElement;
    const menu = container ? container.querySelector('.op-column-menu') : null;
    if (!menu) return;
    const isShown = menu.style.display === 'block';
    document.querySelectorAll('.op-column-menu').forEach(m => m.style.display = 'none');
    menu.style.display = isShown ? 'none' : 'block';
  }

  // --- Inline Add Column Utilities ---
  function showInlineAddColumn(btn) {
    const panel = btn.closest('.op-kanban-add-column-panel');
    if (!panel) return;
    const triggerBtn = panel.querySelector('.op-add-column-trigger-btn');
    const form = panel.querySelector('.op-add-column-form');
    const input = panel.querySelector('.op-add-column-input');
    if (triggerBtn) triggerBtn.style.display = 'none';
    if (form) form.style.display = 'block';
    if (input) {
      input.value = '';
      input.focus();
    }
  }

  function cancelAddColumn(btn) {
    const panel = btn.closest('.op-kanban-add-column-panel');
    if (!panel) return;
    const triggerBtn = panel.querySelector('.op-add-column-trigger-btn');
    const form = panel.querySelector('.op-add-column-form');
    const input = panel.querySelector('.op-add-column-input');
    if (form) form.style.display = 'none';
    if (triggerBtn) triggerBtn.style.display = 'flex';
    if (input) input.value = '';
  }

  function handleColumnInputKey(event, input) {
    if (event.key === 'Enter') {
      event.preventDefault();
      confirmAddColumn(input);
    } else if (event.key === 'Escape') {
      event.preventDefault();
      cancelAddColumn(input);
    }
  }

  function confirmAddColumn(el) {
    const panel = el.closest('.op-kanban-add-column-panel');
    const board = panel ? panel.closest('.op-kanban-board') : document.querySelector('.op-kanban-board');
    if (!panel || !board) return;

    const input = panel.querySelector('.op-add-column-input');
    const title = (input?.value || '').trim();
    if (!title) {
      input?.focus();
      return;
    }

    const modelKey = panel.getAttribute('data-model') || board.getAttribute('data-model') || 'hr.employee';
    const groupBy = panel.getAttribute('data-group-by') || board.getAttribute('data-group-by') || 'department';
    const csrfToken = getCookie('csrftoken') || document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';

    const addBtn = panel.querySelector('.op-btn-add-col');
    if (addBtn) addBtn.disabled = true;

    fetch('/api/kanban-add-column/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
      },
      body: JSON.stringify({
        model_key: modelKey,
        group_by: groupBy,
        title: title
      })
    })
    .then(res => res.json())
    .then(data => {
      if (addBtn) addBtn.disabled = false;
      if (data.success) {
        const colTitle = data.title || title;
        const rawVal = data.raw_val || colTitle;

        const newCol = document.createElement('div');
        newCol.className = 'op-kanban-column';
        newCol.setAttribute('data-group-field', groupBy);
        newCol.setAttribute('data-group-value', rawVal);
        newCol.setAttribute('data-group-label', colTitle);
        newCol.style.cssText = panel.style.width ? `width: ${panel.style.width}; min-width: ${panel.style.minWidth || panel.style.width}; flex-shrink: 0; display: flex; flex-direction: column;` : 'width: 280px; min-width: 280px; flex-shrink: 0; display: flex; flex-direction: column;';

        newCol.innerHTML = `
          <div class="op-kanban-column-header" style="display: flex; justify-content: space-between; align-items: center; padding: 6px 4px 10px 4px; border-bottom: 2px solid #e2e8f0; margin-bottom: 12px; position: relative;">
            <div style="font-size: 14px; font-weight: 700; color: #0f172a;">
              <span>${colTitle}</span>
              <span class="op-column-count" style="color: #64748b; font-weight: 600; margin-left: 4px;">(0)</span>
            </div>
            <div class="op-column-header-actions" style="display: flex; align-items: center; gap: 4px; position: relative;">
              <button type="button" class="op-column-gear-btn" title="Column Options" onclick="toggleColumnMenu(event, this)">⚙</button>
              <div class="op-column-menu" style="display: none;">
                <button type="button" class="op-column-menu-item" onclick="foldKanbanColumn(this)">⇥ Fold Column</button>
              </div>
            </div>
          </div>

          <div class="op-column-folded-view" style="display: none;" onclick="unfoldKanbanColumn(this.closest('.op-kanban-column'))" title="Click to unfold">
            <span class="op-column-folded-badge">(0)</span>
            <span class="op-column-folded-title">${colTitle}</span>
            <span class="op-column-folded-icon">▸</span>
          </div>

          <div class="op-kanban-column-cards" style="display: flex; flex-direction: column; gap: 10px; min-height: 180px; flex: 1; border-radius: 6px; padding: 4px; transition: background 0.15s ease;">
            <div class="op-empty-column-placeholder" style="border: 2px dashed #cbd5e1; border-radius: 8px; padding: 32px 16px; text-align: center; color: #94a3b8; font-size: 13px; font-weight: 500; background: #f8fafc; pointer-events: none; margin-top: 4px;">
              Drop cards here
            </div>
          </div>
        `;

        board.insertBefore(newCol, panel);

        // Bind drag-and-drop drop-zone listeners on newly added column
        if (window._opKanbanDragContext) {
          attachColumnDropListeners(newCol, board, window._opKanbanDragContext);
        }

        cancelAddColumn(panel);
        showToast(data.message || `Column '${colTitle}' added.`, 'success');
      } else {
        showToast(data.error || 'Failed to add column.', 'error');
      }
    })
    .catch(err => {
      if (addBtn) addBtn.disabled = false;
      showToast(`Error: ${err.message}`, 'error');
    });
  }

  // --- Attach Drop Target to Column ---
  function attachColumnDropListeners(col, board, dragCtx) {
    const dropZone = col.querySelector('.op-kanban-column-cards') || col;

    col.addEventListener('dragover', (e) => {
      e.preventDefault();
      e.dataTransfer.dropEffect = 'move';
      if (!col.classList.contains('op-kanban-column-dragover')) {
        col.classList.add('op-kanban-column-dragover');
      }
    });

    col.addEventListener('dragleave', (e) => {
      if (!col.contains(e.relatedTarget)) {
        col.classList.remove('op-kanban-column-dragover');
      }
    });

    col.addEventListener('drop', (e) => {
      e.preventDefault();
      col.classList.remove('op-kanban-column-dragover');

      if (!dragCtx.draggedCard || !dragCtx.sourceColumn) return;
      if (dragCtx.sourceColumn === col) return; // Dropped in same column

      let dragData = {};
      try {
        const raw = e.dataTransfer.getData('text/plain');
        if (raw) dragData = JSON.parse(raw);
      } catch (err) {}

      const recordId = dragData.recordId || dragCtx.draggedCard.getAttribute('data-record-id') || (dragCtx.draggedCard.id ? dragCtx.draggedCard.id.replace(/\D/g, '') : null);
      const modelKey = dragData.modelKey || dragCtx.draggedCard.getAttribute('data-model') || board.getAttribute('data-model') || 'hr.employee';
      const groupField = dragData.groupField || board.getAttribute('data-group-by') || col.getAttribute('data-group-field') || 'department';

      const targetGroupVal = col.getAttribute('data-group-value') || col.getAttribute('data-group-label') || col.querySelector('.op-kanban-column-header span')?.textContent.trim();
      const targetGroupLabel = col.getAttribute('data-group-label') || targetGroupVal;

      if (!recordId) {
        console.warn('[Kanban] No recordId found on dragged card.');
        return;
      }

      // 1. Optimistic DOM update: Move card into target column
      const originalParent = dragCtx.draggedCard.parentNode;
      const originalNextSibling = dragCtx.draggedCard.nextSibling;
      const fromDropZone = dragCtx.sourceDropZone;
      const sourceCol = dragCtx.sourceColumn;
      const movedCard = dragCtx.draggedCard;

      removePlaceholder(dropZone);
      dropZone.appendChild(movedCard);
      ensurePlaceholder(fromDropZone);

      // 2. Optimistic Counters update
      updateColumnCount(sourceCol, -1);
      updateColumnCount(col, +1);

      // 3. Send update to backend API
      const csrfToken = getCookie('csrftoken') || document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';

      fetch('/api/kanban-move/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        body: JSON.stringify({
          model_key: modelKey,
          record_id: recordId,
          field_name: groupField,
          new_value: targetGroupVal
        })
      })
      .then((res) => {
        if (!res.ok) {
          return res.json().then((errData) => {
            throw new Error(errData.error || `HTTP ${res.status}`);
          });
        }
        return res.json();
      })
      .then((data) => {
        if (data.success) {
          movedCard.classList.add('op-card-moved-success');
          setTimeout(() => movedCard?.classList.remove('op-card-moved-success'), 1200);

          // Update badge & buttons if moving a Leave Request
          if (modelKey.includes('leave')) {
            const ribbon = movedCard.querySelector('.op-ribbon');
            if (ribbon && data.display_label) {
              ribbon.textContent = data.display_label;
              ribbon.className = 'op-ribbon';
              if (data.new_value === 'validate' || data.new_value === 'Approved') {
                ribbon.classList.add('op-ribbon-approved');
              } else if (data.new_value === 'refuse' || data.new_value === 'Refused') {
                ribbon.classList.add('op-ribbon-refused');
              } else {
                ribbon.classList.add('op-ribbon-to-approve');
              }
            }

            // Update footer action area
            const footer = movedCard.querySelector('.leave-card-footer') || movedCard.querySelector('[style*="border-top"]');
            if (footer) {
              if (data.new_value === 'validate' || data.new_value === 'Approved') {
                footer.innerHTML = '<div style="font-size: 11.5px; color: #059669; font-weight: 600; display: flex; align-items: center; gap: 4px;"><span>&#10004; Approved</span></div>';
              } else if (data.new_value === 'refuse' || data.new_value === 'Refused') {
                footer.innerHTML = '<div style="font-size: 11.5px; color: #dc2626; font-weight: 600;"><span>&#10006; Refused</span></div>';
              }
            }
          }

          showToast(data.message || `Moved to ${targetGroupLabel}`, 'success');
        } else {
          throw new Error(data.error || 'Server rejected the update.');
        }
      })
      .catch((err) => {
        console.error('[Kanban Move Error]:', err);
        // Revert card back to original column
        if (originalNextSibling) {
          originalParent.insertBefore(movedCard, originalNextSibling);
        } else {
          originalParent.appendChild(movedCard);
        }
        removePlaceholder(fromDropZone);
        ensurePlaceholder(dropZone);

        // Revert counts
        updateColumnCount(sourceCol, +1);
        updateColumnCount(col, -1);

        showToast(`Could not move card: ${err.message}`, 'error');
      });
    });
  }

  // --- Main Board Initializer ---
  function initKanbanDragDrop() {
    const board = document.querySelector('.op-kanban-board');
    if (!board) return;

    // Inject styles if not already present
    if (!document.getElementById('opKanbanDnDStyles')) {
      const styleEl = document.createElement('style');
      styleEl.id = 'opKanbanDnDStyles';
      styleEl.textContent = `
        /* Draggable Cards */
        .op-kanban-card-draggable {
          cursor: grab !important;
          user-select: none;
          touch-action: none;
        }
        .op-kanban-card-draggable:active {
          cursor: grabbing !important;
        }
        .op-kanban-card-dragging {
          opacity: 0.35 !important;
          transform: scale(0.97) !important;
          box-shadow: 0 8px 20px rgba(0,0,0,0.18) !important;
        }
        .op-kanban-column-dragover {
          background: rgba(2, 132, 199, 0.06) !important;
          outline: 2px dashed #0284c7 !important;
          outline-offset: -2px;
          border-radius: 8px !important;
        }
        @keyframes opCardSuccessPulse {
          0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
          70% { box-shadow: 0 0 0 8px rgba(16, 185, 129, 0); }
          100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
        }
        .op-card-moved-success {
          animation: opCardSuccessPulse 1s ease-out;
        }

        /* Column Header actions & Gear menu */
        .op-column-header-actions {
          display: flex;
          align-items: center;
          gap: 4px;
          position: relative;
        }
        .op-column-plus-btn {
          text-decoration: none;
          color: #64748b;
          font-size: 18px;
          font-weight: 400;
          line-height: 1;
          padding: 2px 5px;
          border-radius: 4px;
          transition: background 0.15s, color 0.15s;
        }
        .op-column-plus-btn:hover {
          background: #f1f5f9;
          color: #0f172a;
        }
        .op-column-gear-btn {
          background: transparent;
          border: none;
          color: #64748b;
          font-size: 15px;
          line-height: 1;
          padding: 3px 6px;
          border-radius: 4px;
          cursor: pointer;
          transition: background 0.15s, color 0.15s;
        }
        .op-column-gear-btn:hover {
          background: #f1f5f9;
          color: #0f172a;
        }
        .op-column-menu {
          position: absolute;
          top: 100%;
          right: 0;
          margin-top: 4px;
          background: #ffffff;
          border: 1px solid #e2e8f0;
          border-radius: 6px;
          box-shadow: 0 4px 14px rgba(0,0,0,0.12);
          padding: 4px 0;
          min-width: 140px;
          z-index: 1000;
        }
        .op-column-menu-item {
          width: 100%;
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 7px 12px;
          font-size: 12.5px;
          font-weight: 500;
          color: #334155;
          background: transparent;
          border: none;
          cursor: pointer;
          text-align: left;
          transition: background 0.15s, color 0.15s;
          box-sizing: border-box;
        }
        .op-column-menu-item:hover {
          background: #f8fafc;
          color: #0f172a;
        }

        /* Folded Column styling */
        .op-kanban-column.op-column-folded {
          width: 48px !important;
          min-width: 48px !important;
          max-width: 48px !important;
          background: #f8fafc;
          border: 1px dashed #cbd5e1;
          border-radius: 8px;
          cursor: pointer;
          user-select: none;
          transition: width 0.2s ease, background 0.15s ease;
          padding: 8px 4px !important;
        }
        .op-kanban-column.op-column-folded:hover {
          background: #f1f5f9;
          border-color: #94a3b8;
        }
        .op-kanban-column.op-column-folded .op-kanban-column-header,
        .op-kanban-column.op-column-folded .op-kanban-column-cards {
          display: none !important;
        }
        .op-kanban-column.op-column-folded .op-column-folded-view {
          display: flex !important;
          flex-direction: column;
          align-items: center;
          padding: 12px 0;
          gap: 14px;
          height: 100%;
          min-height: 280px;
        }
        .op-column-folded-badge {
          background: #e2e8f0;
          color: #334155;
          font-size: 11px;
          font-weight: 700;
          border-radius: 12px;
          padding: 2px 6px;
          line-height: 1.2;
        }
        .op-column-folded-title {
          writing-mode: vertical-rl;
          transform: rotate(180deg);
          font-weight: 700;
          font-size: 13px;
          color: #475569;
          letter-spacing: 0.5px;
          white-space: nowrap;
        }
        .op-column-folded-icon {
          font-size: 12px;
          color: #94a3b8;
          margin-top: auto;
        }

        /* Add Column Panel styling */
        .op-kanban-add-column-panel {
          transition: all 0.2s ease;
        }
        .op-add-column-trigger-btn:hover {
          background: #f1f5f9 !important;
          border-color: #94a3b8 !important;
          color: #1e293b !important;
        }
        .op-add-column-input:focus {
          border-color: #0284c7 !important;
          box-shadow: 0 0 0 3px rgba(2, 132, 199, 0.15) !important;
        }
      `;
      document.head.appendChild(styleEl);
    }

    // Dismiss any open column menu when clicking outside
    document.addEventListener('click', (e) => {
      if (!e.target.closest('.op-column-header-actions')) {
        document.querySelectorAll('.op-column-menu').forEach(m => m.style.display = 'none');
      }
    });

    const columns = board.querySelectorAll('.op-kanban-column');
    const dragCtx = {
      draggedCard: null,
      sourceColumn: null,
      sourceDropZone: null,
      lastDragEndTimestamp: 0
    };
    window._opKanbanDragContext = dragCtx;

    // Make all cards draggable
    const cards = board.querySelectorAll('.emp-kanban-panel-card, .leave-kanban-card, [data-kanban-card]');
    cards.forEach((card) => {
      card.setAttribute('draggable', 'true');
      card.classList.add('op-kanban-card-draggable');

      // Prevent link navigation if drag just occurred
      card.addEventListener('click', (e) => {
        if (Date.now() - dragCtx.lastDragEndTimestamp < 450) {
          e.preventDefault();
          e.stopPropagation();
          return false;
        }
      });

      card.addEventListener('dragstart', (e) => {
        dragCtx.draggedCard = card;
        dragCtx.sourceColumn = card.closest('.op-kanban-column');
        dragCtx.sourceDropZone = dragCtx.sourceColumn ? (dragCtx.sourceColumn.querySelector('.op-kanban-column-cards') || dragCtx.sourceColumn) : null;

        const recordId = card.getAttribute('data-record-id') || (card.id ? card.id.replace(/\D/g, '') : null);
        const modelKey = card.getAttribute('data-model') || board.getAttribute('data-model') || 'hr.employee';
        const groupField = board.getAttribute('data-group-by') || card.closest('.op-kanban-column')?.getAttribute('data-group-field') || 'department';

        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setData('text/plain', JSON.stringify({
          recordId: recordId,
          modelKey: modelKey,
          groupField: groupField
        }));

        requestAnimationFrame(() => {
          card.classList.add('op-kanban-card-dragging');
        });
      });

      card.addEventListener('dragend', () => {
        dragCtx.lastDragEndTimestamp = Date.now();
        card.classList.remove('op-kanban-card-dragging');
        columns.forEach((col) => col.classList.remove('op-kanban-column-dragover'));
        setTimeout(() => {
          dragCtx.draggedCard = null;
          dragCtx.sourceColumn = null;
          dragCtx.sourceDropZone = null;
        }, 50);
      });
    });

    // Setup columns: fold restoration & drop targets
    columns.forEach((col) => {
      // 1. Restore fold state from localStorage
      try {
        const key = getColumnStorageKey(col);
        if (localStorage.getItem(key) === '1') {
          col.classList.add('op-column-folded');
        }
      } catch (e) {}

      // 2. Attach drop target listeners
      attachColumnDropListeners(col, board, dragCtx);
    });
  }

  // Expose global methods for inline HTML onclick handlers
  window.toggleColumnMenu = toggleColumnMenu;
  window.foldKanbanColumn = foldKanbanColumn;
  window.unfoldKanbanColumn = unfoldKanbanColumn;
  window.showInlineAddColumn = showInlineAddColumn;
  window.cancelAddColumn = cancelAddColumn;
  window.confirmAddColumn = confirmAddColumn;
  window.handleColumnInputKey = handleColumnInputKey;
  window.initKanbanDragDrop = initKanbanDragDrop;

  // Auto-initialize on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initKanbanDragDrop);
  } else {
    initKanbanDragDrop();
  }
})();
