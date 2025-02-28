const techSupportForm = document.getElementById("techSupportForm");
const descriptionTextArea = document.getElementById('description');
const docNumberinput = document.getElementById('compNumber');
const commonIssuesSelect =document.getElementById('common-issues-select')

techSupportForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const base_url_api = window.location.origin;
    formData = new FormData(event.target);

    let validationResultArray = [checkDescriptionValidity(descriptionTextArea), checkCompNumberValidity(docNumberinput)];

    if (validate(validationResultArray, techSupportForm)) {

        commonIssuesSelect.disabled = true;

        await fetch(base_url_api + '/tech/add_issue', {
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

docNumberinput.addEventListener('input', (event) => {
    let validationResultArray = [checkCompNumberValidity(event.target)];

    if (!validate(validationResultArray, techSupportForm)) {
        event.preventDefault();
    }
});




// Начальная инициализация
//descriptionTextArea.value = commonIssuesSelect.value;

commonIssuesSelect.addEventListener('change', (event) => {
    let descriptionWrapper = document.getElementById("description-wrapper");
    if (event.target.value == "Видео-конференц-связь") {
        descriptionWrapper.childNodes[1].append(createWarningDiv());
    }
    else{
        let warningDiv = document.querySelector('.warning');
        if (warningDiv){
            warningDiv.remove();
        }
    }
});

function createWarningDiv(){
    let warningDiv = document.createElement('div');
    warningDiv.classList.add(...['warning', 'mt-2']);
    warningDiv.innerText ='В описании проблемы обязательно укажите ссылку на конференцию или контакты лица, ответственного за конференцию';
    return warningDiv;
}


