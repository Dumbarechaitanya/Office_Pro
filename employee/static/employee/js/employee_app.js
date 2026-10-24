/* Office Pro - Employee Module Client Script */

(function () {
  'use strict';

  function hexToRgba(hex, alpha) {
    if (!hex || typeof hex !== 'string') return hex;
    var cleaned = hex.trim();
    if (cleaned.startsWith('#')) {
      if (cleaned.length === 7) {
        var r = parseInt(cleaned.slice(1, 3), 16);
        var g = parseInt(cleaned.slice(3, 5), 16);
        var b = parseInt(cleaned.slice(5, 7), 16);
        return 'rgba(' + r + ', ' + g + ', ' + b + ', ' + alpha + ')';
      }
      if (cleaned.length === 4) {
        var r1 = parseInt(cleaned[1] + cleaned[1], 16);
        var g1 = parseInt(cleaned[2] + cleaned[2], 16);
        var b1 = parseInt(cleaned[3] + cleaned[3], 16);
        return 'rgba(' + r1 + ', ' + g1 + ', ' + b1 + ', ' + alpha + ')';
      }
    }
    return cleaned;
  }

  function applyDeptColors() {
    // 1. Department Kanban Cards left border
    document.querySelectorAll('[data-dept-card]').forEach(function (el) {
      var col = el.getAttribute('data-dept-card');
      if (col) {
        el.style.borderLeft = '4px solid ' + col;
      }
    });

    // 2. Department Badges and Icons
    document.querySelectorAll('[data-dept-color]').forEach(function (el) {
      var col = el.getAttribute('data-dept-color');
      if (!col) return;

      if (el.classList.contains('emp-color-dot') || el.classList.contains('emp-square-avatar') || el.classList.contains('emp-mini-org-avatar')) {
        el.style.backgroundColor = col;
      } else if (el.classList.contains('emp-dept-icon-box')) {
        el.style.backgroundColor = hexToRgba(col, 0.14);
        el.style.color = col;
      } else if (el.classList.contains('emp-dept-badge')) {
        el.style.backgroundColor = hexToRgba(col, 0.14);
        el.style.color = col;
      } else {
        el.style.color = col;
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', applyDeptColors);
  } else {
    applyDeptColors();
  }

  window.applyDeptColors = applyDeptColors;
})();
