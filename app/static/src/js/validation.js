function validate(validationResultArray, form){
    validationResultArray.forEach(element => {
        if (!element.valid) {
            if(element.target == form.querySelector('.dropdown-menu')){
                form.querySelector('.dropdown.bootstrap-select.show-tick.form-control').classList.remove('is-invalid');
            }
            element.target.classList.remove('is-invalid');
            if (element.target.nextElementSibling){
                element.target.nextElementSibling.remove();
            } 
            // для поля с № перед началом самого поля, иначе сообщение об ошибке не уберется
            if (element.target.parentNode.classList.contains('input-group')) {
                if (element.target.parentNode.nextElementSibling) {
                    element.target.parentNode.nextElementSibling.remove();
                }
            }

            createErrorView(element.error, element.target, form);
        }
        else { 
            if(element.target == form.querySelector('.dropdown-menu')){
                form.querySelector('.dropdown.bootstrap-select.show-tick.form-control').classList.remove('is-invalid');
            }
            element.target.classList.remove('is-invalid');
            if (element.target.parentNode.classList.contains('input-group')) {
                if (element.target.parentNode.nextElementSibling) {
                    element.target.parentNode.nextElementSibling.remove();
                }
            }
            else{
                if (element.target.nextElementSibling) {
                    if (element.target.nextElementSibling.classList.contains('invalid'))
                        element.target.nextElementSibling.remove();
                }
            }
        }
    });

    return validationResultArray.every(v => v.valid === true);
}

function createErrorView(text, target, form){

    if (target == form.querySelector('.dropdown-menu')){ //здесь проверяем, является ли target-ом тот злополучный селект
        form.querySelector('.dropdown.bootstrap-select.show-tick.form-control').classList.add('is-invalid'); //и для него класс is-invalid ставим для родителя, потому что почему-то оно так работает
    }

    let errorMessageDiv = createDescriptionElement(text);

    target.classList.add('is-invalid');

    if (target.parentNode.classList.contains('input-group')){
        target.parentNode.after(errorMessageDiv);
    }
    else{
        target.after(errorMessageDiv);
    }
}

function createDescriptionElement(text){
    let errorMessageDiv = document.createElement('div');
    errorMessageDiv.className = 'invalid'; //"опознавательный" класс для элементов ошибочной валидации (чтобы было с помощью чего их удалить)
    errorMessageDiv.style.color = 'red';
    errorMessageDiv.innerHTML = text;

    return errorMessageDiv;
}

/////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Валидаторы для полей

// Исполнитель
function checkExecutorSelectValidity(form, select){ // HTMLElement | null
    text_target = form.querySelector('.dropdown-menu'); //здесь передаем как target спрятанные значения дропдауна, потому как с этим селектом дефолтный синтаксис не робит

    if (select.selectedOptions.length == 0)
        return {valid: false, target: text_target, error: "Не выбрано ни одного исполнителя"};

    return {valid: true, target: text_target};
}

// Дата создания
function checkDateCreatedValidity(dateCreatedInput){
    let dateCreatedParts = dateCreatedInput.value.split("-");
    let dateCreatedYear  = parseInt(dateCreatedParts[0]);
    let currentYear = new Date().getFullYear();
    
    if (!dateCreatedInput.value || (dateCreatedYear > currentYear + 1 || dateCreatedYear < currentYear)){
        console.log('invalid date_created')
        return {valid: false, target: dateCreatedInput, error: "Некорректная дата создания"};
    }

    return {valid: true, target: dateCreatedInput};
}

// Дата окончания срока
function checkDeadlineDateValidity(deadlineInput, dateCreatedInput){    

    let deadlineParts = deadlineInput.value.split("-");
    let deadlineYear = parseInt(deadlineParts[0]);
    let currentYear = new Date().getFullYear();

    if (deadlineInput.disabled === false) {
        if (!deadlineInput.value || (deadlineYear > currentYear + 1 || deadlineYear < currentYear) 
            || dateCreatedInput.value > deadlineInput.value) {
            console.log('invalid deadline');
            return { valid: false, target: deadlineInput, error: "Некорректная дата окончания срока" };
        }
    }

    return {valid: true, target: deadlineInput};
}

// Описание
function checkDescriptionValidity(descriptionInput){    
    if (!descriptionInput.value) {
        console.log('invalid description');
        return { valid: false, target: descriptionInput, error: "Необходимо добавить описание" };
    }
    return {valid: true, target: descriptionInput};
}

// Функция валидации для простого селекта в форме редактирования
function checkSimpleExecutorSelect(executorSelect){
    if(!executorSelect.value || executorSelect.value == ""){
        return {valid: false, target: executorSelect, error: "Не выбран исполнитель"};
    }
    return {valid: true, target: executorSelect};
}
/////////////////////////////////////////////////////////////////////////////////////////



function checkReceiverValidity(receiverInput){    
    if (!receiverInput.value || receiverInput.value == '') {
        console.log('invalid receiver');
        return { valid: false, target: receiverInput, error: "Необходимо ввести данные о получателе" };
    }
    return {valid: true, target: receiverInput};
}

function checkDocNumberValidity(numberInput){    
    if (!numberInput.value || numberInput.value == '') {
        console.log('invalid description');
        return { valid: false, target: numberInput, error: "Необходимо ввести номер документа по номенклатуре" };
    }
    return {valid: true, target: numberInput};
}

function checkThemeValidity(themeInput){    
    if (!themeInput.value || themeInput.value == '') {
        console.log('invalid description');
        return { valid: false, target: themeInput, error: "Необходимо ввести тему служебной записки" };
    }
    return {valid: true, target: themeInput};
}

function checkCompNumberValidity(numberInput){    
    if (!numberInput.value || numberInput.value == '') {
        console.log('invalid computer number');
        return { valid: false, target: numberInput, error: "Необходимо ввести номер компьютера" };
    }
    else if (isNaN(numberInput.value)){
        console.log('invalid computer number');
        return { valid: false, target: numberInput, error: "Инвентарный номер компьютера не может содержать буквы и символы" };
    }
    return {valid: true, target: numberInput};
}