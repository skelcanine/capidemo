// Interactive Client-Side Drag & Drop, Slot Selection (A, B, C), and Image Removal Logic

const fingerSlotState = {};
const FINGERS = ['L2', 'L3', 'L4', 'L5', 'R2', 'R3', 'R4', 'R5'];

FINGERS.forEach(f => {
    fingerSlotState[f] = { A: null, B: null, C: null };
});

function clickSlot(finger, slot) {
    const inputId = `input_${finger}_${slot}`;
    const input = document.getElementById(inputId);
    if (input) {
        input.click();
    }
}

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

    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
        addFilesToFinger(finger, files, false);
    }
}

function handleSlotFileSelect(input, finger, slot) {
    if (input.files && input.files[0]) {
        const file = input.files[0];
        fingerSlotState[finger][slot] = { file: file, isPlus: false };
        renderFingerState(finger);
    }
}

function handlePlusFileSelect(input, finger) {
    if (input.files && input.files.length > 0) {
        addFilesToFinger(finger, input.files, true);
    }
}

function addFilesToFinger(finger, files, isPlus) {
    const slots = ['A', 'B', 'C'];
    let fileIdx = 0;

    for (let i = 0; i < slots.length && fileIdx < files.length; i++) {
        const slot = slots[i];
        if (!fingerSlotState[finger][slot]) {
            fingerSlotState[finger][slot] = { file: files[fileIdx], isPlus: isPlus };
            fileIdx++;
        }
    }
    renderFingerState(finger);
}

function removeSlotImage(finger, slot, event) {
    if (event) event.stopPropagation();

    fingerSlotState[finger][slot] = null;

    const inputSlot = document.getElementById(`input_${finger}_${slot}`);
    if (inputSlot) inputSlot.value = '';

    renderFingerState(finger);
}

function renderFingerState(finger) {
    const container = document.getElementById(`thumbs_${finger}`);
    const textElem = document.getElementById(`text_${finger}`);
    if (!container) return;

    container.innerHTML = '';
    const slots = ['A', 'B', 'C'];
    let loadedCount = 0;

    slots.forEach(slot => {
        const badge = document.getElementById(`slot_${finger}_${slot}`);
        const slotData = fingerSlotState[finger][slot];

        if (slotData) {
            loadedCount++;
            if (badge) {
                badge.className = 'slot-badge active';
                badge.title = `Slot ${slot}: ${slotData.file.name}`;
            }

            const thumbWrap = document.createElement('div');
            thumbWrap.className = 'thumb-wrapper';

            const img = document.createElement('img');
            img.className = 'thumb-preview';
            img.title = `Slot ${slot} (${slotData.isPlus ? 'Uploaded via +' : 'Specific Slot'}) - ${slotData.file.name}`;

            const reader = new FileReader();
            reader.onload = function(e) {
                img.src = e.target.result;
            };
            reader.readAsDataURL(slotData.file);

            const slotTag = document.createElement('span');
            slotTag.className = 'thumb-slot-tag';
            slotTag.innerText = slot;

            const removeBtn = document.createElement('button');
            removeBtn.type = 'button';
            removeBtn.className = 'thumb-remove-btn';
            removeBtn.innerHTML = '&times;';
            removeBtn.title = `Remove image from slot ${slot}`;
            removeBtn.onclick = function(e) {
                removeSlotImage(finger, slot, e);
            };

            thumbWrap.appendChild(img);
            thumbWrap.appendChild(slotTag);
            thumbWrap.appendChild(removeBtn);
            container.appendChild(thumbWrap);
        } else {
            if (badge) {
                badge.className = 'slot-badge empty';
                badge.title = `Click to add image for Slot ${slot}`;
            }
        }
    });

    if (textElem) {
        textElem.style.display = loadedCount > 0 ? 'none' : 'block';
    }

    syncFormInputs(finger);
}

function syncFormInputs(finger) {
    const slots = ['A', 'B', 'C'];
    slots.forEach(slot => {
        const slotData = fingerSlotState[finger][slot];
        const input = document.getElementById(`input_${finger}_${slot}`);
        if (input && slotData) {
            const dt = new DataTransfer();
            dt.items.add(slotData.file);
            input.files = dt.files;
        } else if (input) {
            input.files = new DataTransfer().files;
        }
    });
}

function handleFolderUpload(files) {
    const fingers = ['L2', 'L3', 'L4', 'L5', 'R2', 'R3', 'R4', 'R5'];
    let totalMatched = 0;
    let totalRejected = 0;

    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const filename = file.name.toUpperCase();
        const path = file.webkitRelativePath ? file.webkitRelativePath.toUpperCase() : '';

        let matched = false;
        for (const f of fingers) {
            if (filename.includes(f) || path.includes(f)) {
                const slots = ['A', 'B', 'C'];
                for (const s of slots) {
                    if (!fingerSlotState[f][s]) {
                        fingerSlotState[f][s] = { file: file, isPlus: true };
                        totalMatched++;
                        matched = true;
                        break;
                    }
                }
                if (matched) break;
            }
        }
        if (!matched) totalRejected++;
    }

    fingers.forEach(f => renderFingerState(f));

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
