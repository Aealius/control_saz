const createMemoForm = document.getElementById("createMemoForm");
const reportApiUrl = window.location.origin.replace(':5000', ':44364');

const toTextArea = document.getElementById('to');
const docNumberinput = document.getElementById('docNumber');
const themeInput = document.getElementById('theme');


createMemoForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const base_url_api = window.location.origin + '/api';
    formData = new FormData(event.target);

    let validationResultArray = [checkReceiverValidity(toTextArea), checkDocNumberValidity(docNumberinput), checkThemeValidity(themeInput)];

    if (validate(validationResultArray, createMemoForm)) {

        fetch(base_url_api + '/users/current_user_with_head')
            .then((responseUser) => {
                if (responseUser.ok)
                    return responseUser.json();
                else
                    alert('Невозможно сформировать документ!');
                return 0;
            }).then(async user => {
                if (user.full_department) {
                    formData.append("from", user.full_department);
                }
                else {
                    formData.append("from", user.department);
                }
                formData.append("signerName", user.headName[0] + '.' + user.headPatronymic[0] + '.' + user.headSurname);
                formData.append("signerPosition", user.headPosition);
                formData.append("signaturePath", user.headSignaturePath);

                let mainText = await getHtmlFromTextEditor();
                formData.append("mainText", mainText.join('')); //Поскольку получаем массив <p> тегов, нужен join

                fetch(reportApiUrl + '/MemoReport', {
                    method: 'POST',
                    body: formData,
                }).then((response) => {
                    console.log(response)
                    return response.text();
                }).then((text) => {
                    localStorage.setItem('filename', text);
                    window.location.replace(window.location.origin + '/add_memo');
                }).catch(console.error);
            });
    }
});


    //получение примера документа по ссылке справа от формы
document.getElementById('exdocref').addEventListener('click', async (e) => {
    window.open(reportApiUrl + '\/MemoReport?filename=Reports\\Пример служебной записки.pdf', '_blank').focus();
});

toTextArea.addEventListener('change', (event) => {
    let validationResultArray = [checkReceiverValidity(event.target)];

    if (!validate(validationResultArray, createMemoForm)) {
        event.preventDefault();
    }
});

docNumberinput.addEventListener('change', (event) => {
    let validationResultArray = [checkDocNumberValidity(event.target)];

    if (!validate(validationResultArray, createMemoForm)) {
        event.preventDefault();
    }
});

themeInput.addEventListener('change', (event) => {
    let validationResultArray = [checkThemeValidity(event.target)];

    if (!validate(validationResultArray, createMemoForm)) {
        event.preventDefault();
    }
});
