# TrustMiiBro

TrustMiiBro is a password security project with two parts:

1. a browser-based password checker that estimates strength in real time, checks for leaked passwords, and explains basic password requirements;
2. a FastAPI backend that turns a weak password or seed word into a stronger generated password, with a Google Gemini-powered enhancement flow and a local fallback.

The frontend lives in `Web/` and the backend lives in `backend/`.

## What the project does

When you type a password in the checker page, the browser:

- evaluates password strength with `zxcvbn`,
- shows which requirements are satisfied,
- checks whether the password appears in known breaches through the Have I Been Pwned range API.

When you use the generator section, the frontend sends your input to the backend API. The backend:

- reads the Gemini API key from `.env`,
- asks Gemini for a password-like result,
- cleans and adjusts the result to match your options,
- pads or trims the output to the requested length,
- falls back to a local random generator if the AI call fails.

## Project structure

```text
TrustMiiBro/
├── Web/
│   ├── home.html         # Frontend page
│   ├── CSS/home.css      # Page styling
│   └── JS/home.js        # Password checker + API calls
└── backend/
    ├── backend.py        # FastAPI app with /enhance
    ├── ai/
    │   ├── inference.py  # Gemini + fallback password logic
    │   └── start.py      # Writes .env and starts Uvicorn
    ├── requirements.txt
    └── render.yaml       # Render deployment config
```

## Requirements

To run the backend, you need:

- Python 3.10+
- `fastapi`
- `uvicorn`
- `pydantic`
- `python-dotenv`
- `google-genai`

The backend requirements file also includes `torch` and `scikit-learn`, which appear to be leftover packages from earlier experiments.

The frontend uses:

- the `zxcvbn` library from a CDN,
- the Have I Been Pwned password range API,
- the backend running on `http://127.0.0.1:8000`.

## Setup

### 1) Install backend dependencies

From the repository root:

```bash
cd backend
pip install -r requirements.txt
```

If your environment is missing `google-genai` or `python-dotenv`, install them manually:

```bash
pip install google-genai python-dotenv
```

### 2) Add your Gemini API key

`backend/ai/start.py` writes a `.env` file inside the `backend/` folder. That file should contain:

```bash
GEMINI_API_KEY=your_api_key_here
```

Replace the placeholder with your real Gemini API key before starting the server.

### 3) Start the backend

The easiest way is to run the startup script from the repository root:

```bash
python backend/ai/start.py
```

That script creates or updates `backend/.env` and starts Uvicorn on port `8000`.

You can also start it manually from the `backend/` folder after creating `.env` yourself:

```bash
cd backend
uvicorn backend:app --reload
```

## Run the frontend

Open `Web/home.html` in your browser.

The page has two main parts:

- the password checker, which updates as you type;
- the AI password generator, which calls the backend API.

If the backend is not running, the generator button will show an API connection error.

## How to use it

### Password checker

1. Type a password into the input field.
2. Watch the strength bar update.
3. Review the requirement indicators.
4. See whether the password has appeared in known leaks.

### AI password generator

1. Enter a base word, or leave it blank for a random phrase.
2. Choose a target length.
3. Select whether to include uppercase letters, numbers, symbols, and whether to avoid tricky characters such as `I`, `l`, `O`, and `0`.
4. Click **Generate**.
5. Copy the result with the clipboard button.

## API

### `POST /enhance`

Request body:

```json
{
  "weak_password": "dragon",
  "target_len": 16,
  "inc_upper": true,
  "inc_num": true,
  "inc_sym": true,
  "inc_ambig": false
}
```

Response:

```json
{
  "original_password": "dragon",
  "enhanced_password": "...",
  "score_percentage": 100,
  "strength_label": "Rất mạnh"
}
```

### Request fields

- `weak_password`: the base word or password to enhance
- `target_len`: desired final length
- `inc_upper`: include uppercase letters
- `inc_num`: include digits
- `inc_sym`: include symbols
- `inc_ambig`: remove confusing characters like `I`, `l`, `O`, and `0`

## How the backend works

The backend logic in `backend/ai/inference.py` follows this flow:

1. load `.env` and read `GEMINI_API_KEY`,
2. generate a prompt for Gemini,
3. clean the model output,
4. enforce the requested character options,
5. trim or pad the password to the target length,
6. return a strength label and score,
7. fall back to a local generator if Gemini fails.

## Deployment

`backend/render.yaml` is already configured for Render:

- build command: `pip install -r requirements.txt`
- start command: `uvicorn backend:app --host 0.0.0.0 --port $PORT`

## Notes

- The frontend expects the backend at `http://127.0.0.1:8000/enhance`.
- The browser checker still works on its own, but the generator section needs the backend.
- The project is best run from the repository root with the backend script in `backend/ai/start.py`.
