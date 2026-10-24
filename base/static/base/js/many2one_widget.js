// many2one_widget.js -- Odoo-style Many2One input, dropdown & modal dialog

function opDebounce(fn, wait) {
  let t;
  return function (...args) {
    clearTimeout(t);
    t = setTimeout(() => fn.apply(this, args), wait);
  };
}

function opOpenM2oModal(modelKey, fieldLabel, onSelect) {
  let currentPage = 1;
  let totalRecords = 0;
  let totalPages = 1;
  const pageSize = 80;
  let currentQuery = "";

  const overlay = document.createElement("div");
  overlay.className = "op-m2o-modal-overlay";
  overlay.innerHTML = `
    <div class="op-m2o-modal">
      <!-- Modal Header -->
      <div class="op-m2o-modal-header">
        <span class="op-m2o-modal-title">Search: ${fieldLabel || "Model"}</span>
        <button type="button" class="op-m2o-modal-close" aria-label="Close">&#10005;</button>
      </div>

      <!-- Modal Toolbar -->
      <div class="op-m2o-modal-toolbar">
        <div class="op-m2o-modal-search-box">
          <span class="op-m2o-search-icon">&#128269;</span>
          <input type="text" class="op-m2o-modal-search-input" placeholder="Search..." autocomplete="off" />
          <span class="op-m2o-search-caret">&#9662;</span>
        </div>

        <div class="op-m2o-modal-pager">
          <span class="op-m2o-pager-info">0-0 / 0</span>
          <button type="button" class="op-m2o-pager-btn op-m2o-pager-prev" disabled>&lt;</button>
          <button type="button" class="op-m2o-pager-btn op-m2o-pager-next" disabled>&gt;</button>
        </div>
      </div>

      <!-- Modal Table Body -->
      <div class="op-m2o-modal-body">
        <table class="op-m2o-table">
          <thead>
            <tr>
              <th style="width: 250px;">Model</th>
              <th>Model Description</th>
              <th style="width: 120px;">Type</th>
              <th style="width: 80px; text-align: center;">Transient</th>
            </tr>
          </thead>
          <tbody class="op-m2o-table-body">
            <tr>
              <td colspan="4" class="op-m2o-loading">Loading...</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Modal Footer -->
      <div class="op-m2o-modal-footer">
        <button type="button" class="op-m2o-btn-new">New</button>
        <button type="button" class="op-m2o-btn-close">Close</button>
      </div>
    </div>
  `;

  document.body.appendChild(overlay);

  const tbody = overlay.querySelector(".op-m2o-table-body");
  const searchInput = overlay.querySelector(".op-m2o-modal-search-input");
  const pagerInfo = overlay.querySelector(".op-m2o-pager-info");
  const prevBtn = overlay.querySelector(".op-m2o-pager-prev");
  const nextBtn = overlay.querySelector(".op-m2o-pager-next");
  const closeIcon = overlay.querySelector(".op-m2o-modal-close");
  const closeBtn = overlay.querySelector(".op-m2o-btn-close");

  function closeModal() {
    overlay.remove();
  }

  closeIcon.addEventListener("click", closeModal);
  closeBtn.addEventListener("click", closeModal);
  overlay.addEventListener("click", function (e) {
    if (e.target === overlay) closeModal();
  });

  function updatePager() {
    if (totalRecords === 0) {
      pagerInfo.textContent = "0-0 / 0";
      prevBtn.disabled = true;
      nextBtn.disabled = true;
      return;
    }
    const start = (currentPage - 1) * pageSize + 1;
    const end = Math.min(currentPage * pageSize, totalRecords);
    pagerInfo.textContent = `${start}-${end} / ${totalRecords}`;
    prevBtn.disabled = currentPage <= 1;
    nextBtn.disabled = currentPage >= totalPages;
  }

  function renderRows(records) {
    if (!records || !records.length) {
      tbody.innerHTML = `<tr><td colspan="4" class="op-m2o-empty-row">No records found.</td></tr>`;
      return;
    }

    tbody.innerHTML = records
      .map((r) => {
        const modelName = r.model_name || r.display;
        const desc = r.description || r.display;
        const type = r.type || "Base Object";

        return `
        <tr class="op-m2o-row" data-id="${r.id}" data-name="${modelName}" data-desc="${desc}">
          <td class="op-m2o-cell-name"><code>${modelName}</code></td>
          <td class="op-m2o-cell-desc">${desc}</td>
          <td class="op-m2o-cell-type">${type}</td>
          <td class="op-m2o-cell-transient" style="text-align: center;">
            <input type="checkbox" ${r.is_transient ? "checked" : ""} disabled style="accent-color: #714b67;" />
          </td>
        </tr>
      `;
      })
      .join("");

    tbody.querySelectorAll(".op-m2o-row").forEach((row) => {
      row.addEventListener("click", function () {
        const id = this.dataset.id;
        const name = this.dataset.name;
        const desc = this.dataset.desc;
        onSelect(id, desc || name, name);
        closeModal();
      });
    });
  }

  function fetchPage(page, query) {
    currentPage = page;
    currentQuery = query;
    tbody.innerHTML = `<tr><td colspan="4" class="op-m2o-loading">Loading...</td></tr>`;

    const url = `/technical/relation-search/?model=${encodeURIComponent(modelKey || "ir.model")}&q=${encodeURIComponent(query)}&page=${page}&page_size=${pageSize}`;

    fetch(url)
      .then((res) => res.json())
      .then((data) => {
        totalRecords = data.total_count || (data.results ? data.results.length : 0);
        totalPages = data.total_pages || Math.ceil(totalRecords / pageSize) || 1;
        updatePager();
        renderRows(data.results);
      })
      .catch(() => {
        tbody.innerHTML = `<tr><td colspan="4" class="op-m2o-empty-row">Error loading data.</td></tr>`;
      });
  }

  prevBtn.addEventListener("click", () => {
    if (currentPage > 1) {
      fetchPage(currentPage - 1, currentQuery);
    }
  });

  nextBtn.addEventListener("click", () => {
    if (currentPage < totalPages) {
      fetchPage(currentPage + 1, currentQuery);
    }
  });

  const debouncedSearch = opDebounce((q) => {
    fetchPage(1, q);
  }, 250);

  searchInput.addEventListener("input", (e) => {
    debouncedSearch(e.target.value.trim());
  });

  // Initial load
  fetchPage(1, "");
  setTimeout(() => searchInput.focus(), 50);
}

