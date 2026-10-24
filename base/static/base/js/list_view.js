/**
 * list_view.js -- Odoo-style row selection, batch actions, and export for all List Views
 */

function getSelectedIds() {
  const checkboxes = document.querySelectorAll('.op-row-select-checkbox:checked');
  return Array.from(checkboxes).map(cb => cb.value);
}

function updateSelectionState() {
  const allCheckboxes = document.querySelectorAll('.op-row-select-checkbox');
  const checkedBoxes = document.querySelectorAll('.op-row-select-checkbox:checked');
  const selectAll = document.getElementById('selectAllCheckbox');
  const badge = document.getElementById('opSelectionBadge');
  const countSpan = document.getElementById('opSelectionCount');
  const actionsBtn = document.getElementById('opActionsBtn');
  const exportLabel = document.getElementById('opExportActionLabel');
  const batchSection = document.getElementById('opBatchActionsSection');

  const count = checkedBoxes.length;
  const total = allCheckboxes.length;

  // Update rows highlight
  allCheckboxes.forEach(cb => {
    const row = cb.closest('tr');
    if (row) {
      if (cb.checked) {
        row.classList.add('op-row-selected');
      } else {
        row.classList.remove('op-row-selected');
      }
    }
  });

  // Update select all master checkbox state
  if (selectAll) {
    if (count === 0) {
      selectAll.checked = false;
      selectAll.indeterminate = false;
    } else if (count === total) {
      selectAll.checked = true;
      selectAll.indeterminate = false;
    } else {
      selectAll.checked = false;
      selectAll.indeterminate = true;
    }
  }

  // Update selection badge & actions items
  if (count > 0) {
    if (badge) {
      badge.style.display = 'inline-flex';
      badge.classList.add('active');
      if (countSpan) countSpan.textContent = count;
    }
    if (actionsBtn) {
      actionsBtn.classList.add('has-selection');
    }
    if (exportLabel) {
      exportLabel.textContent = `Export (${count})`;
    }
    if (batchSection) {
      batchSection.style.display = 'block';
    }
  } else {
    if (badge) {
      badge.style.display = 'none';
      badge.classList.remove('active');
    }
    if (actionsBtn) {
      actionsBtn.classList.remove('has-selection');
    }
    if (exportLabel) {
      exportLabel.textContent = 'Export All';
    }
    if (batchSection) {
      batchSection.style.display = 'none';
    }
  }
}

function toggleSelectAll(masterCheckbox) {
  const isChecked = masterCheckbox.checked;
  document.querySelectorAll('.op-row-select-checkbox').forEach(cb => {
    cb.checked = isChecked;
  });
  updateSelectionState();
}

function handleRowSelect(checkbox, event) {
  if (event) event.stopPropagation();
  updateSelectionState();
}

function clearSelection() {
  document.querySelectorAll('.op-row-select-checkbox').forEach(cb => {
    cb.checked = false;
  });
  const selectAll = document.getElementById('selectAllCheckbox');
  if (selectAll) {
    selectAll.checked = false;
    selectAll.indeterminate = false;
  }
  updateSelectionState();
}

function toggleActionsMenu(event) {
  if (event) {
    event.preventDefault();
    event.stopPropagation();
  }
  const btn = event ? event.currentTarget : document.getElementById('opActionsBtn');
  const container = btn ? btn.closest('.op-actions-container') : document.querySelector('.op-actions-container');
  const menu = container ? container.querySelector('.op-actions-menu') : document.getElementById('opActionsDropdownMenu');

  if (menu && container) {
    const isShowing = menu.classList.contains('show');

    // Close any other open menus
    document.querySelectorAll('.op-actions-menu').forEach(m => m.classList.remove('show'));
    document.querySelectorAll('.op-actions-container').forEach(c => c.classList.remove('menu-open'));

    if (!isShowing) {
      menu.classList.add('show');
      container.classList.add('menu-open');
    }
  }
}

function openExportModal() {
  const modal = document.getElementById('opExportModal');
  if (modal) {
    modal.style.display = 'flex';
  }
  document.querySelectorAll('.op-actions-menu').forEach(m => m.classList.remove('show'));
  document.querySelectorAll('.op-actions-container').forEach(c => c.classList.remove('menu-open'));
}

function closeExportModal() {
  const modal = document.getElementById('opExportModal');
  if (modal) modal.style.display = 'none';
}

