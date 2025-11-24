"""
FastAPI Backend for Research Paper Analyzer Agent

Provides REST API and WebSocket endpoints for the multi-agent system.
Enables real-time communication with agents through web UI.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional, List
import asyncio
import json
from datetime import datetime

# Import our agent system - Fix paths
import sys
from pathlib import Path

# Add project root and src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from agents.orchestrator import ResearchOrchestrator
from observability.logger import get_logger

logger = get_logger(__name__)

# FastAPI app
app = FastAPI(
    title="Research Paper Analyzer API",
    description="Multi-agent system for research paper analysis",
    version="1.0.0"
)

# Enable CORS for web UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active sessions
active_sessions = {}
active_orchestrators = {}


# Request/Response Models
class AnalysisRequest(BaseModel):
    topic: str
    num_papers: int = 10
    depth: str = "standard"  # quick, standard, comprehensive
    session_id: Optional[str] = None


class QuestionRequest(BaseModel):
    session_id: str
    question: str


class AnalysisResponse(BaseModel):
    session_id: str
    status: str
    message: str
    papers_analyzed: Optional[int] = None
    summary: Optional[str] = None
    key_findings: Optional[List[str]] = None
    research_gaps: Optional[List[str]] = None


class QuestionResponse(BaseModel):
    answer: str
    session_id: str


# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"WebSocket connected: {client_id}")
    
    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"WebSocket disconnected: {client_id}")
    
    async def send_message(self, client_id: str, message: dict):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json(message)
    
    async def send_status(self, client_id: str, status: str, details: str):
        await self.send_message(client_id, {
            "type": "status",
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })


manager = ConnectionManager()


# API Endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Research Paper Analyzer API",
        "version": "1.0.0",
        "docs": "/docs",
        "ui": "/ui"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_sessions": len(active_sessions)
    }


@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_papers(request: AnalysisRequest):
    """
    Analyze research papers on a given topic
    
    This endpoint initiates the multi-agent analysis pipeline.
    """
    try:
        logger.info(f"Analysis request: {request.topic}")
        
        # Create orchestrator
        orchestrator = ResearchOrchestrator(session_id=request.session_id)
        session_id = orchestrator.get_session_id()
        
        # Store for later access
        active_orchestrators[session_id] = orchestrator
        
        # Run analysis
        result = await orchestrator.analyze_topic(
            topic=request.topic,
            num_papers=request.num_papers,
            depth=request.depth
        )
        
        # Store session
        active_sessions[session_id] = {
            "topic": request.topic,
            "created_at": datetime.now().isoformat(),
            "result": result
        }
        
        return AnalysisResponse(
            session_id=session_id,
            status="completed",
            message="Analysis completed successfully",
            papers_analyzed=result.papers_analyzed,
            summary=result.summary,
            key_findings=result.key_findings,
            research_gaps=result.research_gaps
        )
    
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/question", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """
    Ask a question about analyzed papers
    
    Requires a valid session_id from a previous analysis.
    """
    try:
        if request.session_id not in active_orchestrators:
            raise HTTPException(
                status_code=404,
                detail="Session not found. Please run analysis first."
            )
        
        orchestrator = active_orchestrators[request.session_id]
        qa_agent = orchestrator.get_qa_agent()
        
        if not qa_agent:
            raise HTTPException(
                status_code=400,
                detail="No analysis data available. Please run analysis first."
            )
        
        answer = await qa_agent.ask(request.question)
        
        return QuestionResponse(
            answer=answer,
            session_id=request.session_id
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Question error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sessions")
async def list_sessions():
    """List all active sessions"""
    return {
        "sessions": [
            {
                "session_id": sid,
                "topic": data["topic"],
                "created_at": data["created_at"],
                "papers_analyzed": data["result"].papers_analyzed
            }
            for sid, data in active_sessions.items()
        ]
    }


@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    """Get details of a specific session"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    data = active_sessions[session_id]
    result = data["result"]
    
    return {
        "session_id": session_id,
        "topic": data["topic"],
        "created_at": data["created_at"],
        "papers_analyzed": result.papers_analyzed,
        "summary": result.summary,
        "key_findings": result.key_findings,
        "research_gaps": result.research_gaps,
        "cross_references": result.cross_references,
        "synthesis_report": result.synthesis_report
    }


