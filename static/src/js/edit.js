
const deadlineInput = document.getElementById('deadline'); 
const descriptionInput = document.getElementById('description');
const selectedExecutorsDiv = document.getElementById('selected-executors');
const extendDeadlineCheckbox = document.getElementById('extend_deadline');
const extendedDeadlineField = document.getElementById('extended_deadline_field');
const fileUploadInput = document.getElementById('file')
const editTaskForm = document.getElementById('editTaskForm')


document.getElementById('executor').addEventListener('change', (event) => {
    let validationResultArray = [checkExecutorSelectValidity(addTaskForm, executorSelect)];

    if (!validate(validationResultArray, editTaskForm)){
        event.preventDefault();
    }
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

    let validationResultArray = [checkDeadlineDateValidity(deadlineInput),  checkDescriptionValidity(descriptionInput), checkExecutorSelectValidity(editTaskForm, executorSelect)];

    if (validate(validationResultArray, event.target)) {
        let formData = new FormData(event.target);

        files.forEach(file => {
            formData.append('files', file);
        });

        let pInput = document.getElementById("p");
        let snInput = document.getElementById("sn");

        pInput.value = sessionStorage.getItem('p');
        snInput.value = sessionStorage.getItem('sn');

        // сюда фетч и редирект потом
    }
});

function toggleDeadline() {
    let deadlineField = document.getElementById('deadlineField');
    let deadlineInput = document.getElementById('deadline');
    let бессрочноCheckbox = document.getElementById('is_бессрочно');

    if (бессрочноCheckbox.checked) {
        deadlineField.style.display = 'none';
        deadlineInput.value = ''; // Очистить значение поля срока
        extendDeadlineCheckbox.disabled = true;
        extendDeadlineCheckbox.checked = false;
        extendedDeadlineField.style.display = 'none';
    }
    else {
        deadlineField.style.display = 'block';
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