function openImportModal() {
  const modal = document.getElementById('opImportModal');
  if (modal) {
    modal.style.display = 'flex';
  }
  document.querySelectorAll('.op-actions-menu').forEach(m => m.classList.remove('show'));
  document.querySelectorAll('.op-actions-container').forEach(c => c.classList.remove('menu-open'));
}

function closeImportModal() {
  const modal = document.getElementById('opImportModal');
  if (modal) {
    modal.style.display = 'none';
    const form = document.getElementById('opImportForm');
    if (form) form.reset();
    const fileNameEl = document.getElementById('opImportFileName');
    if (fileNameEl) fileNameEl.textContent = 'Click to select CSV / XLSX file';
  }
}

function handleImportFileSelected(input) {
  const fileNameEl = document.getElementById('opImportFileName');
  if (input && input.files && input.files[0] && fileNameEl) {
    fileNameEl.textContent = input.files[0].name;
  }
}

function executeImport(event, modelKey) {
  if (event) event.preventDefault();
  const fileInput = document.getElementById('opImportFileInput');
  if (!fileInput || !fileInput.files || !fileInput.files[0]) {
    alert('Please select a CSV or XLSX file to import.');
    return;
  }

  const form = document.getElementById('opImportForm');
  const formData = new FormData(form || undefined);
  formData.append('csrfmiddlewaretoken', getCsrfToken());
  formData.append('action', 'import_records');
  formData.append('model_key', modelKey || '');
  if (!formData.has('import_file') || !formData.get('import_file')) {
    formData.append('import_file', fileInput.files[0]);
  }

  const submitBtn = document.getElementById('opImportSubmitBtn');
  if (submitBtn) {
    submitBtn.disabled = true;
    submitBtn.textContent = 'Importing...';
  }

  fetch('/batch-action/', {
    method: 'POST',
    body: formData,
  })
    .then(res => res.json())
    .then(data => {
      if (data.status === 'success') {
        closeImportModal();
        alert(data.message || 'Records imported successfully.');
        window.location.reload();
      } else {
        alert(data.message || 'Import failed.');
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.textContent = 'Import';
        }
      }
    })
    .catch(err => {
      console.error(err);
      alert('Failed to process file import.');
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Import';
      }
    });
}

function getCsrfToken() {
  const tokenInput = document.querySelector('[name=csrfmiddlewaretoken]');
  if (tokenInput) return tokenInput.value;
  const cookieMatch = document.cookie.match(/csrftoken=([^;]+)/);
  return cookieMatch ? cookieMatch[1] : '';
}

function executeBatchAction(actionName, modelKey) {
  const ids = getSelectedIds();
  document.querySelectorAll('.op-actions-menu').forEach(m => m.classList.remove('show'));
  document.querySelectorAll('.op-actions-container').forEach(c => c.classList.remove('menu-open'));

  if (actionName === 'export_xlsx' || actionName === 'export_csv') {
    closeExportModal();
    const idsParam = ids.length > 0 ? `&ids=${ids.join(',')}` : '';
    const url = `/batch-action/?action=${encodeURIComponent(actionName)}&model_key=${encodeURIComponent(modelKey || '')}${idsParam}`;
    window.location.href = url;
    return;
  }

  if (ids.length === 0) {
    alert('Please select at least one record.');
    return;
  }

  if (actionName === 'delete') {
    if (!confirm(`Are you sure you want to delete ${ids.length} selected record(s)? This operation cannot be undone.`)) {
      return;
    }
  }

  // POST batch action to backend
  const formData = new FormData();
  formData.append('csrfmiddlewaretoken', getCsrfToken());
  formData.append('action', actionName);
  formData.append('model_key', modelKey || '');
  ids.forEach(id => formData.append('ids', id));

  fetch('/batch-action/', {
    method: 'POST',
    body: formData,
  })
    .then(response => response.json())
    .then(data => {
      if (data.status === 'success') {
        window.location.reload();
      } else {
        alert(data.message || 'An error occurred performing the action.');
      }
    })
    .catch(err => {
      console.error(err);
      alert('Failed to execute batch action.');
    });
}

