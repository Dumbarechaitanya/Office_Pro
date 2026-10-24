document.querySelectorAll(".submenu-toggle").forEach(function (btn) {
  btn.addEventListener("click", function () {
    this.classList.toggle("open");
    this.nextElementSibling.classList.toggle("show");
  });
});
