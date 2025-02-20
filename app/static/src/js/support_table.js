const base_url = window.location.origin;

async function setStatusInWork(issue_id){
    await fetch(base_url + '/tech/issue_in_work/' + issue_id)
        .then(response => console.log(response)).then(() => {
            updatePage();
        })
}

async function setStatusCompleted(issue_id){
    await fetch(base_url + '/tech/issue_completed/' + issue_id)
        .then(response => console.log(response)).then(() => {
            updatePage();
        })

        // fetch(base_url + "/review/" + id, {
        //     method: "POST",
        // }).then((response) => {
        //     console.log(response);
        // }).then(() => {
        //     updateIndex();
        // })
}




// Здесь document.documentElement.innerHTML меняется напрямую, вследствие чего слетает js код, и 
// некоторые вещи могут перестать работать. Приходится заново навешивать все ивенты на html элементы.
// 
// TODO: По-хорошему найти другой способ обновить отдельную строку или хотя бы целую страницу и убрать
// это костыльное решение --- по поводу этого можно было бы посмотреть в сторону htmx (но эта библиотека выглядит странной и непонятной (да и разбираться с ней лень :D))
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