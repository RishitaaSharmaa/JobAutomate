from crewai_tools import ScrapeWebsiteTool , FileReadTool 
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from PyPDF2 import PdfReader
from crewai_tools import SeleniumScrapingTool
from crewai_tools import FileReadTool

from dotenv import load_dotenv
import os, time, json


file_read_tool = FileReadTool(file_path='skills.txt')

search_tool = ScrapeWebsiteTool(website_url="https://internshala.com/internships/machine-learning-internship")


load_dotenv()

from crewai_tools import ScrapeWebsiteTool, SeleniumScrapingTool, FileReadTool
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from PyPDF2 import PdfReader
import os, time, json


load_dotenv()

class InternshalaApplyInput(BaseModel):
    ranked_jobs_path: str = Field(..., description="Path to the ranked jobs JSON file")
    resume_path: str = Field(..., description="Path to the resume PDF file")


class InternshalaApplyTool(SeleniumScrapingTool):
    name: str = "Internshala Apply Tool"
    description: str = "Logs into Internshala and applies to ranked internships using Selenium automation."
    args_schema: Type[BaseModel] = InternshalaApplyInput


    def _login(self, driver):
        email = os.getenv("INTERN_EMAIL")
        password = os.getenv("INTERN_PASSWORD")

        print("Logging into Internshala...")
        driver.get("https://internshala.com/login")
        time.sleep(3)

        driver.find_element("id", "email").send_keys(email)
        driver.find_element("id", "password").send_keys(password)
        driver.find_element("xpath", "//button[contains(text(),'Login')]").click()
        time.sleep(4)
        print("✅ Logged in successfully!")

    def _apply_to_jobs(self, driver, ranked_jobs, resume_path):
        applied_jobs = []

        for job in ranked_jobs:
            try:
                job_link = job.get("apply_link")
                job_title = job.get("job_title")
                company = job.get("company")

                print(f"Applying to {job_title} at {company}...")
                driver.get(job_link)
                time.sleep(3)

                apply_button = driver.find_element("xpath", "//button[contains(text(),'Apply')]")
                apply_button.click()
                time.sleep(3)

                upload = driver.find_element("xpath", "//input[@type='file']")
                upload.send_keys(os.path.abspath(resume_path))
                time.sleep(3)

                submit_btn = driver.find_element("xpath", "//button[contains(text(),'Submit')]")
                submit_btn.click()
                time.sleep(3)

                print(f"✅ Applied successfully to {job_title}")
                applied_jobs.append({
                    "job_title": job_title,
                    "company": company,
                    "apply_link": job_link,
                    "status": "Applied successfully"
                })
            except Exception as e:
                print(f"❌ Failed to apply for {job.get('job_title')}: {str(e)}")
                applied_jobs.append({
                    "job_title": job.get("job_title"),
                    "company": job.get("company"),
                    "apply_link": job.get("apply_link"),
                    "status": f"Failed: {str(e)}"
                })

        with open("Applied.json", "w", encoding="utf-8") as f:
            json.dump(applied_jobs, f, indent=2)

        print("Results saved in Applied.json")

    def run(self, ranked_jobs_path: str, resume_path: str):
        """Main entry point for CrewAI"""
        options = Options()
        options.add_argument("--start-maximized")

        service = Service()
        driver = webdriver.Chrome(service=service, options=options)

        try:
            self._login(driver)
            with open(ranked_jobs_path, "r", encoding="utf-8") as f:
                ranked_jobs = json.load(f)
            self._apply_to_jobs(driver, ranked_jobs, resume_path)
        finally:
            driver.quit()
            print("Browser closed.")

        return "All jobs processed successfully."


# Example usage:
apply_tool = InternshalaApplyTool()
