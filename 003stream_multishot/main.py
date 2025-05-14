import os
import json
from typing import List
from dotenv import load_dotenv
from IPython.display import Markdown, display, update_display
from openai import OpenAI
import Website

load_dotenv(override=True)
api_key = os.getenv('OPENAI_API_KEY')
MODEL = 'gpt-4o-mini'

website = Website()
openai = OpenAI()

link_system_prompt = "You are provided with a list of links found on a webpage. \
You are able to decide which of the links would be most relevant to include in a brochure about the company, \
such as links to an About page, or a Company page, or Careers/Jobs pages.\n\
For instance, if you receive the links in this format:\n"
link_system_prompt += '''
/pricing
/features
/enterprise
/blog
https://forum.cursor.com
https://anysphere.inc/
/api/auth/login
/downloads
/features
/features
/blog/shadow-workspace
mailto:hi@cursor.com
https://x.com/cursor_ai
https://github.com/getcursor/cursor
https://www.reddit.com/r/cursor
https://anysphere.inc
/pricing
/features
/enterprise
/downloads
/students
https://docs.cursor.com
/blog
https://forum.cursor.com
/changelog
https://anysphere.inc
https://anysphere.inc
/community
/terms-of-service
/security
/privacy
'''
link_system_prompt += "You should respond in JSON as in this example (note that this is an example and the actual url should be based on input):"
link_system_prompt += """
{
    {
    'links': [
        {'type': 'about page', 'url': 'https://anysphere.inc'},
        {'type': 'careers page', 'url': 'https://anysphere.inc'},
        {'type': 'features page', 'url': 'https://cursor.com/features'},
        {'type': 'pricing page', 'url': 'https://cursor.com/pricing'},
        {'type': 'enterprise page', 'url': 'https://cursor.com/enterprise'},
        {'type': 'downloads page', 'url': 'https://cursor.com/downloads'},
        {'type': 'blog page', 'url': 'https://cursor.com/blog'},
        {'type': 'community page', 'url': 'https://forum.cursor.com'},
        {'type': 'documentation page', 'url': 'https://docs.cursor.com'}
        ]
    }
}
"""

def get_links_user_prompt(website):
    user_prompt = f"Here is the list of links on the website of {website.url} - "
    user_prompt += "please decide which of these are relevant web links for a brochure about the company, respond with the full https URL in JSON format. \
    Do not include Terms of Service, Privacy, email links.\n"
    user_prompt += "Links (some might be relative links):\n"
    user_prompt += "\n".join(website.links)
    return user_prompt

def get_links(url):
    website = Website(url)
    response = openai.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": link_system_prompt},
            {"role": "user", "content": get_links_user_prompt(website)}
      ],
        response_format={"type": "json_object"}
    )
    result = response.choices[0].message.content
    return json.loads(result)


def get_all_details(url):
    result = "Landing page:\n"
    result += Website(url).get_contents()
    links = get_links(url)
    print("Found links:", links)
    for link in links["links"]:
        result += f"\n\n{link['type']}\n"
        result += Website(link["url"]).get_contents()
    return result

system_prompt = "You are an assistant that analyzes the contents of several relevant pages from a company website \
and creates a brochure about the company for prospective customers, investors and recruits. Respond in markdown and use emojis.\
Include details that might excite customers or investors, details of company culture, customers and careers/jobs if you have the information."

def get_brochure_user_prompt(company_name, url):
    user_prompt = f"You are looking at a company called: {company_name}\n"
    user_prompt += f"Here are the contents of its landing page and other relevant pages; use this information to build a short brochure of the company in markdown.\n"
    user_prompt += get_all_details(url)
    user_prompt = user_prompt[:20_000] # Truncate if more than 20,000 characters
    return user_prompt

def create_brochure(company_name, url):
    response = openai.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": get_brochure_user_prompt(company_name, url)}
          ],
    )
    result = response.choices[0].message.content
    # display(Markdown(result))
    return result

def stream_brochure(company_name, url):
    stream = openai.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": get_brochure_user_prompt(company_name, url)}
          ],
        stream=True
    )
    
    response = ""
    display_handle = display(Markdown(""), display_id=True)
    for chunk in stream:
        response += chunk.choices[0].delta.content or ''
        response = response.replace("```","").replace("markdown", "")
        update_display(Markdown(response), display_id=display_handle.display_id)
        
language_system_prompt = "You will receive a company brochure that promotes a company to its customers and investors. Your task will \
be to translate this natively to another language. It is imperative for you to rebuild the brochure using native structures to that language\
 and not just translate sentence by sentence. Make sure to keep style and everything else the same."

def get_user_language_prompt(brochure):
    prompt = "Translate the following brochure about this company into spanish:\n"
    prompt += brochure
    return prompt

def translate_spanish(company_name, url):
    english_brochure = create_brochure(company_name, url)
    stream = openai.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": language_system_prompt},
            {"role": "user", "content": get_user_language_prompt(english_brochure)}
          ],
        stream=True
    )
    
    response = ""
    display_handle = display(Markdown(""), display_id=True)
    for chunk in stream:
        response += chunk.choices[0].delta.content or ''
        response = response.replace("```","").replace("markdown", "")
        update_display(Markdown(response), display_id=display_handle.display_id)


translate_spanish("HuggingFace", "https://huggingface.co")
