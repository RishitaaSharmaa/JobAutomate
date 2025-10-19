from crewai_tools import ScrapeWebsiteTool , FileReadTool 
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv
import os, json, time 
import undetected_chromedriver as uc
import undetected_chromedriver as uc
from selenium.webdriver.common.keys import Keys

load_dotenv()
class InternshalaLoginTool(BaseTool):
    name: str = "Internshala Login Tool"
    description: str = "Logs into Internshala and stores the Selenium driver for reuse."

    def _run(self, context=None, *args, **kwargs):
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        import time, os

        email = os.getenv("INTERN_EMAIL")
        password = os.getenv("INTERN_PASSWORD")

        chrome_options = Options()
        chrome_options.add_experimental_option("detach", True)
        driver = webdriver.Chrome(options=chrome_options)
        driver.get("https://internshala.com/login")

        wait = WebDriverWait(driver, 20)
        email_box = wait.until(EC.presence_of_element_located((By.ID, "email")))
        password_box = driver.find_element(By.ID, "password")

        for c in email:
            email_box.send_keys(c)
            time.sleep(0.1)
        for c in password:
            password_box.send_keys(c)
            time.sleep(0.1)
        driver.find_element(By.ID, "login_submit").click()

        print("✅ Logged in. Solve CAPTCHA if prompted.")
        time.sleep(20)

        # 🧠 Store driver in CrewAI context so the next tool can access it
        if context is not None:
            context["driver"] = driver

        return "Login successful and driver stored in context."

file_read_tool = FileReadTool(file_path='skills.txt')

class ScrapeWebsiteTool(BaseTool):
    name: str = "Internshala Scraper Tool"
    description: str = "Scrapes internships using an existing logged-in browser session."

    def _run(self, context=None, website_url=None, *args, **kwargs):
        driver = None

        # 🧠 Reuse driver from login tool
        if context and "driver" in context:
            driver = context["driver"]

        if not driver:
            return "⚠️ No driver found. Make sure login_tool ran first."

        try:
            print(f"🌐 Navigating to {website_url} ...")
            driver.get(website_url)
            time.sleep(5)

            internships = driver.find_elements(By.CLASS_NAME, "heading_4_5")
            data = [i.text for i in internships if i.text.strip()]

            return {"internships": data}

        except Exception as e:
            print(f"❌ Scraping failed: {e}")
            return str(e)



class InternshalaApplyTool(BaseTool):
    name: str = "Internshala Apply Tool"
    description: str = (
        "Opens each internship link from ranked.json, uploads the given resume, and submits the application using Selenium."
    )

    def _run(self, *args, **kwargs):
        ranked_file = kwargs.get("ranked_file", "ranked.json")
        resume_path = kwargs.get("resume_path", "Rishita_Sharma.pdf")

        if not os.path.exists(ranked_file):
            return f" {ranked_file} not found."
        if not os.path.exists(resume_path):
            return f" Resume file '{resume_path}' not found."

        with open(ranked_file, "r", encoding="utf-8") as f:
            ranked_jobs = json.load(f)

        results = []

        chrome_options = Options()
        chrome_options.add_experimental_option("detach", True)
        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 20)

        for job in ranked_jobs:
            job_title = job.get("title", "Unknown Job")
            job_link = job.get("link")

            if not job_link:
                continue

            try:
                print(f" Opening {job_title} ...")
                driver.get(job_link)

                apply_btn = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Apply')]"))
                )
                apply_btn.click()
                time.sleep(2)

                upload_input = wait.until(
                    EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
                )
                upload_input.send_keys(os.path.abspath(resume_path))
                print(f" Uploaded resume for {job_title}")

                submit_btn = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Submit')]"))
                )
                submit_btn.click()

                print(f" Successfully applied to {job_title}")
                results.append({"job": job_title, "link": job_link, "status": "Applied"})

                time.sleep(3)

            except Exception as e:
                print(f" Failed for {job_title}: {e}")
                results.append({
                    "job": job_title,
                    "link": job_link,
                    "status": f"Failed - {str(e)}"
                })
                continue

        driver.quit()

        with open("Applied.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=4)

        return results
    
login_tool=InternshalaLoginTool()
success=login_tool.run()
print(success)    
search_tool = ScrapeWebsiteTool(
    website_url="https://internshala.com/internships/machine-learning-internship"
    )
text=search_tool.run()
print(text)


apply_tool = InternshalaApplyTool()