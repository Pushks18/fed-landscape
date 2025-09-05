import os
from arcadepy import Arcade
from dotenv import load_dotenv

load_dotenv()

# --- Initialize Arcade Client ---
ARCADE_API_KEY = os.getenv("ARCADE_API_KEY")
USER_ID = os.getenv("ARCADE_USER_ID")

if not all([ARCADE_API_KEY, USER_ID]):
    raise ValueError("ARCADE_API_KEY and ARCADE_USER_ID must be set in the .env file.")

client = Arcade(api_key=ARCADE_API_KEY)

# --- Tool Definitions ---

def create_document_from_articles(articles: list, keywords: str) -> str:
    """Formats a list of articles into a single text document."""
    print("📄 Creating document content...")
    if not articles:
        return "No articles were found for the given keywords."

    doc_content = f"# Tech Article Summary: {keywords.title()}\n\n"
    doc_content += "Here are the top articles found based on your request:\n\n---\n\n"

    for article in articles:
        doc_content += f"## {article.get('title', 'No Title')}\n"
        doc_content += f"**Source:** {article.get('source', 'N/A')}\n"
        doc_content += f"**Link:** {article.get('link', '#')}\n\n"
        doc_content += f"**Summary:** {article.get('snippet', 'No summary available.')}\n\n---\n\n"
    
    print("✅ Document content created.")
    return doc_content

def add_content_to_gdoc(content: str, file_name: str = "AI Intelligence Report") -> str:
    """
    Creates a new Google Doc with the provided text content and returns its URL.
    """
    if not USER_ID:
        return "Error: ARCADE_USER_ID is not set in the .env file."
    print(f"TOOL CALLED: Creating Google Doc titled '{file_name}'...")
    try:
        # --- FIX: Corrected the case sensitivity of the Google Docs tool name ---
        result = client.tools.execute(
            tool_name="googledocs.CreateDocumentFromText@4.1.0",
            input={"title": file_name, "text_content": content},
            user_id=USER_ID,
        )

        if result.status in ["completed", "success"] and hasattr(result, 'output') and hasattr(result.output, 'value'):
            doc_url = result.output.value.get("documentUrl")
            if doc_url:
                print(f"✅ Google Doc created successfully: {doc_url}")
                return doc_url
        
        error_detail = result.output if hasattr(result, 'output') else 'No output detail.'
        print(f"❌ Arcade tool failed with status: {result.status}, detail: {error_detail}")
        return "Failed to create the Google Document."

    except Exception as e:
        print(f"ERROR: Arcade tool execution failed: {e}")
        return "Failed to create the Google Document due to an error."

def send_email(email_body: str, subject: str, recipient: str):
    """Sends an email with the provided content as the body."""
    print(f"📧 Calling Arcade to send email to {recipient}...")
    try:
        result = client.tools.execute(
            tool_name="Gmail.SendEmail@3.0.0",
            input={"body": email_body, "subject": subject, "recipient": recipient},
            user_id=USER_ID,
        )
        if result.status in ["completed", "success"]:
            print("✅ Email sent successfully!")
            return True
        else:
            error_detail = result.output if hasattr(result, 'output') else 'No output detail.'
            print(f"❌ Arcade tool failed with status: {result.status}, detail: {error_detail}")
            return False
    except Exception as e:
        print(f"❌ ERROR: Arcade tool execution failed: {e}")
        return False
