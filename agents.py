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
    goal="Find and extract detailed information about internship opportunities from job websites",
    backstory=(
        "You are an expert recruiter and web scraping specialist. "
        "You excel at finding job listings, extracting key details like job titles, "
        "company names, locations, stipends, and application links. "
        "You focus on internships in technology fields like machine learning, "
        "data science, and AI."
    ),
    verbose=True,
    llm=llm,
    allow_delegation=False,
)

Filter_agent=Agent(
    role="Job Ranker",
    goal="Rank the extracted jobs on the basis of their similarities with the resume provided",
    backstory=(
    "You are an expert in analysing resumes. "
    "You have to rank the jobs according its similarity with the resume. "
    ),
    verbose=True,
    llm=llm,
)

Apply_agent= Agent(
    role="Job Applier",
    goal="Your goal is to apply for the jobs ranked by the filter agent. ",
    backstory=(
        "You are a highly efficient virtual assistant who can read job details, "
        "open application links, and submit resume details accurately. "
        "You ensure that each application includes a professional message tailored to the job description."
    ),
    verbose=True,
    llm=llm,

)