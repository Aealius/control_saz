let senderSelect = document.getElementById("select-task-sender"); //дропдаун с выбором входящих/исходящих тасок
let filterForm = document.getElementById("filterForm"); //форма фильтрации
let clearFilterHref = document.getElementById("clearFilterHref"); //строка "очистить фильтр" на форме фильтрации
let submitFilterFormButton = document.getElementById("submitFilterformButton"); //кнопка "применить фильтр" на форме фильтрации
let urlParams  = new URLSearchParams(window.location.search);


//получение параметров сохраненных в localStorage или отображенных в searchParams
document.addEventListener('DOMContentLoaded', () => { //задает значение дропдауна из значения, переданного в строке параметров
    let keys = [
        'creator',
        'executor',
        'month',
        'date',
        'overdue',
        'completed',
        'sn',
        'p'
    ];

    keys.forEach(key => {
        if (urlParams.has(key)){
            sessionStorage.setItem(key, urlParams.get(key));
        }
    });

    let senderValue = sessionStorage.getItem('sn') ? sessionStorage.getItem('sn') : "in";

    if (sessionStorage.getItem('executor')) {
        senderSelect.querySelector("option[value='out']").selected = true;
        
    }
    else if (sessionStorage.getItem('creator')) {
        senderSelect.querySelector("option[value='in']").selected = true;
        
    }

    document.getElementById("select-task-sender").querySelector("option[value='" + senderValue + "']").selected = true;
});

//на изменение выбранного значения в дропдайне изменяется текущий URL 
senderSelect.addEventListener('change', () => {
    let senderValue = senderSelect.value;

    window.location.href = buildQueryString(senderValue);
});

//дизейблит поля формы фильтрации, чтобы они не попадали в searchString
filterForm.addEventListener('submit', () => {
    filterForm.querySelectorAll('select').forEach( input => {
        if (input.value == '') input.disabled=true;
    });

    filterForm.querySelectorAll('input[type=month]').forEach( input => {
        if (input.value == '') input.disabled=true;
    });

    filterForm.querySelectorAll('input[type=date]').forEach( input => {
        if (input.value == '') input.disabled=true;
    });

    filterForm.querySelectorAll('input[type=checkbox]').forEach( input => {
        if (input.value == '') input.disabled=true;
    });

    let senderHiddenInput =  document.getElementById("hiddenSender");
    senderHiddenInput.value = senderSelect.value;

});

clearFilterHref.addEventListener('click', () => {
    sessionStorage.setItem('sn', 'in');
    window.location.replace(window.location.origin + window.location.pathname);
});

function buildQueryString(senderValue){ //построение строки параметров для последующей фильтрации по отправителю

    let newUrl =  new URL(window.location.origin + window.location.pathname);

    let urlParams = new URLSearchParams(window.location.search);

    newUrl.searchParams.delete('sn');
    newUrl.searchParams.delete('p');

    urlParams.entries().forEach(([key, value]) => {
        newUrl.searchParams.append(key, value);
    });


    newUrl.searchParams.set('sn', senderValue);
    newUrl.searchParams.set('p', 1);

    return newUrl;
}
