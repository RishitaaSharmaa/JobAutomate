from crewai_tools import  FileReadTool 
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
from selenium.webdriver.common.keys import Keys

load_dotenv()
driver = None


class InternshalaLoginTool(BaseTool):
    name: str = "Internshala Login Tool"
    description: str = (
        "Opens the Internshala login page and waits for the user to log in manually "
        "to avoid CAPTCHA issues. Initializes the global Selenium driver for reuse."
    )

    def _run(self, *args, **kwargs):
        global driver

        chrome_options = Options()
        chrome_options.add_experimental_option("detach", True)
        driver = webdriver.Chrome(options=chrome_options)

        print("🚀 Opening Internshala login page...")
        driver.get("https://internshala.com/login")

        print("\n🔑 Please log in manually in the browser window.")
        print("⚠️ Solve any CAPTCHA if prompted.")
        print("Once you are successfully logged in and your dashboard is visible, press ENTER here to continue...")

        # Wait for user confirmation in console
        input("👉 Press ENTER after you’ve logged in: ")

        try:
            # Verify login by checking if the dashboard/homepage is loaded
            wait = WebDriverWait(driver, 60)
            wait.until(
                EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/internships')]"))
            )
            print("✅ Login detected. Global driver initialized successfully.")
            return "Login successful. You may now use other tools with this driver."
        except Exception as e:
            return f"❌ Login verification failed: {e}"
        


class ScrapeWebsiteTool(BaseTool):
    name: str = "Internshala Scraper Tool"
    description: str = "Scrapes internships using the globally shared Selenium driver."

    def _run(self, *args, **kwargs):
        global driver

        if driver is None:
            return "No global driver found. Please run the login tool first."

        website_url = "https://internshala.com/internships/machine-learning-internship"

        try:
            print(f"Navigating to {website_url} ...")
            driver.get(website_url)
            time.sleep(10)

            # Scroll for lazy-loaded content
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            # Locate internships - match any div with 'individual_internship'
            containers = driver.find_elements(By.XPATH, "//div[contains(@class, 'individual_internship')]")
            print(f"Found {len(containers)} internship containers")

            internships_data = []

            for container in containers:
                # Extract title
                title = ""
                for tag in ["h3", "h4", "h5"]:
                    els = container.find_elements(By.TAG_NAME, tag)
                    if els and els[0].text.strip():
                        title = els[0].text.strip()
                        break
                if not title:
                    strongs = container.find_elements(By.TAG_NAME, "strong")
                    if strongs and strongs[0].text:
                        title = strongs[0].text.strip()

                # Extract company
                company = ""
                possible = container.find_elements(By.XPATH, ".//span | .//div")
                for p in possible:
                    tx = p.text.strip()
                    if tx and len(tx) < 64 and (
                        "Pvt" in tx or "Ltd" in tx or "Limited" in tx or "Private" in tx
                    ):
                        company = tx
                        break
                if not company and possible:
                    company = possible[0].text.strip()

                # Extract link
                link = ""
                anchors = container.find_elements(By.TAG_NAME, "a")
                for a in anchors:
                    href = a.get_attribute("href")
                    if href and "internship/detail" in href:
                        link = href
                        break

                internships_data.append({
                    "title": title,
                    "company": company,
                    "link": link
                })

            print(f"Successfully extracted {len(internships_data)} internships")
            return {"internships": internships_data}

        except Exception as e:
            print(f"Scraping failed: {e}")
            with open("debug_internshala.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            return {"internships": [], "error": str(e)}


class InternshalaApplyTool(BaseTool):
    name: str = "Internshala Apply Tool"
    description: str = (
        "Uses the global logged-in Selenium driver to apply to each internship listed in webdata.json using the provided resume."
    )

    def _run(self, *args, **kwargs):
        global driver

        ranked_file = kwargs.get("ranked_file", "webdata.json")
        resume_path = kwargs.get("resume_path", "Rishita_Sharma.pdf")

        # Check global driver and file availability
        if driver is None:
            return "No active driver found. Please run the login tool first."
        if not os.path.exists(ranked_file):
            return f"{ranked_file} not found."
        if not os.path.exists(resume_path):
            return f"Resume file '{resume_path}' not found."

        # Load internship data
        with open(ranked_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Extract the internship list safely
        ranked_jobs = data.get("internships", [])

        wait = WebDriverWait(driver, 20)
        results = []

        for job in ranked_jobs:
            job_title = job.get("title", "Unknown Job")
            job_link = job.get("link")

            if not job_link:
                continue

            try:
                print(f"Opening {job_title} ...")
                driver.get(job_link)
                time.sleep(3)

                # Click "Apply" button
                apply_btn = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Apply')]"))
                )
                apply_btn.click()
                time.sleep(2)

                # Upload resume
                upload_input = wait.until(
                    EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
                )
                upload_input.send_keys(os.path.abspath(resume_path))
                print(f"Uploaded resume for {job_title}")

                # Click "Submit" button
                submit_btn = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Submit')]"))
                )
                submit_btn.click()
                print(f"Successfully applied to {job_title}")

                results.append({
                    "job": job_title,
                    "link": job_link,
                    "status": "Applied"
                })

                time.sleep(3)

            except Exception as e:
                print(f"Failed for {job_title}: {e}")
                results.append({
                    "job": job_title,
                    "link": job_link,
                    "status": f"Failed - {str(e)}"
                })
                continue

        # Save application log
        with open("Applied.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=4)

        return results

    
    
login_tool=InternshalaLoginTool()    
# login_tool.run()

search_tool = ScrapeWebsiteTool(
    website_url="https://internshala.com/internships/machine-learning-internship"
    )
# search_tool.run()
file_read_tool=FileReadTool(file_path="skills.txt")

apply_tool = InternshalaApplyTool()
# apply_tool.run()
