import os
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from models import Note
from database import Base, engine, SessionLocal

UPLOAD_DIR = "uploads/notes"
os.makedirs(UPLOAD_DIR, exist_ok=True)

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency for DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/content/notes")
async def upload_handwritten_note(
    session_id: int = Form(...),
    teacher_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    file_ext = os.path.splitext(file.filename)[1]
    if file_ext.lower() not in [".pdf", ".jpg", ".jpeg", ".png"]:
        raise HTTPException(status_code=400, detail="Invalid file type.")

    timestamp = datetime.utcnow().isoformat()
    safe_filename = f"{session_id}_{teacher_id}_{timestamp.replace(':', '-')}{file_ext}"
    save_path = os.path.join(UPLOAD_DIR, safe_filename)

    with open(save_path, "wb") as f:
        content = await file.read()
        f.write(content)

    file_url = f"/{save_path}"  # could be changed if using cloud or CDN

    note = Note(
        session_id=session_id,
        teacher_id=teacher_id,
        created_at=timestamp,
        file_url=file_url
    )

    db.add(note)
    db.commit()
    db.refresh(note)

    return {
        "message": "Note uploaded successfully",
        "note_id": note.id,
        "file_url": file_url
    }


@app.get("/classes/{session_id}/notes")
def get_note_path(session_id: int, db: Session = Depends(get_db)):
    note = db.query(Note).filter(Note.session_id == session_id).first()

    if not note:
        raise HTTPException(status_code=404, detail="Note not found.")

    return {
        "session_id": session_id,
        "file_url": note.file_url
    }
