# An LLM-Based Self-Healing Framework for Reliable Multi-Step Task Automation

A resilient, multi-step autonomous AI agent framework designed to execute automated multi-step workflows, detect runtime exceptions, diagnose root causes with Google Gemini, dynamically select recovery strategies, learn from historical failures via episodic memory, and verify intermediate states with calibrated confidence scoring.

---

## 1. System Architecture

```
selfhealing AI/
├── backend/
│   ├── app/
│   │   ├── config.py              # Configuration & runtime settings
│   │   ├── database.py            # SQLite database & session management
│   │   ├── logging_config.py      # Unified structured logging
│   │   ├── main.py                # FastAPI app entry point & static file serving
│   │   ├── api/
│   │   │   └── routes.py          # REST API endpoints (tasks, recovery, memory, etc.)
│   │   ├── core/
│   │   │   ├── task_planner.py        # Gemini-powered task decomposition & dependency graph
│   │   │   ├── task_executor.py       # Multi-step stateful execution engine
│   │   │   ├── failure_detector.py    # Runtime exception classifier & inspector
│   │   │   ├── error_diagnoser.py     # Feature 1: Root-cause diagnosis with Gemini
│   │   │   ├── recovery_planner.py    # Feature 1: Strategy selector (Retry, Arg Adapt, Replan, Stop)
│   │   │   ├── recovery_validator.py  # Feature 1: Safety validation & infinite loop prevention
│   │   │   ├── memory_manager.py      # Feature 2: Episodic memory & similarity retrieval
│   │   │   ├── dynamic_replanner.py   # Feature 3: Dynamic replanning preserving completed state
│   │   │   ├── confidence_verifier.py # Feature 4: Heuristic & calibrated confidence verification
│   │   │   └── failure_predictor.py   # Feature 5: Mathematical failure pattern prediction
│   │   ├── gemini/
│   │   │   └── client.py          # Google Gemini 2.5/1.5 API client with structured JSON
│   │   ├── models/
│   │   │   ├── db_models.py       # SQLAlchemy ORM schemas
│   │   │   └── schemas.py         # Pydantic request/response models
│   │   └── tools/
│   │       └── registry.py        # Secure sandbox tool registry & AST calculator
│   ├── tests/                     # 26 Pytest unit, API & end-to-end self-healing tests
│   ├── requirements.txt
│   └── run.py
├── frontend/
│   ├── src/
│   │   ├── api/client.js          # API client for FastAPI backend
│   │   ├── components/            # Sidebar, Header, StatusBadge, RiskIndicator
│   │   ├── pages/                 # 7 Comprehensive Dark-Themed Dashboard Pages
│   │   │   ├── Dashboard.jsx
│   │   │   ├── TaskExecution.jsx
│   │   │   ├── RecoveryMonitoring.jsx
│   │   │   ├── MemoryManagement.jsx
│   │   │   ├── FailurePrediction.jsx
│   │   │   ├── TaskHistory.jsx
│   │   │   └── Settings.jsx
│   │   ├── App.jsx
│   │   └── index.css              # Dark neon/slate design system
│   ├── package.json
│   └── vite.config.js
├── .env.example
├── start.bat                      # Windows double-click batch launcher
├── start.ps1                      # Windows PowerShell launcher
└── README.md
```

---

## 2. Five Main Research Features

### Feature 1: Intelligent Recovery Strategy Selection
- **Failure Categorization**: Detects exceptions and classifies them into `PARAMETER_ERROR`, `TRANSIENT_NETWORK`, `RESOURCE_UNAVAILABLE`, `SAFETY_VIOLATION`, or `TOOL_EXECUTION_FAILURE`.
- **Gemini Root-Cause Diagnosis**: Prompts Gemini with step context, arguments, and error traces to produce structured JSON root causes.
- **Four Recovery Strategies**:
  1. `RETRY`: For transient network hiccups, using exponential backoff.
  2. `CHANGE_ARGUMENTS`: For parameter validation errors (e.g. division by zero, malformed payload), correcting arguments before re-execution.
  3. `REPLAN`: Replaces failing subtasks with alternative tools while preserving completed steps.
  4. `STOP`: Enforces safety halting if policy limits or malicious parameters are detected.
