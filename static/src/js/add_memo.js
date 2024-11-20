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

document.addEventListener('DOMContentLoaded', () => {
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

        let pInput = document.getElementById("p");
        let snInput = document.getElementById("sn");

        pInput.value = sessionStorage.getItem('p');
        snInput.value = sessionStorage.getItem('sn');

        await fetch(base_url + '/add_memo', {
            method: 'POST',
            body: formData,
        });

        window.location.replace(document.referrer);
    }    
});

function updateSelectedExecutors() {
    let executorSelectedOptions = executorSelect.selectedOptions;
    let selectedValuesArray = [];
    let selectedTextArray = [];

    for (let i = 0; i < executorSelectedOptions.length; i++) {
        selectedValuesArray.push(executorSelectedOptions[i].value);
        selectedTextArray.push(executorSelectedOptions[i].innerHTML);
    }

    addExecutorToSelected(selectedValuesArray, selectedTextArray);
}

function addExecutorToSelected(value, text) {
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
                let selectedText = document.querySelector(".filter-option-inner-inner");

                for (let i = 0; i < elements.length; i++) {
                    if ((elements[i].value) == currentValue) {
                        let removeText = elements[i].innerHTML;
                        elements[i].selected = false;
                        if (i == selectedExecutorsDiv.childElementCount) {
                            if (elements.length == 0) { //когда никого не остается в выбранных
                                $('.selectpicker').selectpicker('deselectAll'); //убираем всех отовсюду, чтобы показало дефолтное состояние дропдауна 
                            }
                            else {
                                selectedText.innerHTML = (selectedText.innerHTML.replace(', ' + removeText, ''));
                            }
                        }
                        else {
                            selectedText.innerHTML = (selectedText.innerHTML.replace(removeText + ', ', ''));
                        }
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
