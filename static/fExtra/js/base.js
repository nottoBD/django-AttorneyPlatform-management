document.addEventListener('DOMContentLoaded', function () {
    const toasts = document.querySelectorAll('.toast');
    toasts.forEach(toast => new bootstrap.Toast(toast).show());

    const languageSelectors = document.querySelectorAll('.language-selector');

    languageSelectors.forEach(function (selector) {
        selector.addEventListener('click', function (e) {
            e.preventDefault();
            const languageCode = this.getAttribute('data-language');
            const form = document.createElement('form');
            form.action = "/i18n/setlang/";
            form.method = "POST";

            // fetch  token from template
            const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
            form.innerHTML = `<input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">` +
                `<input type="hidden" name="language" value="${languageCode}">` +
                `<input type="hidden" name="next" value="${window.location.pathname}">`;

            document.body.appendChild(form);
            form.submit();
        });
    });

// Retenir la position des sous-menus
    const currentUrl = window.location.pathname.endsWith('/') ? window.location.pathname : window.location.pathname + '/';

    const submenus = document.querySelectorAll('ul.collapse.nav.flex-column');

    submenus.forEach(function(submenu) {
        submenu.querySelectorAll('a.nav-link').forEach(function(link) {
            let linkHref = link.getAttribute('href');
            linkHref = linkHref.endsWith('/') ? linkHref : linkHref + '/';

            if (currentUrl === linkHref) {
                submenu.classList.add('show');
                const parentToggle = submenu.closest('li').querySelector('a[data-bs-toggle="collapse"]');
                if (parentToggle) {
                    parentToggle.classList.add('active');
                }
            }
        });
    });
});