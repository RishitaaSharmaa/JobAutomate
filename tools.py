from crewai_tools import ScrapeWebsiteTool , FileReadTool 
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from PyPDF2 import PdfReader
from crewai_tools import SeleniumScrapingTool
from crewai_tools import FileReadTool

file_read_tool = FileReadTool(file_path='skills.txt')

search_tool = ScrapeWebsiteTool(website_url="https://internshala.com/internships/machine-learning-internship")


# apply_tool=SeleniumScrapingTool()


from dotenv import load_dotenv
import os, time, json

load_dotenv()

class InternshalaApplyTool(SeleniumScrapingTool):
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

                print(f"🚀 Applying to {job_title} at {company}...")
                driver.get(job_link)
                time.sleep(3)

                # Click Apply button if present
                apply_button = driver.find_element("xpath", "//button[contains(text(),'Apply')]")
                apply_button.click()
                time.sleep(3)

                # Upload resume
                upload = driver.find_element("xpath", "//input[@type='file']")
                upload.send_keys(os.path.abspath(resume_path))
                time.sleep(3)

                # Submit application
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

        # Save application results
        with open("Applied.json", "w", encoding="utf-8") as f:
            json.dump(applied_jobs, f, indent=2)
        print("📄 Results saved in Applied.json")

    def _run(self, *args, **kwargs):
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options

        # Configure Chrome
        options = Options()
        options.add_argument("--start-maximized")

        service = Service()
        driver = webdriver.Chrome(service=service, options=options)

        resume_path = "Rishita_Sharma.pdf"

        try:
            self._login(driver)

            # Load ranked jobs
            with open("ranked.json", "r", encoding="utf-8") as f:
                ranked_jobs = json.load(f)

            # Apply to jobs
            self._apply_to_jobs(driver, ranked_jobs, resume_path)

        finally:
            driver.quit()
            print("🧹 Browser closed.")
            return "All jobs processed."

# Initialize the tool
apply_tool = InternshalaApplyTool()
