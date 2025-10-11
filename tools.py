from crewai_tools import ScrapeWebsiteTool , FileReadTool 
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from PyPDF2 import PdfReader

search_tool = ScrapeWebsiteTool(website_url="https://internshala.com/internships/machine-learning-internship")

# file_read_tool= FileReadTool(file_path="C:\\Users\\DeLL\\OneDrive\\Documents\\coding\\WebAutomate\\Rishita_Sharma.pdf")


class MyToolInput(BaseModel):
    argument: str =Field(..., description="Path to the PDF file")

class PDFReaderTool(BaseTool):
    name: str = "PDFReader"
    description: str = "Reads a PDF file and returns its full text context. "
    args_schema: Type[BaseModel] = MyToolInput

    def _run(self , pdf_path: str)-> str:
        reader=PdfReader(pdf_path)
        pages=[]
        for page in reader.pages:
            text=page.extract_text()
            if text:
                pages.append(text)
        full_text= "\n".join(pages)
        return full_text
    

pdf_tool = PDFReaderTool()
result_text = pdf_tool.run(pdf_path="Rishita_Sharma.pdf")

