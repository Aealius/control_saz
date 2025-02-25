const base_url = window.location.origin;
const searchInput = document.getElementById('search-input');
const xMarkIcon = document.querySelector('.search-cross');

async function setStatusInWork(issue_id) {
    await fetch(base_url + '/tech/issue_in_work/' + issue_id, {
        method: "POST"
    }).then(response => console.log(response)).then(() => {
        updatePage();
    })
}

async function setStatusCompleted(issue_id){
    await fetch(base_url + '/tech/issue_completed/' + issue_id, {
        method: "POST"
    }).then(response => console.log(response)).then(() => {
            updatePage();
    })
}

async function deleteIssue(issue_id) {
    if (confirm('Вы уверены, что хотите удалить эту задачу?')) {
        await fetch(base_url + '/tech/delete/' + issue_id, {
            method: "DELETE"
        }).then(response => console.log(response)).then(() => {
            updatePage();
        })
    }
}


function toggleClearButton() {
    xMarkIcon.style.display = searchInput.value ? 'block' : 'none';
}

//начальное состояние
toggleClearButton();

searchInput.addEventListener('input', toggleClearButton);

xMarkIcon.addEventListener('click', (e) => {
    let currentURL = new URL(window.location.origin + window.location.pathname + window.location.search);
    if (currentURL.searchParams.get("search")){
        currentURL.searchParams.delete("search");
        window.location.href = currentURL;
    }
    else{
        searchInput.value = '';
        toggleClearButton();
        searchInput.focus();
    }
});


// Здесь document.documentElement.innerHTML меняется напрямую, вследствие чего слетает js код, и 
// некоторые вещи могут перестать работать. Приходится заново навешивать все ивенты на html элементы.
// 
// TODO: По-хорошему найти другой способ обновить отдельную строку или хотя бы целую страницу и убрать
// это костыльное решение --- по поводу этого можно было бы посмотреть в сторону htmx
function updatePage() {
    fetch(window.location.href,
        { method: "GET" })
        .then(response => {
            return response.text();
        })
        .then(html => {
            document.documentElement.innerHTML = html;

            //senderSelect = document.getElementById("select-task-sender");
        })
}