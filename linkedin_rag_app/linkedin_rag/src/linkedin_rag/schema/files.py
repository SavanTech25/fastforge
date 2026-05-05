from pydantic import BaseModel
from typing import Optional

class FilesBase(BaseModel):
    filename: str
    content_type: str
    file_id: str

class FilesCreate(FilesBase):
    pass

class FilesUpdate(BaseModel):
    filename: Optional[str] = None
    content_type: Optional[str] = None
    file_id: Optional[str] = None

class FilesResponse(FilesBase):
    id: int
    class Config:
        from_attributes = True