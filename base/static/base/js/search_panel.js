// search_panel.js -- Odoo-style In-Search-Box Facet Badges, Filters | Group By | Favorites Popover

function opGetCookie(name) {
  const match = document.cookie.match("(^|;)\\s*" + name + "\\s*=\\s*([^;]+)");
  return match ? decodeURIComponent(match.pop()) : "";
}

function opBuildUrl(params) {
  const url = new URL(window.location.href);
  Object.keys(params).forEach(function (k) {
    const v = params[k];
    if (v === null || v === undefined || v === "") {
      url.searchParams.delete(k);
    } else {
      url.searchParams.set(k, v);
    }
  });
  return url.toString();
}

function handleSearchSubmit(event, form) {
  const input = form.querySelector('.op-searchview-input');
  if (!input) return true;
  const val = input.value.trim();
  if (!val) {
    // If input is empty, don't clear facets or navigate with empty q
    event.preventDefault();
    return false;
  }
  return true;
}

document.addEventListener("DOMContentLoaded", function () {
  const panel = document.querySelector(".op-search-panel");
  if (!panel) return;

  const modelKey = panel.dataset.modelKey || "";
  let currentDomain = [];
  try {
    currentDomain = JSON.parse(panel.dataset.currentDomain || "[]");
  } catch (e) {
    currentDomain = [];
  }
  const currentGroupBy = panel.dataset.currentGroupBy || "";
  const filterMode = panel.dataset.filterMode || "";

  const facetsContainer = panel.querySelector(".op-searchview-facets");
  const searchInput = panel.querySelector(".op-searchview-input");

  // --- Render Dynamic Domain Filter Facets into Search Box ---
  if (facetsContainer && currentDomain && currentDomain.length > 0) {
    currentDomain.forEach(function (cond, idx) {
      if (Array.isArray(cond) && cond.length >= 3) {
        const fieldName = cond[0].replace(/__/g, ' ').replace(/\./g, ' ');
        const op = cond[1];
        const val = cond[2];

        const facetEl = document.createElement("div");
        facetEl.className = "op-searchview-facet op-facet-type-domain";
        facetEl.dataset.facet = "domain";
        facetEl.dataset.domainIndex = String(idx);
        facetEl.innerHTML = `
          <span class="op-facet-label">${fieldName}:</span>
          <span class="op-facet-value">${val}</span>
          <button type="button" class="op-facet-remove" data-facet="domain" data-domain-index="${idx}" title="Remove filter">&times;</button>
        `;
        facetsContainer.appendChild(facetEl);
      }
    });
  }

  // Update input placeholder based on facets presence
  function updatePlaceholder() {
    if (!searchInput) return;
    const hasFacets = facetsContainer && facetsContainer.children.length > 0;
    if (hasFacets) {
      searchInput.setAttribute("placeholder", "");
    } else {
      searchInput.setAttribute("placeholder", "Search...");
    }
  }
  updatePlaceholder();

  // --- Handle Facet Removal (Clicking 'x' cross on any chip inside search box) ---
  panel.addEventListener("click", function (e) {
    const removeBtn = e.target.closest(".op-facet-remove");
    if (!removeBtn) return;

    e.preventDefault();
    e.stopPropagation();

    const facetType = removeBtn.dataset.facet;
    const url = new URL(window.location.href);

    if (facetType === "filter") {
      url.searchParams.delete("filter");
      // For attendance, clearing default today switches to all history
      if (modelKey === "hr.attendance" && (filterMode === "today" || !filterMode)) {
        url.searchParams.set("filter", "history");
      }
    } else if (facetType === "group_by") {
      url.searchParams.delete("group_by");
    } else if (facetType === "q") {
      url.searchParams.delete("q");
    } else if (facetType === "domain") {
      const idx = parseInt(removeBtn.dataset.domainIndex, 10);
      if (!isNaN(idx) && currentDomain[idx] !== undefined) {
        currentDomain.splice(idx, 1);
        if (currentDomain.length > 0) {
          url.searchParams.set("domain", JSON.stringify(currentDomain));
        } else {
          url.searchParams.delete("domain");
        }
      }
    }

    window.location.href = url.toString();
  });

  // --- Keyboard Backspace on Empty Search Input (Removes last active facet) ---
  if (searchInput) {
    searchInput.addEventListener("keydown", function (e) {
      if (e.key === "Backspace" && searchInput.value === "") {
        const facets = facetsContainer ? facetsContainer.querySelectorAll(".op-searchview-facet") : [];
        if (facets.length > 0) {
          const lastFacet = facets[facets.length - 1];
          const removeBtn = lastFacet.querySelector(".op-facet-remove");
          if (removeBtn) {
            removeBtn.click();
          }
        }
      }
    });
  }

  // --- Popover Toggle: opens/closes the whole 3-column menu ---
  const toggleBtn = panel.querySelector(".op-searchview-toggle");
  const popover = panel.querySelector("#op-search-popover");
  if (toggleBtn && popover) {
    toggleBtn.addEventListener("click", function (e) {
      e.stopPropagation();
      const isOpen = popover.classList.contains("show");
      popover.classList.toggle("show", !isOpen);
      toggleBtn.setAttribute("aria-expanded", String(!isOpen));
    });
    document.addEventListener("click", function (e) {
      if (!popover.contains(e.target) && e.target !== toggleBtn) {
        popover.classList.remove("show");
        toggleBtn.setAttribute("aria-expanded", "false");
      }
    });
    popover.addEventListener("click", function (e) {
      e.stopPropagation();
    });
  }

  // --- Quick Presets Filter in Popover ---
  panel.querySelectorAll(".op-quick-filter-opt").forEach(function (opt) {
    opt.addEventListener("click", function (e) {
      e.preventDefault();
      const filterId = this.dataset.filterId;
      const url = new URL(window.location.href);
      const activeFilter = url.searchParams.get("filter") || (modelKey === "hr.attendance" ? "today" : "");

      if (activeFilter === filterId) {
        // Toggle off
        url.searchParams.delete("filter");
        if (modelKey === "hr.attendance") {
          url.searchParams.set("filter", "all");
        }
      } else {
        url.searchParams.set("filter", filterId);
      }
      window.location.href = url.toString();
    });
  });

  // --- Custom Filter Builder ---
  const fieldSelect = panel.querySelector(".op-filter-field");
  const opSelect = panel.querySelector(".op-filter-operator");
  const OPERATORS = window.OP_FILTER_OPERATORS || {};

  function refreshOperators() {
    if (!fieldSelect || !opSelect) return;
    const selected = fieldSelect.selectedOptions[0];
    const type = selected ? selected.dataset.type : null;
    const ops = OPERATORS[type] || [["=", "is equal to"], ["ilike", "contains"]];
    opSelect.innerHTML = ops
      .map(function (o) {
        return '<option value="' + o[0] + '">' + o[1] + "</option>";
      })
      .join("");
  }
  if (fieldSelect) {
    fieldSelect.addEventListener("change", refreshOperators);
    refreshOperators();
  }

  const addFilterTrigger = panel.querySelector(".op-add-custom-filter");
  if (addFilterTrigger) {
    addFilterTrigger.addEventListener("click", function () {
      const valInput = panel.querySelector(".op-filter-value");
      const value = valInput ? valInput.value.trim() : "";
      if (value === "") return;
      let parsedValue = value;
      if (value.toLowerCase() === "true") parsedValue = true;
      else if (value.toLowerCase() === "false") parsedValue = false;
      currentDomain.push([fieldSelect.value, opSelect.value, parsedValue]);
      window.location.href = opBuildUrl({
        domain: JSON.stringify(currentDomain),
        group_by: currentGroupBy,
      });
    });
  }

  // --- Group By: Quick Options ---
  panel.querySelectorAll(".op-groupby-option").forEach(function (a) {
    a.addEventListener("click", function (e) {
      e.preventDefault();
      const field = this.dataset.field;
      const url = new URL(window.location.href);
      const activeGroup = url.searchParams.get("group_by") || currentGroupBy;
      if (activeGroup === field) {
        url.searchParams.delete("group_by");
      } else {
        url.searchParams.set("group_by", field);
      }
      window.location.href = url.toString();
    });
  });

  // --- Group By: Custom Select ---
  const customGroupSelect = panel.querySelector(".op-custom-group-select");
  if (customGroupSelect) {
    customGroupSelect.addEventListener("change", function () {
      if (!this.value) return;
      window.location.href = opBuildUrl({
        group_by: this.value,
        domain: JSON.stringify(currentDomain),
      });
    });
  }

  // --- Favorites: Load ---
  panel.querySelectorAll(".op-load-favorite").forEach(function (a) {
    a.addEventListener("click", function (e) {
      e.preventDefault();
      window.location.href = opBuildUrl({
        domain: this.dataset.domain,
        group_by: this.dataset.groupBy || "",
      });
    });
  });

  // --- Favorites: Accordion Toggle for "Save current search" ---
  const favToggle = panel.querySelector(".op-add-favorite");
  const favForm = panel.querySelector(".op-favorite-form");
  if (favToggle && favForm) {
    favToggle.addEventListener("click", function () {
      const isOpen = favForm.style.display !== "none";
      favForm.style.display = isOpen ? "none" : "block";
      this.setAttribute("aria-expanded", String(!isOpen));
    });
  }

  // --- Favorites: Save ---
  const saveBtn = panel.querySelector(".op-save-favorite-btn");
  if (saveBtn) {
    saveBtn.addEventListener("click", function () {
      const nameInput = panel.querySelector(".op-favorite-name");
      const name = nameInput.value.trim();
      if (!name) return;
      const isDefault = panel.querySelector(".op-favorite-default").checked;
      fetch("/technical/filters/save/", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
          "X-CSRFToken": opGetCookie("csrftoken"),
        },
        body: new URLSearchParams({
          model_key: modelKey,
          name: name,
          domain: JSON.stringify(currentDomain),
          group_by: currentGroupBy,
          is_default: isDefault ? "true" : "false",
        }),
      })
        .then(function (r) {
          return r.json();
        })
        .then(function (data) {
          if (data.ok) window.location.reload();
          else alert(data.error || "Could not save filter");
        });
    });
  }

  // --- Favorites: Set Default / Delete ---
  panel.querySelectorAll(".op-set-default-btn").forEach(function (btn) {
    btn.addEventListener("click", function () {
      fetch("/technical/filters/" + this.dataset.id + "/set-default/", {
        method: "POST",
        headers: { "X-CSRFToken": opGetCookie("csrftoken") },
      }).then(function () {
        window.location.reload();
      });
    });
  });
  panel.querySelectorAll(".op-delete-favorite-btn").forEach(function (btn) {
    btn.addEventListener("click", function () {
      fetch("/technical/filters/" + this.dataset.id + "/delete/", {
        method: "POST",
        headers: { "X-CSRFToken": opGetCookie("csrftoken") },
      }).then(function () {
        window.location.reload();
      });
    });
  });
});
