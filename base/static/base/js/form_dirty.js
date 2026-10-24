// form_dirty.js -- shows Save/Discard only when a field has changed.
// Discard resets all fields to original values.

document.addEventListener('DOMContentLoaded', function () {
  const form = document.querySelector('.op-form-sheet');
  const dirtyActions = document.querySelector('.op-form-dirty-actions');
  const discardBtn = document.querySelector('.op-discard-changes-btn');
  if (!form || !dirtyActions) return;

  const originals = {};

  form.querySelectorAll('.op-form-input').forEach(function (el) {
    const key = el.id || el.name || Math.random().toString(36).slice(2);
    if (el.classList.contains('op-m2o-widget')) {
      const hidden = el.querySelector('.op-m2o-value');
      const chipLabel = el.querySelector('.op-m2o-chip-label');
      const chipArea = el.querySelector('.op-m2o-chip-area');
      originals[key] = {
        type: 'many2one',
        value: hidden ? hidden.value : '',
        label: chipLabel ? chipLabel.textContent : '',
        chipVisible: chipArea ? chipArea.style.display !== 'none' : false,
        el: el,
      };
    } else if (el.type === 'checkbox') {
      originals[key] = { type: 'checkbox', checked: el.checked, el: el };
    } else {
      originals[key] = { type: 'value', value: el.value, el: el };
    }
  });

  function isDirty() {
    for (const key in originals) {
      const orig = originals[key];
      if (orig.type === 'many2one') {
        const hidden = orig.el.querySelector('.op-m2o-value');
        if (hidden && hidden.value !== orig.value) return true;
      } else if (orig.type === 'checkbox') {
        if (orig.el.checked !== orig.checked) return true;
      } else {
        if (orig.el.value !== orig.value) return true;
      }
    }
    return false;
  }

  function showBar(show) {
    dirtyActions.style.display = show ? 'flex' : 'none';
  }

  function checkDirty() { showBar(isDirty()); }

  form.addEventListener('input', checkDirty);
  form.addEventListener('change', checkDirty);
  form.addEventListener('click', function () { setTimeout(checkDirty, 50); });

  const observer = new MutationObserver(checkDirty);
  form.querySelectorAll('.op-m2o-value').forEach(function (hidden) {
    observer.observe(hidden, { attributes: true, attributeFilter: ['value'] });
  });

  if (discardBtn) {
    discardBtn.addEventListener('click', function () {
      for (const key in originals) {
        const orig = originals[key];
        if (orig.type === 'many2one') {
          const hidden = orig.el.querySelector('.op-m2o-value');
          const chipLabel = orig.el.querySelector('.op-m2o-chip-label');
          const chipArea = orig.el.querySelector('.op-m2o-chip-area');
          const searchArea = orig.el.querySelector('.op-m2o-search-area');
          const searchInput = orig.el.querySelector('.op-m2o-search');
          if (hidden) hidden.value = orig.value;
          if (chipLabel) chipLabel.textContent = orig.label;
          if (chipArea) chipArea.style.display = orig.chipVisible ? '' : 'none';
          if (searchArea) searchArea.style.display = orig.chipVisible ? 'none' : '';
          if (searchInput) searchInput.value = '';
        } else if (orig.type === 'checkbox') {
          orig.el.checked = orig.checked;
        } else {
          orig.el.value = orig.value;
        }
      }
      showBar(false);
    });
  }
});
