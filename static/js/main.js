/* ── Utilities ────────────────────────────────── */
function getCsrfToken() {
    return document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
}

/**
 * Show a premium toast notification
 * @param {string} message 
 * @param {'success'|'error'|'info'} type 
 */
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    const icons = {
        success: 'bi-check-circle-fill',
        error: 'bi-exclamation-triangle-fill',
        info: 'bi-info-circle-fill'
    };

    toast.innerHTML = `
        <i class="bi ${icons[type]}"></i>
        <span>${message}</span>
    `;

    container.appendChild(toast);

    // Auto remove after 4 seconds
    setTimeout(() => {
        toast.classList.add('hiding');
        toast.addEventListener('animationend', () => toast.remove());
    }, 4000);
}

/* ── Sidebar ──────────────────────────────────── */
function toggleCategory(btn) {
    btn.classList.toggle("open");
    const items = btn.nextElementSibling;
    items.classList.toggle("open");
}

function openSidebar() {
    document.getElementById("sidebar").classList.add("open");
    document.getElementById("overlay").classList.add("open");
}

function closeSidebar() {
    document.getElementById("sidebar").classList.remove("open");
    document.getElementById("overlay").classList.remove("open");
}

// Highlight active nav item & auto-open its category
document.addEventListener("DOMContentLoaded", () => {
    const path = window.location.pathname;
    document.querySelectorAll(".nav-item").forEach(a => {
        if (a.getAttribute("href") === path) {
            a.classList.add("active");
            const items = a.closest(".nav-items");
            if (items) {
                items.classList.add("open");
                const btn = items.previousElementSibling;
                if (btn) btn.classList.add("open");
            }
        }
    });

    initUploadZone();
    initToolForm();
    initDependentOptions();
    initGlobalSearch();
});

/* ── Command Palette ────────────────────────────── */
let allTools = [];

function initGlobalSearch() {
    // Kumpulkan semua alat dari sidebar untuk pencarian
    document.querySelectorAll('.nav-items .nav-item').forEach(el => {
        const iconEl = el.querySelector('i');
        const url = el.getAttribute('href');
        if (url && url !== '#' && !url.includes('/settings') && !url.includes('/history') && !url.includes('/support')) {
            allTools.push({
                name: el.textContent.trim(),
                url: url,
                icon: iconEl ? iconEl.className : 'bi bi-tools'
            });
        }
    });

    const overlay = document.getElementById('cmd-palette-overlay');
    const input = document.getElementById('cmd-input');
    const results = document.getElementById('cmd-results');
    const globalSearchInput = document.getElementById('global-search');
    
    if (!overlay || !input) return;

    if (globalSearchInput) {
        globalSearchInput.addEventListener('click', openCommandPalette);
    }

    // Buka dengan Ctrl+K
    document.addEventListener('keydown', e => {
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            openCommandPalette();
        }
        if (e.key === 'Escape' && overlay.classList.contains('open')) {
            closeCommandPalette();
        }
    });

    // Tutup jika klik di luar modal
    overlay.addEventListener('click', e => {
        if (e.target === overlay) closeCommandPalette();
    });

    input.addEventListener('input', e => {
        const q = e.target.value.toLowerCase();
        results.innerHTML = '';
        
        // Smart Sorting based on usage
        const usage = JSON.parse(localStorage.getItem('tool_usage') || '{}');

        let filtered = allTools;
        if (q) {
            filtered = allTools.filter(t => t.name.toLowerCase().includes(q));
        } else {
            // If empty search, show most used tools
            filtered = [...allTools]
                .sort((a, b) => (usage[b.url] || 0) - (usage[a.url] || 0))
                .slice(0, 8);
        }
        if (filtered.length === 0) {
            results.innerHTML = `<div class="cmd-empty">${window.SERBABISA_TRANS?.cmd_empty || 'No matching tools found.'}</div>`;
            return;
        }

        filtered.forEach(t => {
            const item = document.createElement('a');
            item.className = 'cmd-item';
            item.href = t.url;
            item.innerHTML = `
                <div class="cmd-item-icon"><i class="${t.icon}"></i></div>
                <div class="cmd-item-info">
                    <div class="cmd-item-title">${t.name}</div>
                    <div class="cmd-item-desc">${t.url}</div>
                </div>
            `;
            item.addEventListener('click', () => {
                // Record usage
                const usage = JSON.parse(localStorage.getItem('tool_usage') || '{}');
                usage[t.url] = (usage[t.url] || 0) + 1;
                localStorage.setItem('tool_usage', JSON.stringify(usage));
            });
            results.appendChild(item);
        });
    });

    // Hubungkan search bar global di header untuk membuka command palette
    const headerSearch = document.getElementById('global-search');
    if (headerSearch) {
        headerSearch.addEventListener('click', e => {
            e.preventDefault();
            headerSearch.blur();
            openCommandPalette();
        });
    }

    function openCommandPalette() {
        overlay.classList.add('open');
        input.value = '';
        setTimeout(() => input.focus(), 50);
        // Trigger input event to show suggestions/usage
        input.dispatchEvent(new Event('input'));
    }

    function closeCommandPalette() {
        overlay.classList.remove('open');
        input.blur();
    }
}


