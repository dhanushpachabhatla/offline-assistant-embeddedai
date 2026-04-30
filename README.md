# Offline Assistant Embedded AI

This project is an offline, command-focused Jarvis-style assistant. It listens for
a wake word, converts a short spoken command to text with Vosk, parses the command
locally, and executes a platform action.

## Architecture

### Parser and Grammar

The speech grammar is generated from the parser source of truth:

- `INTENTS`
- `APP_MAP`
- `WORD_NUMBERS`
- a small set of extra command words

This keeps Vosk recognition and parser behavior synced. When you add a new app
or intent, the grammar picks it up automatically.

The parser prefers exact phrase matches on word boundaries before fuzzy matching:

```text
restart -> ParsedCommand(intent='restart')
start chrome -> ParsedCommand(intent='open_app', app='chrome')
```

### Lazy Voice Loading

`main.py cli` does not load the microphone, wake-word model, or Vosk model.
Voice components are loaded only when `run_voice()` starts.

This makes CLI testing faster and safer on machines or embedded boards without a
configured microphone.

### Shorter Command Window

Speech listening defaults to 3 seconds.

Profiles can tune this further:

- `desktop`: 3.0 seconds
- `raspberry-pi`: 2.5 seconds
- `microcontroller`: 2.0 seconds

### Vosk Decoder Tuning

The bundled Vosk model config uses a lighter command-recognition path:

```text
--max-active=1000
--beam=7.0
```

This reduces CPU work during decoding. The tradeoff is that recognition may be
slightly less tolerant of noisy speech, so validate this on the target microphone
and device.

### Platform Executors

The executor layer is split:

```text
assistant/executor_common.py
assistant/executor_windows.py
assistant/executor_linux.py
assistant/executor.py
```

`assistant/executor.py` keeps the public `execute(cmd)` function, but chooses a
backend from the active deployment profile.

Windows backend supports:

- volume via `pycaw`
- brightness via `screen-brightness-control`
- app launching with `.exe` commands
- file explorer
- screenshots
- lock screen
- shutdown/restart
- Windows SAPI speech

Linux backend supports best-effort commands for Raspberry Pi/Linux devices:

- volume via `pactl` or `amixer`
- brightness via `brightnessctl`
- app/file opening via Linux commands
- screenshots via `gnome-screenshot` or `scrot`
- lock screen via common Linux desktop tools
- shutdown/restart via `systemctl`
- optional speech via `espeak`

Microcontroller profile is forward-only. It parses commands and reports the
structured intent instead of executing local OS actions.

### Deployment Profiles

Set `JARVIS_PROFILE` to select the runtime shape:

```powershell
$env:JARVIS_PROFILE="desktop"
$env:JARVIS_PROFILE="raspberry-pi"
$env:JARVIS_PROFILE="microcontroller"
```

Profiles live in `assistant/profiles.py`.

Current profiles:

| Profile | Backend | Purpose |
| --- | --- | --- |
| `desktop` | auto Windows/Linux | Main desktop assistant |
| `raspberry-pi` | Linux | Embedded Linux command assistant |
| `microcontroller` | forward-only | Wake/parse/forward style deployment |

### Benchmarks

`metrics/monitor.py` includes a `BenchmarkReport` helper.

Voice mode prints metrics for:

- wake model load time
- Vosk model load time
- wake waiting segment
- speech recognition segment
- command/action segment
- memory samples
- CPU samples

There is also a benchmark command:

```powershell
$env:UV_CACHE_DIR = (Resolve-Path '.').Path + '\.uv-cache'
uv run python -m metrics.benchmark
```

Example result from this machine:

```text
[benchmark] profile=desktop
[benchmark] grammar_terms=118
[benchmark] parser_samples=0.005s | vosk_load=1.008s | parser_mem=23.6MB | vosk_load_mem=49.1MB | parser_cpu=16.2% | vosk_load_cpu=30.2%
```

## Setup

This project uses `uv` and expects Python 3.13.

```powershell
$env:UV_CACHE_DIR = (Resolve-Path '.').Path + '\.uv-cache'
uv run python --version
```

The first run creates `.venv` and installs dependencies from `uv.lock`.

No `.env` keys are required for the current offline assistant. The project does
not call cloud APIs.

## Running

Interactive CLI:

```powershell
uv run python jarvis.py
```

Direct text command:

```powershell
uv run python jarvis.py "system info"
uv run python jarvis.py "open chrome"
```

Voice mode:

```powershell
uv run python main.py
```

CLI through `main.py` without loading voice models:

```powershell
uv run python main.py cli
```

Microcontroller/forward-only smoke test:

```powershell
$env:JARVIS_PROFILE="microcontroller"
uv run python jarvis.py "restart"
```

## Model Inventory

There is one model folder committed in the repo:

```text
models/vosk-model-small-en-us-0.15
```

It is a small US English Vosk speech-to-text model, about 71 MB on disk.

Runtime also uses a built-in `pymicro_wakeword` model:

```text
Model.OKAY_NABU
```

That wake model is loaded from the Python package, not from the repo's `models`
folder.

## Embedded Notes

The speech stack is suitable for Raspberry Pi-class devices, especially with the
smaller grammar and lower Vosk beam settings. The Windows executor is not
portable, which is why the Linux and forward-only backends now exist.

Recommended validation on real hardware:

- measure wake-word CPU while idle
- measure Vosk load time
- measure recognition latency with the target microphone
- compare accuracy with the current Vosk beam tuning
- decide whether the Raspberry Pi profile should keep Vosk or forward audio/text
  to a stronger local machine
