# 🎬 AI Video Generator - Product Review Videos

Generate professional product review videos using AI. Perfect for TikTok, Reels, and Ads.

## Features

- ✨ **Auto Script Generation** - AI generates compelling review scripts
- 🎙️ **Voice Over** - Natural Indonesian voice using Edge TTS
- 🎥 **Video Creation** - Automatic video creation with product images
- 🎨 **Multiple Styles** - Luxury, Minimal, Tech, and Lifestyle themes

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 14, TypeScript, Tailwind CSS, Shadcn UI |
| Backend | Python 3.11+, FastAPI, SQLAlchemy |
| Database | PostgreSQL |
| TTS | Edge TTS (Free) |
| Video | MoviePy + PIL |
| AI Script | Google Gemini (Optional) |

## Quick Start

### Prerequisites

- Node.js 18+
- Python 3.11+
- PostgreSQL

### 1. Setup Database

```bash
# Create PostgreSQL database
createdb videogen
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your database credentials

# Run backend
uvicorn main:app --reload --port 8000
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create environment file
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Run frontend
npm run dev
```

### 4. Open in Browser

Visit [http://localhost:3000](http://localhost:3000)

## How It Works

1. **Upload** - Upload 1-3 product images
2. **Describe** - Add product name and description
3. **Choose Style** - Select video style (Luxury, Minimal, Tech, Lifestyle)
4. **Generate** - AI creates script, voice over, and video
5. **Download** - Download video for social media

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/videos` | Create video generation request |
| `GET` | `/api/videos/{id}` | Get video details |
| `GET` | `/api/videos/{id}/status` | Get generation status |
| `GET` | `/api/videos/{id}/download` | Download video file |

## Environment Variables

### Backend (.env)

```
DATABASE_URL=postgresql://user:password@localhost:5432/videogen
GEMINI_API_KEY=your_optional_gemini_key
UPLOAD_DIR=./uploads
OUTPUT_DIR=./outputs
```

### Frontend (.env.local)

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Project Structure

```
EstherLabs/
├── frontend/                 # Next.js App
│   ├── src/
│   │   ├── app/             # Pages (App Router)
│   │   ├── components/      # React components
│   │   └── lib/             # Utilities
│   └── package.json
│
├── backend/                  # Python FastAPI
│   ├── app/
│   │   ├── api/             # API endpoints
│   │   ├── services/        # Business logic
│   │   ├── models/          # Database models
│   │   └── core/            # Config
│   ├── requirements.txt
│   └── main.py
│
└── README.md
```

## Video Style Examples

| Style | Description | Best For |
|-------|-------------|----------|
| Luxury | Gold accents, dark background | Premium products |
| Minimal | Clean, modern look | Tech, lifestyle |
| Tech | Cyan/blue, futuristic | Gadgets, electronics |
| Lifestyle | Warm, friendly tones | Fashion, beauty |

## Limitations

- Video output is slideshow-style with voice over (not AI-generated footage)
- Requires product images for best results
- Indonesian language only for now

## Future Improvements

- [ ] Multi-language support
- [ ] More video styles
- [ ] User authentication
- [ ] Video history
- [ ] Sora/Runway API integration (when available)

## License

MIT License
# esther-labs
# esther-labs
# esther-labs
