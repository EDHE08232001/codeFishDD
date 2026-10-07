# Dynamical decoupling demo (Qiskit + IBM Quantum)

A small, modular project that shows how **dynamical decoupling (DD)** keeps a qubit's quantum state alive while it sits idle: first in a fast theory model, then in a local circuit simulation, then on a real IBM quantum computer.

> **Terminology.** IBM and most of the field call DD *error suppression*, not error mitigation. Suppression acts *during* the run: extra pulses change how noise affects the qubit. Mitigation (ZNE, PEC, readout correction) works in post-processing from many runs. DD costs no extra qubits and no extra shots, and it combines with mitigation.

---

## The idea in one minute

A qubit's frequency wanders slowly (stray fields, nearby qubits, defects). While the qubit idles it picks up a phase error, and its superposition scrambles. This is **dephasing**.

Because the drift is *slow*, you can cancel it: flip the qubit with a π pulse halfway through the wait, and the phase error from the second half runs backward and undoes the first half. That is a **spin echo**. Longer pulse trains extend it:

| Sequence | Pulses | Notes |
|---|---|---|
| Hahn echo | X | The simplest echo. Cancels static offsets. |
| CPMG | X X X ... | Evenly spaced X pulses. Strong against dephasing, but sensitive to pulse errors for some states. |
| XY4 | X Y X Y | Alternating axes, so first-order pulse errors cancel. |
| UDD | X X X ... | Uneven (Uhrig) spacing, best when the noise has a sharp high-frequency cutoff. |

DD helps against **slow, correlated noise**. It does not help against T1 decay (energy loss), readout error, or fast white noise.

---

## What the demo contains

Three experiments, in increasing realism. All run from `main.py`.

| Command | What it does | Needs a token? |
|---|---|---|
| `python main.py theory` | NumPy model of dephasing under 1/f noise for free evolution, Hahn, CPMG, UDD and XY4. Instant. | No |
| `python main.py local` | The same physics as real Qiskit circuits: the noise is applied as RZ rotations between DD pulses, simulated exactly. Includes optional pulse over-rotation. Add `--engine numpy` for the identical vectorised simulator (`src/fastsim.py`). | No |
| `python main.py hardware` | The same idle experiment on a real IBM device, with and without DD. | Yes |
| `python main.py hardware --fake` | Dry run of the hardware pipeline on an offline fake device. Checks the code path only (see limitations). | No |

Outputs (a PNG plus, for hardware, a JSON with raw counts) are written to `results/` next to `main.py`, whichever folder you run it from. `--noise` accepts `1/f`, `lorentzian`, `white` or `static` (one constant offset per run, the textbook spin-echo case).

### Sample output of the offline experiments

Default settings (15 kHz rms 1/f noise, seed 7):

```
theory (coherence at 100 us):  free 0.007  hahn 0.024  cpmg8 0.545  udd8 0.523  xy4x2 0.545
local  (P(0) at 80 us, init=y, 3% pulse error):  free 0.571  hahn 0.546  cpmg8 0.796  xy4x2 0.897
```

The theory model treats CPMG and XY4 as identical (both flip a Z phase). The local simulation separates them: with imperfect pulses and a |+i> start, XY4 holds up better than CPMG.

---

## The hardware experiment

### The circuit

One qubit, one circuit per idle time:

1. **Prepare** a superposition (`init x`: H gives |+>; `init y`: H then S gives |+i>).
2. **Idle** for a chosen delay.
3. **Un-prepare** (the inverse of step 1) and **measure**.

If the qubit remembered its state perfectly, the measurement would always give `0`.

### The axes

- **x-axis, idle time (microseconds):** how long the qubit waits in step 2. Delays are rounded to a multiple of 16 `dt`, which IBM hardware requires, so the plotted values are the rounded ones.
- **y-axis, P(0):** the fraction of shots that measured `0`.
  - `1.0` means the state was perfectly preserved.
  - `0.5` means the state is completely scrambled (a coin flip).
  - Below `0.5` means the state rotated *coherently* past the halfway point rather than just fading. This happens when there is a steady frequency offset.

Higher is better.

### The curves (modes)

Every curve uses the same device, qubit, circuit, delays and shot count. Only the DD treatment differs. Choose modes with `--modes`.

| Mode | What it is |
|---|---|
| `none` | No DD. The qubit idles undisturbed. This is the baseline. |
| `runtime-XX` | IBM's Sampler option inserts DD automatically when the job runs. Sequence `XX`: two X (π) pulses. |
| `runtime-XpXm` | Same option, sequence X then X-inverse. |
| `runtime-XY4` | Same option, sequence X, Y, X, Y. |
| `manual-XX` | Our code inserts the pulses before submission with Qiskit's `PadDynamicalDecoupling` pass (`src/runner.py`), with IBM's DD option off. We observed two X gates per idle window. |

