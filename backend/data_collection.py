import os
import httpx
from dotenv import load_dotenv
import asyncio
from typing import List
from bs4 import BeautifulSoup

load_dotenv()

class TechArticleSearch:
    def __init__(self):
        self.api_key = os.getenv("SERPER_API_KEY")
        if not self.api_key:
            raise ValueError("SERPER_API_KEY not found.")
        # Common browser user-agent to avoid being blocked
        self.scraping_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        self.search_headers = {"X-API-KEY": self.api_key, "Content-Type": "application/json"}

    async def _scrape_content(self, article: dict) -> dict:
        """Asynchronously scrapes content from a single article URL using a browser-like header."""
        print(f"  -> Scraping: {article.get('link')}")
        async with httpx.AsyncClient(headers=self.scraping_headers, follow_redirects=True, timeout=20.0) as client:
            try:
                res = await client.get(article['link'])
                res.raise_for_status()
                
                soup = BeautifulSoup(res.text, 'html.parser')
                paragraphs = soup.find_all('p')
                full_content = ' '.join([p.get_text(strip=True) for p in paragraphs])
                
                if len(full_content) < 200:
                    full_content = soup.body.get_text(strip=True, separator=' ')

                article['full_content'] = full_content
                return article
            except Exception as e:
                print(f"  -> ❌ Failed to scrape {article.get('link')}: {e}")
                article['full_content'] = None
                return article

    async def _search_and_scrape_single_query(self, query: str, date_filter: str) -> list:
        print(f"🔎 Running search query: '{query}' for date range '{date_filter}'")
        api_url = "https://google.serper.dev/news"
        payload = {"q": query, "tbs": f"qdr:{date_filter}"}
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(api_url, headers=self.search_headers, json=payload)
                response.raise_for_status()
            return response.json().get("news", [])
        except Exception as e:
            print(f"❌ API search for query '{query}' failed: {e}")
            return []

    async def run_fed_landscape_search(self, selected_keywords: List[str], date_filter: str = "w") -> list:
        if not selected_keywords:
            return []

        search_queries = []
        for keyword in selected_keywords:
            query = (
                f'"{keyword}" AND '
                f'("university research funding" OR "federal grant" OR "innovation ecosystem" OR "R&D policy") AND '
                f'(site:.gov OR site:.edu OR site:.org) -jobs -admissions -curriculum'
            )
            search_queries.append(query)
        
        tasks = [self._search_and_scrape_single_query(q, date_filter) for q in search_queries]
        results_from_all_searches = await asyncio.gather(*tasks)

        combined_articles = {}
        for result_list in results_from_all_searches:
            for article in result_list:
                if article.get('link') and article['link'] not in combined_articles:
                    combined_articles[article['link']] = article
        
        unique_articles = list(combined_articles.values())[:7]
        print(f"Found {len(unique_articles)} unique articles to scrape.")
        
        if not unique_articles:
            return []

        # --- PERFORMANCE IMPROVEMENT ---
        # We are now running the scraping tasks in parallel again for a significant speed boost.
        scraping_tasks = [self._scrape_content(article) for article in unique_articles]
        full_articles = await asyncio.gather(*scraping_tasks)
        
        valid_articles = [art for art in full_articles if art.get('full_content')]
        print(f"✅ Scraped content from {len(valid_articles)} valid articles.")
        return valid_articles
