# 🚀 Internshala Automation Bot

An intelligent, end-to-end automation system for discovering and applying to machine learning internships on Internshala using **CrewAI** agents, **Selenium** web scraping, and **Groq LLMs**.

## 📋 Overview

This project automates the tedious process of job hunting on Internshala by:
- **Logging in** to your Internshala account (with manual CAPTCHA handling)
- **Scraping** top machine learning internship listings
- **Automatically applying** to internships with your resume
- **Tracking applications** in JSON output files

The system uses a multi-agent architecture where specialized agents handle login, scraping, and application workflows sequentially.

---

## ✨ Features

- ✅ **Manual Login with CAPTCHA Support** - Handles manual login to bypass CAPTCHA using Selenium
- ✅ **Intelligent Web Scraping** - Extracts internship title, company, and application links
- ✅ **Automated Applications** - Fills forms, uploads resume, and submits applications
- ✅ **Multi-Agent Architecture** - Uses CrewAI for orchestrated agent workflows
- ✅ **Groq LLM Integration** - Powers intelligent decision-making and text generation
- ✅ **Resume Management** - Automatically uploads your resume (PDF format)
- ✅ **Application Tracking** - Maintains JSON logs of applied positions
- ✅ **Error Handling & Logging** - Comprehensive error tracking and debugging

---

## 🛠️ Tech Stack

| Technology | Purpose |
|-----------|---------|
| **CrewAI** | Multi-agent orchestration framework |
| **Selenium** | Web browser automation and scraping |
| **Groq** | LLM API for intelligent agent reasoning |
| **LangChain** | LLM framework and tools |
| **Python 3.10+** | Core programming language |
| **PyPDF2** | PDF processing for resume handling |
| **Undetected ChromeDriver** | Bypass bot detection |

---

## 📦 Installation