# WebSocket endpoint for real-time updates
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """
    WebSocket endpoint for real-time agent communication
    
    Sends status updates during analysis pipeline execution.
    """
    await manager.connect(websocket, client_id)
    
    try:
        logger.info(f"WebSocket loop started for {client_id}")
        while True:
            # Receive messages from client
            logger.debug(f"Waiting for message from {client_id}...")
            try:
                data = await websocket.receive_json()
                logger.info(f"✅ Received from {client_id}: {data.get('action')}")
            except WebSocketDisconnect as e:
                logger.info(f"🔴 Client {client_id} disconnected during receive: {e}")
                break
            except Exception as e:
                logger.error(f"❌ Error receiving data from {client_id}: {str(e)}")
                # Only break on actual disconnect errors
                if "disconnect" in str(e).lower() or "closed" in str(e).lower():
                    logger.info(f"Connection error detected, breaking loop")
                    break
                # For other errors, try to continue
                logger.info(f"Non-fatal error, continuing...")
                continue
            
            if data.get("action") == "analyze":
                # Start analysis with real-time updates
                await manager.send_status(
                    client_id,
                    "started",
                    "Initializing multi-agent system..."
                )
                
                try:
                    # Create orchestrator
                    orchestrator = ResearchOrchestrator()
                    session_id = orchestrator.get_session_id()
                    
                    await manager.send_status(
                        client_id,
                        "retrieving",
                        "Retrieval Agent searching for papers..."
                    )
                    
                    # Run analysis
                    result = await orchestrator.analyze_topic(
                        topic=data.get("topic"),
                        num_papers=data.get("num_papers", 10),
                        depth=data.get("depth", "standard")
                    )
                    
                    await manager.send_status(
                        client_id,
                        "summarizing",
                        f"Summary Agents processing {result.papers_analyzed} papers..."
                    )
                    
                    await manager.send_status(
                        client_id,
                        "cross_referencing",
                        "Cross-Reference Agent analyzing connections..."
                    )
                    
                    await manager.send_status(
                        client_id,
                        "synthesizing",
                        "Synthesis Agent creating comprehensive report..."
                    )
                    
                    # Store session
                    active_orchestrators[session_id] = orchestrator
                    active_sessions[session_id] = {
                        "topic": data.get("topic"),
                        "created_at": datetime.now().isoformat(),
                        "result": result
                    }
                    
                    # Send complete result
                    await manager.send_message(client_id, {
                        "type": "result",
                        "session_id": session_id,
                        "status": "completed",
                        "data": {
                            "papers_analyzed": result.papers_analyzed,
                            "summary": result.summary,
                            "key_findings": result.key_findings,
                            "research_gaps": result.research_gaps,
                            "papers": [
                                {
                                    "title": paper.get("title", "Untitled"),
                                    "authors": paper.get("authors", "Unknown"),
                                    "url": paper.get("url", "")
                                }
                                for paper in (result.metadata.get("papers", []) if result.metadata else [])
                            ]
                        }
                    })
                    
                    logger.info(f"Analysis complete for session {session_id}, keeping connection open for Q&A")
                
                except Exception as e:
                    logger.error(f"Analysis error: {str(e)}", exc_info=True)
                    await manager.send_message(client_id, {
                        "type": "error",
                        "message": str(e)
                    })
                
                # ✅ Continue loop to keep connection alive for Q&A
                continue
            
            elif data.get("action") == "question":
                # Handle Q&A
                session_id = data.get("session_id")
                question = data.get("question")
                
                logger.info(f"Q&A request - Session: {session_id}, Question: {question[:50]}...")
                
                if not session_id:
                    await manager.send_message(client_id, {
                        "type": "error",
                        "message": "Session ID is required for Q&A"
                    })
                    continue
                
                if not question:
                    await manager.send_message(client_id, {
                        "type": "error",
                        "message": "Question is required"
                    })
                    continue
                
                if session_id not in active_orchestrators:
                    await manager.send_message(client_id, {
                        "type": "error",
                        "message": "Session not found. Please run an analysis first."
                    })
                    continue
                
                try:
                    orchestrator = active_orchestrators[session_id]
                    qa_agent = orchestrator.get_qa_agent()
                    
                    if not qa_agent:
                        await manager.send_message(client_id, {
                            "type": "error",
                            "message": "Q&A agent not available. Please run an analysis first."
                        })
                        continue
                    
                    # Send processing status
                    await manager.send_status(
                        client_id,
                        "processing",
                        "Q&A Agent processing your question..."
                    )
                    
                    # Get answer
                    answer = await qa_agent.ask(question)
                    
                    # Send answer
                    await manager.send_message(client_id, {
                        "type": "answer",
                        "question": question,
                        "answer": answer,
                        "session_id": session_id
                    })
                    
                    logger.info("Q&A response sent successfully")
                    
                except Exception as e:
                    logger.error(f"Q&A error: {str(e)}", exc_info=True)
                    await manager.send_message(client_id, {
                        "type": "error",
                        "message": f"Error processing question: {str(e)}"
                    })
                
                # ✅ Continue loop to allow more questions
                continue
            
            else:
                # Unknown action
                logger.warning(f"Unknown action from {client_id}: {data.get('action')}")
                await manager.send_message(client_id, {
                    "type": "error",
                    "message": f"Unknown action: {data.get('action')}"
                })
                continue
    
    except WebSocketDisconnect:
        manager.disconnect(client_id)
        logger.info(f"Client {client_id} disconnected normally")
    except Exception as e:
        logger.error(f"WebSocket error for {client_id}: {str(e)}", exc_info=True)
        try:
            await manager.send_message(client_id, {
                "type": "error",
                "message": f"WebSocket error: {str(e)}"
            })
        except:
            pass
        manager.disconnect(client_id)


# Serve static files (UI)
try:
    app.mount("/ui", StaticFiles(directory="ui", html=True), name="ui")
except:
    logger.warning("UI directory not found. UI will not be available.")


if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting Research Paper Analyzer API...")
    print("📍 API: http://localhost:8000")
    print("📍 Docs: http://localhost:8000/docs")
    print("📍 UI: http://localhost:8000/ui")
    print()
    
    # Run from project root for proper path resolution
    import os
    os.chdir(Path(__file__).parent.parent)
    
    uvicorn.run(
        "src.api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

