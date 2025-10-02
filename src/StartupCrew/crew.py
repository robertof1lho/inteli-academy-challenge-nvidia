import os
import requests
from bs4 import BeautifulSoup
from crewai import LLM, Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.tools import tool
from typing import List, Optional
from pydantic import BaseModel
from urllib.parse import urljoin, urlparse
import re

# Ferramentas para scraping de startups
@tool("Portfolio Company Extractor")
def portfolio_company_extractor(url: str) -> str:
    """Extract detailed startup information from portfolio pages"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Look for company cards, sections, or lists
        companies = []
        
        # Strategy 1: Look for common portfolio structures
        portfolio_sections = soup.find_all(['div', 'section'], 
                                         class_=re.compile(r'(portfolio|company|startup|investment)', re.I))
        
        # Strategy 2: Look for lists of companies
        company_lists = soup.find_all(['ul', 'ol'])
        for ul in company_lists:
            items = ul.find_all('li')
            if len(items) > 3:  # Likely a company list
                for item in items:
                    company_info = extract_company_info(item, url)
                    if company_info:
                        companies.append(company_info)
        
        # Strategy 3: Look for company cards/grids
        card_patterns = [
            'card', 'company', 'startup', 'portfolio-item', 'investment',
            'empresa', 'portafolio', 'investimento'
        ]
        
        for pattern in card_patterns:
            cards = soup.find_all(['div', 'article'], class_=re.compile(pattern, re.I))
            for card in cards:
                company_info = extract_company_info(card, url)
                if company_info:
                    companies.append(company_info)
        
        # Strategy 4: Look for text patterns that suggest companies
        text_content = soup.get_text()
        company_patterns = find_company_patterns(text_content)
        companies.extend(company_patterns)
        
        # Remove duplicates
        unique_companies = []
        seen_names = set()
        for company in companies:
            name = company.get('name', '').strip().lower()
            if name and name not in seen_names and len(name) > 2:
                seen_names.add(name)
                unique_companies.append(company)
        
        result = f"""
PORTFOLIO EXTRACTION FOR: {url}

COMPANIES FOUND: {len(unique_companies)}

DETAILED COMPANIES:
{format_companies_output(unique_companies)}

PAGE ANALYSIS:
- Total portfolio sections found: {len(portfolio_sections)}
- Company lists found: {len([ul for ul in company_lists if len(ul.find_all('li')) > 3])}
- Response status: {response.status_code}
- Page title: {soup.title.get_text(strip=True) if soup.title else 'No title'}
"""
        return result
        
    except Exception as e:
        return f"Error extracting companies from {url}: {str(e)}"

def extract_company_info(element, base_url):
    """Extract company information from a DOM element"""
    try:
        company = {}
        
        # Get company name
        name_selectors = ['h1', 'h2', 'h3', 'h4', '.name', '.title', '.company-name', 'strong', 'b']
        name = None
        for selector in name_selectors:
            name_elem = element.find(selector)
            if name_elem:
                name = name_elem.get_text(strip=True)
                if name and len(name) > 2 and len(name) < 100:
                    break
        
        if not name:
            # Try to get from link text
            link = element.find('a')
            if link:
                name = link.get_text(strip=True)
        
        if not name or len(name) < 2:
            return None
        
        company['name'] = name
        
        # Get website
        links = element.find_all('a', href=True)
        website = None
        for link in links:
            href = link.get('href')
            if href and not any(social in href.lower() for social in ['linkedin', 'twitter', 'facebook', 'instagram']):
                if href.startswith('http'):
                    website = href
                elif href.startswith('/'):
                    website = urljoin(base_url, href)
                break
        
        company['website'] = website
        
        # Get description
        description_elem = element.find(['p', '.description', '.summary'])
        if description_elem:
            desc = description_elem.get_text(strip=True)
            if desc and len(desc) > 10:
                company['description'] = desc[:500]  # Limit description
        
        # Look for sector/tech keywords
        text = element.get_text().lower()
        tech_keywords = ['ai', 'artificial intelligence', 'machine learning', 'ml', 'deep learning', 
                        'computer vision', 'nlp', 'robotics', 'automation', 'saas', 'fintech',
                        'healthtech', 'edtech', 'blockchain', 'iot', 'cloud']
        
        found_tech = [keyword for keyword in tech_keywords if keyword in text]
        if found_tech:
            company['tech'] = found_tech[:3]  # Limit to top 3
        
        # Look for funding stage
        funding_keywords = ['seed', 'series a', 'series b', 'series c', 'pre-seed', 'ipo']
        found_funding = [keyword for keyword in funding_keywords if keyword in text]
        if found_funding:
            company['funding_stage'] = found_funding[0]
        
        return company
        
    except Exception:
        return None

def find_company_patterns(text):
    """Find company names in text using patterns"""
    companies = []
    
    # Look for patterns like "Company Name - Description"
    pattern = r'([A-Z][a-zA-Z\s]{2,30})\s*[-–]\s*([^.]{10,100})'
    matches = re.findall(pattern, text)
    
    for match in matches[:20]:  # Limit to 20 matches
        name, desc = match
        name = name.strip()
        desc = desc.strip()
        
        if len(name) > 2 and len(name) < 50:
            companies.append({
                'name': name,
                'description': desc,
                'website': None
            })
    
    return companies

def format_companies_output(companies):
    """Format companies for output"""
    if not companies:
        return "No companies found"
    
    output = []
    for i, company in enumerate(companies[:20], 1):  # Limit to 20 companies
        output.append(f"{i}. {company.get('name', 'Unknown')}")
        if company.get('website'):
            output.append(f"   Website: {company['website']}")
        if company.get('description'):
            output.append(f"   Description: {company['description'][:100]}...")
        if company.get('tech'):
            output.append(f"   Tech: {', '.join(company['tech'])}")
        output.append("")
    
    return "\n".join(output)

llm = LLM(
    model="perplexity/sonar",
    base_url="https://api.perplexity.ai/",
    api_key=os.getenv("PERPLEXITY_API_KEY")
)

class LeadershipPerson(BaseModel):
    role: str
    name: str
    linkedin: Optional[str] = None

class StartupCandidate(BaseModel):
    name: str
    website: Optional[str] = None
    description: Optional[str] = None
    sector: Optional[str] = None
    year: Optional[int] = None
    tech: Optional[List[str]] = None
    funding: Optional[str] = None
    investors: Optional[List[str]] = None
    leadership: Optional[List[LeadershipPerson]] = None

class StartupList(BaseModel):
    startups: List[StartupCandidate]

@CrewBase
class StartupCrew():
    agents: list
    tasks: list

    @agent
    def portfolio_scraping_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['portfolio_scraping_agent'],
            verbose=True,
            allow_delegation=False,
            reasoning=True,
            max_reasoning_attempts=2,
            memory=True,
            llm=llm,
            tools=[portfolio_company_extractor]
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
    def scrape_portfolio(self) -> Task:
        return Task(
            config=self.tasks_config['scrape_portfolio'],
            context=None  # Remove context se existir
        )
    
    @task
    def format_startups_json(self) -> Task:
        return Task(
            config=self.tasks_config['format_startup2json'],
            output_pydantic=StartupList,
            context=[self.scrape_portfolio()]  # Adiciona contexto da task anterior
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[self.portfolio_scraping_agent(), self.text2json_agent()],
            tasks=[self.scrape_portfolio(), self.format_startups_json()],
            process=Process.sequential,
            verbose=True
        )