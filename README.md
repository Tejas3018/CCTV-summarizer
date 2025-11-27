# CCTV Summarizer

AI-powered CCTV summarizer using YOLO for human detection and OpenCV for frame extraction. It trims long surveillance videos to human-activity segments, reducing review time by ~80%.

## Run Instructions (Windows)

Run backend and frontend in separate terminals.

### Terminal 1 — Backend (Flask)
```powershell

python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
- Backend runs at `http://localhost:5000`.

### Terminal 2 — Frontend (React)
```powershell

npm install
npm run dev
```
- Frontend runs at `http://localhost:3000` and talks to the backend at `http://localhost:5000`.

Open `http://localhost:3000` in your browser and upload a video to get the summarized output.
