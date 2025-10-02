import os
import requests
from bs4 import BeautifulSoup
from crewai import LLM, Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.tools import tool
from typing import List, Optional
from pydantic import BaseModel
from urllib.parse import urljoin
import re

# Definindo as ferramentas diretamente no arquivo
@tool("Web Scraper")
def web_scraping_tool(url: str) -> str:
    """Access websites and extract content, navigation menus, and links"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract navigation menu
        nav_elements = soup.find_all(['nav', 'header', 'menu'])
        nav_links = []
        for nav in nav_elements:
            links = nav.find_all('a', href=True)
            for link in links:
                href = link.get('href')
                text = link.get_text(strip=True)
                if href and text:
                    full_url = urljoin(url, href)
                    nav_links.append(f"{text}: {full_url}")
        
        # Look for specific portfolio-related terms
        portfolio_keywords = [
            'portfolio', 'portfólio', 'portafolio', 'companies', 'empresas', 
            'investments', 'inversiones', 'startups', 'portfolio companies',
            'our companies', 'nossas empresas', 'nuestras empresas'
        ]
        
        portfolio_links = []
        all_links = soup.find_all('a', href=True)
        for link in all_links:
            href = link.get('href')
            text = link.get_text(strip=True).lower()
            if any(keyword in text for keyword in portfolio_keywords):
                full_url = urljoin(url, href)
                portfolio_links.append(f"{link.get_text(strip=True)}: {full_url}")
        
        result = f"""
WEBSITE ANALYSIS FOR: {url}

NAVIGATION MENU LINKS:
{chr(10).join(nav_links[:10]) if nav_links else "No navigation links found"}

PORTFOLIO-RELATED LINKS FOUND:
{chr(10).join(portfolio_links) if portfolio_links else "No portfolio-related links found"}

PAGE TITLE: {soup.title.get_text(strip=True) if soup.title else "No title"}
"""
        return result
        
    except Exception as e:
        return f"Error accessing {url}: {str(e)}"

@tool("Portfolio Validator")
def portfolio_validator_tool(url: str) -> str:
    """Validate if a portfolio URL actually contains portfolio companies"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Count potential company listings
        company_elements = soup.find_all(['div', 'section', 'article'], 
                                       class_=re.compile(r'(company|portfolio|startup|investment)', re.I))
        
        # Look for lists of companies
        lists = soup.find_all(['ul', 'ol'])
        company_lists = [len(ul.find_all('li')) for ul in lists if len(ul.find_all('li')) > 2]
        
        # Check for company names/logos
        images = soup.find_all('img')
        logo_count = sum(1 for img in images if any(term in img.get('alt', '').lower() or 
                                                  term in img.get('src', '').lower() 
                                                  for term in ['logo', 'company', 'startup']))
        
        # Analyze results
        has_companies = (
            len(company_elements) > 0 or 
            len(company_lists) > 0 or 
            logo_count > 3
        )
        
        result = f"""
PORTFOLIO VALIDATION FOR: {url}

STATUS: {'✅ VALID - Contains portfolio companies' if has_companies else '❌ INVALID - No portfolio companies found'}

ANALYSIS:
- Company-related elements found: {len(company_elements)}
- Potential company lists found: {len(company_lists)}
- Company logos/images found: {logo_count}
- Response status: {response.status_code}
"""
        return result
        
    except Exception as e:
        return f"Error validating {url}: {str(e)}"

class Investor(BaseModel):
    name: str
    type: str
    website: str
    hq_country: str
    focus: str
    portfolio_url: Optional[str]

class InvestorList(BaseModel):
    investors: List[Investor]
    
llm = LLM(
    model="perplexity/sonar",
    base_url="https://api.perplexity.ai/",
    api_key=os.getenv("PERPLEXITY_API_KEY")
)

@CrewBase
class InvestorCrew():
    agents: list
    tasks: list

    @agent
    def investor_research_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['investor_research_agent'],
            verbose=True,
            allow_delegation=False,
            reasoning=True,
            max_reasoning_attempts=2,
            memory=True,
            llm=llm
        )

    @agent
    def investor_validation_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['investor_validation_agent'],
            verbose=True,
            allow_delegation=False,
            reasoning=True,
            max_reasoning_attempts=3,
            memory=True,
            llm=llm,
            tools=[web_scraping_tool, portfolio_validator_tool]
        )

    @agent
    def text2json_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['text2json_agent'],
            verbose=True,
            allow_delegation=False,
            memory=True,
            llm=llm
        )

    @task
    def investor_research(self) -> Task:
        return Task(
            config=self.tasks_config['discover_investors_raw'],
        )

    @task
    def validate_investor_websites(self) -> Task:
        return Task(
            config=self.tasks_config['validate_investors'],
        )

    @task
    def format_investors_json(self) -> Task:
        return Task(
            config=self.tasks_config['format_investors2json'],  # Certifique-se que esse nome está correto
            output_pydantic=InvestorList,
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[
                self.investor_research_agent(),
                self.investor_validation_agent(),
                self.text2json_agent()
            ],
            tasks=[
                self.investor_research(),
                self.validate_investor_websites(),
                self.format_investors_json()
            ],
            process=Process.sequential,
            verbose=True
        )