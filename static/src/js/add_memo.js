let allSelected = false; //флаг, указывающий выбрано ли всем
let executorSelect = document.getElementById('executor');
let selectedExecutorsDiv = document.getElementById('selected-executors');
let descriptionInput = document.getElementById('description');
let addMemoForm = document.getElementById("addMemoForm");
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const fileList = document.getElementById('fileList');
let files = [];
const base_url = window.location.origin;

document.addEventListener('DOMContentLoaded', async () => {
    if(localStorage.getItem('filename') != null) {
        await fetch('https://localhost:44365' + `/Report?filename=${localStorage.getItem('filename')}`, 
        {
            method: 'GET',
        }).then((response) =>{
            return response.blob();
        }).then(blob => {
            let files =  [new File([blob], localStorage.getItem('filename').split('\\')[1], {type:"application/pdf", lastModified:new Date().getTime()}),];
            addFiles(files);
        });
    }
    updateSelectedExecutors();
});

document.getElementById('executor').addEventListener('change', (event) => {
    let validationResultArray = [checkExecutorSelectValidity(addMemoForm, executorSelect)];

    if (!validate(validationResultArray, addMemoForm)) {
        event.preventDefault();
    }
});

document.getElementById('description').addEventListener('change', (event) => {
    let validationResultArray = [checkDescriptionValidity(descriptionInput)];

    if (!validate(validationResultArray, addMemoForm)) {
        event.preventDefault();
    }
});

// Функция из файла fileUpload.js для добавления addEventListener к инпуту
addUploadEventListeners(fileInput, dropZone)

addMemoForm.addEventListener('submit', async (event) => {
    event.preventDefault();

    let validationResultArray = [checkExecutorSelectValidity(addMemoForm, executorSelect), checkDescriptionValidity(descriptionInput)];

    if (validate(validationResultArray, addMemoForm)) {

        formData = new FormData(event.target);

        files.forEach(file => {
            formData.append('files', file);
        });

        await fetch(base_url + '/add_memo', {
            method: 'POST',
            body: formData,
        }).then(() =>
            window.location.replace(document.referrer)
        );  
    }    
});

function updateSelectedExecutors() {
    let executorSelectedOptions = executorSelect.selectedOptions;
    let selectedValuesArray = [...executorSelectedOptions].map(o => o.value);
    let selectedTextArray = [...executorSelectedOptions].map(o => o.innerHTML);

    addExecutorToSelected(selectedValuesArray, selectedTextArray);

    let divSelectEmployee = document.getElementById('selectpicker2');
    let selectEmployee = document.getElementById('employee');

    if (divSelectEmployee != null) {

        // Пока что удаляем все значения и получаем их с бэка заново.
        // В дальнейшем подумать о том, как это улучшить,
        // тк слишком много запросов получится, особенно если будет много отделов
        $('#employee').find('[value!=\'\']').remove();

        // Для теста пока добавляем только глав буху, поэтому тут проверка на id бухгалтерии
        // В дальнейшем это можно/нужно улучшить
        if (selectedValuesArray.includes('27')) {
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
}

function addExecutorToSelected(value, text) {
    selectedExecutorsDiv.innerHTML = "";

    let hiddenInput = createHiddenInput();

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

                updateSelectedExecutors()

            });
            executorSpan.appendChild(closeButton);
            selectedExecutorsDiv.appendChild(executorSpan);
            executorSpan.appendChild(hiddenInput);
        }
        hiddenInput.value = value;
    }
}

function createHiddenInput(){
    let hiddenInput = document.createElement('input');
    hiddenInput.type = 'hidden';
    hiddenInput.name = 'executor[]';
    return hiddenInput;
}
