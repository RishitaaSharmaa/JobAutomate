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
from selenium.webdriver.common.action_chains import ActionChains 


load_dotenv()
driver = None
wait = None  

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

        print(" Opening Internshala login page...")
        driver.get("https://internshala.com/login")

        print("\n Please log in manually in the browser window.")
        print(" Solve any CAPTCHA if prompted.")
        print("Once you are successfully logged in and your dashboard is visible, press ENTER here to continue...")

        # Wait for user confirmation in console
        input(" Press ENTER after you’ve logged in: ")

        try:
            # Verify login by checking if the dashboard/homepage is loaded
            wait = WebDriverWait(driver, 60)
            wait.until(
                EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/internships')]"))
            )
            print("Login detected. Global driver initialized successfully.")
            return "Login successful. You may now use other tools with this driver."
        except Exception as e:
            return f" Login verification failed: {e}"
        

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
    description: str = "Automatically applies to internships by clicking Apply, uploading resume, and submitting."

    def _run(self, *args, **kwargs):
        global driver
        if driver is None:
            return " No global driver found. Please run the login tool first."

        ranked_file = "webdata.json"
        resume_path = os.path.abspath("Rishita_Sharma.pdf")

        if not os.path.exists(ranked_file):
            return " Error: webdata.json not found."

        if not os.path.exists(resume_path):
            return f" Error: Resume file not found at {resume_path}"

        # Load internship data
        with open(ranked_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        ranked_jobs = data if isinstance(data, list) else data.get("internships", [])

        if not ranked_jobs:
            return " No internships found in webdata.json."

        wait = WebDriverWait(driver, 25)
        print(f"\n Starting automated applications for {len(ranked_jobs)} internships...")

        for job in ranked_jobs:
            job_title = job.get("title", "Unknown Job")
            job_link = job.get("link")

            if not job_link:
                continue

            try:
                print(f"\n🔹 Opening job: {job_title}")
                driver.get(job_link)
                time.sleep(4)

                # ----------------------------
                # CLICK APPLY BUTTON
                # ----------------------------
                try:
                    apply_btn = wait.until(EC.element_to_be_clickable((
                        By.XPATH, "//button[contains(text(),'Apply') or contains(text(),'Apply Now')]"
                    )))
                except:
                    apply_btn = wait.until(EC.element_to_be_clickable((
                        By.XPATH, "//a[contains(text(),'Apply') or contains(text(),'Apply Now')]"
                    )))

                driver.execute_script("arguments[0].scrollIntoView(true);", apply_btn)
                ActionChains(driver).move_to_element(apply_btn).pause(1).click().perform()
                print("Clicked Apply button.")
                time.sleep(3)

                # ----------------------------
                # UPLOAD RESUME
                # ----------------------------
                try:
                    upload_input = wait.until(
                        EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
                    )
                    upload_input.send_keys(resume_path)
                    print("📎 Resume uploaded automatically.")
                except:
                    print("⚠ No upload field detected (Internshala auto_resume used).")

                time.sleep(2)

                # ----------------------------
                # FIND & CLICK SUBMIT BUTTON
                # ----------------------------
                print("🔍 Locating the submit button...")

                submit_btn = None

                # 1️⃣ Exact match (your screenshot)
                try:
                    submit_btn = wait.until(EC.element_to_be_clickable((
                        By.XPATH, "//input[@type='submit' and @id='submit']"
                    )))
                    print("✔ Found submit id='submit'")
                except:
                    pass

                # 2️⃣ Fallback to value
                if submit_btn is None:
                    try:
                        submit_btn = wait.until(EC.element_to_be_clickable((
                            By.XPATH, "//input[@value='Submit']"
                        )))
                        print("✔ Found submit value='Submit'")
                    except:
                        pass

                # 3️⃣ Fallback: any input[type='submit']
                if submit_btn is None:
                    try:
                        all_submits = driver.find_elements(By.XPATH, "//input[@type='submit']")
                        for s in all_submits:
                            if s.is_displayed():
                                submit_btn = s
                                print("✔ Found visible submit <input>")
                                break
                    except:
                        pass

                # 4️⃣ Last fallback → button with text
                if submit_btn is None:
                    try:
                        submit_btn = wait.until(EC.element_to_be_clickable((
                            By.XPATH, "//button[contains(text(),'Submit')]"
                        )))
                        print("✔ Found <button> Submit")
                    except:
                        pass

                if submit_btn is None:
                    print("❌ Submit button NOT FOUND!")
                    continue

                # SCROLL INTO VIEW
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit_btn)
                time.sleep(1)

                # JS CLICK (most reliable)
                try:
                    driver.execute_script("arguments[0].click();", submit_btn)
                    print("✔ Submit clicked (JS)")
                except:
                    print("⚠ JS click failed → trying ActionChains")
                    try:
                        ActionChains(driver).move_to_element(submit_btn).pause(1).click().perform()
                        print("✔ Submit clicked (ActionChains)")
                    except:
                        print("⚠ Both failed → dispatching click event")
                        driver.execute_script("""
                            arguments[0].dispatchEvent(new MouseEvent('click', {bubbles:true}));
                        """, submit_btn)

                time.sleep(2)

                print(f"🎯 Application submitted for: {job_title}")
                time.sleep(3)

            except Exception as e:
                print(f"❌ Failed for {job_title}: {e}")

        print("\n All internships processed successfully.")
        return "All applications submitted."

    
login_tool=InternshalaLoginTool()    
# login_tool.run()

search_tool = ScrapeWebsiteTool(
    website_url="https://internshala.com/internships/machine-learning-internship"
    )
# search_tool.run()
file_read_tool=FileReadTool(file_path="skills.txt")

apply_tool = InternshalaApplyTool()
# apply_tool.run()
