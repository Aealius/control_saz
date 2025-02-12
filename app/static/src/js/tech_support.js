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

        await fetch(base_url_api + '/tech_support', {
            method: 'POST',
            body: formData,
        }).then(() =>
            window.location.replace(document.referrer)
        );  
    }
});

descriptionTextArea.addEventListener('change', (event) => {
    let validationResultArray = [checkDescriptionValidity(event.target)];

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
descriptionTextArea.value = "Не печатает принтер";

commonIssuesSelect.addEventListener('change', (event) => {
    let descriptionWrapper = document.getElementById("description-wrapper");
    if (event.target.value == "Другое"){
        descriptionTextArea.value = "";
        descriptionWrapper.style.display = "block";
    }
    else{
        if (descriptionWrapper){
            descriptionWrapper.style.display = "none";
            descriptionTextArea.value = event.target.value;
        }
        else
            descriptionTextArea.value = event.target.value;
    }
});


