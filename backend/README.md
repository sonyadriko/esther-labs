# Python FastAPI Backend for AI Video Generator

## Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run Development Server
```bash
uvicorn main:app --reload --port 8000
```

## Environment Variables
Create a `.env` file with:
```
DATABASE_URL=postgresql://user:password@localhost:5432/videogen
GEMINI_API_KEY=your_gemini_api_key
```
# esther-labs
