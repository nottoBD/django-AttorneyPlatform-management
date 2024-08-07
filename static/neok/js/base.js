/*
Neok-Budget: A Django-based web application for budgeting.
Copyright (C) 2024  David Botton, Arnaud Mahieu

Developed for Jurinet and its branch Neok-Budget.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
*/

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

            const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
            form.innerHTML = `<input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">` +
                `<input type="hidden" name="language" value="${languageCode}">` +
                `<input type="hidden" name="next" value="${window.location.pathname}">`;

            document.body.appendChild(form);
            form.submit();
        });
    });

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