`runtime-XX` and `manual-XX` are the same kind of sequence but different implementations. Exact pulse placement inside IBM's service is IBM's, so the two can differ.

### Sample result: `ibm_quebec`, qubit 5, `init y`, 2000 shots per point (2026-10-05)

| idle (us) | none | runtime-XX | runtime-XY4 | manual-XX |
|---|---|---|---|---|
| 25 | 0.77 | 0.95 | 0.96 | 0.95 |
| 50 | 0.60 | 0.90 | 0.90 | 0.91 |
| 100 | 0.24 | 0.76 | 0.75 | 0.85 |
| 150 | 0.27 | 0.61 | 0.63 | 0.81 |
| 200 | 0.51 | 0.51 | 0.52 | 0.76 |

Statistical error at 2000 shots is about +/-0.01 near 0.5 and +/-0.005 near 0.95.

What it shows:

- **The baseline rotates.** `none` drops below 0.5 (to 0.24 at 100 us) and then comes back up. Random dephasing alone cannot push P(0) below 0.5, so this indicates a steady frequency offset on this qubit (a rough guess is a few kHz, from only 8 points).
- **DD removes the rotation.** All DD curves decay smoothly toward 0.5. At 100 us the baseline is 0.24 and the DD curves are 0.75 to 0.85.
- **The ceiling (about 0.95 at 25 us) is not DD's job.** It comes from readout and gate errors, which DD cannot touch.
- **`runtime-XX` and `runtime-XY4` are indistinguishable.** That is expected when the X and Y gates are good and dephasing dominates.
- **`manual-XX` stayed highest at long delays.** This is a single run on a single qubit. Do not conclude that the manual pass is better than IBM's option. The four modes ran as separate jobs at different times, and low-frequency noise drifts. To check, repeat with the mode order reversed, and run `none` twice to see whether the oscillation is reproducible.

---

## Setup

macOS / Linux (zsh or bash):

```zsh
cd backend/dd_demo
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # then paste your IBM Quantum API key into .env
```

Windows (PowerShell):

```powershell
cd backend\dd_demo
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env  # then paste your IBM Quantum API key into .env
.\.venv\Scripts\Activate.ps1   # afterwards `python main.py ...` works as below
```

You can also reuse the repository's top-level `.venv` (`pip install -r backend/dd_demo/requirements.txt` on top of `backend/requirements.txt`).

`.env`:

```
IBM_QUANTUM_TOKEN=your_api_key_here
IBM_QUANTUM_INSTANCE=
```

`IBM_QUANTUM_INSTANCE` is optional: set it to an instance name or CRN only if you have several. `.env` is in `.gitignore`; never commit it. If the token is blank, the code falls back to an account saved earlier with `QiskitRuntimeService.save_account(...)`.

Tested with qiskit 2.5.2, qiskit-aer 0.17.2, qiskit-ibm-runtime 0.50.0, numpy 2.5.3, matplotlib 3.11.2. The offline commands and tests also pass with qiskit-ibm-runtime 0.47.0 (the version pinned by the web app) on Python 3.13. The code logs in on the `ibm_quantum_platform` channel, so very old qiskit-ibm-runtime versions may fail.

---

## Running the hardware experiment

```zsh
python main.py hardware --backend ibm_quebec --qubit 5 --init y \
    --points 8 --max-delay-us 200 --shots 2000 \
    --modes none,runtime-XX,runtime-XY4,manual-XX
```

| Option | Default | Meaning |
|---|---|---|
| `--fake` | off | Use the offline FakeTorino instead of a real device |
| `--backend` | least busy | Device name, for example `ibm_quebec` |
| `--qubit` | 0 | Physical qubit to test |
| `--shots` | 2000 | Shots per circuit |
| `--points` | 10 | Number of idle times |
| `--max-delay-us` | 100 | Longest idle time, in microseconds |
| `--init` | x | `x` starts in |+>, `y` starts in |+i> |
| `--modes` | none,runtime-XX,runtime-XY4 | Comma-separated list of the modes above |

On Windows use `.\run.ps1` (or the same command with `python`); on macOS/Linux `./run.sh` runs it.

Each mode is one job containing all delays. Real QPU time is limited on most plans, so check your allowance, and start small (`--points 6 --shots 1000`) the first time.

Output files in `results/`: `hardware_<backend>_<timestamp>.png` and `.json` (delays, P(0) per mode, and raw counts).

For a fair comparison across runs, pin the same backend and qubit, and interleave or repeat runs, since device noise drifts between jobs.

