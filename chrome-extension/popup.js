// ===============================
// CONFIG — CHANGE THIS WHEN YOU DEPLOY BACKEND
// ===============================
const API_BASE = "http://127.0.0.1:8000";   // local backend for now

// ===============================
// ELEMENTS
// ===============================
const uploadBtn = document.getElementById("upload_btn");
const optimizeBtn = document.getElementById("optimize_btn");

const uploadStatus = document.getElementById("upload_status");
const optimizeStatus = document.getElementById("optimize_status");

// ===============================
// SAVE USER ID LOCALLY
// ===============================
function saveUserId(userId) {
    chrome.storage.local.set({ user_id: userId });
}

async function getUserId() {
    return new Promise((resolve) => {
        chrome.storage.local.get(["user_id"], (result) => {
            resolve(result.user_id || null);
        });
    });
}

// ===============================
// 1) UPLOAD RESUME + USER INFO
// ===============================
uploadBtn.addEventListener("click", async () => {
    const full_name = document.getElementById("full_name").value.trim();
    const phone = document.getElementById("phone").value.trim();
    const email = document.getElementById("email").value.trim();
    const linkedin = document.getElementById("linkedin").value.trim();
    const github = document.getElementById("github").value.trim();
    const fileInput = document.getElementById("resume_file");

    if (!full_name || !email || !phone) {
        uploadStatus.textContent = "Full name, phone, and email are required.";
        uploadStatus.style.color = "red";
        return;
    }

    if (!fileInput.files[0]) {
        uploadStatus.textContent = "Please upload a resume file.";
        uploadStatus.style.color = "red";
        return;
    }

    const file = fileInput.files[0];

    uploadStatus.textContent = "Uploading...";
    uploadStatus.style.color = "black";

    // Create a new user_id if not exists
    let user_id = await getUserId();
    if (!user_id) {
        user_id = crypto.randomUUID();
        saveUserId(user_id);
    }

    // Build FormData
    const formData = new FormData();
    formData.append("user_id", user_id);
    formData.append("full_name", full_name);
    formData.append("phone", phone);
    formData.append("email", email);
    formData.append("linkedin", linkedin);
    formData.append("github", github);
    formData.append("file", file);

    try {
        const res = await fetch(`${API_BASE}/resume/upload`, {
            method: "POST",
            body: formData,
        });

        const data = await res.json();

        if (data.error) {
            uploadStatus.textContent = "Error: " + data.error;
            uploadStatus.style.color = "red";
            return;
        }

        uploadStatus.textContent = "Resume uploaded successfully!";
        uploadStatus.style.color = "green";

    } catch (err) {
        uploadStatus.textContent = "Upload failed.";
        uploadStatus.style.color = "red";
        console.error(err);
    }
});

// ===============================
// 2) OPTIMIZE FOR JOB DESCRIPTION
// ===============================
optimizeBtn.addEventListener("click", async () => {
    const job_description = document.getElementById("job_description").value.trim();

    if (!job_description) {
        optimizeStatus.textContent = "Please paste a job description.";
        optimizeStatus.style.color = "red";
        return;
    }

    let user_id = await getUserId();
    if (!user_id) {
        optimizeStatus.textContent = "Please upload your resume first!";
        optimizeStatus.style.color = "red";
        return;
    }

    optimizeStatus.textContent = "Optimizing resume...";
    optimizeStatus.style.color = "black";

    try {
        const res = await fetch(`${API_BASE}/optimize`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                user_id: user_id,
                job_description: job_description,
            }),
        });

        const data = await res.json();

        if (data.error) {
            optimizeStatus.textContent = "Error: " + data.error;
            optimizeStatus.style.color = "red";
            return;
        }

        // Trigger file download
        const url = data.file_url;
        chrome.downloads.download({ url });

        optimizeStatus.textContent = "Optimized resume downloaded!";
        optimizeStatus.style.color = "green";

    } catch (err) {
        optimizeStatus.textContent = "Optimization failed.";
        optimizeStatus.style.color = "red";
        console.error(err);
    }
});