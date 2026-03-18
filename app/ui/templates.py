def index_html() -> str:
    return """
<!DOCTYPE html>
<html>
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Enterprise AI Copilot</title>
  <style>
    :root {
      --card: #fffaf0;
      --text: #1f1f1f;
      --accent: #0f766e;
      --accent-2: #b45309;
    }
    body {
      margin: 0;
      font-family: \"Avenir Next\", \"Segoe UI\", sans-serif;
      background: radial-gradient(circle at 10% 10%, #fff4d6, transparent 35%), linear-gradient(135deg, #f7f3eb, #f0fdf4);
      color: var(--text);
    }
    .wrap { max-width: 900px; margin: 32px auto; padding: 20px; }
    .card {
      background: var(--card);
      border: 1px solid #eadfcd;
      border-radius: 16px;
      padding: 20px;
      box-shadow: 0 8px 24px rgba(20, 20, 20, 0.06);
    }
    h1 { margin-top: 0; }
    textarea {
      width: 100%;
      min-height: 120px;
      border-radius: 12px;
      border: 1px solid #d4c8b5;
      padding: 12px;
      font-size: 15px;
    }
    button {
      margin-top: 12px;
      margin-right: 8px;
      background: var(--accent);
      color: white;
      border: 0;
      padding: 10px 16px;
      border-radius: 10px;
      cursor: pointer;
    }
    pre {
      white-space: pre-wrap;
      background: #fcf8ef;
      border: 1px solid #eadfcd;
      border-radius: 12px;
      padding: 12px;
    }
    .row { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }
    .links a { color: var(--accent-2); }
    select { padding: 8px; border-radius: 8px; border: 1px solid #d4c8b5; }
  </style>
</head>
<body>
  <div class=\"wrap\">
    <div class=\"card\">
      <h1>Enterprise AI Knowledge Copilot</h1>
      <p>FastAPI + Databricks Mosaic AI + Vector Search + MLflow + JWT RBAC</p>
      <div class=\"row\">
        <label for=\"role\">Role:</label>
        <select id=\"role\">
          <option value=\"analyst\">analyst</option>
          <option value=\"operator\">operator</option>
          <option value=\"admin\">admin</option>
          <option value=\"viewer\">viewer</option>
        </select>
        <button onclick=\"getToken()\">Get Demo Token</button>
      </div>
      <textarea id=\"q\" placeholder=\"Ask about Jira, policy docs, SQL, or APIs...\"></textarea>
      <div class=\"row\">
        <button onclick=\"ask()\">Ask Copilot</button>
        <button onclick=\"askStream()\">Stream</button>
      </div>
      <pre id=\"out\">Response will appear here...</pre>
      <p class=\"links\"><a href=\"/dashboard\">Open Evaluation Dashboard</a></p>
    </div>
  </div>
  <script>
    let token = '';

    async function getToken() {
      const role = document.getElementById('role').value;
      const res = await fetch('/auth/demo-token?user_id=demo-user&roles=' + role);
      const data = await res.json();
      token = data.access_token;
      document.getElementById('out').textContent = 'Token ready for role=' + role;
    }

    async function ask() {
      if (!token) await getToken();
      const question = document.getElementById('q').value;
      const res = await fetch('/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ' + token,
        },
        body: JSON.stringify({question: question})
      });
      const data = await res.json();
      document.getElementById('out').textContent = JSON.stringify(data, null, 2);
    }

    async function askStream() {
      if (!token) await getToken();
      const question = document.getElementById('q').value;
      const res = await fetch('/chat/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ' + token,
        },
        body: JSON.stringify({question: question})
      });
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let result = '';
      while (true) {
        const chunk = await reader.read();
        if (chunk.done) break;
        result += decoder.decode(chunk.value, { stream: true });
        document.getElementById('out').textContent = result;
      }
    }
  </script>
</body>
</html>
"""


def dashboard_html() -> str:
    return """
<!DOCTYPE html>
<html>
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Evaluation Dashboard</title>
  <style>
    body {
      margin: 0;
      font-family: \"Avenir Next\", \"Segoe UI\", sans-serif;
      background: linear-gradient(120deg, #eff6ff, #f0fdfa);
      color: #0f172a;
    }
    .wrap { max-width: 860px; margin: 30px auto; padding: 20px; }
    .panel {
      background: #ffffff;
      border: 1px solid #dbeafe;
      border-radius: 16px;
      padding: 20px;
    }
    button {
      background: #1d4ed8;
      color: white;
      border: 0;
      padding: 10px 16px;
      border-radius: 10px;
      cursor: pointer;
    }
    pre {
      white-space: pre-wrap;
      background: #f8fafc;
      border: 1px solid #dbeafe;
      border-radius: 12px;
      padding: 12px;
      min-height: 180px;
    }
  </style>
</head>
<body>
  <div class=\"wrap\">
    <div class=\"panel\">
      <h1>MLflow Evaluation Dashboard</h1>
      <p>Evaluation requires <code>admin</code> role. Click run to auto-create an admin demo token.</p>
      <button onclick=\"runEval()\">Run Evaluation</button>
      <pre id=\"out\">Metrics will appear here...</pre>
    </div>
  </div>
  <script>
    async function runEval() {
      const tokenRes = await fetch('/auth/demo-token?user_id=demo-admin&roles=admin');
      const tokenData = await tokenRes.json();
      const res = await fetch('/evaluate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ' + tokenData.access_token,
        },
        body: JSON.stringify({run_name: 'dashboard-eval'})
      });
      const data = await res.json();
      document.getElementById('out').textContent = JSON.stringify(data, null, 2);
    }
  </script>
</body>
</html>
"""
