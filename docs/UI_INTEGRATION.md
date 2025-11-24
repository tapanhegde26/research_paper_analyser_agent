# Web UI Integration Guide

## 🌐 Overview

The Research Paper Analyzer now includes a modern web interface with real-time agent status updates, interactive Q&A, and comprehensive results visualization.

---

## 🏗️ Architecture

```
┌─────────────────┐
│   Web Browser   │
│   (UI Client)   │
└────────┬────────┘
         │ HTTP/WebSocket
         ▼
┌─────────────────┐
│   FastAPI       │
│   Backend API   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Multi-Agent    │
│     System      │
└─────────────────┘
```

### Components

1. **FastAPI Backend** (`src/api.py`)
   - REST API endpoints
   - WebSocket for real-time updates
   - Session management
   - Agent orchestration

2. **Web UI** (`ui/index.html`)
   - Modern, responsive interface
   - Real-time agent status visualization
   - Interactive Q&A chat
   - Results display with metrics

3. **WebSocket Communication**
   - Real-time status updates
   - Live agent coordination display
   - Instant Q&A responses

---

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
cd /Users/thegde/learning/sai-kumar-projects/research-paper-analyzer-agent

# Activate virtual environment
source venv/bin/activate

# Install new dependencies
pip install fastapi uvicorn[standard] websockets python-multipart
```

### Step 2: Start the Backend

```bash
# Option 1: Using uvicorn directly
cd src
uvicorn api:app --reload --host 0.0.0.0 --port 8000

# Option 2: Run the api.py file
python src/api.py
```

### Step 3: Access the UI

Open your browser and navigate to:

```
http://localhost:8000/ui
```

**Alternative URLs:**
- API Documentation: `http://localhost:8000/docs`
- API Health Check: `http://localhost:8000/health`
- Root: `http://localhost:8000/`

---

## 📡 API Endpoints

### REST API

#### 1. Analyze Papers
```http
POST /api/analyze
Content-Type: application/json

{
  "topic": "Quantum Entanglement",
  "num_papers": 10,
  "depth": "standard"
}
```

**Response:**
```json
{
  "session_id": "abc123...",
  "status": "completed",
  "papers_analyzed": 10,
  "summary": "...",
  "key_findings": [...],
  "research_gaps": [...]
}
```

#### 2. Ask Question
```http
POST /api/question
Content-Type: application/json

{
  "session_id": "abc123...",
  "question": "What are the main challenges?"
}
```

**Response:**
```json
{
  "answer": "The main challenges are...",
  "session_id": "abc123..."
}
```

#### 3. List Sessions
```http
GET /api/sessions
```

#### 4. Get Session Details
```http
GET /api/session/{session_id}
```

### WebSocket API

#### Connect
```javascript
ws://localhost:8000/ws/{client_id}
```

#### Send Analysis Request
```json
{
  "action": "analyze",
  "topic": "Quantum Computing",
  "num_papers": 10,
  "depth": "standard"
}
```

#### Send Question
```json
{
  "action": "question",
  "session_id": "abc123...",
  "question": "What methodologies are used?"
}
```

#### Receive Updates
```json
{
  "type": "status",
  "status": "retrieving",
  "details": "Retrieval Agent searching...",
  "timestamp": "2025-11-24T..."
}
```

---

## 🎨 UI Features

### 1. Analysis Configuration
- **Topic Input**: Enter any research topic
- **Number of Papers**: 1-50 papers
- **Analysis Depth**: Quick, Standard, or Comprehensive

### 2. Real-Time Agent Status
Visual display of all 6 agents:
- **Orchestrator** - Workflow coordination
- **Retrieval** - Paper discovery
- **Summary** - Parallel processing
- **Cross-Ref** - Connection identification
- **Synthesis** - Knowledge synthesis
- **Q&A** - Interactive queries

### 3. Live Status Updates
- Connection status
- Current agent activity
- Progress indicators
- Error handling

### 4. Results Display
- **Executive Summary**: High-level overview
- **Key Findings**: Important discoveries (with highlights)
- **Research Gaps**: Unanswered questions
- **Metrics**: Papers analyzed, processing time

### 5. Interactive Q&A
- Chat-like interface
- Real-time responses
- Context-aware answers
- Conversation history

---

## 🔌 Integration Examples

### Example 1: Python Client

```python
import requests

# Start analysis
response = requests.post("http://localhost:8000/api/analyze", json={
    "topic": "Large Language Models",
    "num_papers": 5,
    "depth": "standard"
})

result = response.json()
session_id = result["session_id"]

# Ask questions
response = requests.post("http://localhost:8000/api/question", json={
    "session_id": session_id,
    "question": "What are the main architectures?"
})

answer = response.json()["answer"]
print(answer)
```

### Example 2: JavaScript Client

```javascript
// Using WebSocket
const ws = new WebSocket('ws://localhost:8000/ws/client_123');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
};

// Start analysis
ws.send(JSON.stringify({
    action: 'analyze',
    topic: 'Quantum Physics',
    num_papers: 10,
    depth: 'standard'
}));
```

### Example 3: cURL

