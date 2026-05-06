# TrustMiiBro – Password Enhancer Backend

TrustMiiBro is a FastAPI backend that takes a weak password or a short seed phrase and returns an enhanced password with a target length and optional character requirements.

The active backend logic is in `backend/backend.py`, and the password generation pipeline is implemented in `backend/ai/inference.py`.

## What this project does

The API accepts:

- a base password or phrase
- a target length
- options to include uppercase letters, numbers, symbols, and to avoid ambiguous characters

It then:

1. asks Google Gemini 1.5 Flash for a creative password candidate,
2. cleans and adjusts the output in Python,
3. pads or trims the result to match the requested length,
4. falls back to a local generator if the AI call fails.

## Project structure

- `backend/backend.py` – FastAPI app and `/enhance` endpoint
- `backend/ai/inference.py` – password enhancement logic
- `backend/ai/start.py` – creates a `.env` file and starts Uvicorn
- `Web/` – frontend files that call the backend API
- `backend/render.yaml` – Render deployment config

## Requirements

The runtime code uses:

- `fastapi`
- `uvicorn`
- `pydantic`
- `python-dotenv`
- `google-genai`

The repository also contains older AI artifacts and dependency files under `backend/ai/`, but the currently active backend path is the FastAPI + Gemini flow above.

## Setup

### 1) Install dependencies

From the `backend` directory:

```bash
pip install -r requirements.txt
```

If you are running only the Gemini-backed password enhancer code under `backend/ai/`, install:

```bash
pip install fastapi uvicorn pydantic google-genai python-dotenv
```

### 2) Add your Gemini API key

`backend/ai/start.py` writes a `.env` file at the project root with:

```bash
GEMINI_API_KEY=your_key_here
```

In the current file, `API_KEY` is just a placeholder, so replace it with your real key before starting the app.

### 3) Run the backend

You can start the app with:

```bash
python backend/ai/start.py
```

That script creates `.env` and launches:

```bash
uvicorn backend:app --reload
```

The API runs locally at:

```bash
http://127.0.0.1:8000
```

## API

### POST `/enhance`

Request body:

```json
{
  "weak_password": "my weak password",
  "target_len": 16,
  "inc_upper": true,
  "inc_num": true,
  "inc_sym": true,
  "inc_ambig": false
}
```

### Response

```json
{
  "original_password": "my weak password",
  "enhanced_password": "TrUStMiiBr0!7X",
  "score_percentage": 100,
  "strength_label": "Rất mạnh"
}
```

## Parameter meaning

- `weak_password`: input text used as the base for generation
- `target_len`: final password length
- `inc_upper`: include uppercase letters
- `inc_num`: include numbers
- `inc_sym`: include symbols
- `inc_ambig`: avoid ambiguous characters like `0`, `O`, `l`, `1`

## Behavior details

- If the Gemini call succeeds, the code uses the model response and then enforces the requested constraints.
- If the Gemini call throws an exception, the code falls back to a local Python generator.
- If `GEMINI_API_KEY` is missing, the function returns an error message inside `enhanced_password` rather than producing a generated password.

## Frontend connection

The frontend in `Web/JS/home.js` sends requests to:

```bash
http://127.0.0.1:8000/enhance
```

So the frontend and backend must run on the expected local address and port unless you update the fetch URL.

## Deployment note

`backend/render.yaml` is configured for Render with:

- build command: `pip install -r requirements.txt`
- start command: `uvicorn backend:app --host 0.0.0.0 --port $PORT`

## Notes

This repository contains both a backend API and older AI experiment files under `backend/ai/`. The README above describes the code path that is actually used by `backend/backend.py` today.
