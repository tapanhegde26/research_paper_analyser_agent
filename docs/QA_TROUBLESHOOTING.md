# Q&A Feature Troubleshooting Guide

## Overview
This guide helps diagnose and fix issues with the Interactive Q&A feature in the Research Paper Analyzer.

---

## Common Issues & Solutions

### 1. **WebSocket Connection Closes After Analysis**

#### Symptoms:
- Analysis completes successfully
- Unable to ask questions afterward
- "Connection lost" or "Session not found" errors

#### Root Cause:
- WebSocket connection was closing prematurely
- Error handling was causing connection drops

#### Solution (FIXED):
✅ **Backend (api.py)**:
- Added proper exception handling in WebSocket endpoint
- Improved error recovery without closing connection
- Added `continue` statements to keep connection alive after errors
- Better logging for debugging

✅ **Frontend (index.html)**:
- Added automatic reconnection logic
- Better validation before sending Q&A requests
- Connection state checking before sending messages
- Clear error messages for users

#### Test:
```bash
# Terminal 1: Start server
cd research-paper-analyzer-agent
./start_ui.sh

# Terminal 2: Check logs
tail -f logs/agent_system.log

# Browser: Open http://localhost:8000/ui
# 1. Run analysis
# 2. Wait for completion
# 3. Try asking multiple questions
```

---

### 2. **"Session not found" Error**

#### Symptoms:
- Error message: "Session not found. Please run an analysis first."
- Q&A button doesn't work

#### Causes:
1. Analysis hasn't been run yet
2. Server restarted (sessions are in-memory)
3. Session ID not captured properly

#### Solutions:

**For Users:**
1. Run a new analysis first
2. Wait for "Analysis complete!" status
3. Then ask questions

**For Developers:**
```python
# Check active sessions
curl http://localhost:8000/api/sessions

# Response should show active sessions:
{
  "sessions": [
    {
      "session_id": "abc123",
      "topic": "Quantum Physics",
      "created_at": "2025-11-24T...",
      "papers_analyzed": 10
    }
  ]
}
```

---

### 3. **"Q&A agent not available" Error**

#### Symptoms:
- Session exists but Q&A fails
- Error: "Q&A agent not available"

#### Cause:
- QA Agent is only initialized after successful analysis
- Analysis may have failed or incomplete

#### Solution:
1. Check analysis completed successfully
2. Look for "Analysis complete" in status panel
3. Verify papers were retrieved and analyzed
4. If needed, run analysis again

---

### 4. **WebSocket Disconnects Randomly**

#### Symptoms:
- Connection drops during use
- "Disconnected from server" message

#### Causes:
1. Network issues
2. Server overload
3. Long-running operations timing out

#### Solutions:

**Automatic Reconnection (IMPLEMENTED):**
```javascript
// UI automatically reconnects after 3 seconds
ws.onclose = (event) => {
    if (!event.wasClean) {
        setTimeout(() => {
            initWebSocket();
        }, 3000);
    }
};
```

**Manual Fix:**
- Refresh the browser page
- Check server is still running
- Restart server if needed

---

### 5. **Questions Take Too Long / Timeout**

#### Symptoms:
- Question sent but no response
- Loading indefinitely

#### Causes:
1. Large context in memory bank
2. Complex question requiring extensive processing
3. Gemini API rate limits

#### Solutions:

**Backend Optimization:**
```python
# In qa_agent.py - reduce context
answer = await qa_agent.ask(
    question=question,
    context_limit=3  # Reduced from 5
)
```

**Check API Logs:**
```bash
# Look for errors or timeouts
grep "Q&A" logs/agent_system.log
grep "ERROR" logs/agent_system.log
```

---

## Validation Checklist

Before asking questions, ensure:

- [ ] ✅ WebSocket status shows "Connected"
- [ ] ✅ Analysis has been run and completed
- [ ] ✅ "Analysis complete!" message appears
- [ ] ✅ Results are displayed (summary, findings, gaps)
- [ ] ✅ Session ID is captured (check browser console)
- [ ] ✅ Question input field is enabled

