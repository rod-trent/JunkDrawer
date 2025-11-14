import os
import requests
import re
import json
from bs4 import BeautifulSoup
from xai_sdk import Client
from xai_sdk.chat import user, system
from xai_sdk.tools import x_search
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Function to parse salary string to min and max
def parse_salary(salary_str):
    if not salary_str or salary_str == 'N/A':
        return None, None
    salary_str = salary_str.upper().replace('(EMPLOYER EST.)', '').replace('(GLASSDOOR EST.)', '').replace('A YEAR', '').replace('$', '').replace(',', '').strip()
    multiplier = 1000 if 'K' in salary_str else 1
    parts = re.split(r'-|TO|–', salary_str)
    numbers = []
    for part in parts:
        num_str = ''.join(c for c in part if c.isdigit() or c == '.')
        if num_str:
            num = float(num_str) * multiplier
            numbers.append(num)
    if len(numbers) == 2:
        return min(numbers), max(numbers)
    elif len(numbers) == 1:
        return numbers[0], numbers[0]
    return None, None

# Function to check if salary ranges overlap
def ranges_overlap(a_min, a_max, b_min, b_max):
    if a_min is None or b_min is None:
        return True
    a_max = a_max if a_max is not None else float('inf')
    b_max = b_max if b_max is not None else float('inf')
    return max(a_min, b_min) <= min(a_max, b_max)

# Function to check if job salary matches user range
def salary_matches(job_salary, user_min, user_max):
    if user_min is None:
        return True
    j_min, j_max = parse_salary(job_salary)
    if j_min is None:
        return True  # No salary info, keep
    return ranges_overlap(user_min, user_max, j_min, j_max)

# Function to check if work type matches description or location
def work_type_matches(description, location, wt):
    if not wt:
        return True
    wt = wt.lower()
    text = (description + ' ' + location).lower()
    keywords = {
        'remote': ['remote'],
        'hybrid': ['hybrid'],
        'on-site': ['on-site', 'onsite', 'in-office', 'office-based', 'on site']
    }.get(wt, [])
    return any(k in text for k in keywords)

# Ask if user wants to be prompted
prompt_user = input("Do you want to be prompted for job role, salary range, and work type? If you answer 'no' your preferences stored in the JobAgentReq.txt file will be used. (yes/no): ").strip().lower()

if prompt_user == 'yes':
    job_role = input("Enter the job role: ").strip()
    salary_range = input("Enter the salary range (e.g., 100000-150000): ").strip()
    work_type = input("Enter the work type (remote, hybrid, or on-site): ").strip()
else:
    # Pull from JobAgentReq.txt
    file_path = 'JobAgentReq.txt'
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"{file_path} not found in the current directory.")
    
    job_role = ''
    salary_range = ''
    work_type = ''
    
    with open(file_path, 'r') as f:
        lines = f.readlines()
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()
                if key == 'job_role':
                    job_role = value
                elif key == 'salary_range':
                    salary_range = value
                elif key == 'work_type':
                    work_type = value

    if not job_role or not salary_range or not work_type:
        raise ValueError("JobAgentReq.txt is missing required fields: job_role, salary_range, work_type")

print("Please wait...searching X")

# Parse user salary range
try:
    min_str, max_str = salary_range.split('-')
    user_min = float(min_str.strip())
    user_max = float(max_str.strip())
except:
    user_min = user_max = None

x_jobs = []

# Search X using Grok API with tools enabled
api_key = os.getenv("XAI_API_KEY")
if not api_key:
    raise ValueError("XAI_API_KEY not found in .env file. Please add it to the .env file.")

client = Client(api_key=api_key)
chat = client.chat.create(model="grok-4", tools=[x_search()])
chat.append(system('You are a helpful assistant that searches X for job postings. Respond strictly with a JSON array of objects, each with "title", "company", "location", "salary", "description", "link". Do not include any other text.'))
prompt = f"Search X for open job postings that closely match the role '{job_role}', mention a salary in the range {salary_range}, and are {work_type}. Use semantic search if appropriate. Provide the top 25 matching results in the specified JSON format."
chat.append(user(prompt))

# Stream the response and collect content
content = ""
for _, chunk in chat.stream():
    if chunk.content:
        content += chunk.content

# Parse the collected content as JSON
try:
    x_results = json.loads(content)
except json.JSONDecodeError:
    x_results = []
    print("Warning: Failed to parse X search response as JSON. Content was:", content)

for res in x_results:
    job = {
        "title": res.get('title', 'N/A'),
        "company": res.get('company', 'N/A'),
        "location": res.get('location', 'N/A'),
        "link": res.get('link', 'N/A'),
        "source": "X",
        "salary": res.get('salary', 'N/A'),
        "description": res.get('description', 'N/A')
    }
    x_jobs.append(job)

filtered_x = [
    job for job in x_jobs 
    if salary_matches(job['salary'], user_min, user_max) and work_type_matches(job['description'], job['location'], work_type)
]

# Combine and get top 25 (X only)
all_jobs = filtered_x
top_25 = all_jobs[:25]

# Print results
print("\nTop 25 Matching Job Results:\n")
for idx, job in enumerate(top_25, 1):
    print(f"{idx}. {job['title']}")
    print(f"   Company: {job['company']}")
    print(f"   Location: {job['location']}")
    print(f"   Salary: {job['salary']}")
    print(f"   Description: {job['description']}")
    print(f"   Link: {job['link']}")
    print(f"   Source: {job['source']}")
    print("---")
