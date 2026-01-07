from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from textblob import TextBlob
from collections import Counter
import re

from database import SessionLocal, engine
import models

app = FastAPI(title="Thought Mirror API")

# ---------- CORS ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- DB ----------
models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------- REQUEST MODELS ----------
class LoginRequest(BaseModel):
    email: str
    password: str

class JournalRequest(BaseModel):
    user_id: int
    content: str

# ---------- ROOT ----------
@app.get("/")
def root():
    return {"message": "Thought Mirror backend running 🚀"}

# ---------- LOGIN ----------
@app.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == data.email).first()

    if not user:
        user = models.User(email=data.email, password=data.password)
        db.add(user)
        db.commit()
        db.refresh(user)

    return {"user_id": user.id, "email": user.email}

# ---------- SAVE JOURNAL ----------
@app.post("/journal")
def save_journal(data: JournalRequest, db: Session = Depends(get_db)):
    journal = models.Journal(
        user_id=data.user_id,
        content=data.content,
        created_at=datetime.utcnow()
    )
    db.add(journal)
    db.commit()
    return {"message": "Journal saved successfully"}

# ---------- FETCH JOURNALS ----------
@app.get("/journal/{user_id}")
def get_journals(user_id: int, db: Session = Depends(get_db)):
    journals = (
        db.query(models.Journal)
        .filter(models.Journal.user_id == user_id)
        .order_by(models.Journal.created_at.desc())
        .all()
    )

    return [
        {
            "id": j.id,
            "content": j.content,
            "created_at": j.created_at.strftime("%d %b %Y, %I:%M %p")
        }
        for j in journals
    ]

# ---------- AUTOMATIC SUMMARY GENERATOR ----------
def generate_reflection_summary(text: str) -> str:
    blob = TextBlob(text)
    sentences = blob.sentences

    # If too little content, return raw text
    if len(sentences) <= 2:
        return str(blob)

    # Rank sentences by emotional strength
    ranked = sorted(
        sentences,
        key=lambda s: abs(s.sentiment.polarity),
        reverse=True
    )

    # Pick top emotionally meaningful sentences
    top_sentences = ranked[:3]

    summary = " ".join(str(sentence) for sentence in top_sentences)
    return summary

# ---------- INSIGHTS ----------
@app.get("/insights/{user_id}")
def get_insights(user_id: int, db: Session = Depends(get_db)):
    journals = db.query(models.Journal).filter(
        models.Journal.user_id == user_id
    ).all()

    if not journals:
        return {
            "sentiment": "Neutral",
            "score": 0,
            "keywords": [],
            "summary": "You haven’t written enough journal entries yet to generate insights."
        }

    # Combine all journal content
    full_text = " ".join(j.content for j in journals)
    clean_text = re.sub("<.*?>", "", full_text)

    blob = TextBlob(clean_text)
    polarity = blob.sentiment.polarity

    # Sentiment label
    if polarity > 0.1:
        sentiment = "Positive 😊"
    elif polarity < -0.1:
        sentiment = "Negative 😟"
    else:
        sentiment = "Neutral 😐"

    # Keyword extraction
    words = [
        w.lower() for w in clean_text.split()
        if len(w) > 4 and w.isalpha()
    ]
    keywords = [w for w, _ in Counter(words).most_common(5)]

    # 🔥 AUTOMATIC SUMMARY
    summary = generate_reflection_summary(clean_text)

    return {
        "sentiment": sentiment,
        "score": round(polarity, 2),
        "keywords": keywords,
        "summary": summary
    }
