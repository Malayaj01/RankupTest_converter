const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const browseLink = document.querySelector('.browse-link'); // Changed from ID to class
const statusDiv = document.getElementById('status-message'); // Changed ID
const examNameInput = document.getElementById('exam-name');

// Drag and drop handlers
dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
    dropZone.style.borderColor = 'var(--primary)';
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('dragover');
    dropZone.style.borderColor = 'var(--border-color)';
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    dropZone.style.borderColor = 'var(--border-color)';
    const files = e.dataTransfer.files;
    if (files.length) handleFile(files[0]);
});

// Click handlers
browseLink.addEventListener('click', (e) => {
    e.stopPropagation();
    fileInput.click();
});

dropZone.addEventListener('click', () => {
    fileInput.click();
});

fileInput.addEventListener('change', () => {
    if (fileInput.files.length) handleFile(fileInput.files[0]);
});

async function handleFile(file) {
    // Validate File Type
    if (!file.name.endsWith('.xlsx')) {
        showStatus('Please upload an Excel file (.xlsx)', 'error');
        return;
    }

    // Validate Exam Name
    const examName = examNameInput.value.trim();
    if (!examName) {
        showStatus('Please enter an Exam Name first.', 'error');
        examNameInput.focus();
        return;
    }

    showStatus('Generating PDF... Please wait.', 'loading');

    const formData = new FormData();
    formData.append('file', file);
    formData.append('exam_name', examName);

    try {
        // Use relative path so it works on localhost AND ngrok
        const response = await fetch('/convert', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.error || 'Conversion failed');
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `RankUp_${examName.replace(/\s+/g, '_')}.pdf`;
        document.body.appendChild(a);
        a.click();
        
        // Use a timeout to give the browser time to initiate the download 
        // before we revoke the URL. Otherwise, it generates a 0-byte file!
        setTimeout(() => {
            window.URL.revokeObjectURL(url);
            a.remove();
        }, 1000);

        showStatus('Success! Download started.', 'success');

        // Reset after success
        fileInput.value = '';
        setTimeout(() => {
            statusDiv.style.display = 'none';
        }, 5000);

    } catch (error) {
        showStatus('Error: ' + error.message, 'error');
    }
}

function showStatus(msg, type) {
    statusDiv.textContent = msg;
    statusDiv.className = 'status ' + type; // success, error, or loading
    statusDiv.style.display = 'block';
}
