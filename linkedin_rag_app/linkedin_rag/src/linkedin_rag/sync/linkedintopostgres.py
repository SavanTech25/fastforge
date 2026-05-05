from loguru import logger
from decouple import config
from pymongo import MongoClient
import pandas as pd
from sqlalchemy import create_engine
from apscheduler.schedulers.blocking import BlockingScheduler

# Config
API_URL = config("API_URL", default="https://api.example.com/data")
API_KEY = config("API_KEY", default="")

POSTGRES_URI = config("POSTGRES_URI", default="postgresql://user:password@localhost:5432/linkedin_rag")

# Define which collections/endpoints to sync
SYNC_TARGETS = [
    "raw_linkedin_posts"
]

def get_mock_linkedin_posts():
    """Generates mock LinkedIn posts about Data and AI."""
    return [
        {"id": 1, "text": "AI is transforming the way we handle big data in 2024! #AI #DataScience", "author": "Alice", "created_at": "2024-05-04 10:00:00"},
        {"id": 2, "text": "Just implemented a RAG system with Upstash and it works like a charm. #RAG #Upstash", "author": "Bob", "created_at": "2024-05-04 11:30:00"},
        {"id": 3, "text": "Data engineering is the foundation of any successful AI project. #DataEngineering", "author": "Charlie", "created_at": "2024-05-04 12:45:00"},
        {"id": 4, "text": "New LinkedIn API updates are making it easier to fetch last posts. #LinkedInAPI", "author": "Dave", "created_at": "2024-05-04 14:15:00"},
    ]

def sync_data():
    logger.info(f"Starting ELT sync: Mock LinkedIn API -> Postgres")
    try:
        # Destination Connection
        engine = create_engine(POSTGRES_URI)
        
        for target in SYNC_TARGETS:
            logger.info(f"Extracting '{target}' from mock API...")
            
            data = get_mock_linkedin_posts()
            df = pd.DataFrame(data)
            
            if df.empty:
                logger.info(f"Target '{target}' is empty. Skipping.")
                continue
                
            logger.info(f"Loading {len(df)} records into postgres table '{target}'...")
            
            # Loading Logic
            df.to_sql(name=target, con=engine, if_exists="replace", index=False)
            
            logger.info(f"Successfully synced '{target}'.")

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