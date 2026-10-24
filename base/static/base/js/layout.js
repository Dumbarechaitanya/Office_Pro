// Toggle app-menu dropdowns (only items with .menu-dropdown-toggle have submenus)
document.querySelectorAll('.menu-dropdown-toggle').forEach(function (btn) {
    btn.addEventListener('click', function (e) {
        e.stopPropagation();
        const dropdown = this.nextElementSibling;
        const isOpen = dropdown.classList.contains('show');

        // close any other open dropdowns first
        document.querySelectorAll('.menu-dropdown.show').forEach(function (d) {
            d.classList.remove('show');
        });

        if (!isOpen) {
            dropdown.classList.add('show');
        }
    });
});

// Close menu dropdowns when clicking outside
document.addEventListener('click', function () {
    document.querySelectorAll('.menu-dropdown.show').forEach(function (d) {
        d.classList.remove('show');
    });
});

// Profile dropdown (separate from app menus)
document.addEventListener('click', function (e) {
    const dropdown = document.getElementById('profileDropdown');
    const btn = document.querySelector('.profile-btn');
    if (dropdown && !dropdown.contains(e.target) && btn && !btn.contains(e.target)) {
        dropdown.classList.remove('show');
    }
});
