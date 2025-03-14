let senderSelect = document.getElementById("select-task-sender"); //дропдаун с выбором входящих/исходящих тасок
let filterForm = document.getElementById("filterForm"); //форма фильтрации
let resendForm = document.getElementById("resendForm");
let resendModal = document.getElementById("resendModal");
let clearFilterHref = document.getElementById("clearFilterHref"); //строка "очистить фильтр" на форме фильтрации
let submitFilterFormButton = document.getElementById("submitFilterformButton"); //кнопка "применить фильтр" на форме фильтрации
let resendSelect = document.getElementById("executorResend"); //дропдаун с выбором исполнителей по отделам
let nomenclatureSelect = document.getElementById("nm-select");
let urlParams = new URLSearchParams(window.location.search);
let globalTaskId = '';
let currentUserLogin = '';
const base_url_api = window.location.origin + '/api';

function setTaskId(taskId) {
    globalTaskId = taskId;
}

function taskConfirmation(id, path) {
    let base_url = window.location.origin;
    let addNote = '';

    addNote = document.getElementById("admin_note_" + id).value;

    console.log(addNote);
    const myHeaders = new Headers();
    myHeaders.append("Content-Type", "application/json");

    fetch(base_url + "/tasks/" + id + "/" + path, {
        method: "POST",
        body: JSON.stringify({ note: addNote }),
        headers: myHeaders,
    }).then((response) => {
        console.log(response);
    }).then(() => {
        updateIndex();
    })
}

function taskReview(id) {
    let base_url = window.location.origin;

    fetch(base_url + "/review/" + id, {
        method: "POST",
    }).then((response) => {
        console.log(response);
    }).then(() => {
        updateIndex();
    })
}

