document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("op-model-create-form");
  if (!form) return;

  const tbody = document.getElementById("op-inline-fields-body");
  const addBtn = document.getElementById("op-add-field-row");
  const fieldsJsonInput = document.getElementById("op-fields-json");
  const typeOptionsHtml = tbody.querySelector(".op-row-field-type").innerHTML;
  const relationOptionsHtml = tbody.querySelector(".op-row-relation").innerHTML;

  function bindRow(row) {
    row.querySelector(".op-row-delete").addEventListener("click", function () {
      row.remove();
    });

    const typeSelect = row.querySelector(".op-row-field-type");
    const relationSelect = row.querySelector(".op-row-relation");
    function syncRelationEnabled() {
      const isFk = typeSelect.value === "FK";
      relationSelect.disabled = !isFk;
      if (!isFk) relationSelect.value = "";
    }
    typeSelect.addEventListener("change", syncRelationEnabled);
    syncRelationEnabled();
  }
  tbody.querySelectorAll(".op-inline-row").forEach(bindRow);

  addBtn.addEventListener("click", function () {
    const row = document.createElement("tr");
    row.className = "op-inline-row";
    row.innerHTML =
      '<td><input type="text" class="op-row-field-name"></td>' +
      '<td><select class="op-row-field-type">' +
      typeOptionsHtml +
      "</select></td>" +
      '<td><select class="op-row-relation" disabled>' +
      relationOptionsHtml +
      "</select></td>" +
      '<td><input type="checkbox" class="op-row-required"></td>' +
      '<td><button type="button" class="op-row-delete" title="Remove row">&#10005;</button></td>';
    tbody.appendChild(row);
    bindRow(row);
  });

  form.addEventListener("submit", function () {
    const rows = [];
    tbody.querySelectorAll(".op-inline-row").forEach(function (row) {
      const name = row.querySelector(".op-row-field-name").value.trim();
      if (!name) return;
      const fieldType = row.querySelector(".op-row-field-type").value;
      const relationVal = row.querySelector(".op-row-relation").value;
      rows.push({
        field_name: name,
        field_type: fieldType,
        is_required: row.querySelector(".op-row-required").checked,
        relation_model_id:
          fieldType === "FK" && relationVal ? parseInt(relationVal, 10) : null,
      });
    });
    fieldsJsonInput.value = JSON.stringify(rows);
  });
});
