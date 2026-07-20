# test_ingest.py
from ingest_service import insert_job_description

# Notice the tricky single quotes and punctuation in the raw text ('AI Product Engineer's role')
test_title = "AI Product Engineer"
test_company = "Cosmos Nexus Labs"
test_text = "Here is a manager's draft for the AI Product Engineer's role. Must know Python, PostgreSQL, and LLMs."
test_keywords = ["Python", "PostgreSQL", "LLMs", "AI Product Engineering"]

print("🚀 Testing safe data ingestion...")
new_id = insert_job_description(test_title, test_company, test_text, test_keywords)