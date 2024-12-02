let senderSelect = document.getElementById("select-task-sender"); //дропдаун с выбором входящих/исходящих тасок
let filterForm = document.getElementById("filterForm"); //форма фильтрации
let resendForm = document.getElementById("resendForm");
let resendModal = document.getElementById("resendModal");
let clearFilterHref = document.getElementById("clearFilterHref"); //строка "очистить фильтр" на форме фильтрации
let submitFilterFormButton = document.getElementById("submitFilterformButton"); //кнопка "применить фильтр" на форме фильтрации
let resendSelect = document.getElementById("executorResend"); //дропдаун с выбором исполнителей по отделам
let urlParams = new URLSearchParams(window.location.search);
let globalTaskId = '';

function setTaskId(taskId) {
    globalTaskId = taskId;
}

function taskConfirmation(id, path, role) {
    var base_url = window.location.origin;
    let addNote = '';

    addNote = document.getElementById(role + "_note_" + id).value;

    console.log(addNote);
    const myHeaders = new Headers();
    myHeaders.append("Content-Type", "application/json");

    fetch(base_url + "/" + role + "/tasks/" + id + "/" + path, {
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
    var base_url = window.location.origin;

    fetch(base_url + "/review/" + id, {
        method: "POST",
    }).then((response) => {
        console.log(response);
    }).then(() => {
        updateIndex();
    })
}

// Здесь document.documentElement.innerHTML меняется напрямую, вследствие чего слетает js код и 
// некоторые вещи могут перестать работать. Приходится заного навешивать все ивенты на html элементы.
// 
// TODO: По хорошему найти другой способ обновить отдельную строку или хотя бы целую страницу и убрать
// это костыльное решение
function updateIndex() {
    var base_url = window.location.origin;
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


$(document).on('show.bs.modal', '#resendModal', function () {
    $('.selectpicker').selectpicker('deselectAll');
});

// Для модалки пересылки
function updateEmployee(userLogin) {
    let executorResendSelect = document.getElementById('executorResend'); //множественный select дял выбора исполнителя
    let selectEmployeeDiv = document.getElementById('selectpicker2'); //div с выбором ответственного лица
    let employeeSelectpicker = document.getElementById('employee');

    let executorResendSelectedOptions = executorResendSelect.selectedOptions;

    // Пока что удаляем все значения и получаем их с бэка заново.
    // В дальнейшем подумать о том, как это улучшить,
    // тк слишком много запросов получится, особенно если будет много отделов
    $('#employee').find('[value!=\'\']').remove();

    // Для теста пока добавляем только глав буху, поэтому тут проверка на id бухгалтерии
    // В дальнейшем это можно/нужно улучшить
    if (executorResendSelectedOptions.length !== 0) {
        eResendValueArray = [...executorResendSelectedOptions].map(o => o.value);

        if (eResendValueArray.includes('27') && userLogin == '8') {
            employeeSelectpicker.disabled = false;
            selectEmployeeDiv.style.display = 'block';

            // Опять же пока заглушка чисто для бухгалтерии
            let employeeId = '27';
            $('#employeeLabel').text('Сотрудник (234 Бухгалтерия):');

            const base_url = window.location.origin;

            // Получение из бэка сотрудников отдела
            fetch(base_url + "/api/users/" + employeeId + "/employees", {
                method: "GET"
            }).then((response) => {
                console.log(response);
                return response.text();
            }).then((text) => {
                let obj = JSON.parse(text);
                let selectEmployee = document.getElementById('employee');

                for (var i = 0; i < obj.length; i++) {
                    var opt = document.createElement('option');
                    opt.value = obj[i].id;
                    opt.innerHTML = obj[i].surname + " " + obj[i].name + " " + obj[i].patronymic;
                    selectEmployee.appendChild(opt);
                }

                // Оставляем здесь, ибо если вынести из then - сработает слишком рано
                $('.selectpicker').selectpicker('refresh');
            })
        }
    }
    else {
        selectEmployeeDiv.style.display = 'none';
        selectEmployeeDiv.disabled = true;
        $('.selectpicker').selectpicker('refresh');
    }
}

// Пересылка задачи
function resendTask() {

    if (validate([checkSimpleExecutorSelect(document.getElementById("executorResend"))], resendForm)) {
        var base_url = window.location.origin;
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

function updateSelectedExecutors(userLogin) {
    let resendSelectedOptions = resendSelect.selectedOptions;
    let selectedValuesArray = [...resendSelectedOptions].map(o => o.value);
    let selectedTextArray = [...resendSelectedOptions].map(o => o.innerHTML);

    addExecutorToSelected(selectedValuesArray, selectedTextArray);

    updateEmployee(userLogin);
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
                updateSelectedExecutors()

            });
            executorSpan.appendChild(closeButton);
            selectedExecutorsDiv.appendChild(executorSpan);
            executorSpan.appendChild(hiddenInput);
        }
        hiddenInput.value = valueArray;
    }
}