---

## Debugging Steps

### 1. **Browser Console Debugging**

Open browser DevTools (F12) and check:

```javascript
// Check WebSocket state
console.log(ws.readyState); 
// 0 = CONNECTING, 1 = OPEN, 2 = CLOSING, 3 = CLOSED

// Check current session
console.log(currentSessionId); 
// Should show a UUID after analysis

// Monitor messages
// Watch for "Received:" and "Sending:" logs
```

### 2. **Server-Side Debugging**

Check server logs for Q&A flow:

```bash
# Real-time log monitoring
tail -f logs/agent_system.log | grep -E "Q&A|WebSocket|ERROR"

# Expected flow:
# [INFO] Q&A request - Session: <id>, Question: <question>
# [INFO] Q&A question: <question>
# [INFO] Q&A answer generated
# [INFO] Q&A response sent successfully
```

### 3. **Network Debugging**

Check WebSocket traffic in Browser DevTools:

1. Open **Network** tab
2. Filter by **WS** (WebSocket)
3. Click on the WebSocket connection
4. View **Messages** tab
5. Verify messages are being sent/received

---

## API Testing

Test Q&A independently using REST API:

```bash
# 1. Run analysis
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Quantum Physics",
    "num_papers": 5,
    "depth": "standard"
  }'

# Response includes session_id

# 2. Ask question
curl -X POST http://localhost:8000/api/question \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "<session_id_from_step_1>",
    "question": "What are the main findings?"
  }'

# Should return answer
```

---

## Recent Fixes (v1.1)

### Backend Improvements:
1. ✅ Enhanced error handling in WebSocket endpoint
2. ✅ Added validation for session_id and question
3. ✅ Improved logging for Q&A flow
4. ✅ Added "continue" statements to prevent connection closure
5. ✅ Better exception catching and recovery

### Frontend Improvements:
1. ✅ Automatic reconnection on disconnect
2. ✅ Input validation before sending requests
3. ✅ Connection state checking
4. ✅ Better error messages with actionable guidance
5. ✅ Improved Q&A UI with formatted answers
6. ✅ Clear visual feedback for all states

---

## Performance Tips

### For Faster Q&A:
1. Use `depth: "quick"` for initial analysis
2. Analyze fewer papers (5-10 instead of 20+)
3. Keep questions specific and focused
4. Use shorter, more direct phrasing

### For Better Answers:
1. Use `depth: "comprehensive"` analysis
2. Analyze more papers (15-20)
3. Ask specific, detailed questions
4. Reference particular aspects from the summary

---

## Known Limitations

1. **In-Memory Sessions**: Sessions are lost on server restart
2. **No Persistence**: Q&A history not saved between sessions
3. **Context Window**: Limited by Gemini API context size
4. **Rate Limits**: Subject to Google API quotas

---

## Future Enhancements

Planned improvements:
- [ ] Persistent session storage (Redis/Database)
- [ ] Q&A history export
- [ ] Multi-turn conversation context
- [ ] Streaming responses for real-time feedback
- [ ] Citation links in Q&A answers
- [ ] Voice input for questions
- [ ] Answer quality ratings

---

## Getting Help

If issues persist:

1. **Check Logs**: `logs/agent_system.log`
2. **Restart Server**: `./start_ui.sh`
3. **Clear Browser Cache**: Hard refresh (Ctrl+Shift+R)
4. **Test REST API**: Use curl commands above
5. **Check Console**: Look for JavaScript errors

For bug reports, include:
- Browser console logs
- Server logs (last 50 lines)
- Steps to reproduce
- Expected vs actual behavior

---

## Success Indicators

Q&A is working correctly when:

✅ WebSocket stays connected throughout session  
✅ Multiple questions can be asked sequentially  
✅ Answers appear within 3-10 seconds  
✅ Answers are relevant to analyzed papers  
✅ No connection drops between questions  
✅ Clear status updates for each action  

Happy questioning! 🎉

