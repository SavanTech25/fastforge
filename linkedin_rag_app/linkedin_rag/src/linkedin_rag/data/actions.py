
# SQL Actions implementation
from sqlalchemy.orm import Session
from fastapi import UploadFile
from loguru import logger
import os
import uuid
import shutil

actions = [
    "insert_one", "delete_one", "find_one", "update_one", "find_all",
    "purge", "insert_many", "update_many"
]

def make_crud_action(db: Session, model_class, action: str, **kwargs):
    if action not in actions:
        raise ValueError(f"action must be one of: {actions}")
    
    if action == "insert_one":
        document = kwargs.get("document", {})
        instance = model_class(**document)
        db.add(instance)
        db.commit()
        db.refresh(instance)
        return instance
        
    elif action == "find_one":
        filter_args = kwargs.get("filter", {})
        query = db.query(model_class)
        for attr, value in filter_args.items():
            query = query.filter(getattr(model_class, attr) == value)
        return query.first()
        
    elif action == "update_one":
        filter_args = kwargs.get("filter", {})
        update_args = kwargs.get("update", {}).get("$set", {})
        query = db.query(model_class)
        for attr, value in filter_args.items():
            query = query.filter(getattr(model_class, attr) == value)
        instance = query.first()
        if instance:
            for k, v in update_args.items():
                setattr(instance, k, v)
            db.commit()
            db.refresh(instance)
        return instance
        
    elif action == "delete_one":
        filter_args = kwargs.get("filter", {})
        query = db.query(model_class)
        for attr, value in filter_args.items():
            query = query.filter(getattr(model_class, attr) == value)
        instance = query.first()
        if instance:
            db.delete(instance)
            db.commit()
        return True
        
    elif action == "find_all":
        filter_args = kwargs.get("filter", {})
        query = db.query(model_class)
        for attr, value in filter_args.items():
            query = query.filter(getattr(model_class, attr) == value)
        return query.all()
        
    elif action == "purge":
        filter_args = kwargs.get("filter", {})
        query = db.query(model_class)
        for attr, value in filter_args.items():
            query = query.filter(getattr(model_class, attr) == value)
        count = query.delete()
        db.commit()
        return count
        
    elif action == "insert_many":
        documents = kwargs.get("documents", [])
        instances = [model_class(**doc) for doc in documents]
        db.add_all(instances)
        db.commit()
        for instance in instances:
            db.refresh(instance)
        return instances
        
    elif action == "update_many":
        filter_args = kwargs.get("filter", {})
        update_args = kwargs.get("update", {}).get("$set", {})
        query = db.query(model_class)
        for attr, value in filter_args.items():
            query = query.filter(getattr(model_class, attr) == value)
        count = query.update(update_args)
        db.commit()
        return count

UPLOAD_DIR = "static/uploads"

def handle_file(action: str, file: UploadFile = None, file_content: bytes = None, filename: str = "", id: str = ""):
    if action not in actions:
        raise ValueError(f"action must be one of: {actions}")
        
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    try:
        if action == "insert_one":
            file_id = str(uuid.uuid4())
            safe_filename = f"{file_id}_{file.filename if file else filename}"
            file_path = os.path.join(UPLOAD_DIR, safe_filename)
            
            if file_content:
                with open(file_path, "wb") as f:
                    f.write(file_content)
            elif file:
                with open(file_path, "wb") as f:
                    shutil.copyfileobj(file.file, f)
            return file_id

        elif action == "find_one":
            if filename:
                return os.path.join(UPLOAD_DIR, filename)
            elif id:
                for f in os.listdir(UPLOAD_DIR):
                    if f.startswith(id):
                        return os.path.join(UPLOAD_DIR, f)
            return None

        elif action == "delete_one":
            if id:
                for f in os.listdir(UPLOAD_DIR):
                    if f.startswith(id):
                        os.remove(os.path.join(UPLOAD_DIR, f))
                        return True
            return False
            
    except Exception as e:
        logger.error(f"Error handling file: {e}")
        return None
