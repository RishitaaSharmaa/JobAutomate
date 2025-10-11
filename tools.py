from crewai_tools import ScrapeWebsiteTool , FileReadTool 
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from PyPDF2 import PdfReader

search_tool = ScrapeWebsiteTool(website_url="https://internshala.com/internships/machine-learning-internship")

# file_read_tool= FileReadTool(file_path="C:\\Users\\DeLL\\OneDrive\\Documents\\coding\\WebAutomate\\Rishita_Sharma.pdf")


class PDFReaderInput(BaseModel):
    pdf_path: str = Field(..., description="Path to the PDF file to extract text from")

class PDFReaderTool(BaseTool):
    name: str = "PDF Reader Tool"
    description: str = "Reads a PDF file and returns its full text content."
    args_schema: Type[BaseModel] = PDFReaderInput

    def _run(self, pdf_path: str) -> str:  
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            return text if text.strip() else "No text could be extracted from the PDF."
        except Exception as e:
            return f"Error reading PDF: {str(e)}"


pdf_tool = PDFReaderTool()
result_text = pdf_tool.run(pdf_path="Rishita_Sharma.pdf")

