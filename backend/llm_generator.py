import os
from openai import OpenAI, APIError
from dotenv import load_dotenv

load_dotenv()

class ReportGenerator:
    """
    Uses OpenAI's powerful language models to generate high-quality, structured summaries.
    """
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("⚠️ OpenAI API key not found. Summarization will be basic.")
            self.client = None
        else:
            self.client = OpenAI(api_key=api_key)
            print("✅ Report Generator configured to use OpenAI GPT-4o.")

    # --- NEW: Main public method to get both summaries ---
    def generate_full_summary(self, article_content: str) -> dict:
        """
        Generates a full summary for an article, including a short paragraph
        and a 5-point bulleted list.

        Returns:
            A dictionary with 'paragraph' and 'points' as keys.
            Example: {'paragraph': 'A short summary...', 'points': '- Point 1...'}
        """
        if not self.client or not article_content:
            return {
                "paragraph": "No content provided or OpenAI client not configured.",
                "points": "No content provided or OpenAI client not configured."
            }
        
        # Call the specialized methods for each summary type
        paragraph_summary = self._generate_paragraph_summary(article_content)
        point_summary = self._generate_point_summary(article_content)

        return {
            "paragraph": paragraph_summary,
            "points": point_summary
        }

    # --- NEW: Internal method for the 1-2 sentence paragraph summary ---
    def _generate_paragraph_summary(self, article_content: str) -> str:
        """
        Generates a very short, 1-2 sentence paragraph summary for an article.
        """
        system_prompt = (
            "You are a specialized analyst for a university-focused real estate investment trust (TUFF). "
            "Your task is to read a news article and produce a very concise, 1-2 sentence paragraph summary. "
            "This summary should capture the core idea or main takeaway of the article, providing a quick, "
            "high-level overview. It must be a single, short paragraph."
        )
        
        user_prompt = f"Please create a 1-2 sentence paragraph summary for the following article:\n\n---\n\n{article_content}"

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=150,
            )
            return response.choices[0].message.content.strip()

        except APIError as e:
            print(f"❌ OpenAI API error during paragraph summary generation: {e}")
            return "Failed to generate paragraph summary due to an API error."
        except Exception as e:
            print(f"❌ An unexpected error occurred during paragraph summary generation: {e}")
            return "An unexpected error occurred."

    # --- UPDATED: Your original method, now an internal helper for the 5-point summary ---
    def _generate_point_summary(self, article_content: str) -> str:
        """
        Generates a concise, 5-point technical summary for a single article's content.
        """
        system_prompt = (
            "You are a specialized analyst for a university-focused real estate investment trust (TUFF). "
            "Your task is to read a news article and produce a concise, technical, 5-point summary. "
            "Focus on details relevant to federal grants, research funding, innovation ecosystems, "
            "semiconductors, AI policy, and economic development affecting universities. "
            "Each point should be a distinct, informative bullet."
        )
        
        user_prompt = f"Please create a 5-point bulleted summary for the following article:\n\n---\n\n{article_content}"

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=300,
            )
            summary = response.choices[0].message.content.strip()
            summary_lines = [line.strip() for line in summary.split('\n') if line.strip()]
            return "\n".join(summary_lines)

        except APIError as e:
            print(f"❌ OpenAI API error during point summarization: {e}")
            return "Failed to generate summary due to an API error."
        except Exception as e:
            print(f"❌ An unexpected error occurred during point summarization: {e}")
            return "An unexpected error occurred."
