from linkedin_rag.utils.crud_router import create_crud_router
from linkedin_rag.entity.files import Files
from linkedin_rag.schema.files import FilesCreate

r_files = create_crud_router(Files, FilesCreate, "files")