from crewai_tools import ScrapeWebsiteTool , FileReadTool

search_tool = ScrapeWebsiteTool(website_url="https://internshala.com/internships/machine-learning-internship")

file_read_tool= FileReadTool(file_path="Rishita_Sharma (1).pdf")