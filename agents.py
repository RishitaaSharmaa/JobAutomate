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
    role="Job Finder",
    goal="Login into user's accoutn and find ML/AI internship listings with title, company, location, stipend, and link.",
    backstory="An efficient recruiter skilled in scraping tech internship data.",
    verbose=False,
    llm=llm,
    allow_delegation=False,
)

Filter_agent = Agent(
    role="Job Ranker",
    goal="Rank internships based on similarity with the resume content.",
    backstory="An expert resume analyst ranking jobs for best fit.",
    verbose=False,
    llm=llm,
    allow_delegation=False,
)

Apply_agent = Agent(
    role="Job Applier",
    goal="Apply to the ranked jobs with a tailored professional message.",
    backstory="A reliable virtual assistant applying accurately and professionally",
    verbose=False,
    llm=llm,
    allow_delegation=False,
)