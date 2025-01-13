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


if (document.getElementById('create_memo') != null) {
    document.getElementById("create_memo").addEventListener('click', () => {
        let referrerQueryString = document.referrer.slice(document.referrer.indexOf("?"));
        localStorage.setItem('refqstr', referrerQueryString);
    });
}

document.addEventListener('DOMContentLoaded', async () => {
    let reportApiUrl = window.location.origin.replace(':5000', ':44364');

    if(localStorage.getItem('filename') != null) {
        await fetch(reportApiUrl + `/MemoReport?filename=${localStorage.getItem('filename')}`, 
        {
            method: 'GET',
        }).then((response) =>{
            return response.blob();
        }).then(blob => {
            let files =  [new File([blob], localStorage.getItem('filename').split('\\')[1], {type:"application/pdf", lastModified:new Date().getTime()}),];
            addFiles(files);
            localStorage.removeItem('filename');
        });
    }
    updateSelectedExecutors(executorSelect, selectedExecutorsDiv);
});

document.getElementById('executor').addEventListener('change', (event) => {

    updateSelectedExecutors(executorSelect, selectedExecutorsDiv);

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
            window.location.replace(window.location.origin + (localStorage.getItem('refqstr') ?? '/?sn=in&p=1'))   
        );  
    }    
});
