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

    const timeFilter = document.getElementById("filter-time");
    const typeFilter = document.getElementById("filter-type");
    if (timeFilter) timeFilter.addEventListener("change", fetchStats);
    if (typeFilter) typeFilter.addEventListener("change", fetchStats);
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

        // Apply filters before rendering
        const timeFilter = document.getElementById("filter-time")?.value || "all";
        const typeFilter = document.getElementById("filter-type")?.value || "all";

        const filteredLogs = filterLogs(data.recent_logs, timeFilter, typeFilter);

        // Backend returns logs ordered by timestamp DESC (newest first)
        // No need to reverse, just display as-is
        filteredLogs.forEach(log => {
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

            const actionLabel = log.is_blocked ? "Blocked" : "Unblocked";
            const actionColor = log.is_blocked ? "var(--danger)" : "var(--success)";

            tr.innerHTML = `
                <td>${localTime}</td>
                <td>${log.ip}</td>
                <td><span class="${badgeClass}">${log.type}</span></td>
                <td>${escapeHtml(log.username)}</td>
                <td>${maskedAndToggle}</td>
                <td><button style="padding: 6px 12px; font-size: 0.9rem; background: var(--primary); cursor: pointer; border: none; border-radius: 4px; color: white;" onclick="viewAttackDetails(${log.id})">View Details</button></td>
                <td>
                    <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                        <button id="btn-${log.id}" style="padding: 4px 8px; font-size: 0.8rem; background: ${actionColor};" onclick="toggleBlockIp('${log.ip}', 'btn-${log.id}', ${log.is_blocked})">${actionLabel}</button>
                        <button style="padding: 4px 8px; font-size: 0.8rem; background: var(--danger);" onclick="deleteLog(${log.id})">Delete</button>
                    </div>
                </td>
            `;
            tbody.appendChild(tr);
        });

    } catch (err) {
        console.error("Failed to fetch stats", err);
    }
}

function openActiveThreats() {
    const modal = document.getElementById("active-threats-modal");
    if (!modal) return;
    modal.style.display = "flex";
    fetchActiveThreats();
}

function closeActiveThreats() {
    const modal = document.getElementById("active-threats-modal");
    if (!modal) return;
    modal.style.display = "none";
}

async function fetchActiveThreats() {
    const tbody = document.getElementById("active-threats-body");
    if (!tbody) return;
    tbody.innerHTML = `<tr><td colspan="5" style="color: var(--text-muted);">Loading...</td></tr>`;

    try {
        const res = await fetch(`${API_BASE}/api/admin/active_threats`);
        const data = await res.json();
        const threats = Array.isArray(data.active_threats) ? data.active_threats : [];

        if (!threats.length) {
            tbody.innerHTML = `<tr><td colspan="5" style="color: var(--text-muted);">No active threats</td></tr>`;
            return;
        }

        tbody.innerHTML = "";
        threats.forEach(threat => {
            const tr = document.createElement("tr");
            const lastUpdated = formatLocalTime(threat.last_updated);
            tr.innerHTML = `
                <td>${threat.ip}</td>
                <td>${threat.score.toFixed(2)}</td>
                <td>${threat.risk}</td>
                <td>${lastUpdated}</td>
                <td>
                    <button class="delete-btn" onclick="deleteThreat('${threat.ip}')" style="background: var(--danger); border: none; color: white; padding: 4px 8px; border-radius: 4px; cursor: pointer; font-size: 0.85rem;">Delete</button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (err) {
        console.error("Failed to fetch active threats", err);
        tbody.innerHTML = `<tr><td colspan="5" style="color: var(--text-muted);">Failed to load</td></tr>`;
    }
}

function filterLogs(logs, timeFilter, typeFilter) {
    if (!Array.isArray(logs)) return [];

    const now = new Date();
    const startOfToday = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const oneHourAgo = new Date(now.getTime() - 60 * 60 * 1000);
    const oneWeekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);

    return logs.filter(log => {
        const logTime = log.time ? new Date(log.time) : null;

        if (timeFilter === "hour") {
            if (!logTime || logTime < oneHourAgo) return false;
        } else if (timeFilter === "today") {
            if (!logTime || logTime < startOfToday) return false;
        } else if (timeFilter === "week") {
            if (!logTime || logTime < oneWeekAgo) return false;
        }

        if (typeFilter === "successful") {
            return log.type === "Successful Login";
        }
        if (typeFilter === "failed") {
            return log.type === "Failed Login";
        }
        if (typeFilter === "malicious") {
            return log.type !== "Successful Login" && log.type !== "Failed Login";
        }

        return true;
    });
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

async function deleteLog(logId) {
    if (!confirm("Delete this log entry? This action cannot be undone.")) return;

    try {
        const res = await fetch(`${API_BASE}/api/admin/log/${logId}`, {
            method: "DELETE"
        });

        const data = await res.json();
        if (res.ok && !data.error) {
            fetchStats();
        } else {
            alert(data.error || "Failed to delete log");
        }
    } catch (err) {
        console.error(err);
        alert("Error deleting log");
    }
}

async function deleteThreat(ip) {
    if (!confirm(`Delete threat score for ${ip}? This action cannot be undone.`)) return;

    try {
        const res = await fetch(`${API_BASE}/api/admin/threat/${encodeURIComponent(ip)}`, {
            method: "DELETE"
        });

        const data = await res.json();
        if (res.ok && !data.error) {
            await fetchActiveThreats();
            fetchStats();
        } else {
            alert(data.error || "Failed to delete threat");
        }
    } catch (err) {
        console.error(err);
        alert("Error deleting threat");
    }
}

async function toggleBlockIp(ip, btnId, isBlocked) {
    const action = isBlocked ? "unblock" : "block";
    const confirmText = isBlocked
        ? `Are you sure you want to unblock IP: ${ip}?`
        : `Are you sure you want to block IP: ${ip}?`;
    if (!confirm(confirmText)) return;

    try {
        const res = await fetch(`${API_BASE}/api/admin/${action}_ip`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ ip: ip })
        });

        if (res.ok) {
            if (btnId) {
                const btn = document.getElementById(btnId);
                if (btn) {
                    if (isBlocked) {
                        btn.textContent = "Unblocked";
                        btn.style.background = "var(--success)";
                    } else {
                        btn.textContent = "Blocked";
                        btn.style.background = "var(--danger)";
                    }
                }
            }
            fetchStats(); // Refresh
        } else {
            alert(`Failed to ${action} IP`);
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
                await fetch(`${API_BASE}/portal/execute`, {
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
