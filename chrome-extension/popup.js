// ===============================
// CONFIG — CHANGE WHEN YOU DEPLOY
// ===============================
const API_BASE = "https://resumemodificationbot-production.up.railway.app";


// ===============================
// ELEMENTS
// ===============================
const uploadBtn = document.getElementById("upload_btn");
const optimizeBtn = document.getElementById("optimize_btn");
const resetBtn = document.getElementById("reset_btn");

const uploadStatus = document.getElementById("upload_status");
const optimizeStatus = document.getElementById("optimize_status");

const uploadSection = document.getElementById("upload_section");

const atsDiv = document.getElementById("ats_result");
const atsValue = document.getElementById("ats_score_value");


// ===============================
// STORAGE HELPERS
// ===============================
function saveUserId(userId) {
    chrome.storage.local.set({ user_id: userId });
}

function saveUserInfo(info) {
    chrome.storage.local.set({ user_info: info });
}

async function getStoredUser() {
    return new Promise((resolve) => {
        chrome.storage.local.get(["user_id", "user_info"], (result) => {
            resolve({
                user_id: result.user_id || null,
                user_info: result.user_info || null
            });
        });
    });
}


// ===============================
// ON LOAD — AUTO POPULATE + HIDE
// ===============================
document.addEventListener("DOMContentLoaded", async () => {
    const { user_id, user_info } = await getStoredUser();

    if (user_info) {
        document.getElementById("full_name").value = user_info.full_name || "";
        document.getElementById("phone").value = user_info.phone || "";
        document.getElementById("email").value = user_info.email || "";
        document.getElementById("linkedin").value = user_info.linkedin || "";
        document.getElementById("github").value = user_info.github || "";
    }

    if (user_id && user_info) {
        uploadSection.style.display = "none";
    }
});


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

    // Create or get user_id
    let { user_id } = await getStoredUser();
    if (!user_id) {
        user_id = crypto.randomUUID();
        saveUserId(user_id);
    }

    // FormData
    const formData = new FormData();
    formData.append("user_id", user_id);
    formData.append("full_name", full_name);
    formData.append("phone", phone);
    formData.append("email", email);
    formData.append("linkedin", linkedin);
    formData.append("github", github);
    formData.append("file", file);

    uploadStatus.textContent = "Uploading...";
    uploadStatus.style.color = "black";

    try {
        const res = await fetch(`${API_BASE}/resume/upload`, {
            method: "POST",
            body: formData,
        });

        const data = await res.json();

        if (!res.ok || data.error) {
            uploadStatus.textContent = "Error: " + (data.error || "Upload failed");
            uploadStatus.style.color = "red";
            return;
        }

        // Save locally
        saveUserInfo({
            full_name,
            phone,
            email,
            linkedin,
            github,
        });

        uploadStatus.textContent = "Resume uploaded successfully!";
        uploadStatus.style.color = "green";

        uploadSection.style.display = "none";

    } catch (err) {
        console.error(err);
        uploadStatus.textContent = "Upload failed.";
        uploadStatus.style.color = "red";
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

    const { user_id } = await getStoredUser();
    if (!user_id) {
        optimizeStatus.textContent = "Please upload your resume first!";
        optimizeStatus.style.color = "red";
        return;
    }

    optimizeStatus.textContent = "Optimizing resume...";
    optimizeStatus.style.color = "black";

    // Clear old ATS score
    atsDiv.style.display = "none";
    atsValue.textContent = "";

    try {
        const res = await fetch(`${API_BASE}/optimize`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                user_id,
                job_description,
            }),
        });

        const data = await res.json();

        if (!res.ok || data.error) {
            optimizeStatus.textContent = "Error: " + (data.error || "Optimization failed");
            optimizeStatus.style.color = "red";
            return;
        }

        // ⭐ Show ATS Score ⭐
        atsValue.textContent = `${data.ats_score} / 100`;
        atsDiv.style.display = "block";

        // Download optimized resume
        chrome.downloads.download({ url: data.file_url });

        optimizeStatus.textContent = "Optimized resume downloaded!";
        optimizeStatus.style.color = "green";

    } catch (err) {
        console.error(err);
        optimizeStatus.textContent = "Optimization failed.";
        optimizeStatus.style.color = "red";
    }
});


// ===============================
// RESET BUTTON — CLEAR EVERYTHING
// ===============================
resetBtn.addEventListener("click", () => {
    chrome.storage.local.clear(() => {
        location.reload();
    });
});