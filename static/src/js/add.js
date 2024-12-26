let allSelected = false; //флаг, указывающий выбрано ли всем
let executorSelect = document.getElementById('executor'); //множественный select дял выбора исполнителя
let selectedExecutorsDiv = document.getElementById('selected-executors');
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
const base_api_url = window.location.origin + '/api';

let files  = [];

document.addEventListener('DOMContentLoaded', async () => {
    toggleDeadline();
    updateSelectedExecutors(executorSelect, selectedExecutorsDiv);

    await fetch(base_api_url + '/nomenclature/counters')
            .then((response) => {
                console.log(response);
                return response.json();
            }).then((data) => localStorage.setItem('nm', JSON.stringify(data)))
            .then(() =>{
                if (document.getElementById('nm-select'))
                    changeValue(document.getElementById('nm-select').value);
            })

});


document.getElementById('nm-select') && document.getElementById('nm-select').addEventListener('change', (e) =>{
    changeValue(e.target.value);
});

function changeValue(el){
    if (el === "0"){
        document.getElementById("nm-number-div").style.display = 'none';
        document.getElementById('nm-number').disabled = true;
    }
    else{
        document.getElementById("nm-number-div").style.display = 'flex';
        document.getElementById('nm-number').disabled = false;
    }
    let nm_arr_str = localStorage.getItem('nm');
    let nm_arr = JSON.parse(nm_arr_str);
    let current_doc = nm_arr[el - 1];

    document.getElementById('nm-number').value = current_doc.counter + 1;
}

document.getElementById('is_бессрочно').addEventListener('change', toggleDeadline);
document.getElementById('executor').addEventListener('change', (event) => {

    updateSelectedExecutors(executorSelect, selectedExecutorsDiv);

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
addUploadEventListeners(fileInput, dropZone);

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



