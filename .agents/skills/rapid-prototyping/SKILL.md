---
name: rapid-prototyping
description: "Opinionated, fast-ship scaffolding patterns for common hackathon tech stacks. Provides '5-minute scaffolds' that produce working, deployable skeletons for FastAPI, Streamlit, Gradio, and HTMX apps. TRIGGERS: 'scaffold a web app', 'quick prototype', 'fast API setup', 'streamlit template', 'gradio demo', 'bootstrap project', 'hackathon starter', 'quick deploy'."
---

# Rapid Prototyping Skill

Speed-optimized project scaffolds for hackathons. Each scaffold produces a
working, deployable application in under 5 minutes. The scaffolds are
opinionated — they make decisions for you so you can focus on the unique logic.

---

## Scaffold Selection Guide

| If You're Building... | Use This Scaffold | Deploy To |
|:---|:---|:---|
| A data dashboard | **Streamlit** | Streamlit Cloud / HF Spaces |
| An ML model demo | **Gradio** | HF Spaces |
| A REST API with simple UI | **FastAPI + HTMX** | HF Spaces (Docker) |
| A full web app | **FastAPI + Jinja2** | HF Spaces (Docker) |
| A CLI tool | **Typer** | PyPI / GitHub Release |

---

## Scaffold 1: Streamlit (Data Dashboard)

```bash
# Initialize
mkdir -p .streamlit && touch app.py requirements.txt .streamlit/config.toml
```

**app.py:**
```python
import streamlit as st

st.set_page_config(
    page_title="[Project Name]",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("[Project Name]")
st.markdown("*[One-line description]*")

# Sidebar for controls
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("API Key", type="password")

# Main content
col1, col2 = st.columns(2)
with col1:
    st.subheader("Input")
    user_input = st.text_area("Enter your query", height=150)
    if st.button("Analyze", type="primary"):
        with st.spinner("Processing..."):
            # TODO: Replace with actual logic
            st.success("Analysis complete!")

with col2:
    st.subheader("Results")
    st.info("Results will appear here after analysis.")
```

**.streamlit/config.toml:**
```toml
[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#0E1117"
secondaryBackgroundColor = "#262730"
textColor = "#FAFAFA"

[server]
headless = true
address = "0.0.0.0"
port = 8501
```

**requirements.txt:**
```
streamlit>=1.30.0
```

Deploy: `streamlit run app.py` // turbo

---

## Scaffold 2: Gradio (ML Demo)

**app.py:**
```python
import gradio as gr
import os

def process(input_text: str, api_key: str) -> str:
    """Main processing function. Replace with your ML logic."""
    if not api_key:
        return "Please provide an API key."
    # TODO: Replace with actual model inference
    return f"Processed: {input_text}"

demo = gr.Interface(
    fn=process,
    inputs=[
        gr.Textbox(label="Input", placeholder="Enter text...", lines=5),
        gr.Textbox(label="API Key", type="password"),
    ],
    outputs=gr.Textbox(label="Output", lines=10),
    title="[Project Name]",
    description="[One-line description of what this does]",
    examples=[
        ["Example input 1", ""],
        ["Example input 2", ""],
    ],
    theme=gr.themes.Soft(),
)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
```

**requirements.txt:**
```
gradio>=4.0.0
```

Deploy: `python app.py` // turbo

---

## Scaffold 3: FastAPI + HTMX (Interactive Web App)

**main.py:**
```python
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import os

app = FastAPI(title="[Project Name]")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>[Project Name]</title>
    <script src="https://unpkg.com/htmx.org@1.9.10"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: system-ui, sans-serif; background: #0f0f0f; color: #e0e0e0; }
        .container { max-width: 800px; margin: 0 auto; padding: 2rem; }
        h1 { font-size: 2rem; margin-bottom: 1rem; background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-color: transparent; }
        .card { background: #1a1a2e; border-radius: 12px; padding: 1.5rem; margin: 1rem 0; }
        input, textarea { width: 100%; padding: 0.75rem; border: 1px solid #333; border-radius: 8px; background: #16213e; color: #e0e0e0; font-size: 1rem; }
        button { padding: 0.75rem 1.5rem; background: linear-gradient(135deg, #667eea, #764ba2); color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 1rem; }
        button:hover { opacity: 0.9; }
        #result { min-height: 100px; }
        .htmx-indicator { display: none; }
        .htmx-request .htmx-indicator { display: inline; }
    </style>
</head>
<body>
    <div class="container">
        <h1>[Project Name]</h1>
        <div class="card">
            <form hx-post="/api/process" hx-target="#result" hx-indicator="#spinner">
                <textarea name="input_text" rows="4" placeholder="Enter your query..."></textarea>
                <br><br>
                <button type="submit">Analyze</button>
                <span id="spinner" class="htmx-indicator">⏳ Processing...</span>
            </form>
        </div>
        <div class="card" id="result">
            <p>Results will appear here.</p>
        </div>
    </div>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML_TEMPLATE

@app.post("/api/process", response_class=HTMLResponse)
async def process(request: Request):
    form = await request.form()
    input_text = form.get("input_text", "")
    # TODO: Replace with actual processing logic
    return f"<p>Processed: {input_text}</p>"

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)
```

**requirements.txt:**
```
fastapi>=0.109.0
uvicorn>=0.27.0
python-multipart>=0.0.6
```

**Dockerfile (for HF Spaces):**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 7860
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
```

Deploy: `uvicorn main:app --reload --host 0.0.0.0 --port 7860` // turbo

---

## Post-Scaffold Checklist

After scaffolding, immediately verify:
1. `python app.py` or equivalent starts without errors // turbo
2. `curl http://localhost:PORT/health` returns 200 // turbo
3. The UI loads in a browser
4. Commit the working skeleton before adding features