### Prerequisites
- Python 3.10 or higher
- Google Chrome browser installed
- Groq API key ([Get it here](https://console.groq.com))
- Active Internshala account

### Setup Steps

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd internshala-automation
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Environment Variables**
   Create a `.env` file in the project root:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```

5. **Prepare Resume**
   - Place your resume as `Rishita_Sharma.pdf` in the project root
   - Update the filename in `tools.py` if needed

6. **Update Skills**
   - Edit `skills.txt` with your relevant skills and experience
   - Format: `Category: Skill1, Skill2, Skill3`

---

## 🚀 Quick Start

### Run the Full Automation Pipeline

```bash
python crew.py
```

This will execute the complete workflow:
1. **Agent 1 (Scraper)** - Logs in and scrapes top 5 internships
2. **Agent 2 (Applier)** - Automatically applies to each internship

### Output Files

After execution, check these files:

| File | Purpose |
|------|---------|
| `webdata.json` | Scraped internship listings |
| `Applied.json` | Successfully applied positions |
| `debug_internshala.html` | HTML debug file (if scraping fails) |

---

## 📁 Project Structure

```
internshala-automation/
├── crew.py                 # Main entry point - CrewAI workflow
├── agents.py              # Agent definitions (Scraper & Applier)
├── tasks.py               # Task definitions for agents
├── tools.py               # Custom Selenium-based tools
├── requirements.txt       # Python dependencies
├── skills.txt             # Your skills and experience
├── Rishita_Sharma.pdf    # Your resume (rename as needed)
├── .env                   # Environment variables (not in repo)
├── webdata.json          # Scraped internships (generated)
├── Applied.json          # Applied jobs (generated)
└── README.md             # This file
```

---

## 🔧 Component Details

### 1. **Agents** (`agents.py`)

#### Webscraping Agent
- **Role**: Login and Scraping Agent
- **Goal**: Successfully log in and scrape top 5 machine learning internships
- **LLM**: Groq (qwen3-32b model)

#### Apply Agent
- **Role**: Job Applier
- **Goal**: Apply to jobs with tailored professional messages
- **LLM**: Groq (qwen3-32b model)

### 2. **Tools** (`tools.py`)

#### InternshalaLoginTool
```python
- Opens Internshala login page
- Waits for manual user login (CAPTCHA handling)
- Initializes global Selenium driver for reuse
```

#### ScrapeWebsiteTool
```python
- Navigates to machine-learning internship listings
- Extracts: title, company name, and application link
- Returns list of up to 10 internships
- Saves results to webdata.json
```

#### InternshalaApplyTool
```python
- Iterates through scraped internships
- Clicks "Apply" button
- Uploads resume automatically
- Locates and clicks submit button
- Handles multiple submit button variations
- Tracks applications in Applied.json
```

### 3. **Tasks** (`tasks.py`)

#### Scrape Task
- Uses Login & Scraping tools
- Outputs to `webdata.json`
- Sequential execution (no parallelization)

#### Apply Task
- Uses Apply tool
- Takes context from Scrape Task
- Outputs to `Applied.json`
- Depends on successful scraping

---

## ⚙️ Configuration

### Modify Target Internship Type

In `tools.py`, line 61:
```python
website_url = "https://internshala.com/internships/machine-learning-internship"
# Change "machine-learning-internship" to other categories:
# - data-science-internship
# - web-development-internship
# - python-internship
# etc.
```

### Adjust Number of Internships

In `tools.py`, line 78:
```python
containers = containers[:10]  # Change 10 to desired number
```

### Update Resume File Path

In `tools.py`, line 145:
```python
resume_path = os.path.abspath("Rishita_Sharma.pdf")
# Update filename to your resume
```

### Change LLM Model

In `agents.py`, line 12:
```python
model="groq/qwen/qwen3-32b"
# Available Groq models: mixtral, llama2, gemma, etc.
```

---

## 🎯 Workflow Execution

```
┌─────────────────────────────────────┐
│   Start: crew.kickoff()             │
└──────────────┬──────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│   Task 1: Scrape Task                │
│   ├─ InternshalaLoginTool            │
│   │  └─ Manual login + CAPTCHA       │
│   └─ ScrapeWebsiteTool               │
│      └─ Extract 5 internships        │
│      └─ Save to webdata.json         │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│   Task 2: Apply Task                 │
│   └─ InternshalaApplyTool            │
│      ├─ Load webdata.json            │
│      ├─ For each internship:         │
│      │  ├─ Open job link             │
│      │  ├─ Click Apply button        │
│      │  ├─ Upload resume             │
│      │  └─ Submit application        │
│      └─ Save to Applied.json         │
└──────────────┬───────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   End: Return results               │
└─────────────────────────────────────┘
```

---

## 📊 Output Examples

### webdata.json (Scraped Internships)
```json
{
  "internships": [
    {
      "title": "Machine Learning Intern",
      "company": "Tech Startup Pvt Ltd",
      "link": "https://internshala.com/internship/detail/..."
    },
    {
      "title": "AI/ML Internship",
      "company": "Data Science Corp Limited",
      "link": "https://internshala.com/internship/detail/..."
    }
  ]
}
```

### Applied.json (Application Results)
```json
{
  "applied": [
    {
      "title": "Machine Learning Intern",
      "company": "Tech Startup Pvt Ltd",
      "status": "submitted",
      "timestamp": "2025-11-11 09:45:23"
    }
  ]
}
```

---

## 🐛 Troubleshooting

### Issue: JSONDecodeError in webdata.json

**Solution**: Ensure the scraper tool saves JSON properly. The file should contain valid JSON in format:
```json
{"internships": [...]}
```

### Issue: CAPTCHA not being handled

**Solution**: The login tool waits for manual login. Solve the CAPTCHA in the browser window that opens, then press ENTER in the console.

### Issue: Resume not uploading

**Solutions**:
1. Verify resume file exists: `ls Rishita_Sharma.pdf`
2. Check absolute path: `os.path.abspath("Rishita_Sharma.pdf")`
3. Internshala may auto-fill resume - check if application still succeeds

### Issue: Submit button not found

**Debugging**:
- The tool tries multiple XPath selectors for submit buttons
- Check `debug_internshala.html` for actual button structure
- Update XPath in `tools.py` line 175-195 if needed

### Issue: Driver not initialized

**Solution**: Ensure login tool runs first:
```python
# In crew.py, ensure Scrape Task comes before Apply Task
# and login_tool is called as dependency
```

---

## 🔐 Security Considerations

- **API Keys**: Never commit `.env` file to Git
- **Resume**: Keep resume file locally, don't share sensitive versions
- **Account Access**: Use a dedicated account for automation
- **Rate Limiting**: The crew is configured with `max_rpm=100` to avoid blocking
- **CAPTCHA**: Handled manually to avoid detection

---

## 📝 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GROQ_API_KEY` | Groq API key for LLM | Yes |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/improvement`)
5. Create Pull Request

---

## ⚠️ Disclaimer

This project is for **educational and personal use only**. Users are responsible for:
- Complying with Internshala's Terms of Service
- Not violating any website's robots.txt or automation policies
- Using this tool ethically and responsibly
- Ensuring they have permission to automate applications on their account

The authors are not responsible for account suspensions or violations resulting from misuse.

---

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

---

## 💡 Future Enhancements

- [ ] Support for multiple internship categories
- [ ] Intelligent cover letter generation using LLMs
- [ ] Application status tracking and analytics
- [ ] Email notifications for successful applications
- [ ] Integration with LinkedIn job postings
- [ ] Database storage for application history
- [ ] Dashboard for monitoring and reporting
- [ ] Multi-threaded application processing

---

## 📧 Contact & Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing issues for solutions
- Review the troubleshooting section

---

## 🙏 Acknowledgments

- **CrewAI** for the amazing multi-agent framework
- **Groq** for fast and powerful LLM APIs
- **Selenium** community for web automation tools
- **Internshala** for the internship platform

---

**Happy Job Hunting! 🎯**

Built with ❤️ for automating the job search process.