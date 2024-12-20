let createMemoForm = document.getElementById("createMemoForm");

createMemoForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const base_url_api = window.location.origin + '/api';
    formData = new FormData(event.target);

    fetch(base_url_api + '/users/current_user_with_head')
        .then(responseUser => responseUser.json())
        .then(async user => {
            if(user.full_department){
                formData.append("from", user.full_department);
            }
            else{
                formData.append("from", user.department);
            }
            
            formData.append("signerName",  user.headName[0] + '.' + user.headPatronymic[0] + '.' + user.headSurname);
            formData.append("signerPosition", user.headPosition);
            formData.append("filePathForSave",user.savePath);
            formData.append("signaturePath",user.headSignaturePath);
            
            let mainText = await getHtmlFromTextEditor();
            formData.append("mainText", mainText.join('')); //Поскольку получаем массив <p> тегов, нужен join

            let reportApiUrl = window.location.origin.replace(':5000', ':44364');

            fetch(reportApiUrl + '/MemoReport', {
                method: 'POST',
                body: formData,
            }).then((response) =>{
                console.log(response)
                return response.text();
            }).then((text) => {
                localStorage.setItem('filename', text);
                window.location.replace(document.referrer);
            });
        })
        .catch(console.error);

    
         

    // let validationResultArray = [checkExecutorSelectValidity(createMemoForm, executorSelect), checkDescriptionValidity(descriptionInput)];

    // if (validate(validationResultArray, createMemoForm)) {

        
    // }    
});