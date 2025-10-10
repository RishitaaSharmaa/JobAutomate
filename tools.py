from crewai_tools import ScrapeWebsiteTool , FileReadTool

search_tool = ScrapeWebsiteTool(website_url="https://internshala.com/internships/machine-learning-internship")

file_read_tool= FileReadTool(file_path="C:\\Users\\DeLL\\OneDrive\\Documents\\coding\\WebAutomate\\Rishita_Sharma.pdf")