- **Recovery Validator**: Enforces max retry bounds, prevents repeat execution of known failed strategies, and screens arguments for path traversal or command injection.

### Feature 2: Learning from Past Failures
- **Episodic Memory Storage**: Persistent dual storage in SQLite (`episodic_memories`) and JSON (`episodic_memory.json`).
- **Similarity Scoring**: Calculates a transparent similarity metric combining tool matching, error category, error text Jaccard overlap, and task description overlap:
  $$\text{Similarity} = 0.30 \cdot M_{\text{tool}} + 0.25 \cdot M_{\text{cat}} + 0.30 \cdot J(\text{error}) + 0.15 \cdot J(\text{task})$$
- **Prompt Injection & Avoidance**: Retrieves past similar experiences before diagnosing, injecting what worked and explicitly instructing Gemini to avoid strategies that previously failed for this error pattern.

### Feature 3: Dynamic Task Re-planning
- **Subtask Decomposition**: Breaks user tasks into 2 to 5 discrete steps with explicit dependency links (`step_0`, `step_1`).
- **Result Preservation**: When Step $k$ fails, steps $0 \dots k-1$ and their outputs are frozen and preserved.
- **Dynamic Replanning**: Gemini generates replacement steps starting from the current state, replacing the broken subtask with alternative tools (e.g. failing API gateway replaced by mock knowledge search and synthesizer).
- **Loop Prevention**: Strictly caps task replans to `MAX_REPLAN_ATTEMPTS = 2`.

### Feature 4: Confidence-Based Verification
- **Output Inspection**: Verifies output of every step before advancing execution.
- **Heuristic vs Calibrated Distinction**:
  - **Heuristic Confidence**: Deterministic score based on schema compliance, non-emptiness, and absence of error indicators.
  - **Calibrated Empirical Probability**: Historical success likelihood estimated from past episodic memory using Laplace smoothing:
    $$P_{\text{calibrated}} = \frac{N_{\text{success}} + 1}{N_{\text{total}} + 2}$$
- **Threshold Rejection**: Combined score below `CONFIDENCE_THRESHOLD = 0.65` rejects output and triggers self-healing error diagnosis.

### Feature 5: Failure Pattern Prediction
- **Pre-Execution Vulnerability Analysis**: Evaluates proposed task steps *before* execution against historical tool failure rates and parameter volatility.
- **Mathematical Risk Formula**:
  $$\text{RiskScore} = \text{clamp}\left(\max_{i} \left[ 0.50 \cdot R_{\text{tool}}(T_i) + V_{\text{param}}(A_i) \right] + 0.05 \cdot (N_{\text{steps}} - 2), 0.0, 1.0\right)$$
- **Risk Categorization**: `LOW` (< 0.35), `MEDIUM` (0.35 - 0.70), `HIGH` (≥ 0.70).
- **Preventive Recommendations**: Provides actionable pre-execution recommendations.
- **Accuracy Evaluation**: Compares predicted risk against actual execution outcomes to measure empirical calibration.

---

## 3. Technology Stack

- **Frontend**: React 18, Vite, Lucide Icons, Custom Dark Neon/Slate CSS Design System.
- **Backend**: Python 3.13, FastAPI, Pydantic v2, SQLAlchemy, Uvicorn.
- **AI**: Google Gemini API (`google-genai` SDK / `gemini-2.5-flash`), Structured JSON Output, Deterministic Fallback Mode for offline reliability.
- **Storage**: SQLite (`self_healing_ai.db`), JSON episodic memory (`episodic_memory.json`).
- **Testing**: Pytest, Pytest-Asyncio, HTTPX (26 automated test cases).

---

## 4. Setup & Running Locally on Windows

### Prerequisites
- Python 3.10+ (Python 3.13 tested)
- Node.js v18+ (Node v24 tested) & npm

### Quick Start (One-Click)

**Using Batch File:**
```cmd
start.bat
```

**Using PowerShell:**
```powershell
.\start.ps1
```

---

