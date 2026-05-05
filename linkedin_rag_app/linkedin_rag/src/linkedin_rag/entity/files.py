from sqlalchemy import Column, Integer, String, Boolean, Float, Text
from sqlalchemy.orm import relationship
from linkedin_rag.data.database import Base

class Files(Base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True, index=True)
    _filename = Column("filename", String(255))
    _content_type = Column("content_type", String(255))
    _file_id = Column("file_id", String(255))

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, value):
        self._filename = value

    @property
    def content_type(self):
        return self._content_type

    @content_type.setter
    def content_type(self, value):
        self._content_type = value

    @property
    def file_id(self):
        return self._file_id

    @file_id.setter
    def file_id(self, value):
        self._file_id = value

    def __repr__(self):
        return f"<Files id={self.id}>"
