from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import asyncio

from data_collection import TechArticleSearch
from classifier import ContentClassifier
from llm_generator import ReportGenerator
import tools

# --- App Setup ---
app = FastAPI()
report_generator = ReportGenerator()
searcher = TechArticleSearch()
classifier = ContentClassifier()

# Final, robust CORS configuration to prevent connection errors
origins = ["*"] 
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

class ProcessRequest(BaseModel):
    recipient_email: str
    selected_keywords: List[str] = []
    date_filter: str = "w"

@app.post("/api/process")
async def process_request_endpoint(request: ProcessRequest):
    try:
        print("🚀 Task started: Searching for articles...")
        articles = await searcher.run_fed_landscape_search(request.selected_keywords, request.date_filter)
        
        if not articles:
            print("⏹️ Task finished: No articles found.")
            return {
                "status": "success", 
                "articles": [], 
                "report_content": "", 
                "message": "No new articles were found for your selected keywords."
            }

        print(f"🔬 Classifying {len(articles)} articles for relevance...")
        relevance_context = (
            "A relevant article discusses federal activities like new grants, programs, or policy "
            f"affecting universities and innovation ecosystems related to {', '.join(request.selected_keywords)}."
        )
        
        # --- FIX: Reverted to a synchronous loop to call the correct classifier method ---
        for article in articles:
            score = classifier.evaluate_relevance(article.get('full_content', ''), relevance_context)
            article['relevance_score'] = score

        sorted_articles = sorted(articles, key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        print("🤖 Generating final intelligence report...")
        report_title = "TUFF Fed Landscape Report"
        report_content = f"# {report_title}\n\nThis report summarizes recent federal activities.\n\n---\n\n"
        
        for article in sorted_articles[:7]:
            full_summary = report_generator.generate_full_summary(article.get('full_content', ''))
            paragraph = full_summary.get('paragraph', 'Summary not available.')
            points = full_summary.get('points', 'Key points not available.')
            
            report_content += f"## {article.get('title', 'No Title')}\n"
            report_content += f"**Source:** {article.get('source', 'N/A')}\n"
            report_content += f"**Relevance:** {int(article.get('relevance_score', 0) * 100)}%\n\n"
            report_content += f"{paragraph}\n\n**Key Points:**\n{points}\n\n"
            report_content += f"[Read Full Article]({article.get('link', '#')})\n\n---\n\n"

        print("✅ Task completed successfully!")
        
        # --- Send the final data back to the frontend ---
        return {
            "status": "success",
            "articles": sorted_articles,
            "report_content": report_content,
            "message": f"Success! Generated a report from {len(sorted_articles)} articles."
        }

    except Exception as e:
        print(f"❌ Error during processing: {e}")
        return {"status": "error", "message": str(e), "articles": [], "report_content": ""}

