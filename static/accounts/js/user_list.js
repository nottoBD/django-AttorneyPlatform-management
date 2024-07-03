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
                const magistratesTab = document.querySelector('.magistrates-list');
                const parentsTab = document.querySelector('.parents-list');

                if (!magistratesTab || !parentsTab) {
                    console.error('One or more table bodies not found!');
                    return;
                }

                magistratesTab.innerHTML = '';
                parentsTab.innerHTML = '';

                data.magistrates.forEach(magistrate => {
                    const tr = document.createElement('tr');
                    tr.setAttribute('data-user-id', magistrate.id);
                    tr.classList.add('magistrate-item');
                    tr.innerHTML = `<td><img src="${magistrate.profile_image_url}" alt="Profile Image" width="30" height="30" class="rounded-circle"></td><td>${magistrate.last_name}</td><td>${magistrate.first_name}</td><td>${magistrate.email}</td><td>${magistrate.role}</td><td>${magistrate.parents_count}</td>`;
                    magistratesTab.appendChild(tr);
                });

                data.parents.forEach(parent => {
                    const tr = document.createElement('tr');
                    tr.setAttribute('data-user-id', parent.id);
                    tr.classList.add('parent-item');
                    tr.innerHTML = `<td><img src="${parent.profile_image_url}" alt="Profile Image" width="30" height="30" class="rounded-circle"></td><td>${parent.last_name}</td><td>${parent.first_name}</td><td>${parent.email}</td><td>${parent.avocats_assigned.join('<br>')}<br>${parent.juges_assigned.join('<br>')}</td>`;
                    parentsTab.appendChild(tr);
                });

                attachRowEventListeners();
                reapplyHighlight();
            })
            .catch(error => console.error('Fetch error:', error));
    }

    function attachRowEventListeners() {
        document.querySelectorAll('tr[data-user-id]').forEach(row => {
            row.addEventListener('click', function(event) {
                clearTimeout(clickTimeout);
                clickTimeout = setTimeout(function() {
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
        });
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

    let clickTimeout;

    fetchUsers();
    isActiveCheckbox.addEventListener('change', fetchUsers);

    setInterval(fetchUsers, 10000);
});
