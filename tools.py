from crewai_tools import ScrapeWebsiteTool , FileReadTool 
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from PyPDF2 import PdfReader
from crewai_tools import SeleniumScrapingTool
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv
import os, json, time , random
import undetected_chromedriver as uc


file_read_tool = FileReadTool(file_path='skills.txt')

search_tool = ScrapeWebsiteTool(website_url="https://internshala.com/internships/machine-learning-internship")



load_dotenv()


# ---------- INPUT SCHEMA ----------
class InternshalaApplyInput(BaseModel):
    ranked_jobs_path: str = Field(..., description="Path to ranked jobs JSON file")
    resume_path: str = Field(..., description="Path to resume PDF file")
    debug_mode: bool = Field(default=True, description="If True, shows browser & logs each step")


# ---------- TOOL DEFINITION ----------
class InternshalaApplyTool(SeleniumScrapingTool):
    name: str = "Internshala Apply Tool"
    description: str = "Automates Internshala job applications using undetected Chrome and Selenium."
    args_schema: Type[BaseModel] = InternshalaApplyInput

    # ========== LOGIN ==========
    def _login(self, driver):
        email = os.getenv("INTERN_EMAIL")
        password = os.getenv("INTERN_PASSWORD")

        print("🔐 Logging into Internshala...")
        driver.get("https://internshala.com/login")
        wait = WebDriverWait(driver, 25)

        email_box = wait.until(EC.presence_of_element_located((By.ID, "email")))
        email_box.send_keys(email)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.XPATH, "//button[contains(text(),'Login')]").click()

        time.sleep(random.uniform(3, 5))
        print("✅ Logged in successfully!\n")

    # ========== APPLY ==========
    def _apply_to_jobs(self, driver, ranked_jobs, resume_path, debug_mode):
        wait = WebDriverWait(driver, 20)
        os.makedirs("screenshots", exist_ok=True)
        applied_jobs = []

        for i, job in enumerate(ranked_jobs, start=1):
            try:
                job_link = job.get("apply_link")
                job_title = job.get("job_title")
                company = job.get("company")

                print(f"[{i}] Applying to {job_title} at {company}...")
                driver.get(job_link)
                time.sleep(random.uniform(3, 5))
                driver.save_screenshot(f"screenshots/step_{i}_opened.png")

                # Step 1: Click "Apply Now"
                apply_btn = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Apply Now')]"))
                )
                apply_btn.click()
                time.sleep(random.uniform(2, 4))

                # Step 2: Upload resume
                try:
                    upload_input = wait.until(
                        EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
                    )
                    upload_input.send_keys(os.path.abspath(resume_path))
                    print("📎 Resume uploaded.")
                    time.sleep(random.uniform(2, 3))
                except Exception:
                    print("No file upload found, skipping upload.")

                # Step 3: Click Submit
                submit_btn = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Submit')]"))
                )
                submit_btn.click()
                time.sleep(random.uniform(3, 5))
                driver.save_screenshot(f"screenshots/step_{i}_submitted.png")

                # Step 4: Check confirmation
                page = driver.page_source.lower()
                if "application submitted" in page or "applied successfully" in page:
                    status = "Applied successfully"
                else:
                    status = "Submission uncertain"
                print(status)

                applied_jobs.append({
                    "job_title": job_title,
                    "company": company,
                    "apply_link": job_link,
                    "status": status
                })

            except Exception as e:
                print(f"Error applying for {job.get('job_title')}: {str(e)}")
                applied_jobs.append({
                    "job_title": job.get("job_title"),
                    "company": job.get("company"),
                    "apply_link": job.get("apply_link"),
                    "status": f"Failed: {str(e)}"
                })

        # Save summary
        with open("Applied.json", "w", encoding="utf-8") as f:
            json.dump(applied_jobs, f, indent=2)
        print("\nResults saved in Applied.json")

    # ========== MAIN ENTRY ==========
    def run(self, ranked_jobs_path: str, resume_path: str, debug_mode: bool = True):
        print("Starting Internshala automation...")

        options = uc.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")

        # Optional: Use your real Chrome profile to prevent detection
        # options.add_argument("--user-data-dir=C:\\Users\\DeLL\\AppData\\Local\\Google\\Chrome\\User Data")
        # options.add_argument("--profile-directory=Default")

        driver = uc.Chrome(options=options)
        print("Browser launched (Visible Mode)" if debug_mode else "🤖 Running headless...")

        try:
            self._login(driver)
            with open(ranked_jobs_path, "r", encoding="utf-8") as f:
                ranked_jobs = json.load(f)
            self._apply_to_jobs(driver, ranked_jobs, resume_path, debug_mode)

            if debug_mode:
                print("Leaving browser open for inspection (debug mode).")
                input("Press Enter to close the browser...")
        finally:
            driver.quit()
            print(" Browser closed.\n")

        return "Automation finished!"

# Example usage:
apply_tool = InternshalaApplyTool()
