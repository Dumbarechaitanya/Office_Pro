/**
 * Office Pro - Universal Kanban Drag and Drop Module
 * Allows moving record cards between grouped columns (e.g., departments, statuses).
 * Automatically updates the model record via /api/kanban-move/.
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
    if (countEl) {
      const match = countEl.textContent.match(/\d+/);
      if (match) {
        const currentCount = parseInt(match[0], 10);
        const newCount = Math.max(0, currentCount + delta);
        countEl.textContent = `(${newCount})`;
      }
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

  function initKanbanDragDrop() {
    const board = document.querySelector('.op-kanban-board');
    if (!board) return;

    // Inject styles if not already present
    if (!document.getElementById('opKanbanDnDStyles')) {
      const styleEl = document.createElement('style');
      styleEl.id = 'opKanbanDnDStyles';
      styleEl.textContent = `
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
      `;
      document.head.appendChild(styleEl);
    }

    const columns = board.querySelectorAll('.op-kanban-column');
    let draggedCard = null;
    let sourceColumn = null;
    let sourceDropZone = null;
    let lastDragEndTimestamp = 0;

    // Make all cards draggable
    const cards = board.querySelectorAll('.emp-kanban-panel-card, .leave-kanban-card, [data-kanban-card]');
    cards.forEach((card) => {
      card.setAttribute('draggable', 'true');
      card.classList.add('op-kanban-card-draggable');

      // Prevent link navigation if drag just occurred
      card.addEventListener('click', (e) => {
        if (Date.now() - lastDragEndTimestamp < 450) {
          e.preventDefault();
          e.stopPropagation();
          return false;
        }
      });

      card.addEventListener('dragstart', (e) => {
        draggedCard = card;
        sourceColumn = card.closest('.op-kanban-column');
        sourceDropZone = sourceColumn ? (sourceColumn.querySelector('.op-kanban-column-cards') || sourceColumn) : null;

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
        lastDragEndTimestamp = Date.now();
        card.classList.remove('op-kanban-card-dragging');
        columns.forEach((col) => col.classList.remove('op-kanban-column-dragover'));
        setTimeout(() => {
          draggedCard = null;
          sourceColumn = null;
          sourceDropZone = null;
        }, 50);
      });
    });

    // Setup columns as drop targets
    columns.forEach((col) => {
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

        if (!draggedCard || !sourceColumn) return;
        if (sourceColumn === col) return; // Dropped in same column

        let dragData = {};
        try {
          const raw = e.dataTransfer.getData('text/plain');
          if (raw) dragData = JSON.parse(raw);
        } catch (err) {}

        const recordId = dragData.recordId || draggedCard.getAttribute('data-record-id') || (draggedCard.id ? draggedCard.id.replace(/\D/g, '') : null);
        const modelKey = dragData.modelKey || draggedCard.getAttribute('data-model') || board.getAttribute('data-model') || 'hr.employee';
        const groupField = dragData.groupField || board.getAttribute('data-group-by') || col.getAttribute('data-group-field') || 'department';

        const targetGroupVal = col.getAttribute('data-group-value') || col.getAttribute('data-group-label') || col.querySelector('.op-kanban-column-header span')?.textContent.trim();
        const targetGroupLabel = col.getAttribute('data-group-label') || targetGroupVal;

        if (!recordId) {
          console.warn('[Kanban] No recordId found on dragged card.');
          return;
        }

        // 1. Optimistic DOM update: Move card into target column
        const originalParent = draggedCard.parentNode;
        const originalNextSibling = draggedCard.nextSibling;
        const fromDropZone = sourceDropZone;

        removePlaceholder(dropZone);
        dropZone.appendChild(draggedCard);
        ensurePlaceholder(fromDropZone);

        // 2. Optimistic Counters update
        updateColumnCount(sourceColumn, -1);
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
            draggedCard.classList.add('op-card-moved-success');
            setTimeout(() => draggedCard?.classList.remove('op-card-moved-success'), 1200);

            // Update badge & buttons if moving a Leave Request
            if (modelKey.includes('leave')) {
              const ribbon = draggedCard.querySelector('.op-ribbon');
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
              const footer = draggedCard.querySelector('.leave-card-footer') || draggedCard.querySelector('[style*="border-top"]');
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
            originalParent.insertBefore(draggedCard, originalNextSibling);
          } else {
            originalParent.appendChild(draggedCard);
          }
          removePlaceholder(fromDropZone);
          ensurePlaceholder(dropZone);

          // Revert counts
          updateColumnCount(sourceColumn, +1);
          updateColumnCount(col, -1);

          showToast(`Could not move card: ${err.message}`, 'error');
        });
      });
    });
  }

  // Initialize on DOM load and export to window for dynamic view reloads
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initKanbanDragDrop);
  } else {
    initKanbanDragDrop();
  }

  window.initKanbanDragDrop = initKanbanDragDrop;
})();
