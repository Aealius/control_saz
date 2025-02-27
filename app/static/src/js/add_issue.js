const techSupportForm = document.getElementById("techSupportForm");
const descriptionTextArea = document.getElementById('description');
const docNumberinput = document.getElementById('compNumber');
const commonIssuesSelect =document.getElementById('common-issues-select')

techSupportForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const base_url = window.location.origin;
    formData = new FormData(event.target);

    let validationResultArray = [checkDescriptionValidity(descriptionTextArea), checkCompNumberValidity(docNumberinput)];

    if (validate(validationResultArray, techSupportForm)) {

        await fetch(base_url + '/tech/add_issue', {
            method: 'POST',
            body: formData,
        }).then((response) => {
            console.log(response);
            window.location.replace(document.referrer);
        });  
    }
});



descriptionTextArea.addEventListener('input', (event) => {
    let validationResultArray = [checkDescriptionValidity(event.target)];

    if (!validate(validationResultArray, techSupportForm)) {
        event.preventDefault();
    }
});


descriptionTextArea.addEventListener('change', (event) => {
    let validationResultArray = [checkDescriptionValidity(event.target)];

    if (!validate(validationResultArray, techSupportForm)) {
        event.preventDefault();
    }
});


docNumberinput.addEventListener('input', (event) => {
    let validationResultArray = [checkCompNumberValidity(event.target)];

    
    if (!validate(validationResultArray, techSupportForm)) {
        event.preventDefault();
    }
});

docNumberinput.addEventListener('change', (event) => {
    let validationResultArray = [checkCompNumberValidity(event.target)];

    
    if (!validate(validationResultArray, techSupportForm)) {
        event.preventDefault();
    }
});

// Начальная инициализация
//descriptionTextArea.defaultValue = commonIssuesSelect.value;

document.addEventListener('DOMContentLoaded', () => {
    handleConferenceSelect(commonIssuesSelect); 
});

commonIssuesSelect.addEventListener('change', (event) => {
    handleConferenceSelect(event.target);
});

function createWarningDiv(){
    let descriptionDiv = document.createElement('div');
    descriptionDiv.classList.add(...['warning']);
    descriptionDiv.style.color = '#E29C45';
    descriptionDiv.style.fontWeight = '600';
    descriptionDiv.innerText = 'В описании проблемы обязательно укажите ссылку на видео-конференцию или контакты лица, ответственного за конференцию';
    return descriptionDiv;
}

function createWarningBorder(targetElement){
    if (targetElement instanceof Element){
        targetElement.style.border ='1px solid #E29C45';
    }
}

function handleConferenceSelect(target) {
    let descriptionWrapper = document.getElementById('description-wrapper');

    if (target.value == "Видео-конференц-связь"){
        descriptionWrapper.insertAdjacentElement('beforeend', createWarningDiv());
        createWarningBorder(descriptionWrapper.childNodes[3]);
        descriptionTextArea.value = '';
    }
    else {

        let warningDiv = document.querySelector('.warning');

        if (warningDiv){
            warningDiv.remove();
            descriptionTextArea.style.border = '1px solid #ced4da';
        }
        else{
            descriptionTextArea.style.border = '1px solid #ced4da';
        }

        if (target.value != "Другое")
            descriptionTextArea.value = target.value;
        else{
            descriptionTextArea.value = '';
        }
    }
}


