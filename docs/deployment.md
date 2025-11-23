# Deployment Guide

## Deployment Options

This guide covers multiple deployment options for the Research Paper Analyzer Agent.

## Option 1: Local Development

### Prerequisites
- Python 3.10+
- Google API Key for Gemini

### Steps

1. **Clone the repository**
```bash
cd /Users/thegde/learning/sai-kumar-projects/research-paper-analyzer-agent
```

2. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set environment variables**
```bash
export GOOGLE_API_KEY="your_api_key_here"
export LOG_LEVEL="INFO"
```

5. **Run the application**
```bash
python src/main.py
```

## Option 2: Docker Deployment

### Create Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run application
CMD ["python", "src/main.py"]
```

### Build and Run

```bash
# Build image
docker build -t research-analyzer .

# Run container
docker run -e GOOGLE_API_KEY="your_key" research-analyzer
```

## Option 3: Google Cloud Run

### Prerequisites
- Google Cloud account
- `gcloud` CLI installed
- Docker installed

### Steps

1. **Create Dockerfile** (see above)

2. **Build and push to Container Registry**
```bash
# Set project
gcloud config set project YOUR_PROJECT_ID

# Build and push
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/research-analyzer

# Deploy to Cloud Run
gcloud run deploy research-analyzer \
  --image gcr.io/YOUR_PROJECT_ID/research-analyzer \
  --platform managed \
  --region us-central1 \
  --set-env-vars GOOGLE_API_KEY=your_key \
  --allow-unauthenticated \
  --memory 2Gi \
  --timeout 300
```

3. **Access the service**
```bash
# Get service URL
gcloud run services describe research-analyzer --region us-central1
```

## Option 4: Vertex AI Agent Engine

### Prerequisites
- Google Cloud project with Vertex AI enabled
- Agent Engine access

### Steps

1. **Prepare agent configuration**
```yaml
# agent_config.yaml
name: research-paper-analyzer
description: Multi-agent system for research paper analysis
runtime: python310
model: gemini-1.5-pro

agents:
  - name: orchestrator
    type: coordinator
  - name: retrieval
    type: worker
  - name: summary
    type: worker
    parallel: 5
  - name: cross_reference
    type: worker
  - name: synthesis
    type: worker
  - name: qa
    type: interactive
```

2. **Deploy to Agent Engine**
```bash
# Create agent
gcloud alpha vertex-ai agents create research-analyzer \
  --config agent_config.yaml \
  --region us-central1

# Deploy agent
gcloud alpha vertex-ai agents deploy research-analyzer \
  --region us-central1
```

3. **Invoke agent**
```python
from google.cloud import aiplatform

client = aiplatform.gapic.AgentServiceClient()

response = client.invoke_agent(
    agent="projects/YOUR_PROJECT/locations/us-central1/agents/research-analyzer",
    query="Analyze papers on transformers"
)
```

## Option 5: Kubernetes Deployment

### Prerequisites
- Kubernetes cluster
- kubectl configured
- Container image pushed to registry

### Create Kubernetes Manifests

**deployment.yaml**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: research-analyzer
spec:
  replicas: 2
  selector:
    matchLabels:
      app: research-analyzer
  template:
    metadata:
      labels:
        app: research-analyzer
    spec:
      containers:
      - name: agent
        image: gcr.io/YOUR_PROJECT/research-analyzer:latest
        env:
        - name: GOOGLE_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: google-api-key
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        ports:
        - containerPort: 8080
```

**service.yaml**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: research-analyzer
spec:
  selector:
    app: research-analyzer
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8080
  type: LoadBalancer
```

**secret.yaml**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: api-keys
type: Opaque
data:
  google-api-key: <base64-encoded-key>
```

### Deploy

```bash
# Create secret
kubectl apply -f secret.yaml

# Deploy application
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml

# Check status
kubectl get pods
kubectl get services
```

## Environment Variables

### Required
- `GOOGLE_API_KEY`: Gemini API key

### Optional
- `LLM_MODEL`: Model name (default: gemini-1.5-pro)
- `LLM_TEMPERATURE`: Temperature (default: 0.7)
- `MAX_PARALLEL_AGENTS`: Max parallel agents (default: 5)
- `LOG_LEVEL`: Logging level (default: INFO)
- `MEMORY_BACKEND`: Memory backend (default: in_memory)

## Production Considerations

### 1. Secrets Management

**Never hardcode API keys!** Use:
- Google Secret Manager
- Kubernetes Secrets
- Environment variables
- Cloud Run secrets

### 2. Scaling

**Horizontal Scaling:**
- Multiple instances behind load balancer
- Shared Redis for sessions
- Shared ChromaDB for memory

**Vertical Scaling:**
- Increase memory/CPU per instance
- Adjust based on paper volume

### 3. Monitoring

**Set up:**
- Cloud Monitoring / Prometheus
- Alert on errors
- Track response times
- Monitor costs

**Key Metrics:**
- Request rate
- Error rate
- Latency (p50, p95, p99)
- Cost per request

### 4. Caching

**Implement caching for:**
- Paper metadata
- arXiv responses
- Frequently requested analyses

**Options:**
- Redis
- Memcached
- Cloud CDN

### 5. Rate Limiting

**Protect against:**
- API abuse
- Cost overruns
- Quota exhaustion

**Implementation:**
```python
from ratelimit import limits, sleep_and_retry

@sleep_and_retry
@limits(calls=60, period=60)
def call_api():
    # Your API call
    pass
```

### 6. Error Handling

**Implement:**
- Retry logic with exponential backoff
- Circuit breakers
- Graceful degradation
- Error reporting (Sentry, Cloud Error Reporting)

### 7. Cost Optimization

**Strategies:**
- Use appropriate model sizes
- Implement response caching
- Batch LLM requests
- Monitor token usage
- Set spending limits

## Health Checks

### Add health endpoint

```python
# src/api/health.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/ready")
async def readiness_check():
    # Check dependencies
    return {"status": "ready"}
```

## Backup and Recovery

### Session Backup
- Regular dumps of session data
- Store in Cloud Storage/S3
- Implement restore mechanism

### Memory Backup
- Export memory bank periodically
- Store embeddings separately
- Test restore process

## Security Checklist

- [ ] API keys stored in secrets manager
- [ ] HTTPS/TLS enabled
- [ ] Authentication implemented
- [ ] Rate limiting configured
- [ ] Input validation in place
- [ ] Output sanitization enabled
- [ ] Logging (no sensitive data)
- [ ] Regular security updates
- [ ] Access control configured
- [ ] Audit logging enabled

## Performance Tuning

### Profile your application
```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Your code here

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)
```

### Optimize hot paths
- Cache expensive operations
- Use async/await properly
- Minimize LLM calls
- Batch where possible

## Troubleshooting

### Common Issues

**1. Out of Memory**
- Increase instance memory
- Implement memory limits
- Clear old sessions

**2. Slow Response**
- Check parallel agent count
- Verify network latency
- Profile slow operations

**3. API Quota Exceeded**
- Implement caching
- Add rate limiting
- Use exponential backoff

**4. High Costs**
- Monitor token usage
- Optimize prompts
- Use smaller models for simple tasks

## Support

For deployment issues:
1. Check logs: `kubectl logs <pod-name>`
2. Check metrics: Cloud Console
3. Review documentation
4. Open GitHub issue

## Next Steps

After deployment:
1. Monitor metrics
2. Set up alerts
3. Test load
4. Optimize costs
5. Implement backups
6. Document runbooks