/* ── Upload Zone ──────────────────────────────── */
let selectedFiles = [];

function initUploadZone() {
    const zone = document.getElementById("upload-zone");
    const input = document.getElementById("file-input");
    if (!zone || !input) return;

    zone.addEventListener("dragover", e => { e.preventDefault(); zone.classList.add("dragover"); });
    zone.addEventListener("dragleave", () => zone.classList.remove("dragover"));
    zone.addEventListener("drop", e => {
        e.preventDefault();
        zone.classList.remove("dragover");
        addFiles(e.dataTransfer.files);
    });

    input.addEventListener("change", () => {
        addFiles(input.files);
        input.value = "";
    });
}

function addFiles(fileList) {
    const input = document.getElementById("file-input");
    const isMultiple = input && input.hasAttribute("multiple");

    if (isMultiple) {
        selectedFiles.push(...Array.from(fileList));
    } else {
        selectedFiles = [fileList[0]];
    }
    renderFileList();
}

function removeFile(idx) {
    selectedFiles.splice(idx, 1);
    renderFileList();
}

function renderFileList() {
    const list = document.getElementById("file-list");
    const prompt = document.getElementById("upload-prompt");
    if (!list) return;

    if (selectedFiles.length === 0) {
        list.innerHTML = "";
        if (prompt) prompt.style.display = "";
        return;
    }
    if (prompt) prompt.style.display = "none";

    list.innerHTML = selectedFiles.map((f, i) => `
        <div class="file-item">
            <span><i class="bi bi-file-earmark"></i> ${f.name}
            <small>(${formatSize(f.size)})</small></span>
            <button type="button" class="remove-file" onclick="removeFile(${i})">&times;</button>
        </div>
    `).join("");
}

function formatSize(bytes) {
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1048576) return (bytes / 1024).toFixed(1) + " KB";
    return (bytes / 1048576).toFixed(1) + " MB";
}


/* ── Form Submission ──────────────────────────── */
function initToolForm() {
    const form = document.getElementById("tool-form");
    if (!form) return;

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const endpoint = form.dataset.endpoint;
        if (!endpoint) return;

        const btnText = document.querySelector(".btn-text");
        const btnLoad = document.querySelector(".btn-loading");
        const submitBtn = document.getElementById("submit-btn");
        const resultArea = document.getElementById("result-area");

        // Validate: either files or text input required
        const textInput = form.querySelector("textarea[name='text']");
        if (!textInput && selectedFiles.length === 0) {
            showError("Please select a file first.");
            return;
        }
        if (textInput && !textInput.value.trim()) {
            showError("Please enter some text.");
            return;
        }

        // Show loading and progress bar
        submitBtn.style.display = "none"; // Hide button
        const progContainer = document.getElementById("progress-container");
        const progFill = document.getElementById("progress-fill");
        const progText = document.getElementById("progress-text");
        const progPct = document.getElementById("progress-pct");
        
        if (progContainer) {
            progContainer.style.display = "block";
            progFill.style.width = "0%";
            progPct.textContent = "0%";
            progText.textContent = window.SERBABISA_TRANS?.uploading || "Uploading...";
            
            let p = 0;
            const interval = setInterval(() => {
                if (p < 85) {
                    p += Math.random() * 5 + 2;
                    if (p > 85) p = 85;
                    progFill.style.width = p + "%";
                    progPct.textContent = Math.round(p) + "%";
                    if (p > 30) progText.textContent = window.SERBABISA_TRANS?.processing_wait || "Processing...";
                    if (p > 60) progText.textContent = window.SERBABISA_TRANS?.almost_done || "Almost done...";
                }
            }, 800);
            form._progInterval = interval;
        } else {
            if (btnText) btnText.style.display = "none";
            if (btnLoad) btnLoad.style.display = "inline-flex";
            submitBtn.disabled = true;
        }
        
        resultArea.style.display = "none";

        const formData = new FormData(form);

        // Remove the empty file input and add our tracked files
        formData.delete("files");
        selectedFiles.forEach(f => formData.append("files", f));

        try {
            const resp = await fetch(endpoint, { 
                method: "POST", 
                body: formData,
                headers: {
                    'X-CSRFToken': getCsrfToken()
                }
            });

            if (!resp.ok) {
                let msg = "Processing failed.";
                try {
                    const json = await resp.json();
                    msg = json.error || msg;
                } catch (_) {}
                showError(msg);
                return;
            }

            const ct = resp.headers.get("Content-Type") || "";

            if (ct.includes("application/json")) {
                const json = await resp.json();
                if (json.error) {
                    showError(json.error);
                } else if (json.text !== undefined) {
                    showTextResult(json.text);
                } else if (json.data !== undefined) {
                    showTextResult(typeof json.data === "string" ? json.data : JSON.stringify(json.data, null, 2));
                }
            } else {
                // Binary file download
                const blob = await resp.blob();
                const cd = resp.headers.get("Content-Disposition") || "";
                let filename = "download";
                const match = cd.match(/filename="?([^";\n]+)"?/);
                if (match) filename = match[1];

                const url = URL.createObjectURL(blob);

                // If image, show preview
                if (ct.startsWith("image/")) {
                    showFileResult(url, filename, true, blob);
                } else {
                    showFileResult(url, filename, false, blob);
                }
            }
        } catch (err) {
            showError("Network error: " + err.message);
        } finally {
            if (form._progInterval) {
                clearInterval(form._progInterval);
                const progFill = document.getElementById("progress-fill");
                const progPct = document.getElementById("progress-pct");
                const progText = document.getElementById("progress-text");
                if (progFill) {
                    progFill.style.width = "100%";
                    progPct.textContent = "100%";
                    progText.textContent = window.SERBABISA_TRANS?.done || "Done!";
                    setTimeout(() => {
                        const progContainer = document.getElementById("progress-container");
                        if (progContainer) progContainer.style.display = "none";
                        submitBtn.style.display = "";
                        submitBtn.disabled = false;
                        if (btnText) btnText.style.display = "";
                        if (btnLoad) btnLoad.style.display = "none";
                    }, 1000);
                }
            } else {
                if (btnText) btnText.style.display = "";
                if (btnLoad) btnLoad.style.display = "none";
                submitBtn.disabled = false;
            }
        }
    });
}

