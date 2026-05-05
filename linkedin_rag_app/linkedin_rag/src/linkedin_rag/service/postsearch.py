import os
from decouple import config
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

class PostSearchService:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0)
        self.embeddings = OpenAIEmbeddings()
        
        # =====================================================================
        # VECTOR STORE SETUP
        # =====================================================================
        from langchain_community.vectorstores.upstash import UpstashVectorStore
        self.vector_store = UpstashVectorStore(
            embedding=self.embeddings,
            index_url=config("UPSTASH_VECTOR_REST_URL"),
            index_token=config("UPSTASH_VECTOR_REST_TOKEN")
        )
        
    def _retrieve_context(self, query: str) -> str:
        docs = self.vector_store.similarity_search(query, k=3)
        return "\n\n".join([doc.page_content for doc in docs])

    async def invoke(self, query: str, session_id: str = None) -> str:
        template = """Answer the question based only on the following context:
        {context}
        
        Question: {question}
        """
        prompt = PromptTemplate.from_template(template)
        
        chain = (
            {"context": lambda q: self._retrieve_context(q), "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )
        
        return await chain.ainvoke(query)