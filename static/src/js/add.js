let allSelected = false; //флаг, указывающий выбрано ли всем
let executorSelect = document.getElementById('executor'); //множественный select дял выбора исполнителя
let addTaskForm = document.getElementById('addTaskForm'); //форма добавления задачи
let бессрочноCheckbox = document.getElementById('is_бессрочно');
let dateCreatedInput = document.getElementById('date_created');
let deadlineInput = document.getElementById('deadline'); 
let descriptionInput = document.getElementById('description');
let submitButton = document.getElementById('submit');
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const fileList = document.getElementById('fileList');
const base_url = window.location.origin;

let files  = [];

document.addEventListener('DOMContentLoaded', () => {
    toggleDeadline();
    updateSelectedExecutors();
});

document.getElementById('is_бессрочно').addEventListener('change', toggleDeadline);
document.getElementById('executor').addEventListener('change', (event) => {
    let validationResultArray = [checkExecutorSelectValidity(addTaskForm, executorSelect)];

    if (!validate(validationResultArray, addTaskForm)){
        event.preventDefault();
    }
});

document.getElementById('date_created').addEventListener('change', (event) => {
    let validationResultArray = [checkDateCreatedValidity(dateCreatedInput)];

    if (!deadlineInput.disabled && deadlineInput.value){
        validationResultArray = [checkDateCreatedValidity(dateCreatedInput),checkDeadlineDateValidity(deadlineInput, dateCreatedInput)];
    }
    if (!validate(validationResultArray, addTaskForm)){
        event.preventDefault();
    }
});

document.getElementById('deadline').addEventListener('change', (event) => {
    let validationResultArray = [checkDeadlineDateValidity(deadlineInput, dateCreatedInput)];

    if (!validate(validationResultArray, addTaskForm)){
        event.preventDefault();
    }
});

document.getElementById('description').addEventListener('change', (event) => {
    let validationResultArray = [checkDescriptionValidity(descriptionInput)];

    if (!validate(validationResultArray, addTaskForm)){
        event.preventDefault();
    }
});

// Функция из файла fileUpload.js для добавления addEventListener к инпуту
addUploadEventListeners(fileInput, dropZone)

addTaskForm.addEventListener('submit', async (event) => {
    event.preventDefault();

    let validationResultArray = [checkDeadlineDateValidity(deadlineInput, dateCreatedInput), checkDateCreatedValidity(dateCreatedInput), checkDescriptionValidity(descriptionInput), checkExecutorSelectValidity(addTaskForm, executorSelect)];

    if (validate(validationResultArray, addTaskForm)) {
        formData = new FormData(event.target);

        files.forEach(file => {
            formData.append('files', file);
        });

        await fetch(base_url + '/add', {
            method: 'POST',
            body: formData,
        }).then( () => window.location.replace(document.referrer));
    }
});

function updateSelectedExecutors() {
    let executorSelectedOptions = executorSelect.selectedOptions;
    let selectedValuesArray = [...executorSelectedOptions].map(o => o.value);
    let selectedTextArray = [...executorSelectedOptions].map(o => o.innerHTML);

    addExecutorToSelected(selectedValuesArray, selectedTextArray);

    let divSelectEmployee = document.getElementById('selectpicker2');
    let selectEmployee = document.getElementById('employee');

    // Пока что удаляем все значения и получаем их с бэка заново.
    // В дальнейшем подумать о том, как это улучшить,
    // тк слишком много запросов получится, особенно если будет много отделов
    $('#employee').find('[value!=\'\']').remove();

    // Для теста пока добавляем только глав буху, поэтому тут проверка на id бухгалтерии
    // В дальнейшем это можно/нужно улучшить
    if(selectedValuesArray.includes('27')){
        divSelectEmployee.style.display = 'block';
        selectEmployee.disabled = false;

        // Опять же пока заглушка чисто для бухгалтерии
        let employeeId = '27';
        $('#employeeLabel').text('Сотрудник (234 Бухгалтерия):');
    
        // Получение из бэка сотрудников отдела
        fetch(base_url + "/api/users/" + employeeId + "/employees", {
            method: "GET"
        }).then((response) => {
            return response.text();
        }).then((text) => {
            let obj = JSON.parse(text);

            for (let i = 0; i < obj.length; i++) {
                let opt = document.createElement('option');
                opt.value = obj[i].id;
                opt.innerHTML = obj[i].surname + " " + obj[i].name + " " + obj[i].patronymic;
                selectEmployee.appendChild(opt);
            }
            
            // Оставляем здесь, ибо если вынести из then - сработает слишком рано
            $('.selectpicker').selectpicker('refresh');
        })          
    }
    else {
        divSelectEmployee.style.display = 'none';
        selectEmployee.disabled = true;
        $('.selectpicker').selectpicker('refresh');
    }
} 

function addExecutorToSelected(value, text) {
    let selectedExecutorsDiv = document.getElementById('selected-executors'); //контейнер для полосочек с выбранными исполнителями
    selectedExecutorsDiv.innerHTML = "";

    let hiddenInput = document.createElement('input');
    hiddenInput.type = 'hidden';
    hiddenInput.name = 'executor[]';

    if (executorSelect.options.length == executorSelect.selectedOptions.length) {
        let allSpan = document.createElement('span');
        allSpan.classList.add('badge', 'badge-primary', 'mr-2', 'mb-2', 'executor-item');
        allSpan.textContent = 'Всем';
        allSpan.setAttribute('data-value', 'all');

        let closeButton = document.createElement('button');
        closeButton.type = 'button';
        closeButton.classList.add('close', 'small-close');
        closeButton.innerHTML = '×';
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
        for (let i = 0; i < value.length; i++) {

            let executorSpan = document.createElement('span');
            executorSpan.classList.add('badge', 'badge-primary', 'mr-2', 'mb-2', 'executor-item');
            executorSpan.textContent = text[i];
            executorSpan.setAttribute('data-value', value[i]);

            let closeButton = document.createElement('button');
            closeButton.type = 'button';
            closeButton.classList.add('close', 'small-close');
            closeButton.innerHTML = '×';
            closeButton.addEventListener('click', function () {
                let currentValue = this.parentNode.dataset.value;  // get the value
                if (currentValue == 'all') { // Удаление  allSelected  
                    allSelected = false // ставим false allSelected
                }
                this.parentNode.remove();

                let elements = executorSelect.selectedOptions;
                for (let i = 0; i < elements.length; i++) {
                    if ((elements[i].value) == currentValue) {
                        elements[i].selected = false;
                        $('.selectpicker').selectpicker('refresh');
                    }
                }
                updateSelectedExecutors();
            });
            executorSpan.appendChild(closeButton);
            selectedExecutorsDiv.appendChild(executorSpan);
            executorSpan.appendChild(hiddenInput);
        }
        hiddenInput.value = value;
    }
}

function toggleDeadline() {
    let deadlineField = document.getElementById('deadline-field');
    let deadlineInput = document.getElementById('deadline');

    if (бессрочноCheckbox.checked) {
        deadlineField.style.display = 'none';
        deadlineInput.value = ''; // Очистить значение поля срока
        deadlineInput.disabled = true;
    }
    else {
        deadlineField.style.display = 'block';
        deadlineInput.disabled  = false;
    }
}



