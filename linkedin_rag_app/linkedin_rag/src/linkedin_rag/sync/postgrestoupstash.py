from loguru import logger
from decouple import config
from pymongo import MongoClient
import pandas as pd
from sqlalchemy import create_engine
from apscheduler.schedulers.blocking import BlockingScheduler

# Config

UPSTASH_VECTOR_URL = config("UPSTASH_VECTOR_REST_URL")
UPSTASH_VECTOR_TOKEN = config("UPSTASH_VECTOR_REST_TOKEN")

POSTGRES_URI = config("POSTGRES_URI", default="postgresql://user:password@localhost:5432/linkedin_rag")
OPENAI_API_KEY = config("OPENAI_API_KEY")

# Define which collections/endpoints to sync
SYNC_TARGETS = [
    "int_linkedin_posts"
]

def sync_data():
    logger.info(f"Starting ELT sync: postgres -> upstash")
    try:
        # Source Connection
        engine = create_engine(POSTGRES_URI)
        
        # Destination Connection
        from upstash_vector import Index
        from langchain_openai import OpenAIEmbeddings
        
        index = Index(url=UPSTASH_VECTOR_URL, token=UPSTASH_VECTOR_TOKEN)
        embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY)
        
        for target in SYNC_TARGETS:
            logger.info(f"Extracting '{target}' from postgres...")
            
            df = pd.read_sql(f"SELECT * FROM {target}", con=engine)
            
            if df.empty:
                logger.info(f"Target '{target}' is empty. Skipping.")
                continue
                
            logger.info(f"Indexing {len(df)} records into Upstash Vector index...")
            
            for i, row in df.iterrows():
                # Generate vector for the post text
                vector = embeddings.embed_query(row['text'])
                
                # Metadata to store
                metadata = {
                    "text": row['text'],
                    "author": row.get('author', 'Unknown'),
                    "created_at": str(row.get('created_at', ''))
                }
                
                # Upsert to Upstash
                index.upsert(vectors=[(str(row.get('id', i)), vector, metadata)])
            
            logger.info(f"Successfully synced and indexed '{target}'.")

        logger.info("Sync completed successfully.")

    except Exception as e:
        logger.error(f"Sync failed: {e}")
    finally:
        engine.dispose()

if __name__ == "__main__":
    # To run immediately:
    # sync_data()
    
    # To run on a schedule (e.g. every hour):
    logger.info("Starting ELT Scheduler...")
    scheduler = BlockingScheduler()
    scheduler.add_job(sync_data, 'interval', hours=1)
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass