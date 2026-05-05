from sqlalchemy.orm import Session
from typing import Optional
from linkedin_rag.entity.files import Files
from linkedin_rag.schema.files import FilesCreate, FilesUpdate

def get_files(db: Session, files_id: int) -> Optional[Files]:
    return db.query(Files).filter(Files.id == files_id).first()

def get_filess(db: Session, skip: int = 0, limit: int = 100) -> list:
    return db.query(Files).offset(skip).limit(limit).all()

def create_files(db: Session, data: FilesCreate) -> Files:
    obj = Files(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def update_files(db: Session, files_id: int, data: FilesUpdate) -> Optional[Files]:
    obj = get_files(db, files_id)
    if not obj:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, key, value)
    db.commit()
    db.refresh(obj)
    return obj

def delete_files(db: Session, files_id: int) -> bool:
    obj = get_files(db, files_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True