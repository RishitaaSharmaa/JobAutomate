from crewai import Agent
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
load_dotenv()

api_key= os.getenv("GROQ_API_KEY")

llm = ChatGroq(
    model="groq/qwen/qwen3-32b",
    api_key=api_key
)
Webscrapingagent = Agent(
    role="Login and Scraping Agent",
    goal="Login into the user's account successfully and Scrape top 5 internships. ",
    backstory="You are a automation agent who has to login into a user's account and scrape internships. ",
    verbose=False,
    llm=llm,
    allow_delegation=False,
)

Apply_agent = Agent(
    role="Job Applier",
    goal="Apply to the with a tailored professional message .",
    backstory="A reliable virtual assistant applying to jobs",
    verbose=False,
    llm=llm,
    allow_delegation=False,
    cache=True,
    
)