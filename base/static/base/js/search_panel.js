// search_panel.js -- single toggle opens a 3-column popover: Filters | Group By | Favorites

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

document.addEventListener("DOMContentLoaded", function () {
  const panel = document.querySelector(".op-search-panel");
  if (!panel) return;

  const modelKey = panel.dataset.modelKey;
  let currentDomain = [];
  try {
    currentDomain = JSON.parse(panel.dataset.currentDomain || "[]");
  } catch (e) {
    currentDomain = [];
  }
  const currentGroupBy = panel.dataset.currentGroupBy || "";

  // --- single toggle opens/closes the whole popover ---
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

  // --- custom filter builder ---
  const fieldSelect = panel.querySelector(".op-filter-field");
  const opSelect = panel.querySelector(".op-filter-operator");
  const OPERATORS = window.OP_FILTER_OPERATORS || {};

  function refreshOperators() {
    if (!fieldSelect || !opSelect) return;
    const selected = fieldSelect.selectedOptions[0];
    const type = selected ? selected.dataset.type : null;
    const ops = OPERATORS[type] || [["=", "is"]];
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
      const value = panel.querySelector(".op-filter-value").value;
      if (value === "") return;
      let parsedValue = value;
      if (value === "true") parsedValue = true;
      else if (value === "false") parsedValue = false;
      currentDomain.push([fieldSelect.value, opSelect.value, parsedValue]);
      window.location.href = opBuildUrl({
        domain: JSON.stringify(currentDomain),
        group_by: currentGroupBy,
      });
    });
  }

  // --- group by: quick options ---
  panel.querySelectorAll(".op-groupby-option").forEach(function (a) {
    a.addEventListener("click", function (e) {
      e.preventDefault();
      const field = this.classList.contains("active") ? "" : this.dataset.field;
      window.location.href = opBuildUrl({
        group_by: field,
        domain: JSON.stringify(currentDomain),
      });
    });
  });

  // --- group by: custom select ---
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

  // --- favorites: load ---
  panel.querySelectorAll(".op-load-favorite").forEach(function (a) {
    a.addEventListener("click", function (e) {
      e.preventDefault();
      window.location.href = opBuildUrl({
        domain: this.dataset.domain,
        group_by: this.dataset.groupBy || "",
      });
    });
  });

  // --- favorites: accordion toggle for "Save current search" ---
  const favToggle = panel.querySelector(".op-add-favorite");
  const favForm = panel.querySelector(".op-favorite-form");
  if (favToggle && favForm) {
    favToggle.addEventListener("click", function () {
      const isOpen = favForm.style.display !== "none";
      favForm.style.display = isOpen ? "none" : "block";
      this.setAttribute("aria-expanded", String(!isOpen));
    });
  }

  // --- favorites: save ---
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

  // --- favorites: set default / delete ---
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