window.opOpenM2oModal = opOpenM2oModal;

function opInitM2oWidget(widget) {
  const modelKey = widget.dataset.relationModel || "ir.model";
  const fieldLabel = widget.dataset.fieldLabel || "Model";
  const hiddenInput = widget.querySelector(".op-m2o-value");
  const displayInput = widget.querySelector(".op-m2o-display-input");
  const dropdown = widget.querySelector(".op-m2o-dropdown");
  const caretBtn = widget.querySelector(".op-m2o-caret-btn");
  const internalLink = widget.querySelector(".op-m2o-internal-link");

  function selectItem(id, display, rawName) {
    hiddenInput.value = id;
    if (displayInput) {
      displayInput.value = display;
    }
    if (internalLink) {
      if (modelKey === "ir.model" && id) {
        internalLink.href = `/settings/technical/models/${id}/`;
        internalLink.style.display = "inline-flex";
      }
    }
    if (dropdown) {
      dropdown.innerHTML = "";
      dropdown.style.display = "none";
    }
  }

  function loadAndRenderDropdown(query) {
    const url = `/technical/relation-search/?model=${encodeURIComponent(modelKey)}&q=${encodeURIComponent(query || "")}&page=1&page_size=8`;
    fetch(url)
      .then((r) => r.json())
      .then((data) => {
        const results = data.results || [];
        let html = results
          .map(
            (r) =>
              `<div class="op-m2o-dropdown-item" data-id="${r.id}" data-display="${r.display}">${r.display}</div>`
          )
          .join("");

        html += `<div class="op-m2o-dropdown-search-more">Search more...</div>`;

        dropdown.innerHTML = html;
        dropdown.style.display = "block";

        dropdown.querySelectorAll(".op-m2o-dropdown-item").forEach((item) => {
          item.addEventListener("click", function (e) {
            e.stopPropagation();
            selectItem(this.dataset.id, this.dataset.display);
          });
        });

        const searchMore = dropdown.querySelector(".op-m2o-dropdown-search-more");
        if (searchMore) {
          searchMore.addEventListener("click", function (e) {
            e.stopPropagation();
            dropdown.style.display = "none";
            opOpenM2oModal(modelKey, fieldLabel, selectItem);
          });
        }
      });
  }

  if (displayInput && dropdown) {
    // On click or focus, show dropdown immediately with first records
    displayInput.addEventListener("click", function () {
      this.select();
      loadAndRenderDropdown("");
    });

    displayInput.addEventListener("focus", function () {
      loadAndRenderDropdown("");
    });

    const debouncedInput = opDebounce(function () {
      loadAndRenderDropdown(displayInput.value.trim());
    }, 200);

    displayInput.addEventListener("input", debouncedInput);

    if (caretBtn) {
      caretBtn.addEventListener("click", function (e) {
        e.preventDefault();
        e.stopPropagation();
        if (dropdown.style.display === "block") {
          dropdown.style.display = "none";
        } else {
          displayInput.focus();
          loadAndRenderDropdown("");
        }
      });
    }

    document.addEventListener("click", function (e) {
      if (!widget.contains(e.target)) {
        dropdown.style.display = "none";
      }
    });
  }
}

document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll(".op-m2o-field, .op-m2o-widget").forEach(opInitM2oWidget);
});
