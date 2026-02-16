const API_BASE = window.location.origin;

// Helper function to escape HTML
function escapeHtml(text) {
    if (!text) return "-";
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

// Helper function to format timestamp to local time
function formatLocalTime(isoString) {
    if (!isoString) return "N/A";
    try {
        const date = new Date(isoString);
        // Format: YYYY-MM-DD HH:MM:SS
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');
        const seconds = String(date.getSeconds()).padStart(2, '0');
        return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
    } catch {
        return isoString;
    }
}

document.addEventListener("DOMContentLoaded", () => {
    // Determine page
    if (document.getElementById("loginForm")) {
        setupLogin();
    } else if (document.getElementById("total-attacks")) {
        setupDashboard();
    } else if (document.getElementById("fake-cmd")) {
        setupHoneypot();
    }
});

function setupLogin() {
    const form = document.getElementById("loginForm");

    // Login Handler
    if (form) {
        form.addEventListener("submit", async (e) => {
            e.preventDefault();
            const formData = new FormData(form);

            try {
                const res = await fetch(`${API_BASE}/auth/login`, {
                    method: "POST",
                    body: formData
                });

                const data = await res.json();

                if (res.ok) {
                    window.location.href = data.redirect;
                } else {
                    document.getElementById("errorMsg").innerText = data.detail || "Invalid credentials";
                    document.getElementById("errorMsg").style.display = "block";
                }
            } catch (err) {
                console.error(err);
            }
        });
    }

    // Register Handler
    const regForm = document.getElementById("registerForm");
    if (regForm) {
        regForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const formData = new FormData(regForm);
            try {
                const res = await fetch(`${API_BASE}/auth/register`, {
                    method: "POST",
                    body: formData
                });
                const data = await res.json();
                if (res.ok) {
                    alert("Registration Successful! Please login.");
                    toggleRegister();
                } else {
                    alert("Registration Failed: " + (data.detail || "User likely already exists"));
                }
            } catch (err) {
                console.error(err);
                alert("Registration Error");
            }
        });
    }
}

function toggleRegister() {
    const loginForm = document.getElementById("loginForm");
    const regForm = document.getElementById("registerForm");
    const btn = document.getElementById("toggleBtn");
    const title = document.querySelector(".login-container h2");

    if (loginForm.style.display === "none") {
        loginForm.style.display = "block";
        regForm.style.display = "none";
        btn.innerText = "Need an account? Register";
        if (title) title.innerText = "Secure Portal";
    } else {
        loginForm.style.display = "none";
        regForm.style.display = "block";
        btn.innerText = "Already have an account? Login";
        if (title) title.innerText = "Create Account";
    }
}

async function setupDashboard() {
    // Poll for stats every 5 seconds
    fetchStats();
    setInterval(fetchStats, 5000);
}

async function fetchStats() {
    try {
        const res = await fetch(`${API_BASE}/api/admin/stats`);
        const data = await res.json();

        // Fix: Update Total Logins
        if (document.getElementById("total-logins"))
            document.getElementById("total-logins").innerText = data.total_logins;

        document.getElementById("total-attacks").innerText = data.total_attacks;
        document.getElementById("active-threats").innerText = data.active_threats;

        const tbody = document.getElementById("attack-log-body");
        tbody.innerHTML = "";

        // Backend returns logs ordered by timestamp DESC (newest first)
        // No need to reverse, just display as-is
        data.recent_logs.forEach(log => {
            const tr = document.createElement("tr");

            let badgeClass = "alert-badge";
            if (log.type === "Successful Login") badgeClass += " badge-success";
            else if (log.type === "Failed Login") badgeClass += " badge-warning";
            else if (log.type === "Honeypot Session") badgeClass += " badge-sql";
            else badgeClass += " badge-sql";

            // Format Payload Detail
            let detail = log.attack_detail;
            if (log.attack_detail === "-" && log.type !== "Successful Login" && log.type !== "Failed Login" && log.type !== "Honeypot Session") {
                detail = "Detected via AI/Signature";
            } else if (log.attack_detail === "-") {
                detail = "";
            }

            // Password Toggle UI
            const safePassword = escapeHtml(log.password);
            // Default masked
            const maskedAndToggle = `
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span id="pwd-${log.id}" style="font-family: monospace;">••••••</span>
                    <button style="background: none; border: none; padding: 0; cursor: pointer; opacity: 0.7;" 
                        title="Show/Hide Password"
                        onclick="togglePassword('${log.id}', '${safePassword}')">
                        👁️
                    </button>
                </div>
            `;

            // Convert UTC timestamp to local time
            const localTime = formatLocalTime(log.time);

            // For honeypot sessions, show expanded detail
            if (log.is_session) {
                tr.innerHTML = `
                    <td>${localTime}</td>
                    <td>${log.ip}</td>
                    <td><span class="${badgeClass}">${log.type}</span></td>
                    <td>-</td>
                    <td>-</td>
                    <td><button style="padding: 6px 12px; font-size: 0.9rem; background: var(--primary); cursor: pointer; border: none; border-radius: 4px; color: white;" onclick="viewSessionDetails('${log.session_id}')">View Session (${log.num_commands} cmds)</button></td>
                    <td><button id="btn-${log.id}" style="padding: 4px 8px; font-size: 0.8rem;" onclick="blockIp('${log.ip}', 'btn-${log.id}')">Block</button></td>
                `;
            } else {
                tr.innerHTML = `
                    <td>${localTime}</td>
                    <td>${log.ip}</td>
                    <td><span class="${badgeClass}">${log.type}</span></td>
                    <td>${escapeHtml(log.username)}</td>
                    <td>${maskedAndToggle}</td>
                    <td><button style="padding: 6px 12px; font-size: 0.9rem; background: var(--primary); cursor: pointer; border: none; border-radius: 4px; color: white;" onclick="viewAttackDetails(${log.id})">View Details</button></td>
                    <td><button id="btn-${log.id}" style="padding: 4px 8px; font-size: 0.8rem;" onclick="blockIp('${log.ip}', 'btn-${log.id}')">Block</button></td>
                `;
            }
            tbody.appendChild(tr);
        });

    } catch (err) {
        console.error("Failed to fetch stats", err);
    }
}

function togglePassword(id, realPassword) {
    const span = document.getElementById(`pwd-${id}`);
    if (span.innerText === "••••••") {
        span.innerText = realPassword;
    } else {
        span.innerText = "••••••";
    }
}

async function clearLogs() {
    if (!confirm("Are you sure you want to delete ALL attack logs? This action cannot be undone.")) return;

    try {
        const res = await fetch(`${API_BASE}/api/admin/clear_logs`, {
            method: "POST",
            headers: { "Content-Type": "application/json" }
        });

        if (res.ok) {
            alert("All attack logs cleared successfully");
            fetchStats(); // Refresh dashboard
        } else {
            alert("Failed to clear logs");
        }
    } catch (err) {
        console.error(err);
        alert("Error clearing logs");
    }
}

async function blockIp(ip, btnId) {
    if (!confirm(`Are you sure you want to block IP: ${ip}?`)) return;

    try {
        const res = await fetch(`${API_BASE}/api/admin/block_ip`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ ip: ip })
        });

        if (res.ok) {
            alert("IP Blocked Successfully");
            if (btnId) document.getElementById(btnId).disabled = true;
            fetchStats(); // Refresh
        } else {
            alert("Failed to block IP");
        }
    } catch (err) {
        console.error(err);
    }
}

// Fake File System
const FAKE_FS = {
    "confidential_memo_2024.txt": "TO: All Staff\nFROM: CEO\nSUBJECT: MERGER\n\nWe are merging with CorpCorp. Keep this quiet.",
    "passwords.txt": "admin:SuperSecretPass123!\ndb_user:password123\nroot:toor",
    "network_map.png": "[BINARY DATA CORRUPTED]"
};

function setupHoneypot() {
    const input = document.getElementById("fake-cmd");
    const historyFn = document.getElementById("terminal-history");

    if (input) {
        input.focus(); // Auto focus

        input.addEventListener("keypress", async (e) => {
            if (e.key === "Enter") {
                const cmdLine = input.value.trim();
                input.value = "";

                // Echo command
                const promptLine = document.createElement("div");
                promptLine.innerHTML = `<span style="color: var(--success);">user@internal:~$</span> ${escapeHtml(cmdLine)}`;
                historyFn.appendChild(promptLine);

                // Process Command locally for fake effect
                const args = cmdLine.split(" ");
                const cmd = args[0].toLowerCase();
                let output = "";

                if (cmd === "help") {
                    output = "Available commands: ls, cat, download, whoami, pwd, clear, exit";
                }
                else if (cmd === "ls") {
                    output = Object.keys(FAKE_FS).join("    ");
                }
                else if (cmd === "cat") {
                    const filename = args[1];
                    if (FAKE_FS[filename]) {
                        output = FAKE_FS[filename];
                    } else if (!filename) {
                        output = "Usage: cat [filename]";
                    } else {
                        output = `cat: ${filename}: No such file or directory`;
                    }
                }
                else if (cmd === "download") {
                    const filename = args[1];
                    if (FAKE_FS[filename]) {
                        downloadFakeFile(filename, FAKE_FS[filename]);
                        output = `Downloading ${filename}... Done.`;
                    } else {
                        output = `File not found.`;
                    }
                }
                else if (cmd === "clear") {
                    historyFn.innerHTML = "";
                }
                else if (cmd === "") {
                    // Do nothing
                }
                else {
                    output = `Command not found: ${cmd}`;
                }

                if (output && cmd !== "clear") {
                    const outDiv = document.createElement("div");
                    outDiv.style.color = "#ccc";
                    outDiv.style.whiteSpace = "pre-wrap"; // Preserve spacing
                    outDiv.innerText = output;
                    historyFn.appendChild(outDiv);
                }

                // Scroll to bottom
                const terminalContainer = input.parentElement.parentElement;
                terminalContainer.scrollTop = terminalContainer.scrollHeight;

                // Send to backend to log
                await fetch(`${API_BASE}/internal/execute`, {
                    method: "POST",
                    body: cmdLine
                });
            }
        });
    }
}

function downloadFakeFile(filename, content) {
    const element = document.createElement('a');
    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(content));
    element.setAttribute('download', filename);

    element.style.display = 'none';
    document.body.appendChild(element);

    element.click();

    document.body.removeChild(element);
}

function logout() {
    window.location.href = "/static/login.html";
}

function viewAttackDetails(logId) {
    window.location.href = `/static/attack_details.html?id=${logId}`;
}

function viewSessionDetails(sessionId) {
    window.location.href = `/static/honeypot_session_details.html?id=${sessionId}`;
}

function escapeHtml(text) {
    if (!text) return "";
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