---

## Project layout

```
dd_demo/
├── main.py              # CLI: theory | local | hardware
├── conftest.py          # lets plain `pytest` find src/
├── requirements.txt
├── .env.example         # copy to .env and add your token
├── run.sh / run.ps1     # the hardware example command (macOS-Linux / Windows)
├── src/
│   ├── sequences.py     # Hahn, CPMG, XY4, UDD pulse timings (pure Python)
│   ├── noise.py         # 1/f, Lorentzian, white and static noise generators
│   ├── theory.py        # switching-function dephasing model
│   ├── circuits.py      # local noisy-idle circuits and the hardware Ramsey circuit
│   ├── fastsim.py       # vectorised NumPy twin of noisy_idle_circuit + Bloch trajectories
│   ├── game.py          # seeded levels and sequence explorer for the web game
│   ├── ibm.py           # token loading, backend choice, offline fake backend
│   ├── runner.py        # transpile, DD modes, SamplerV2 (blocking run or submit-only)
│   ├── analysis.py      # P(0) and error bars from counts, saved-result loading, JSON saving
│   └── plotting.py      # matplotlib helper
├── tests/test_basics.py
└── results/             # plots and JSON land here
```

Data flow for a hardware run: `main.py` -> `ibm.py` (backend) -> `runner.py` (transpile, add DD, run) -> `analysis.py` (P(0), JSON) -> `plotting.py` (PNG).

---

## Testing

Every module has a self-test in its `__main__` block. Run them from the project root with `-m` (relative imports fail if you run the file path directly):

```zsh
python -m src.sequences
python -m src.noise
python -m src.theory
python -m src.circuits
python -m src.fastsim      # checks the NumPy simulator against Qiskit Statevector
python -m src.game         # the web game's levels behave as designed
python -m src.ibm          # also tests your login if a token is set
python -m src.runner       # offline, about 30 s
python -m src.analysis
python -m src.plotting
pytest                     # unit tests (or: python -m pytest, or python -m unittest discover -s tests)
```

Quick smoke test of the whole CLI:

```zsh
python main.py --help
python main.py theory
python main.py local
python main.py hardware --fake --points 3 --max-delay-us 60 --shots 300 --modes none,manual-XX
```

---

---

## In the CODFISH web app

The web game imports this package as `backend.dd_demo.src` (see `backend/dd_api.py`); it needs only `backend/requirements.txt`, not matplotlib, qiskit-aer or python-dotenv.

| Endpoint | Uses |
|---|---|
| `GET /api/dd/levels`, `POST /api/dd/play` | `game.py` levels, scored with `fastsim.py`, plus an animation of 12 sample spins |
| `POST /api/dd/explore` | `theory.coherence_curve` (theory) or `fastsim` (circuit) curves, like `main.py theory/local` |
| `GET /api/dd/hardware[/<id>]` | every `results/hardware_*.json`, with binomial error bars |
| `POST /api/dd/hardware/runs`, `GET /api/dd/hardware/runs/<id>` | `runner.submit_sweep` on a real IBM backend (needs `IBM_ENABLE=true` and the IBM variables), saved in the same JSON format as the CLI |

The game reports **signal = 2·P(0) − 1**: 1 = state kept, 0 = scrambled, negative = rotated towards the opposite state.

## Limitations and known caveats

- **`--fake` shows no DD benefit.** The fake device models only T1/T2 relaxation, which DD cannot fix, and local mode ignores the `runtime-*` options. Use it to check the code path only.
- **One pulse pair per idle window.** `manual-XX` adds a single XX pair per idle window regardless of its length. It is an echo, not a repeated CPMG train. Repeating the sequence is a natural improvement for long idles.
- **Single qubit, single run.** The sample result is one qubit on one device on one day. Device noise drifts, so repeat before drawing conclusions.
- **T1 and readout set the floor and ceiling.** Compare modes against each other, not against 1.0.
- **Short idles.** DD can be slightly worse at very short delays because the pulses add their own error. A crossover in the plot is expected.
- **Delay granularity.** Delays are rounded to multiples of 16 `dt` to satisfy IBM hardware.

---

## Ideas for next steps

- **Bell-state experiment:** keep one qubit of a Bell pair idle while the other does gates, and compare the fidelity with and without DD. This shows "same circuit, better answer."
- **Spectator/crosstalk test:** idle one qubit while its neighbour is kept busy, since crosstalk is a classic low-frequency error DD cancels well.
- **Repeated sequences:** insert several XX pairs or XY4 blocks across long idle windows.
- **Combine with mitigation:** add readout error mitigation to lift the roughly 0.95 ceiling.
- **Error bars:** run several repeats and plot the spread.