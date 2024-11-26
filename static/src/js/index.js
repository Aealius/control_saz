let senderSelect = document.getElementById("select-task-sender"); //дропдаун с выбором входящих/исходящих тасок
let filterForm = document.getElementById("filterForm"); //форма фильтрации
let clearFilterHref = document.getElementById("clearFilterHref"); //строка "очистить фильтр" на форме фильтрации
let submitFilterFormButton = document.getElementById("submitFilterformButton"); //кнопка "применить фильтр" на форме фильтрации
let urlParams  = new URLSearchParams(window.location.search);

function taskConfirmation(id, path, role) {
    var base_url = window.location.origin;
    let addNote = '';

    addNote = document.getElementById(role + "_note_"+ id).value;

    console.log(addNote);
    const myHeaders = new Headers();
    myHeaders.append("Content-Type", "application/json");

    fetch(base_url + "/"+ role +"/tasks/" + id + "/" + path, {
        method: "POST",
        body: JSON.stringify({ note: addNote }),
        headers: myHeaders,
      }).then((response) => {
        console.log(response);
      }).then(() =>{
        const queryString = window.location.search;

        fetch(base_url + "/" + queryString, 
            {method: "GET"})
            .then(response => {
                return response.text();
            })
            .then(html => {
                let oldValue = document.getElementById("select-task-sender").value;
                document.documentElement.innerHTML = html;

                // Тк после обновления html селект ломается, необходимо заного привязывать on change
                // TODO: если возможно, разобраться подробнее в чем причина поломки и убрать это полукостыльное решение
                $('.selectpicker').selectpicker();
                $('#select-task-sender').val(oldValue); 
                $('#select-task-sender').change();
                document.getElementById("select-task-sender").addEventListener('change', Event => {
                    let options = Event.target.options;
                    let senderValue = "in";

                    for(let i = 0; i < options.length; i++){
                        if(options[i].selected){
                            senderValue = options[i].value;
                        }
                    }
                
                    window.location.href = buildQueryString(senderValue);
                });
            })
      })
}

function taskReview(id) {
    var base_url = window.location.origin;

    fetch(base_url + "/review/" + id, {
        method: "POST",
      }).then((response) => {
        console.log(response);
      }).then(() =>{
        const queryString = window.location.search;

        fetch(base_url + "/" + queryString, 
            {method: "GET"})
            .then(response => {
                return response.text();
            })
            .then(html => {
                let oldValue = document.getElementById("select-task-sender").value;
                document.documentElement.innerHTML = html;

                // Тк после обновления html селект ломается, необходимо заного привязывать on change
                // TODO: если возможно, разобраться подробнее в чем причина поломки и убрать это полукостыльное решение
                $('.selectpicker').selectpicker();
                $('#select-task-sender').val(oldValue); 
                $('#select-task-sender').change();
                document.getElementById("select-task-sender").addEventListener('change', Event => {
                    let options = Event.target.options;
                    let senderValue = "in";

                    for(let i = 0; i < options.length; i++){
                        if(options[i].selected){
                            senderValue = options[i].value;
                        }
                    }
                
                    window.location.href = buildQueryString(senderValue);
                });
            })
      })
}


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

    //если есть фильтрация по исполнителю, то значения дропдауна станет "Исходящие"
    if (sessionStorage.getItem('executor')) {
        senderSelect.querySelector("option[value='out']").selected = true;
        
    }
    else if (sessionStorage.getItem('creator')) { // если есть фильтрация по создателю, то значение дропдауна станет "Входящие"
        senderSelect.querySelector("option[value='in']").selected = true;
        
    }
    //когда нет фильтра по отправителю,
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

    //добавляет спрятанное поле для того, чтобы отпралять параметр "sn" на бэк
    let senderHiddenInput =  document.getElementById("hiddenSender");
    senderHiddenInput.value = senderSelect.value;

});

clearFilterHref.addEventListener('click', () => {
    let newUrl =  new URL(window.location.origin + window.location.pathname);
    sessionStorage.setItem('sn', urlParams.get('sn') ? urlParams.get('sn') : 'in');

    newUrl.searchParams.set('sn', urlParams.get('sn') ? urlParams.get('sn') : 'in');
    newUrl.searchParams.set('p', 1);

    window.location.replace(newUrl);
});

function buildQueryString(senderValue){ //построение строки параметров для последующей фильтрации по отправителю

    let newUrl =  new URL(window.location.origin + window.location.pathname);

    newUrl.searchParams.delete('sn');
    newUrl.searchParams.delete('p');

    [...urlParams.entries()].forEach(([key, value]) => {
        newUrl.searchParams.append(key, value);
    });

    newUrl.searchParams.set('sn', senderValue);
    newUrl.searchParams.set('p', 1);

    return newUrl;
}
