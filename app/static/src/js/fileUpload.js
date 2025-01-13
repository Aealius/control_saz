function addUploadEventListeners(fileInput, dropZone) {
    fileInput.addEventListener('change', handleFileSelect);
    dropZone.addEventListener('click', () => fileInput.click());
    dropZone.addEventListener('dragover', (e) => e.preventDefault());
    dropZone.addEventListener('drop', handleDrop);
}

function handleDrop(e) {
    e.preventDefault();
    const droppedFiles = e.dataTransfer.files;
    addFiles(droppedFiles);
}

function handleFileSelect(e) {
    const selectedFiles = e.target.files;
    addFiles(selectedFiles);
}

function addFiles(newFiles) {
    files = [...files, ...Array.from(newFiles)];
    updateFileList();
}

function updateFileList() {
    fileList.innerHTML = '';
    files.forEach((file, index) => {
        const li = document.createElement('li');
        li.className = 'file-item mb-1';
        li.innerHTML = `
            <div class="card justify-content-between flex-row p-1" style="box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);"> 
                <div class="ml-3">
                    <a href="${URL.createObjectURL(file)}" target="_blank" class="file-name">${file.name}</a>
                    <span class="file-size ml-2">${formatFileSize(file.size)}</span>
                </div>
                <button class="delete-btn" data-index="${index}">&times</button>
            </div>  
        `;
        fileList.appendChild(li);
    });

    document.querySelectorAll('.delete-btn').forEach(btn => {
        btn.addEventListener('click', handleDelete);
    });
}

function handleDelete(e) {
    const index = parseInt(e.target.getAttribute('data-index'));
    files.splice(index, 1);
    updateFileList();
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 байт';
    const k = 1024;
    const sizes = ['байт', 'Кб', 'Мб', 'Гб'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}