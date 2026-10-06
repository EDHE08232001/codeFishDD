# CODFISH — Quantum Reef

A colorful pixel-art learning game about quantum noise and error mitigation. Built with React, Python/FastAPI, and a Qiskit IBM Runtime adapter.

![CODFISH cover](docs/cover.png)
![Focused mission](docs/mission.png)

## Current version

- Six scenario questions with three answer choices, hints, completion checks, and session progress.
- A separate toolkit for exploring each mini-game.
- ZNE: backend-generated teaching measurements, linear/exponential extrapolation, and an optional IBM hardware adapter.
- DD, Pauli twirling, readout mitigation, PEC, and noise learning: simplified local concept activities.

**IBM hardware integration is not yet verified with a real job. The five other activities do not currently use IBM data.** QML is not implemented. Mission progress resets on refresh. Do not present synthetic teaching data as hardware measurements.

## Run locally

Prerequisites: Python 3.12+ and Node.js 22.12+.

From this directory in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
npm.cmd --prefix frontend ci
.\start-local.ps1
```

Open the `Ready:` URL printed by the launcher. Ports default to 8000/5173 and automatically advance if occupied. Logs are saved in `.local/`. The launcher prints process IDs and a stop command.

Alternatively run two terminals:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

```powershell
cd frontend
npm.cmd run dev
```

## IBM credentials

Set these in your local PowerShell before starting the services. Keep credentials out of Git and out of the browser.

```powershell
$env:IBM_ENABLE = 'true'
$env:IBM_QUANTUM_TOKEN = '<your API key>'
$env:IBM_QUANTUM_INSTANCE = '<your instance CRN>'
$env:IBM_BACKEND = '<accessible QPU backend>'
.\start-local.ps1
```

Restart the backend after changing configuration. The code does not load `.env` files automatically. IBM mode submits a real job and uses your account allocation.

The ZNE adapter submits three manually folded circuits through SamplerV2. Python derives means from counts and fits the extrapolation; this is not built-in Sampler ZNE. The ideal reference is calculated separately. Mitigation is not guaranteed to improve a result.

## Validation

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s backend/tests -v
npm.cmd --prefix frontend run build
```

For browser tests, start both services first:

```powershell
cd frontend
npx.cmd playwright install chromium
$env:ZNE_TEST_URL = 'http://127.0.0.1:5173'
npx.cmd playwright test
```

Use the actual launcher URL if its port differs. Backend tests use mocks and do not submit IBM jobs.

## Project structure

- `frontend/src/LearningHub.jsx`: cover, missions, toolkit, and concept activities.
- `frontend/src/Codfish.jsx`: pixel fish variants.
- `frontend/src/main.jsx`: ZNE game and chart.
- `backend/app.py`: experiment API and persisted runs.
- `backend/core.py`: sampling, means, fitting, and uncertainty.
- `backend/ibm_adapter.py`: Qiskit circuits and IBM submission/results.
- `start-local.ps1`: Windows launcher.
- `docs/ZNE-technical-notes.md`: detailed ZNE notes in Chinese.

This is a local prototype. Authentication, multi-user isolation, and public-deployment controls are not implemented.
