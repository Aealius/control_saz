let createMemoForm = document.getElementById("createMemoForm");

createMemoForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const base_url_api = window.location.origin + '/api';
    formData = new FormData(event.target);

    fetch(base_url_api + '/users/current_user_with_head')
        .then(responseUser => responseUser.json())
        .then(user => {
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

            fetch('https://localhost:44365' + '/Report/createMemoReport', {
                method: 'POST',
                body: formData,
            }).then((response) =>{
                console.log(response)
            }); 

            currentUserLogin = user.login;
        })
        .catch(console.error);

    
         

    // let validationResultArray = [checkExecutorSelectValidity(createMemoForm, executorSelect), checkDescriptionValidity(descriptionInput)];

    // if (validate(validationResultArray, createMemoForm)) {

        
    // }    
});