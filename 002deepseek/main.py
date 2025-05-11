from IPython.display import Markdown, display
from openai import OpenAI
import Website

OLLAMA_API = "http://localhost:11434/api/chat"
HEADERS = {"Content-Type": "application/json"}
MODEL = "llama3.2"



def user_prompt(website):
    user_prompt = f"The content below are the contents of a website with the title {website.title}. I want you to thoroughly analyze\
    the contents and summarize them to understand what the website is about and write the summary in markdown format\n\n"
    user_prompt += website.text
    return user_prompt

ollama_via_openai = OpenAI(base_url='http://localhost:11434/v1', api_key='ollama')

def display_content(website_url):
    website = Website(website_url)
    response = ollama_via_openai.chat.completions.create(
        model="deepseek-r1:1.5b",
        messages=[{"role": "user", "content": user_prompt(website)}]
    )    
    display(Markdown(response.choices[0].message.content))

display_content("https://apple.com")