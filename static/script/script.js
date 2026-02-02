// Toggle Step Accordion
function toggleStep(stepId) {
    const content = document.getElementById(stepId);
    content.classList.toggle('open');
}

// Start VM (Load Guacamole Iframe)
// Start VM (Load Guacamole Iframe)
// Start VM (Load Guacamole Iframe)
function startVM(containerId, url, labName, vmType = 'target') {
    const container = document.getElementById(containerId);
    if (!container) return;

    // Tampilkan Loading
    container.innerHTML = `
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; color: #64748b;">
            <span class="spinner" style="border-color: #64748b; border-top-color: transparent; width: 2em; height: 2em; border-width: 3px; margin-bottom: 10px;"></span>
            <p>Menyiapkan Virtual Machine...</p>
        </div>
    `;

    // Jika labName diberikan, coba nyalakan VM dulu via API
    if (labName) {
        fetch(`/lab/${labName}/start`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ vm_type: vmType })
        })
            .then(response => response.json())
            .then(data => {
                console.log("Start VM Status:", data);
                // Lanjut load iframe apapun hasilnya (karena mungkin user hanya perlu refresh koneksi)
                loadGuacamoleIframe(container, containerId, url);
            })
            .catch(error => {
                console.error('Error starting VM:', error);
                // Tetap coba load iframe
                loadGuacamoleIframe(container, containerId, url);
            });
    } else {
        // Fallback backward compatibility
        loadGuacamoleIframe(container, containerId, url);
    }
}

function loadGuacamoleIframe(container, containerId, url) {
    // Create iframe with permissions
    const iframeId = containerId + '-iframe';
    container.innerHTML = `
        <iframe 
            id="${iframeId}"
            src="${url}" 
            width="100%" 
            height="100%" 
            frameborder="0" 
            style="border:none;"
            allow="clipboard-read; clipboard-write; autoplay; camera; microphone; display-capture"
        ></iframe>
    `;

    // Focus iframe after load
    const iframe = document.getElementById(iframeId);
    iframe.onload = function () {
        iframe.contentWindow.focus();
    };

    // Additional focus attempt
    setTimeout(() => {
        if (iframe.contentWindow) iframe.contentWindow.focus();
    }, 1000);
}

// Reset VM to Snapshot
function resetVM(labName) {
    if (!confirm("Apakah Anda yakin ingin melakukan reset pada VM Target? Semua perubahan akan hilang.")) {
        return;
    }

    // Show Loading
    const btn = event.currentTarget;
    const originalText = btn.innerHTML;
    btn.innerHTML = `<span class="spinner"></span> Resetting...`;
    btn.disabled = true;

    fetch(`/lab/${labName}/reset`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert("Berhasil: " + data.message);
                // Reload halaman untuk refresh koneksi Guacamole jika diperlukan
                location.reload();
            } else {
                alert("Gagal: " + data.message);
                btn.innerHTML = originalText;
                btn.disabled = false;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert("Terjadi kesalahan sistem saat reset VM.");
            btn.innerHTML = originalText;
            btn.disabled = false;
        });
}
