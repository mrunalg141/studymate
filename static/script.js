const sendBtn = document.getElementById("send-btn");
const userInput = document.getElementById("user-input");
const chatBox = document.getElementById("chat-box");
const uploadBtn = document.getElementById("upload-btn");
const pdfUpload = document.getElementById("pdf-upload");
const uploadStatus = document.getElementById("upload-status");
const uploadDropzone = document.getElementById("upload-dropzone");
const fileNameDisplay = document.getElementById("file-name-display");
const clearBtn = document.getElementById("clear-btn");

window.addEventListener("DOMContentLoaded", () => {
    chatBox.scrollTop = chatBox.scrollHeight;
});

sendBtn.addEventListener("click", sendMessage);
userInput.addEventListener("keypress", function (e) {
    if (e.key === "Enter") {
        sendMessage();
    }
});

async function sendMessage() {
    const message = userInput.value.trim();
    if (!message) return;

    appendMessage("user", message);
    userInput.value = "";

    const response = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: message })
    });

    const data = await response.json();
    appendMessage("bot", data.reply);
}

function appendMessage(sender, text) {
    const msgDiv = document.createElement("div");
    msgDiv.classList.add("message", sender);

    if (sender === "bot") {
        msgDiv.innerHTML = marked.parse(text);

        if (window.renderMathInElement) {
            renderMathInElement(msgDiv, {
                delimiters: [
                    { left: "$$", right: "$$", display: true },
                    { left: "$", right: "$", display: false }
                ],
                throwOnError: false
            });
        }
    } else {
        msgDiv.textContent = text;
    }

    chatBox.appendChild(msgDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

pdfUpload.addEventListener("change", () => {
    if (pdfUpload.files.length > 0) {
        fileNameDisplay.textContent = pdfUpload.files[0].name;
    } else {
        fileNameDisplay.textContent = "Choose a PDF to upload";
    }
});

uploadDropzone.addEventListener("dragover", (e) => {
    e.preventDefault();
    uploadDropzone.classList.add("dragover");
});

uploadDropzone.addEventListener("dragleave", () => {
    uploadDropzone.classList.remove("dragover");
});

uploadDropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    uploadDropzone.classList.remove("dragover");
    if (e.dataTransfer.files.length > 0) {
        pdfUpload.files = e.dataTransfer.files;
        pdfUpload.dispatchEvent(new Event("change"));
    }
});

uploadBtn.addEventListener("click", async () => {
    const file = pdfUpload.files[0];
    if (!file) {
        uploadStatus.textContent = "Please choose a PDF first.";
        uploadStatus.className = "upload-status-text error";
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    uploadBtn.disabled = true;
    uploadStatus.textContent = "Uploading...";
    uploadStatus.className = "upload-status-text";

    try {
        const response = await fetch("/upload", {
            method: "POST",
            body: formData
        });
        const data = await response.json();
        uploadStatus.textContent = data.message;
        uploadStatus.className = "upload-status-text success";
    } catch (err) {
        uploadStatus.textContent = "Upload failed. Try again.";
        uploadStatus.className = "upload-status-text error";
    }

    uploadBtn.disabled = false;
});

clearBtn.addEventListener("click", async () => {
    const confirmed = confirm("Clear all chat history? This can't be undone.");
    if (!confirmed) return;

    const response = await fetch("/clear", { method: "POST" });
    const data = await response.json();

    if (response.ok) {
        chatBox.innerHTML = "";
    }
});