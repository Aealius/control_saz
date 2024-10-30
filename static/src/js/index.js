const tabListLinks = document.querySelectorAll("#status-filter-tabs a"); //ссылки фильтрации по статусам
const senderSelect = document.getElementById("select-task-sender"); //дропдаун с выбором входящих/исходящих тасок

tabListLinks.forEach((tabLink) => {
    const tabElement = new bootstrap.Tab(tabLink);

    tabLink.addEventListener('click', (event) =>{
        event.preventDefault();
        tabElement.show();
    });
});

senderSelect.addEventListener('change', (event) => {
    event.preventDefault();
});