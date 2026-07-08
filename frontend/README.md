# Firestore emulator
cd backend
npx firebase-tools emulators:start --only firestore --project civiclens-ai-dev

# API
cd backend
.\.venv\Scripts\python run.py

# Frontend
cd frontend
npm run dev