### Manual Step-by-Step Execution

#### 1. Setup Backend
```powershell
# Create & activate virtual environment (already created in venv/)
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r backend\requirements.txt

# Configure environment variables (optional, or configure via UI Settings)
Copy-Item .env.example .env

# Run backend server
cd backend
python run.py
```
Backend will be live at: **`http://127.0.0.1:8000`**
Swagger Interactive API Docs: **`http://127.0.0.1:8000/docs`**

#### 2. Setup Frontend
```powershell
cd frontend
npm install
npm run dev
```
Frontend dashboard will be live at: **`http://localhost:5173`**

---

## 5. Google Gemini API Configuration

1. Get your free API key from [Google AI Studio](https://aistudio.google.com/).
2. You can configure it either:
   - **Through the UI**: Navigate to **Settings** in the dashboard, enter your key, and click **Save Runtime Settings**.
   - **Through `.env` file**:
     ```env
     GEMINI_API_KEY=your_actual_key_here
     GEMINI_MODEL=gemini-2.5-flash
     ```
3. *Note*: If no API key is provided, the framework operates in an intelligent, deterministic local simulation mode so all 26 automated tests, self-healing demonstrations, and UI pages function smoothly offline.

---

## 6. Running Automated Tests

Run the complete test suite (26 tests covering all 5 features):
```powershell
cd backend
..\venv\Scripts\pytest.exe -v
```

Test Results Breakdown:
- `test_failure_detector.py`: 4 tests (parameter errors, network timeouts, resource missing, safety violations).
- `test_recovery.py`: 4 tests (retry limits, avoiding failed strategies, path traversal detection, strategy selection).
- `test_memory.py`: 3 tests (similarity calculation, separating success/failure memories, experience recording).
- `test_dynamic_replan.py`: 2 tests (state preservation of completed steps, replan bound enforcement).
- `test_confidence_verifier.py`: 3 tests (heuristic scoring, calibrated probability, threshold rejection).
- `test_failure_predictor.py`: 3 tests (high-risk parameter detection, benign prediction, accuracy evaluation).
- `test_api.py`: 5 tests (health check, settings update, memories query, dashboard stats, task execution).
- `test_e2e_healing.py`: 2 tests (end-to-end self-healing for division by zero fault and service failover replan).

---

## 7. REST API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Health check & Gemini status |
| `GET` | `/api/dashboard/stats` | KPI metrics, recovery success rate, risk distribution |
| `POST` | `/api/tasks` | Decomposes task into steps and predicts failure risk |
| `POST` | `/api/tasks/{task_id}/execute` | Executes task with autonomous self-healing |
| `GET` | `/api/tasks/{task_id}` | Retrieves full task details, steps, recoveries, verifications |
| `GET` | `/api/tasks` | Lists historical tasks with status filters |
| `GET` | `/api/recovery/history` | Telemetry of all recovery attempts, diagnoses, and actions |
| `GET` | `/api/memories` | Retrieves episodic memory with type & text search |
| `GET` | `/api/predictions` | Audit log of pre-execution risk predictions & accuracy |
| `GET` | `/api/settings` | Returns runtime configuration & allowed tools |
| `POST` | `/api/settings` | Updates Gemini key, model, retry limits, and thresholds |

---

## 8. Security & Sandbox Allowlist

- **API Key Safety**: API keys are strictly confined to backend memory/environment variables and are never emitted in browser responses.
- **Tool Allowlist**: Tools must be explicitly registered in `ALLOWED_TOOLS` (`calculator`, `web_search_mock`, `text_summarizer`, `json_validator`, `data_transformer`, `http_client_mock`, `file_sandbox_reader`, `file_sandbox_writer`).
- **File Sandbox Protection**: All file read/write operations are confined to `sandbox_storage/`. Path traversal (`..`, `/`, `\`) is blocked with `PermissionError`.
- **Safe Calculator**: Evaluates arithmetic through AST parsing rather than raw `eval()`.
- **Loop Bounding**: Enforces `MAX_RECOVERY_ATTEMPTS = 3` and `MAX_REPLAN_ATTEMPTS = 2`.
