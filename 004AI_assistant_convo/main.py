import os
from dotenv import load_dotenv
from openai import OpenAI
import anthropic
from IPython.display import Markdown, display, update_display
import google.generativeai


load_dotenv(override=True)
openai_api_key = os.getenv('OPENAI_API_KEY')
anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
google_api_key = os.getenv('GOOGLE_API_KEY')

openai = OpenAI()
google.generativeai.configure()
claude = anthropic.Anthropic()

gpt_model = "gpt-4o-mini"
claude_model = "claude-3-haiku-20240307"

gpt_system = "You are a chatbot who is very argumentative called Sean; \
you disagree with anything in the conversation and you challenge everything, in a snarky way. Gabe and Valerie will also be part of \
the conversation"

claude_system = "You are a very polite, courteous chatbot called Gabe. You try to agree with \
everything the other person (called Sean) says, or find common ground. If the other person is argumentative, \
you try to calm them down and keep chatting."

gemini_system = "You are a nice but tired chatbot called Valerie. You will have to complain about Sean and Gabe endless discussion \
and try to make them both stop. "

def call_gpt():
    messages = [{"role": "system", "content": gpt_system}]
    for gpt, claude, gemini in zip(gpt_messages, claude_messages, gemini_messages):
        messages.append({"role": "assistant", "content": gpt})
        messages.append({"role": "user", "content": claude})
        messages.append({"role": "user", "content": gemini})
    completion = openai.chat.completions.create(
        model=gpt_model,
        messages=messages
    )
    return completion.choices[0].message.content

def call_claude():
    messages = []
    for gpt, claude_message, gemini in zip(gpt_messages, claude_messages, gemini_messages):
        messages.append({"role": "user", "content": gpt})
        messages.append({"role": "assistant", "content": claude_message})
        messages.append({"role": "user", "content": gemini})
    messages.append({"role": "user", "content": gpt_messages[-1]}) # zip stops when the shortest of its input lists is exhausted 
    # So we have to add the additional gpt message manually
    message = claude.messages.create(
        model=claude_model,
        system=claude_system,
        messages=messages,
        max_tokens=500
    )
    return message.content[0].text

def call_gemini():
    messages = []
    for gpt, claude, gemini in zip (gpt_messages, claude_messages, gemini_messages):
        messages.append({"role": "user", "parts": [{"text": gpt}]})
        messages.append({"role": "user", "parts": [{"text": claude}]})
        messages.append({"role": "model", "parts": [{"text": gemini}]})
    messages.append({"role": "user", "parts": [{"text": gpt_messages[-1]}]})
    messages.append({"role": "user", "parts": [{"text": claude_messages[-1]}]}) # zip stops when the shortest of its input lists is exhausted 
    # So we have to add the additional gpt and claude messages manually
    gemini = google.generativeai.GenerativeModel(
        model_name='gemini-2.0-flash',
        system_instruction=gemini_system
    )
    response = gemini.generate_content(messages)
    return response.text

gpt_messages = ["Hi there"]
claude_messages = ["Hi"]
gemini_messages = ["Hey Guys"]

print(f"GPT:\n{gpt_messages[0]}\n")
print(f"Claude:\n{claude_messages[0]}\n")
print(f"Gemini:\n{claude_messages[0]}\n")

for i in range(5):
    gpt_next = call_gpt()
    print(f"GPT:\n{gpt_next}\n")
    gpt_messages.append(gpt_next)
    
    claude_next = call_claude()
    print(f"Claude:\n{claude_next}\n")
    claude_messages.append(claude_next)

    gemini_next = call_gemini()
    print(f"Gemini:\n{gemini_next}\n")
    gemini_messages.append(gemini_next)