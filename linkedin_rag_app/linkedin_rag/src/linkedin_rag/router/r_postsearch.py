from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from linkedin_rag.service.postsearch import PostSearchService
from linkedin_rag.middleware.middleware import JWTBearer

r_postsearch = APIRouter(prefix="/postsearch", tags=["PostSearch"])

class PostSearchRequest(BaseModel):
    query: str
    session_id: str | None = None

@r_postsearch.post("", dependencies=[Depends(JWTBearer())])
async def execute_postsearch(req: PostSearchRequest):
    try:
        service = PostSearchService()
        result = await service.invoke(req.query, req.session_id)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))