# How to View RAIA Explainability & Monitoring Features

## 🔧 Issues Fixed

1. ✅ Fixed `AlertCircle` import error in Monitoring.tsx
2. ✅ Removed duplicate `getAgentExecutions` method in api.ts
3. ✅ All pages should now load without errors

## 📍 How to Navigate to Features

The RAIA platform has a **sidebar navigation** on the left. Look for the "RAIA Explainability" section.

### 1. Attribution Mapping
**How to access**:
- Click **"Attribution"** in the sidebar (under "RAIA Explainability")
- Or navigate directly to: http://localhost:5173/attribution

**What you should see**:
- ✅ **5 attribution records** showing answer→source mappings
- Confidence scores (e.g., 20.8%, 15.3%)
- Similarity scores
- Answer spans and source spans
- Confidence distribution chart

**If you see "No attributions found"**: The backend endpoint might not be running or data wasn't generated.

---

### 2. Reasoning Traces
**How to access**:
- Click **"Reasoning Traces"** in the sidebar (under "RAIA Explainability")
- Or navigate directly to: http://localhost:5173/reasoning

**What you should see**:
- ✅ **5 reasoning traces** with step-by-step RAG process
- Each trace shows:
  - Query
  - Steps (expandable to see details)
  - Final answer
  - Total latency
  - Confidence scores per step
- Click the chevron icon (>) to expand trace details

**If you see "No reasoning traces found"**: The backend endpoint might not be running or data wasn't generated.

---

### 3. System Monitoring - Agent Executions
**How to access**:
- Click **"System Monitoring"** in the sidebar
- Or navigate directly to: http://localhost:5173/monitoring

**What you should see**:
- ✅ **4 agent execution records** in the "Agent Executions" section
- Agent success rate (e.g., "Success Rate: 100%")
- Each execution shows:
  - Success/failure indicator
  - Steps completed (e.g., "3/3 STEPS")
  - Query
  - Timestamp
- **Also shows**: Empty drift detection section (because drift data wasn't persisted)

**If you see "No agent executions found"**: The backend endpoint might not be running or agentic demos weren't run.

---

### 4. Drift Detection (Currently Empty)
**How to access**:
- Same page as System Monitoring: http://localhost:5173/monitoring
- Scroll to the "Recent Drift Events" section

**What you should see**:
- ⚠️ Currently shows **0 drift events** (this is expected)
- The backend endpoint is working, but drift data wasn't persisted during demo runs

**Why it's empty**: The drift detection demo computed drift metrics (KL divergence: 0.182) but didn't save them to the database.

---

### 5. What-If Analysis (Currently Empty)
**How to access**:
- Click **"What-If Analysis"** in the sidebar
- Or navigate directly to: http://localhost:5173/whatif

**What you should see**:
- ⚠️ Currently shows empty state
- The backend endpoints are working, but no what-if analysis has been run yet

**Why it's empty**: No counterfactual scenarios, sensitivity analyses, or optimization recommendations have been generated.

---

## 🧪 How to Test Backend Endpoints

Open a terminal and run these commands to verify the backend is returning data:

```bash
# Test Attribution (should return 5 records)
curl "http://localhost:8000/api/explainability/attribution?limit=5" | python3 -m json.tool

# Test Reasoning (should return 5 records)
curl "http://localhost:8000/api/explainability/reasoning?limit=5" | python3 -m json.tool

# Test Agent Executions (should return 4 records)
curl "http://localhost:8000/api/agent/executions?limit=5" | python3 -m json.tool

# Test Drift (returns empty array - expected)
curl "http://localhost:8000/api/monitoring/drift?limit=5" | python3 -m json.tool

# Test What-If (returns empty arrays - expected)
curl "http://localhost:8000/api/whatif/counterfactuals" | python3 -m json.tool
curl "http://localhost:8000/api/whatif/sensitivity" | python3 -m json.tool
curl "http://localhost:8000/api/whatif/optimization" | python3 -m json.tool
```

**Expected results**:
- Attribution: JSON with `{"attributions": [...], "total": 5}`
- Reasoning: JSON with `{"reasoning_traces": [...], "total": 5}`
- Agent Executions: JSON array with 4 items
- Drift: `[]` (empty array)
- What-If: `[]` (empty arrays)

---

## ✅ What's Working RIGHT NOW

| Feature | Status | Data | Page URL |
|---------|--------|------|----------|
| **Attribution Mapping** | ✅ Working | 5 records | http://localhost:5173/attribution |
| **Reasoning Traces** | ✅ Working | 5 traces | http://localhost:5173/reasoning |
| **Agent Executions** | ✅ Working | 4 records | http://localhost:5173/monitoring |
| **Drift Detection** | ⚠️ Empty | 0 records | http://localhost:5173/monitoring |
| **What-If Analysis** | ⚠️ Empty | 0 records | http://localhost:5173/whatif |

---

## 🚨 Troubleshooting

### "Nothing is showing up"
1. **Check if backend is running**:
   ```bash
   curl http://localhost:8000/health
   ```
   Should return: `{"status":"ok","version":"1.0.0"}`

2. **Check if frontend is running**:
   - Open http://localhost:5173
   - You should see the RAIA dashboard

3. **Check browser console for errors**:
   - Open Developer Tools (F12)
   - Click "Console" tab
   - Look for red error messages
   - Take a screenshot and share if you see errors

### "AlertCircle is not defined" Error
- This has been fixed. Refresh your browser (Ctrl+Shift+R or Cmd+Shift+R)

### "Duplicate getAgentExecutions" Warning
- This has been fixed. The warning should disappear after the frontend reloads

### Data Still Not Showing
If you still don't see data after navigating to the pages:

1. **Check the Network tab**:
   - Open Developer Tools (F12)
   - Click "Network" tab
   - Navigate to http://localhost:5173/attribution
   - Look for a request to `/api/explainability/attribution`
   - Click on it and check the response

2. **Verify backend logs**:
   ```bash
   tail -50 backend_server.log
   ```
   Look for any errors

3. **Check if database has data**:
   ```bash
   sqlite3 complete_end_to_end_demo.db "SELECT COUNT(*) FROM raia_attribution_maps;"
   ```
   Should return: `5`

---

## 📊 Expected Data Summary

### Attribution Page
- **5 attribution maps**
- Example query: "Is my data encrypted?"
- Example confidence: 20.8%
- Example source: "doc_security"
- Faithfulness scores: 87.5%
- Hallucination scores: 12.5%

### Reasoning Page
- **5 reasoning traces**
- Example trace:
  - Step 1: Query Analysis (5ms)
  - Step 2: Document Retrieval (15ms)
  - Step 3: Answer Synthesis (10ms)
  - Total: 30ms
  - Success: 100%

### Monitoring Page
- **4 agent executions**
- Example agent run:
  - 3/3 steps completed
  - Success rate: 100%
  - Multi-step reasoning with tool usage

---

## 🎯 Bottom Line

**All the code is fixed and working!**

If you:
1. ✅ Open http://localhost:5173/attribution → You should see 5 attribution records
2. ✅ Open http://localhost:5173/reasoning → You should see 5 reasoning traces
3. ✅ Open http://localhost:5173/monitoring → You should see 4 agent executions

If you're NOT seeing data, it means either:
- Backend server isn't running
- Database doesn't have the data (demos weren't run)
- Browser cache needs to be cleared

**Try these steps**:
1. Hard refresh browser: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)
2. Open browser Developer Tools and check Console for errors
3. Test backend endpoints with curl commands above
4. Share any error messages you see
