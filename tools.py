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
import os, json, time 
import undetected_chromedriver as uc

load_dotenv()

class InternshalaApplyTool(BaseTool):
    name:str  = "Internshala Auto Apply Tool"
    description:str = (
        "Logs into Internshala visibly and applies to jobs listed in scraped_jobs.json. "
        "Reads job metadata like title, company, and similarity score."
    )

    def _run(self, *args, **kwargs):
        email = os.getenv("INTERN_EMAIL")
        password = os.getenv("INTERN_PASSWORD")

        if not email or not password:
            return "⚠️ Missing credentials. Add INTERNSHALA_EMAIL and INTERNSHALA_PASSWORD to credentials.env"

        # Open visible Chrome browser
        chrome_options = Options()
        chrome_options.add_experimental_option("detach", True)  # keeps window open
        driver = webdriver.Chrome(options=chrome_options)
        driver.maximize_window()
        wait = WebDriverWait(driver, 20)

        driver.get("https://internshala.com/login")
        print("🌐 Opening Internshala login page...")

        try:
            email_input = wait.until(EC.presence_of_element_located((By.ID, "email")))
            password_input = driver.find_element(By.ID, "password")
            email_input.send_keys(email)
            password_input.send_keys(password)
            driver.find_element(By.ID, "login_submit").click()
            print("✅ Logged in successfully.")
        except Exception as e:
            driver.quit()
            return f"❌ Login failed: {e}"

        time.sleep(5)

        if not os.path.exists("ranked.json"):
            driver.quit()
            return "⚠️ scraped_jobs.json not found."

        with open("ranked.json", "r", encoding="utf-8") as f:
            jobs = json.load(f)

        applied_count = 0
        skipped_jobs = []
        failed_jobs = []

        for job in jobs:
            title = job.get("title", "Unknown Title")
            company = job.get("company", "Unknown Company")
            link = job.get("link")
            score = job.get("similarity_score", 0)

            if not link:
                print(f"⚠️ Skipping job {title} — no link found.")
                continue

            # Skip jobs below threshold similarity
            if score < 0.8:
                print(f"⏩ Skipping {title} ({company}) — similarity {score}")
                skipped_jobs.append(job)
                continue

            try:
                print(f"\n🚀 Applying to {title} at {company}...")
                driver.get(link)
                time.sleep(4)

                # Click "Apply Now"
                apply_button = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Apply')]"))
                )
                apply_button.click()
                time.sleep(2)

                # Try to fill textarea
                try:
                    textarea = wait.until(EC.presence_of_element_located((By.TAG_NAME, "textarea")))
                    textarea.clear()
                    textarea.send_keys(
                        f"Dear {company} team,\n\nI am excited to apply for the {title} position. "
                        f"My background in machine learning and automation aligns closely with your requirements. "
                        "I look forward to contributing effectively.\n\nBest regards,\nRishita Sharma"
                    )
                except:
                    print("✍️ No textarea found, skipping input.")

                # Click submit button
                submit = driver.find_element(By.XPATH, "//button[contains(text(),'Submit application')]")
                submit.click()
                applied_count += 1
                print(f"✅ Successfully applied to {title} at {company}.")
                time.sleep(3)

            except Exception as e:
                print(f"❌ Failed to apply for {title} at {company}: {e}")
                failed_jobs.append({"title": title, "company": company, "error": str(e)})

        driver.quit()

        result = {
            "applied": applied_count,
            "skipped": len(skipped_jobs),
            "failed": len(failed_jobs),
        }

        return f"\n🎯 Process finished.\nApplied: {result['applied']}, Skipped: {result['skipped']}, Failed: {result['failed']}"


file_read_tool = FileReadTool(file_path='skills.txt')

search_tool = ScrapeWebsiteTool(website_url="https://internshala.com/internships/machine-learning-internship")

apply_tool=InternshalaApplyTool()

