# 📝 RankUp Test — Question Paper Generator

A web application that converts Excel files into beautifully formatted PDF question papers with Hindi/Devanagari support, watermarks, and answer keys.

![RankUp Test](frontend/logo.png)

## ✨ Features

- **Excel to PDF** — Upload `.xlsx` files and get professionally formatted question papers
- **Hindi/Devanagari Support** — Custom font rendering for Hindi language papers
- **Two-Column Layout** — Clean, print-ready question paper format
- **Answer Key & Explanations** — Auto-generated answer section with explanations
- **Watermark Support** — Custom watermark on every page
- **Drag & Drop** — Modern UI with drag-and-drop file upload
- **Exam Name Header** — Custom exam name on every page

## 📋 Excel File Format

Your Excel file (`.xlsx`) must have these columns:

| Column | Description |
|--------|-------------|
| `question` | The question text |
| `optionA` | Option A |
| `optionB` | Option B |
| `optionC` | Option C |
| `optionD` | Option D |
| `correctAnswer` | The correct answer |
| `explanation` | (Optional) Explanation for the answer |

A sample file (`sample_questions.xlsx`) is included in the repo.

## 🚀 Quick Start (Local Development)

### Prerequisites
- Python 3.9+
- Google Chrome or Microsoft Edge installed

### Setup
```bash
# Clone the repo
git clone https://github.com/Malayaj01/RankupTest_converter.git
cd RankupTest_converter

# Create virtual environment
cd backend
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

Open `http://localhost:5001` in your browser.

## 🐳 Docker Deployment

The app is Docker-ready with Chromium for PDF generation:

```bash
# Build
docker build -t rankup-convertor .

# Run
docker run -p 10000:10000 rankup-convertor
```

Open `http://localhost:10000` in your browser.

## ☁️ Deploy on Render (Free)

1. Push code to GitHub
2. Go to [render.com](https://render.com) → **New +** → **Web Service**
3. Connect your GitHub repo → Select **prod** branch
4. Set Runtime to **Docker**
5. Leave Start Command **blank**
6. Select **Free** plan → Deploy!

The `render.yaml` auto-configures everything.

## 🏗️ Project Structure

```
Rankup-convertor/
├── backend/
│   ├── app.py              # Flask server + PDF generation
│   ├── requirements.txt    # Python dependencies
│   ├── fonts/              # Hindi/Devanagari fonts
│   └── watermark.png       # Watermark image
├── frontend/
│   ├── index.html          # Main page
│   ├── script.js           # Upload & download logic
│   ├── style.css           # Styling
│   └── logo.png            # App logo
├── Dockerfile              # Docker config (Python + Chromium)
├── render.yaml             # Render.com deployment config
├── .dockerignore
└── sample_questions.xlsx   # Example Excel file
```

## 🛠️ Tech Stack

- **Backend:** Python, Flask, Pandas
- **Frontend:** HTML, CSS, JavaScript
- **PDF Engine:** Chromium (headless, via `--print-to-pdf`)
- **Deployment:** Docker, Gunicorn, Render.com

## 📄 License

© 2026 RankUp Test. All rights reserved.
