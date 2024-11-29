
const deadlineInput = document.getElementById('deadline'); 
const executorSelect = document.getElementById('executor');
const descriptionInput = document.getElementById('description');
const selectedExecutorsDiv = document.getElementById('selected-executors');
const extendDeadlineCheckbox = document.getElementById('extend_deadline');
const extendedDeadlineField = document.getElementById('extended_deadline_field');
const dateCreatedInput = document.getElementById('date_created');
const fileUploadInput = document.getElementById('file')
const editTaskForm = document.getElementById('editTaskForm')
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const fileList = document.getElementById('fileList');
const base_url = window.location.origin;

let files = [];

document.addEventListener('DOMContentLoaded', () => {
    handleDepartmentAppearing(executorSelect);
});

document.getElementById('executor').addEventListener('change', (event) => {
    let validationResultArray = [checkSimpleExecutorSelect(executorSelect)];

    if (!validate(validationResultArray, editTaskForm)){
        event.preventDefault();
    }

    handleDepartmentAppearing(executorSelect);
});

document.getElementById('deadline').addEventListener('change', (event) => {
    let validationResultArray = [checkDeadlineDateValidity(deadlineInput, dateCreatedInput)];

    if (!validate(validationResultArray, editTaskForm)){
        event.preventDefault();
    }
});

document.getElementById('description').addEventListener('change', (event) => {
    let validationResultArray = [checkDescriptionValidity(descriptionInput)];

    if (!validate(validationResultArray, editTaskForm)){
        event.preventDefault();
    }
});

editTaskForm.addEventListener('submit', async (event) => {
    event.preventDefault();

    let validationResultArray = [checkDeadlineDateValidity(deadlineInput, dateCreatedInput),  checkDescriptionValidity(descriptionInput), checkSimpleExecutorSelect(executorSelect)];

    if (validate(validationResultArray, event.target)) {
        let formData = new FormData(event.target);

        files.forEach(file => {
            formData.append('files', file);
        });

        let pInput = document.getElementById("p");
        let snInput = document.getElementById("sn");

        pInput.value = sessionStorage.getItem('p');
        snInput.value = sessionStorage.getItem('sn');

        var base_url = window.location.origin;
        await fetch(base_url + window.location.pathname, {
            method: 'POST',
            body: formData,
        });

        document.location.replace(document.referrer);
    }
});

// Функция из файла fileUpload.js для добавления addEventListener к инпуту
addUploadEventListeners(fileInput, dropZone)

function toggleDeadline() {
    let deadlineField = document.getElementById('deadlineField');
    let deadlineInput = document.getElementById('deadline');
    let бессрочноCheckbox = document.getElementById('is_бессрочно');

    if (бессрочноCheckbox.checked) {
        deadlineField.style.display = 'none';
        deadlineInput.value = ''; // Очистить значение поля срока
        extendDeadlineCheckbox.disabled = true;
        deadlineInput.disabled = true; 
        extendDeadlineCheckbox.checked = false;
        extendedDeadlineField.style.display = 'none';
    }
    else {
        deadlineField.style.display = 'block';
        deadlineInput.disabled  = false;
        extendDeadlineCheckbox.disabled = false;
    }
}

extendDeadlineCheckbox.addEventListener('change', function () {
    if (this.checked) {
        extendedDeadlineField.style.display = 'block';
        extendedDeadlineField.disabled = false;


    } else {
        extendedDeadlineField.style.display = 'none';
        extendedDeadlineField.disabled = true;
    }
});

//функция фетчит сотрудников отдела, когда выбирается отдел из первого дропдауна
async function handleDepartmentAppearing(executorSelect){
    let divSelectEmployee = document.getElementById('selectpicker2');

    // Пока что удаляем все значения и получаем их с бэка заново.
    // В дальнейшем подумать о том, как это улучшить,
    // тк слишком много запросов получится, особенно если будет много отделов
    $('#employee').find('[value!=\'\']').remove();

    // Для теста пока добавляем только глав буху, поэтому тут проверка на id бухгалтерии
    // В дальнейшем это можно/нужно улучшить
    if(executorSelect.value  == '27'){
        divSelectEmployee.style.display = 'block';

        // Опять же пока заглушка чисто для бухгалтерии
        let employeeId = '27';
        $('#employeeLabel').text('Сотрудник (234 Бухгалтерия):');
    
        // Получение из бэка сотрудников отдела
        await fetch(base_url + "/api/users/" + employeeId + "/employees", {
            method: "GET"
        }).then((response) => {
            return response.text();
        }).then((text) => {
            let obj = JSON.parse(text);
            
            // Получаем задачу, чтобы узнать id прикрепленного исполнителя
            let taskId = window.location.pathname.split('/')[2];
            fetch(base_url + "/api/tasks/" + taskId, {
                method: "GET"
            }).then((TaskResponse) => {
                return TaskResponse.text();
            }).then((TaskResponse) => {
                let TaskObj = JSON.parse(TaskResponse);

                let selectEmployee = document.getElementById('employee');

                for (var i = 0; i < obj.length; i++) {
                    var opt = document.createElement('option');
                    opt.value = obj[i].id;
                    opt.innerHTML = obj[i].surname + " " + obj[i].name + " " + obj[i].patronymic;

                    if(TaskObj.employeeId == obj[i].id){
                        opt.selected = true;
                    }

                    selectEmployee.appendChild(opt);
                }
    
                // Оставляем здесь, ибо если вынести из then - сработает слишком рано
                $('.selectpicker').selectpicker('refresh');
                $('.selectpicker').selectpicker('render');
            })
        })          
    }
    else {
        divSelectEmployee.style.display = 'none';
        $('.selectpicker').selectpicker('refresh');
        $('.selectpicker').selectpicker('render');
    }
}