function showError(msg) {
    showToast(msg, 'error');
    const area = document.getElementById("result-area");
    if (!area) return;
    area.style.display = "block";
    document.getElementById("result-success").style.display = "none";
    document.getElementById("result-text")?.style.setProperty("display", "none");
    const errEl = document.getElementById("result-error");
    errEl.style.display = "flex";
    document.getElementById("error-message").textContent = msg;
}

function showFileResult(url, filename, isImage, blob = null) {
    showToast(window.SERBABISA_TRANS?.done || "Done!", 'success');
    const area = document.getElementById("result-area");
    if (!area) return;
    area.style.display = "block";
    document.getElementById("result-error").style.display = "none";
    document.getElementById("result-text")?.style.setProperty("display", "none");

    const success = document.getElementById("result-success");
    success.style.display = "flex";
    document.getElementById("result-message").textContent = window.SERBABISA_TRANS?.done || "Done!";

    const btn = document.getElementById("download-btn");
    btn.innerHTML = `<i class="bi bi-download"></i> ${(window.SERBABISA_TRANS?.download_prefix || 'Download')} ` + filename;
    
    if (window.pywebview && window.pywebview.api && blob) {
        btn.removeAttribute("download");
        btn.removeAttribute("href");
        btn.onclick = (e) => {
            e.preventDefault();
            const originalHtml = btn.innerHTML;
            btn.innerHTML = `<i class="bi bi-hourglass-split"></i> ${(window.SERBABISA_TRANS?.saving || 'Saving...')}`;
            const reader = new FileReader();
            reader.onloadend = function() {
                const b64 = reader.result.split(',')[1];
                window.pywebview.api.save_file(b64, filename).then((success) => {
                    btn.innerHTML = originalHtml;
                });
            };
            reader.readAsDataURL(blob);
        };
    } else {
        btn.href = url;
        btn.download = filename;
        btn.onclick = null;
    }

    const preview = document.getElementById("result-preview");
    if (isImage) {
        preview.style.display = "block";
        preview.innerHTML = `<img src="${url}" alt="Preview">`;
    } else {
        preview.style.display = "none";
    }
}

function showTextResult(text) {
    showToast(window.SERBABISA_TRANS?.done || "Done!", 'success');
    const area = document.getElementById("result-area");
    if (!area) return;
    area.style.display = "block";
    document.getElementById("result-error").style.display = "none";
    document.getElementById("result-success").style.display = "none";

    const textBox = document.getElementById("result-text");
    if (textBox) {
        textBox.style.display = "block";
        document.getElementById("result-text-content").textContent = text;
    }
}

function copyResult() {
    const text = document.getElementById("result-text-content")?.textContent;
    if (text) {
        navigator.clipboard.writeText(text);
        showToast(window.SERBABISA_TRANS?.copied_to_clipboard || "Tersalin ke clipboard!", 'success');
    }
}


/* ── Dependent Options ────────────────────────── */
function initDependentOptions() {
    document.querySelectorAll("[data-depends-on]").forEach(el => {
        const parentName = el.dataset.dependsOn;
        const requiredVal = el.dataset.dependsValue;
        const parentInput = document.querySelector(`[name="${parentName}"]`);
        if (!parentInput) return;

        const check = () => {
            // Support comma-separated values
            const vals = requiredVal.split(",");
            el.style.display = vals.includes(parentInput.value) ? "" : "none";
        };
        parentInput.addEventListener("change", check);
        check();
    });
}
