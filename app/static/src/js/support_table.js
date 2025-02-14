const base_url = window.location.origin;

async function setStatusInWork(issue_id){
    await fetch(base_url + '/tech/issue_in_work/' + issue_id)
        .then(response => console.log(response))

}

async function setStatusCompleted(issue_id){
    await fetch(base_url + '/tech/issue_completed/' + issue_id)
        .then(response => console.log(response))

}