function toggleColPickerMenu(button, event) {
  if (event) event.stopPropagation();
  const menu = button.nextElementSibling;
  if (menu) {
    const isVisible = menu.style.display === 'block';
    document.querySelectorAll('.op-col-picker-menu').forEach(m => m.style.display = 'none');
    menu.style.display = isVisible ? 'none' : 'block';
  }
}

function toggleColumnVisibility(colName, isVisible) {
  const ths = document.querySelectorAll(`th.op-col-${colName}`);
  const tds = document.querySelectorAll(`td.op-col-${colName}`);

  ths.forEach(th => th.style.display = isVisible ? '' : 'none');
  tds.forEach(td => td.style.display = isVisible ? '' : 'none');

  // Save preference in localStorage
  const storageKey = `op_col_vis_${window.location.pathname}`;
  let visMap = {};
  try {
    visMap = JSON.parse(localStorage.getItem(storageKey) || '{}');
  } catch (e) {}
  visMap[colName] = isVisible;
  localStorage.setItem(storageKey, JSON.stringify(visMap));
}

function restoreColumnPreferences() {
  const storageKey = `op_col_vis_${window.location.pathname}`;
  try {
    const visMap = JSON.parse(localStorage.getItem(storageKey) || '{}');
    Object.keys(visMap).forEach(colName => {
      const isVisible = visMap[colName];
      const cb = document.querySelector(`.op-col-toggle-cb[data-col="${colName}"]`);
      if (cb) {
        cb.checked = isVisible;
      }
      toggleColumnVisibility(colName, isVisible);
    });
  } catch (e) {}
}

// Global click to close actions & col picker menus & handle data-href clicks
document.addEventListener('click', function(e) {
  if (!e.target.closest('.op-actions-container')) {
    document.querySelectorAll('.op-actions-menu').forEach(m => {
      m.classList.remove('show');
    });
    document.querySelectorAll('.op-actions-container').forEach(c => {
      c.classList.remove('menu-open');
    });
  }

  // Close col picker if clicked outside
  if (!e.target.closest('.op-col-picker-th')) {
    document.querySelectorAll('.op-col-picker-menu').forEach(m => m.style.display = 'none');
  }

  // Handle data-href row / card clicks
  const clickable = e.target.closest('[data-href]');
  if (clickable) {
    if (!e.target.closest('.op-select-col') && !e.target.closest('a') && !e.target.closest('button') && !e.target.closest('input')) {
      const url = clickable.getAttribute('data-href');
      if (url) window.location.href = url;
    }
  }
});

// Global Odoo-style List Group Row Toggle
function toggleGroupRow(groupId, event) {
  if (event && (event.target.tagName === 'INPUT' || event.target.tagName === 'BUTTON' || event.target.tagName === 'A')) {
    return;
  }
  const headerRow = document.querySelector(`tr.op-group-header-row[data-group-id="${groupId}"]`);
  if (!headerRow) return;
  const caret = headerRow.querySelector('.op-group-caret');
  const childRows = document.querySelectorAll(`tr.op-group-row.${groupId}`);
  if (childRows.length === 0) return;

  const isCurrentlyOpen = childRows[0].style.display !== 'none';
  childRows.forEach(row => {
    row.style.display = isCurrentlyOpen ? 'none' : '';
  });

  if (caret) {
    caret.innerHTML = isCurrentlyOpen ? '&#9654;' : '&#9660;';
  }
  headerRow.classList.toggle('collapsed', isCurrentlyOpen);
}

// Group collapse toggles & initialize
document.addEventListener('DOMContentLoaded', function () {
  // Delegated click for op-group-header-row
  document.addEventListener('click', function (e) {
    const grpHeader = e.target.closest('tr.op-group-header-row');
    if (grpHeader) {
      const grpId = grpHeader.getAttribute('data-group-id');
      if (grpId) {
        toggleGroupRow(grpId, e);
      }
    }
  });

  // Backward compatibility with legacy .op-group-toggle
  document.querySelectorAll('.op-group-toggle').forEach(function (header) {
    header.addEventListener('click', function () {
      const table = this.nextElementSibling;
      const caret = this.querySelector('.op-group-caret');
      if (table) {
        const isOpen = table.style.display !== 'none';
        table.style.display = isOpen ? 'none' : '';
        if (caret) caret.innerHTML = isOpen ? '&#9654;' : '&#9660;';
      }
    });
  });
  updateSelectionState();
  restoreColumnPreferences();
});


