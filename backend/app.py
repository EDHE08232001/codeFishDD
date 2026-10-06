import json
import logging
import os
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Literal
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
# backend/.env (then a repo-root .env) supplies IBM settings; real environment variables win.
BACKEND_DIR = Path(__file__).resolve().parent
load_dotenv(BACKEND_DIR / '.env')
load_dotenv(BACKEND_DIR.parent / '.env')

from .core import simulate, fit
from .dd_api import router as dd_router
from .twirl_api import router as twirl_router

app = FastAPI(title='ZNE Learning Game')
frontend_port = int(os.getenv('ZNE_FRONTEND_PORT', '5173'))
app.add_middleware(CORSMiddleware, allow_origins=[f'http://localhost:{frontend_port}',f'http://127.0.0.1:{frontend_port}'],
    allow_methods=['GET','POST'], allow_headers=['Content-Type'])
app.include_router(dd_router)
app.include_router(twirl_router)
DATA = BACKEND_DIR / 'data'
LOCK = threading.RLock()
POOL = ThreadPoolExecutor(max_workers=1)

class RunRequest(BaseModel):
    mode: Literal['teaching','ibm'] = 'teaching'
    level: Literal['linear','exponential'] = 'linear'
    shots: int = Field(default=2000, ge=100, le=10000)
    seed: int = Field(default=42, ge=0, le=2**32-1)

class Guess(BaseModel):
    model: Literal['linear','exponential']
    guess: float = Field(ge=-1, le=1, allow_inf_nan=False)

def path_for(run_id):
    try:
        canonical = str(uuid.UUID(run_id))
    except ValueError:
        raise HTTPException(404, 'Run not found')
    return DATA / (canonical+'.json')

def save(run):
    with LOCK:
        DATA.mkdir(parents=True, exist_ok=True)
        path = path_for(run['id'])
        temporary = path.with_suffix('.tmp')
        temporary.write_text(json.dumps(run, allow_nan=False), encoding='utf-8')
        temporary.replace(path)

def read(run_id):
    with LOCK:
        path = path_for(run_id)
        if not path.exists():
            raise HTTPException(404, 'Run not found')
        return json.loads(path.read_text(encoding='utf-8'))

def public(run):
    return {key:value for key,value in run.items() if key != 'reference'}

def submit_ibm(run_id):
    run = read(run_id)
    try:
        from . import ibm_adapter
        details = ibm_adapter.submit(run['shots'])
        run.update(details, status='queued')
    except Exception:
        logging.exception('IBM submission failed for %s', run_id)
        run.update(status='failed', error='IBM submission failed; check backend logs and credentials.')
    save(run)

@app.get('/api/health')
def health():
    return {'ok':True, 'ibm_enabled':os.getenv('IBM_ENABLE','').lower()=='true'}

@app.post('/api/runs', status_code=202)
def create_run(request: RunRequest):
    if request.mode == 'ibm':
        if os.getenv('IBM_ENABLE','').lower() != 'true':
            raise HTTPException(403, 'IBM execution is disabled on this server')
        if not all(os.getenv(name) for name in ('IBM_QUANTUM_TOKEN','IBM_BACKEND')):
            raise HTTPException(503, 'IBM server configuration is incomplete')
        with LOCK:
            active = [json.loads(p.read_text(encoding='utf-8')) for p in DATA.glob('*.json')]
            if any(r.get('mode')=='ibm' and r.get('status') not in ('completed','failed') for r in active):
                raise HTTPException(409, 'An IBM experiment is already active')
            run = dict(id=str(uuid.uuid4()), **request.model_dump(), status='submitting', source='IBM QPU')
            save(run)
        POOL.submit(submit_ibm, run['id'])
    else:
        run = dict(id=str(uuid.uuid4()), **request.model_dump(), status='completed',
            source='Synthetic teaching model (not a quantum simulator)', reference=0.9,
            points=simulate(request.level, request.shots, request.seed))
        save(run)
    return public(run)

@app.get('/api/runs/{run_id}')
def get_run(run_id: str):
    with LOCK:
        run = read(run_id)
        if run['mode']=='ibm' and run['status'] in ('queued','running'):
            try:
                from . import ibm_adapter
                run.update(ibm_adapter.poll(run['job_id']))
                run.pop('poll_error', None)
                save(run)
            except Exception:
                logging.exception('IBM polling failed')
                run['poll_error'] = 'Could not refresh IBM job; try again.'
    return public(run)

@app.post('/api/runs/{run_id}/reveal')
def reveal(run_id: str, request: Guess):
    run = read(run_id)
    if run['status'] != 'completed':
        raise HTTPException(409, 'Measurements are not complete')
    try:
        fitted = fit(run['points'], request.model)
    except (ValueError, RuntimeError):
        raise HTTPException(422, 'Model fitting failed; try another model or experiment')
    ref = run['reference']
    return dict(**fitted, reference=ref, guess=request.guess,
        player_error=abs(request.guess-ref), fitted_error=abs(fitted['estimate']-ref),
        raw_error=abs(run['points'][0]['mean']-ref))