// Здесь document.documentElement.innerHTML меняется напрямую, вследствие чего слетает js код, и 
// некоторые вещи могут перестать работать. Приходится заново навешивать все ивенты на html элементы.
// 
// TODO: По-хорошему найти другой способ обновить отдельную строку или хотя бы целую страницу и убрать
// это костыльное решение --- по поводу этого можно было бы посмотреть в сторону htmx
function updateIndex() {
    let base_url = window.location.origin;
    const queryString = window.location.search;

    fetch(base_url + "/" + queryString,
        { method: "GET" })
        .then(response => {
            return response.text();
        })
        .then(html => {
            let oldValue = document.getElementById("select-task-sender").value;
            document.documentElement.innerHTML = html;

            senderSelect = document.getElementById("select-task-sender");
            filterForm = document.getElementById("filterForm");
            clearFilterHref = document.getElementById("clearFilterHref");
            submitFilterFormButton = document.getElementById("submitFilterformButton");
            resendForm = document.getElementById("resendForm");
            resendModal = document.getElementById("resendModal");
            resendSelect = document.getElementById("executorResend");

            $('.selectpicker').selectpicker();
            $('#select-task-sender').val(oldValue);
            $('#select-task-sender').change();
            document.getElementById("select-task-sender").addEventListener('change', Event => {
                let options = Event.target.options;
                let senderValue = "in";

                for (let i = 0; i < options.length; i++) {
                    if (options[i].selected) {
                        senderValue = options[i].value;
                    }
                }

                window.location.href = buildQueryString(senderValue);
            });

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
                    'dn',
                    'p'
                ];

                keys.forEach(key => {
                    if (urlParams.has(key)) {
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


            //дизейблит поля формы фильтрации, чтобы они не попадали в searchString
            filterForm.addEventListener('submit', () => {
                filterForm.querySelectorAll('select').forEach(input => {
                    if (input.value == '') input.disabled = true;
                });

                filterForm.querySelectorAll('input[type=month]').forEach(input => {
                    if (input.value == '') input.disabled = true;
                });

                filterForm.querySelectorAll('input[type=date]').forEach(input => {
                    if (input.value == '') input.disabled = true;
                });

                filterForm.querySelectorAll('input[type=checkbox]').forEach(input => {
                    if (input.value == '') input.disabled = true;
                });

                filterForm.querySelectorAll('input[type=text]').forEach(input => {
                    if (input.value == '') input.disabled = true;
                });

                //добавляет спрятанное поле для того, чтобы отпралять параметр "sn" на бэк
                let senderHiddenInput = document.getElementById("hiddenSender");
                senderHiddenInput.value = senderSelect.value;

            });


            clearFilterHref.addEventListener('click', () => {
                let newUrl = new URL(window.location.origin + window.location.pathname);
                sessionStorage.setItem('sn', urlParams.get('sn') ? urlParams.get('sn') : 'in');

                newUrl.searchParams.set('sn', urlParams.get('sn') ? urlParams.get('sn') : 'in');
                newUrl.searchParams.set('p', 1);

                window.location.replace(newUrl);
            });

            $(document).on('show.bs.modal', '#resendModal', function () {
                $('.selectpicker').selectpicker('deselectAll');
            });

            //на изменение выбранного значения в дропдайне изменяется текущий URL 
            senderSelect.addEventListener('change', () => {
                let senderValue = senderSelect.value;

                window.location.href = buildQueryString(senderValue);
            });
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
        if (urlParams.has(key)) {
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

    fetch(base_url_api + '/users/current_user')
        .then(response => response.json())
        .then(user => {
            currentUserLogin = user.login;
        })
        .catch(console.error);
});

//на изменение выбранного значения в дропдайне изменяется текущий URL 
senderSelect.addEventListener('change', () => {
    let senderValue = senderSelect.value;

    window.location.href = buildQueryString(senderValue);
});

//дизейблит поля формы фильтрации, чтобы они не попадали в searchString
filterForm.addEventListener('submit', () => {
    filterForm.querySelectorAll('select').forEach(input => {
        if (input.value == '') input.disabled = true;
    });

    filterForm.querySelectorAll('input[type=month]').forEach(input => {
        if (input.value == '') input.disabled = true;
    });

    filterForm.querySelectorAll('input[type=date]').forEach(input => {
        if (input.value == '') input.disabled = true;
    });

    filterForm.querySelectorAll('input[type=checkbox]').forEach(input => {
        if (input.value == '') input.disabled = true;
    });

    filterForm.querySelectorAll('input[type=text]').forEach(input => {
        if (input.value == '') input.disabled = true;
    });


    //добавляет спрятанное поле для того, чтобы отпралять параметр "sn" на бэк
    let senderHiddenInput = document.getElementById("hiddenSender");
    senderHiddenInput.value = senderSelect.value;

});

clearFilterHref.addEventListener('click', () => {
    let newUrl = new URL(window.location.origin + window.location.pathname);
    sessionStorage.setItem('sn', urlParams.get('sn') ? urlParams.get('sn') : 'in');

    newUrl.searchParams.set('sn', urlParams.get('sn') ? urlParams.get('sn') : 'in');
    newUrl.searchParams.set('p', 1);

    window.location.replace(newUrl);
});



function buildQueryString(senderValue) { //построение строки параметров для последующей фильтрации по отправителю

    let newUrl = new URL(window.location.origin + window.location.pathname);

    newUrl.searchParams.delete('sn');
    newUrl.searchParams.delete('p');

    [...urlParams.entries()].forEach(([key, value]) => {
        newUrl.searchParams.append(key, value);
    });

    newUrl.searchParams.set('sn', senderValue);
    newUrl.searchParams.set('p', 1);

    return newUrl;
}

//дизейблим "№ документа" в фильтрации если выбрано "все"
nomenclatureSelect.addEventListener('change', (event) => {
    let docnumberInput = document.getElementById('doc-number-input');
    docnumberInput.disabled = event.target.value == '' ? true : false;
    if (docnumberInput.disabled){
        docnumberInput.value = '';
    }
});

//снимаем выбор с множественного селекта при его показе при пересылке
$(document).on('show.bs.modal', '#resendModal', function () {
    $('.selectpicker').selectpicker('deselectAll');
});

//при загрузке множ селекта получаем с бэка сотрудников бухгалтерии (!!! загружен он уже при загрузке страницы и спрятан и это не совсем гуд)
$(document).on('loaded.bs.select', '#employee', function () {
    if (currentUserLogin == "8") {
        let employeeId = '27';
        $('#employeeLabel').text('Сотрудник (234 Бухгалтерия):');

        // Получение из бэка сотрудников отдела
        fetch(base_url_api + "/users/" + employeeId + "/employees", {
            method: "GET"
        }).then((response) => {
            console.log(response);
            return response.text();
        }).then((text) => {
            let obj = JSON.parse(text);
            let selectEmployee = document.getElementById('employee');

            let optDef = document.createElement('option');
            optDef.value = '';
            optDef.innerHTML = 'Для отдела';
            selectEmployee.appendChild(optDef);

            for (let i = 0; i < obj.length; i++) {
                let opt = document.createElement('option');
                opt.value = obj[i].id;
                opt.innerHTML = obj[i].surname + " " + obj[i].name + " " + obj[i].patronymic;
                selectEmployee.appendChild(opt);
            }

            // Оставляем здесь, ибо если вынести из then - сработает слишком рано
            $('.selectpicker').selectpicker('refresh');
        });
    }
});

// Для модалки пересылки
function updateEmployee() {
    currentUser = '';
    let executorResendSelect = document.getElementById('executorResend'); //множественный select дял выбора исполнителя
    let selectEmployeeDiv = document.getElementById('selectpicker2'); //div с выбором ответственного лица

    let executorResendSelectedOptions = executorResendSelect.selectedOptions;

    if (executorResendSelectedOptions.length !== 0) {
        eResendValueArray = [...executorResendSelectedOptions].map(o => o.value);

        if (eResendValueArray.includes("27") && currentUserLogin === "8") {
            $("#employee").prop("disabled", false);
            $("#employee").next("button").removeClass("disabled");
            selectEmployeeDiv.style.display = 'block';
        }
    }
    else {
        selectEmployeeDiv.style.display = 'none';
        selectEmployeeDiv.disabled = true;
        $('.selectpicker').selectpicker('refresh');
    }
}



//валидация формы в переслыке задачи
resendSelect && resendSelect.addEventListener('change', (event) => {

    let validationArray = [checkExecutorSelectValidity(resendForm, resendSelect)];

    if (!validate(validationArray, resendForm)){
        event.preventDefault();
    }
});

// Пересылка задачи
function resendTask() {

    if (validate([checkExecutorSelectValidity(resendForm, resendSelect)], resendForm)) {
        let base_url = window.location.origin;
        let employee = '';
        let executors = '';

        employee = document.getElementById('employee').value;
        executors = document.getElementById('executors').value;

        const myHeaders = new Headers();
        myHeaders.append("Content-Type", "application/json");

        fetch(base_url + "/resend/" + globalTaskId, {
            method: "POST",
            body: JSON.stringify({ employee: employee, executors: executors }),
            headers: myHeaders,
        }).then((response) => {
            console.log(response);
        }).then(() => {
            updateIndex();
        })
    }
}


//необходимо для пересылки задачи так как там используется множественный селект с немного изменной логикой
function updateSelectedExecutors() {
    let resendSelectedOptions = resendSelect.selectedOptions;
    let selectedValuesArray = [...resendSelectedOptions].map(o => o.value);
    let selectedTextArray = [...resendSelectedOptions].map(o => o.innerHTML);

    addExecutorToSelected(selectedValuesArray, selectedTextArray);

    updateEmployee();
}

function addExecutorToSelected(valueArray, textArray) {
    let selectedExecutorsDiv = document.getElementById("selectedExecutors");
    selectedExecutorsDiv.innerHTML = "";

    let hiddenInput = document.createElement('input');
    hiddenInput.type = 'hidden';
    hiddenInput.id = 'executors';

    if (resendSelect.options.length == resendSelect.selectedOptions.length) {
        let allSpan = document.createElement('span');
        allSpan.classList.add('badge', 'badge-primary', 'mr-2', 'mb-2', 'executor-item');
        allSpan.textContent = 'Всем';
        allSpan.setAttribute('data-value', 'all');

        let closeButton = document.createElement('button');
        closeButton.type = 'button';
        closeButton.classList.add('close', 'small-close');
        closeButton.innerHTML = '×';
        closeButton.style.fontSize = '1rem';

        allSpan.appendChild(closeButton);
        selectedExecutorsDiv.appendChild(allSpan);
        closeButton.addEventListener('click', function () {
            this.parentNode.remove();
            $('.selectpicker').selectpicker('deselectAll');
        });
        allSpan.appendChild(hiddenInput);
        hiddenInput.value = 'all';
    }
    else {
        for (let i = 0; i < valueArray.length; i++) {

            let executorSpan = document.createElement('span');
            executorSpan.classList.add('badge', 'badge-primary', 'mr-2', 'mb-2', 'executor-item');
            executorSpan.textContent = textArray[i];
            executorSpan.setAttribute('data-value', valueArray[i]);

            let closeButton = document.createElement('button');
            closeButton.type = 'button';
            closeButton.classList.add('close', 'small-close', 'fs-1');
            closeButton.innerHTML = '×';
            closeButton.addEventListener('click', function () {
                let currentValue = this.parentNode.dataset.value;  // get the value
                if (currentValue == 'all') { // Удаление  allSelected  
                    allSelected = false // ставим false allSelected
                }

                this.parentNode.remove();

                let elements = resendSelect.selectedOptions;

                for (let i = 0; i < elements.length; i++) {
                    if ((elements[i].value) == currentValue) {
                        if (elements[i].value == '27') {
                            let employeeDiv = document.getElementById('selectpicker2');
                            let employeeSelectpicker = document.getElementById('employee');
                            employeeDiv.style.display = 'none';
                            employeeSelectpicker.disabled = true;
                        }
                        elements[i].selected = false;
                        $('#executorResend').selectpicker('render');
                    }
                }
                updateSelectedExecutors();

            });
            executorSpan.appendChild(closeButton);
            selectedExecutorsDiv.appendChild(executorSpan);
            executorSpan.appendChild(hiddenInput);
        }
        hiddenInput.value = valueArray;
    }
}


