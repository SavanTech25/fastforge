import streamlit as st
import pandas as pd
import requests
from sqlalchemy import create_engine
from decouple import config

# Config
POSTGRES_URI = config("POSTGRES_URI", default="postgresql://user:password@localhost:5432/linkedin_rag")
API_URL = config("API_URL", default="http://localhost:8000")

st.set_page_config(page_title="LinkedIn Post Insights", layout="wide")

st.title("📊 LinkedIn Post Insights & RAG Search")

# Sidebar for Navigation
page = st.sidebar.selectbox("Choose a page", ["KPIs & Data", "AI Post Search"])

if page == "KPIs & Data":
    st.header("📈 Key Performance Indicators")
    
    try:
        engine = create_engine(POSTGRES_URI)
        
        # Load KPIs
        kpi_df = pd.read_sql("SELECT * FROM kpi_posts", con=engine)
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Posts per Author")
            st.bar_chart(kpi_df.set_index("author")["post_count"])
            
        with col2:
            st.subheader("Avg Post Length per Author")
            st.table(kpi_df)
            
        st.divider()
        
        st.header("📄 Cleaned Posts (Silver Layer)")
        int_df = pd.read_sql("SELECT * FROM int_linkedin_posts", con=engine)
        st.dataframe(int_df, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error loading data from Postgres: {e}")
        st.info("Make sure you have run the dbt models and your POSTGRES_URI is correct.")

elif page == "AI Post Search":
    st.header("🔍 AI-Powered Post Search (RAG)")
    st.write("Search through LinkedIn posts using natural language. Powered by Upstash Vector & OpenAI.")
    
    query = st.text_input("What are you looking for?", placeholder="e.g. Find posts about RAG and Upstash")
    
    if st.button("Search") and query:
        with st.spinner("Searching..."):
            try:
                # Call FastAPI RAG endpoint
                response = requests.post(f"{API_URL}/postsearch", json={"query": query})
                if response.status_code == 200:
                    result = response.json()
                    st.markdown(f"### AI Answer:\n{result}")
                else:
                    st.error(f"FastAPI Error: {response.text}")
            except Exception as e:
                st.error(f"Request failed: {e}")
                st.info("Make sure your FastAPI server is running on localhost:8000")

st.sidebar.divider()
st.sidebar.info("Built with FastForge ⚡")
