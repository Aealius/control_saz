let allSelected = false; //флаг, указывающий выбрано ли всем
let executorSelect = document.getElementById('executor'); //множественный select дял выбора исполнителя
let selectedExecutorsDiv = document.getElementById('selected-executors'); //контейнер для полосочек с выбранными исполнителями
let addTaskForm = document.getElementById('addTaskForm'); //форма добавления задачи
let бессрочноCheckbox = document.getElementById('is_бессрочно');
let dateCreatedInput = document.getElementById('date_created');
let deadlineInput = document.getElementById('deadline'); 

document.addEventListener('DOMContentLoaded', () => {
    toggleDeadline();
    updateSelectedExecutors();
});

document.getElementById('is_бессрочно').addEventListener('change', toggleDeadline);

addTaskForm.addEventListener('submit', (event) => {
    
    if (!validate()){
        event.preventDefault();
    }

    let pInput = document.getElementById("p");
    let snInput = document.getElementById("sn");

    pInput.value = sessionStorage.getItem('p');
    snInput.value = sessionStorage.getItem('sn');
});

function checkDateCreatedValidity(){
    let dateCreatedParts = dateCreatedInput.value.split("-");
    let dateCreatedYear  = parseInt(dateCreatedParts[0]);

    if (dateCreatedYear > 2050 || dateCreatedYear < 2024){
        console.log('invalid date_created')
        return {valid: false, target: dateCreatedInput, error: "Некорректная дата создания"};
    }

    return {valid: true, target: dateCreatedInput};
}

function checkDeadlineDateValidity(){    

    let deadlineParts = deadlineInput.value.split("-");
    let deadlineYear = parseInt(deadlineParts[0]);

    if (deadlineInput.disabled === false) {
        if (deadlineYear > 2050 || deadlineYear < 2024) {
            console.log('invalid deadline');
            return { valid: false, target: deadlineInput, error: "Некорректная дата окончания срока" };
        }
    
    
        if (dateCreatedInput.value > deadlineInput.value) {
            console.log('invalid deadline');
            return { valid: false, target: deadlineInput, error: "Некорректная дата окончания срока" };
        } 
    }

    return {valid: true, target: deadlineInput};
}

function createErrorView(text, target){
    let errorMessageDiv = document.createElement('div');
    errorMessageDiv.className = 'invalid'; //"опознавательный" класс для элементов ошибочной валидации (чтобы было с помощью чего их удалить)
    errorMessageDiv.style.color = 'red';
    errorMessageDiv.innerHTML = text;

    if (target == addTaskForm.querySelector('.dropdown-menu')){ //здесь проверяем, является ли target-ом тот злополучный селект
        addTaskForm.querySelector('.dropdown.bootstrap-select.show-tick.form-control').classList.add('is-invalid'); //и для него класс is-invalid ставим для родителя, потому что почему-то оно так работает
    }

    target.classList.add('is-invalid');

    target.after(errorMessageDiv);
}

function validate(){

    let validationResultArray = [checkDeadlineDateValidity(), checkDateCreatedValidity(), checkSelectValidity()];

    validationResultArray.forEach(element => {
        if (!element.valid) {
            if(element.target == addTaskForm.querySelector('.dropdown-menu')){
                addTaskForm.querySelector('.dropdown.bootstrap-select.show-tick.form-control').classList.remove('is-invalid');
            }
            element.target.classList.remove('is-invalid');
            if (element.target.nextElementSibling){
                element.target.nextElementSibling.remove();
            }
            createErrorView(element.error, element.target);
        }
        else { 
            if(element.target == addTaskForm.querySelector('.dropdown-menu')){
                addTaskForm.querySelector('.dropdown.bootstrap-select.show-tick.form-control').classList.remove('is-invalid');
            }
            element.target.classList.remove('is-invalid');
            if (element.target.nextElementSibling){
                element.target.nextElementSibling.remove();
            }
        }
    });

    return validationResultArray.every(v => v.valid === true);
}


function checkSelectValidity(){
    text_target = addTaskForm.querySelector('.dropdown-menu'); //здесб передаем как target спрятанные значения дропдауна, потому как с этим селектом дефолтный синтаксис не робит

    if (executorSelect.selectedOptions.length == 0)
        return {valid: false, target: text_target, error: "Не выбрано ни одного исполнителя"};

    return {valid: true, target: text_target};
}


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

function toggleDeadline() {
    var deadlineField = document.getElementById('deadline-field');
    var deadlineInput = document.getElementById('deadline');

    if (бессрочноCheckbox.checked) {
        deadlineField.style.display = 'none';
        deadlineInput.required = false;  // Снять требование при бессрочной задаче
        deadlineInput.value = ''; // Очистить значение поля срока
        deadlineInput.disabled = true;
    }
    else {
        deadlineField.style.display = 'block';
        deadlineInput.required = true;   // Вернуть требование
        deadlineInput.disabled  = false;
    }
}


