from sqlalchemy import Column, Integer, String
from database import Base

class Note(Base):
    __tablename__ = "notes"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, index=True)
    teacher_id = Column(Integer, index=True)
    created_at = Column(String, nullable=False)
    file_url = Column(String, nullable=False)
