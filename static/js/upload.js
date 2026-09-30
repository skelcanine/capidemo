// Client-Side Drag & Drop and Preview Logic for Capillaroscopy Uploads

function handleDragOver(e, finger) {
    e.preventDefault();
    e.stopPropagation();
    const card = document.getElementById(`card_${finger}`);
    if (card) card.classList.add('drag-over');
}

function handleDragLeave(finger) {
    const card = document.getElementById(`card_${finger}`);
    if (card) card.classList.remove('drag-over');
}

function handleDrop(e, finger) {
    e.preventDefault();
    e.stopPropagation();
    handleDragLeave(finger);

    const dt = e.dataTransfer;
    const files = dt.files;
    if (files && files.length > 0) {
        const fileInput = document.getElementById(`input_${finger}`);
        if (fileInput) {
            const dataTransfer = new DataTransfer();
            for (let i = 0; i < Math.min(files.length, 3); i++) {
                dataTransfer.items.add(files[i]);
            }
            fileInput.files = dataTransfer.files;
            updateThumbnails(finger, fileInput.files);
        }
    }
}

function handleFileSelect(input, finger) {
    if (input.files && input.files.length > 0) {
        updateThumbnails(finger, input.files);
    }
}

function updateThumbnails(finger, files) {
    const container = document.getElementById(`thumbs_${finger}`);
    const textElem = document.getElementById(`text_${finger}`);
    if (!container) return;

    container.innerHTML = '';
    const slots = ['A', 'B', 'C'];
    
    // Reset slot badges A, B, C
    slots.forEach(s => {
        const badge = document.getElementById(`slot_${finger}_${s}`);
        if (badge) badge.className = 'slot-badge empty';
    });

    const count = Math.min(files.length, 3); // Max 3 images per finger
    if (count > 0 && textElem) {
        textElem.style.display = 'none';
    } else if (textElem) {
        textElem.style.display = 'block';
    }

    for (let i = 0; i < count; i++) {
        const file = files[i];
        const slotLetter = slots[i];
        
        const badge = document.getElementById(`slot_${finger}_${slotLetter}`);
        if (badge) badge.className = 'slot-badge';

        const reader = new FileReader();
        reader.onload = function(e) {
            const img = document.createElement('img');
            img.src = e.target.result;
            img.className = 'thumb-preview';
            img.title = file.name;
            container.appendChild(img);
        };
        reader.readAsDataURL(file);
    }
}

// Whole Folder Upload Parser & Validator
function handleFolderUpload(files) {
    const fingers = ['L2', 'L3', 'L4', 'L5', 'R2', 'R3', 'R4', 'R5'];
    const fingerFilesMap = {};
    fingers.forEach(f => fingerFilesMap[f] = []);

    let totalMatched = 0;
    let totalRejected = 0;

    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const filename = file.name.toUpperCase();
        const path = file.webkitRelativePath ? file.webkitRelativePath.toUpperCase() : '';
        
        let matched = false;
        for (const f of fingers) {
            if (filename.includes(f) || path.includes(f)) {
                if (fingerFilesMap[f].length < 3) { // Max 3 images per finger
                    fingerFilesMap[f].push(file);
                    totalMatched++;
                    matched = true;
                    break;
                }
            }
        }
        if (!matched) {
            totalRejected++;
        }
    }

    const alertContainer = document.getElementById('folderAlertContainer');
    
    if (totalMatched === 0) {
        if (alertContainer) {
            alertContainer.innerHTML = `
                <div class="alert alert-danger" style="margin-bottom: 1.5rem;">
                    <div>
                        <strong>⚠️ Folder Upload Rejected:</strong> None of the ${files.length} files in the uploaded folder matched finger codes (L2, L3, L4, L5, R2, R3, R4, R5).
                        <br><span style="font-size: 0.85rem;">Please ensure filenames or subfolders include finger identifiers like <code>L2_01.jpg</code> or <code>R4_scan.png</code>.</span>
                    </div>
                    <button onclick="this.parentElement.remove()" style="background:none; border:none; cursor:pointer; font-weight:bold; font-size:1.1rem; color:inherit;">&times;</button>
                </div>
            `;
        }
        return;
    }

    fingers.forEach(f => {
        const fileInput = document.getElementById(`input_${f}`);
        if (fileInput) {
            const dt = new DataTransfer();
            fingerFilesMap[f].forEach(file => dt.items.add(file));
            fileInput.files = dt.files;
            updateThumbnails(f, dt.files);
        }
    });

    if (alertContainer) {
        alertContainer.innerHTML = `
            <div class="alert alert-success" style="margin-bottom: 1.5rem;">
                <div>
                    <strong>✅ Folder Upload Processed:</strong> Successfully mapped ${totalMatched} image(s) to finger dropzones.
                    ${totalRejected > 0 ? `<br><span style="font-size: 0.85rem; color: #92400E;">(${totalRejected} file(s) ignored because they lacked finger tags L2–L5 / R2–R5).</span>` : ''}
                </div>
                <button onclick="this.parentElement.remove()" style="background:none; border:none; cursor:pointer; font-weight:bold; font-size:1.1rem; color:inherit;">&times;</button>
            </div>
        `;
    }
}