```bash
# Analyze papers
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Machine Learning",
    "num_papers": 5,
    "depth": "standard"
  }'

# Ask question
curl -X POST http://localhost:8000/api/question \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "your_session_id",
    "question": "What are the key findings?"
  }'
```

---

## 🛠️ Customization

### Modify UI Theme

Edit `ui/index.html` CSS variables:

```css
/* In the <style> section */
body {
    background: linear-gradient(135deg, #your_color1, #your_color2);
}

button {
    background: linear-gradient(135deg, #your_primary, #your_secondary);
}
```

### Add Custom Endpoints

In `src/api.py`:

```python
@app.get("/api/custom-endpoint")
async def custom_endpoint():
    # Your logic here
    return {"message": "Custom response"}
```

### Enhance Agent Visualization

Modify the agent status display in `ui/index.html`:

```html
<div class="agent-box" id="agent-custom">
    <div>Custom Agent</div>
    <div class="loader hidden"></div>
</div>
```

---

## 🔐 Security Considerations

### Production Deployment

1. **CORS Configuration**
```python
# In src/api.py, change:
allow_origins=["*"]  # Development

# To:
allow_origins=["https://yourdomain.com"]  # Production
```

2. **API Authentication**
```python
from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.post("/api/analyze")
async def analyze(request: AnalysisRequest, credentials: HTTPBasic = Depends(security)):
    # Verify credentials
    pass
```

3. **Rate Limiting**
```python
from slowapi import Limiter

limiter = Limiter(key_func=lambda: "global")

@app.post("/api/analyze")
@limiter.limit("10/minute")
async def analyze(request: AnalysisRequest):
    pass
```

4. **Environment Variables**
```bash
# Never hardcode secrets
API_SECRET_KEY=your_secret_here
MAX_PAPERS_PER_REQUEST=50
```

---

## 📊 Monitoring & Logging

### Enable Request Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

@app.middleware("http")
async def log_requests(request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    return response
```

### Track Metrics

```python
from prometheus_fastapi_instrumentator import Instrumentator

# Add to your FastAPI app
Instrumentator().instrument(app).expose(app)

# Access metrics at /metrics
```

---

## 🚀 Deployment Options

### Option 1: Docker

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

EXPOSE 8000
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t research-analyzer-ui .
docker run -p 8000:8000 -e GOOGLE_API_KEY=your_key research-analyzer-ui
```

### Option 2: Cloud Run

```bash
gcloud run deploy research-analyzer \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY=your_key
```

### Option 3: Traditional Server

```bash
# Using systemd service
sudo nano /etc/systemd/system/research-analyzer.service

[Unit]
Description=Research Paper Analyzer API
After=network.target

[Service]
User=your_user
WorkingDirectory=/path/to/project
Environment="GOOGLE_API_KEY=your_key"
ExecStart=/path/to/venv/bin/uvicorn src.api:app --host 0.0.0.0 --port 8000

[Install]
WantedBy=multi-user.target
```

---

## 🐛 Troubleshooting

### UI Not Loading

**Issue**: "Cannot GET /ui"

**Solution**:
```bash
# Ensure ui directory exists
ls ui/index.html

# Restart server
python src/api.py
```

### WebSocket Connection Failed

**Issue**: "WebSocket connection to 'ws://localhost:8000/ws/...' failed"

**Solution**:
- Check server is running
- Verify firewall settings
- Update WebSocket URL in UI if using different host

### CORS Errors

**Issue**: "Access-Control-Allow-Origin" error

**Solution**:
```python
# In src/api.py, add your domain:
allow_origins=["http://localhost:3000", "https://yourdomain.com"]
```

### Agent Not Responding

**Issue**: Analysis hangs or times out

**Solution**:
- Check API key is valid
- Verify internet connection
- Check logs: `tail -f logs/agent.log`
- Reduce number of papers

---

## 📚 Additional Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **WebSocket Guide**: https://developer.mozilla.org/en-US/docs/Web/API/WebSocket
- **Uvicorn Docs**: https://www.uvicorn.org/

---

## ✅ Testing the UI

### Manual Testing Checklist

- [ ] UI loads at http://localhost:8000/ui
- [ ] Can enter research topic
- [ ] Analysis starts when clicking "Start Analysis"
- [ ] Agent status boxes update in real-time
- [ ] Results display after completion
- [ ] Can ask questions in Q&A section
- [ ] Answers appear in chat interface
- [ ] Metrics show correct values
- [ ] WebSocket reconnects on disconnect

### Automated Testing

```python
# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from src.api import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200

def test_analyze():
    response = client.post("/api/analyze", json={
        "topic": "Test Topic",
        "num_papers": 2,
        "depth": "quick"
    })
    assert response.status_code == 200
```

---

## 🎉 You're Ready!

Your Research Paper Analyzer now has a fully functional web interface!

**Start the server:**
```bash
python src/api.py
```

**Open the UI:**
```
http://localhost:8000/ui
```

**Try it out:**
1. Enter "Quantum Entanglement" as topic
2. Click "Start Analysis"
3. Watch agents work in real-time
4. Ask questions in the Q&A section

**Happy analyzing!** 🔬✨

