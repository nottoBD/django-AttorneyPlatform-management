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
    const container = document.querySelector('.container-fluid');
    const isActiveCheckbox = document.getElementById('isActiveFilter');
    let highlightedRowId = null;

    if (!isActiveCheckbox) {
        console.error('isActiveFilter checkbox not found!');
        return;
    }
    if (!container) {
        console.error('Container not found!');
        return;
    }

    function fetchUsers() {
        const isActive = isActiveCheckbox.checked;

        fetch(`/accounts/list?is_active=${isActive}`, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                renderAdministrators(data.administrators);
                renderMagistrates(data.magistrates);
                renderParents(data.parents);
                attachRowEventListeners();
                reapplyHighlight();
            })
            .catch(error => console.error('Fetch error:', error));
    }

    function renderAdministrators(administrators) {
        const administratorsTab = document.querySelector('.administrators-list');

        if (!administratorsTab) {
            console.error('Administrators table body not found!');
            return;
        }

        administratorsTab.innerHTML = '';

        administrators.forEach(admin => {
            const tr = document.createElement('tr');
            tr.setAttribute('data-user-id', admin.id);
            tr.classList.add('administrator-item');
            tr.innerHTML = `
                <td><img src="${admin.profile_image_url}" alt="Profile Image" width="30" height="30" class="rounded-circle"></td>
                <td>${admin.last_name}</td>
                <td>${admin.first_name}</td>
                <td>${admin.email}</td>
                <td>${admin.role}</td>
            `;
            administratorsTab.appendChild(tr);
        });
    }

    function renderMagistrates(magistrates) {
        const magistratesTab = document.querySelector('.magistrates-list');

        if (!magistratesTab) {
            console.error('Magistrates table body not found!');
            return;
        }

        magistratesTab.innerHTML = '';

        magistrates.forEach(magistrate => {
            const tr = document.createElement('tr');
            tr.setAttribute('data-user-id', magistrate.id);
            tr.classList.add('magistrate-item');
            tr.innerHTML = `
                <td><img src="${magistrate.profile_image_url}" alt="Profile Image" width="30" height="30" class="rounded-circle"></td>
                <td>${magistrate.last_name}</td>
                <td>${magistrate.first_name}</td>
                <td>${magistrate.email}</td>
                <td>${magistrate.role}</td>
                <td>${magistrate.cases_count}</td>
            `;
            magistratesTab.appendChild(tr);
        });
    }

    function renderParents(parents) {
        const parentsTab = document.querySelector('.parents-list');

        if (!parentsTab) {
            console.error('Parents table body not found!');
            return;
        }

        parentsTab.innerHTML = '';

        parents.forEach(parent => {
            const tr = document.createElement('tr');
            tr.setAttribute('data-user-id', parent.id);
            tr.classList.add('parent-item');
            tr.innerHTML = `
                <td><img src="${parent.profile_image_url}" alt="Profile Image" width="30" height="30" class="rounded-circle"></td>
                <td>${parent.last_name}</td>
                <td>${parent.first_name}</td>
                <td>${parent.email}</td>
                <td>${parent.avocats_assigned.join('<br>')}<br>${parent.juges_assigned.join('<br>')}</td>
            `;
            parentsTab.appendChild(tr);
        });
    }

    function attachRowEventListeners() {
        document.querySelectorAll('tr[data-user-id]').forEach(row => {
            let touchStartTime = 0;
            let touchTimeout;
            let clickTimeout;

            row.addEventListener('click', function(event) {
                clearTimeout(clickTimeout);
                clickTimeout = setTimeout(() => {
                    if (!event.ctrlKey) {
                        document.querySelectorAll('tr[data-user-id]').forEach(r => {
                            r.classList.remove('highlight');
                        });
                    }
                    row.classList.toggle('highlight');
                    highlightedRowId = row.classList.contains('highlight') ? row.getAttribute('data-user-id') : null;
                }, 200);
            });

            row.addEventListener('dblclick', function(event) {
                clearTimeout(clickTimeout);
                let userId = row.getAttribute('data-user-id');
                window.location.href = `/accounts/update/${userId}/`;
            });

            row.addEventListener('touchstart', function(event) {
                touchStartTime = new Date().getTime();
                if (touchTimeout) {
                    clearTimeout(touchTimeout);
                }
                touchTimeout = setTimeout(() => {
                    handleRowClick(event);
                }, 200);
            });

            row.addEventListener('touchend', function(event) {
                let touchDuration = new Date().getTime() - touchStartTime;
                if (touchDuration < 200) {
                    clearTimeout(touchTimeout);
                    handleRowDoubleClick(event);
                }
            });
        });
    }

    function handleRowClick(event) {
        if (!event.ctrlKey) {
            document.querySelectorAll('tr[data-user-id]').forEach(r => {
                r.classList.remove('highlight');
            });
        }
        event.currentTarget.classList.toggle('highlight');
        highlightedRowId = event.currentTarget.classList.contains('highlight') ? event.currentTarget.getAttribute('data-user-id') : null;
    }

    function handleRowDoubleClick(event) {
        let userId = event.currentTarget.getAttribute('data-user-id');
        window.location.href = `/accounts/update/${userId}/`;
    }

    function reapplyHighlight() {
        if (highlightedRowId) {
            const rowToHighlight = document.querySelector(`tr[data-user-id='${highlightedRowId}']`);
            if (rowToHighlight) {
                rowToHighlight.classList.add('highlight');
            }
        }
    }

    document.addEventListener('click', function(event) {
        if (!container.contains(event.target)) {
            document.querySelectorAll('tr[data-user-id]').forEach(row => {
                row.classList.remove('highlight');
            });
            highlightedRowId = null;
        }
    });

    fetchUsers();
    isActiveCheckbox.addEventListener('change', fetchUsers);

    setInterval(fetchUsers, 10000);
});
