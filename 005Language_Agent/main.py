import os
import json
from dotenv import load_dotenv
from openai import OpenAI
import gradio as gr
# For image processing:
import base64
from io import BytesIO
from PIL import Image
# For audio processing:
from pydub import AudioSegment
from pydub.playback import play


load_dotenv(override=True)

openai_api_key = os.getenv('OPENAI_API_KEY')
if not bool(openai_api_key):
    raise("Api key not found")
else:
    print(f'Key found, key: {openai_api_key[:9]}')

MODEL = "gpt-4o-mini"
openai = OpenAI()

system_prompt = '''
You are a helpful assistant that helps students learn new languages. You promote and engage conversation with them and try to correct their mistakes couteously and friendly. 
You start with very low-level, understandable conversation. As you gauge their knowledge, you may slightly elevate language level.
If user doesn't know what to talk about in the conversation, gracefully guide them towards wanting to learn or practice a language.
'''

def talker(message):
    response = openai.audio.speech.create(model="gpt-4o-mini-tts", voice="onyx", input=message)

    audio_stream = BytesIO(response.content)

    audio = AudioSegment.from_file(audio_stream, format="mp3")

    play(audio)
                                
def create_image(country): 
    image_response = openai.images.generate(
        model = "dall-e-3",
        prompt = f"An image representing a happy teacher from {country}, add details and characteristics that make it obvious it is from that country with a vibrant style",
        size = "1024x1024",
        n=1,
        response_format="b64_json",
    )
    
    image_base64 = image_response.data[0].b64_json

    return image_base64

nationality_function = {
    "name": "create_image",
    "description": "updates the image object of a teacher from the country given, returns the base 64 of the image when done. Call this whenever a user changes the language they want to practice or speak. For example at the beginning of a conversation, or whenever he asks to learn or practice a different language",
    "parameters": {
        "type": "object",
        "properties": {
            "country": {
                "type": "string",
                "description": "The main country of the language the user wants to practice or learn or speak"
            },
        },
        "required": ["country"],
        "additionalProperties": False
    }
}        
        
tools = [{"type": "function", "function": nationality_function}]

old_image = None

def chat(history):
    messages = [{"role": "system", "content": system_prompt}] + history
    response = openai.chat.completions.create(model=MODEL, messages=messages, tools=tools)
    image = None

    if response.choices[0].finish_reason=="tool_calls":
        message = response.choices[0].message
        response, base64_str = handle_image_tool(message)
        image_data = base64.b64decode(base64_str) # from imports
        image = Image.open(BytesIO(image_data))  # from imports 
        global old_image
        old_image = image
        messages.append(message)
        messages.append(response)
        response = openai.chat.completions.create(model=MODEL, messages=messages)

    reply = response.choices[0].message.content
    history += [{"role":"assistant", "content":reply}]

    if not image:        
        image = old_image
    
    talker(reply)
    
    return history, image
        
       
def handle_image_tool(message):
    tool_call = message.tool_calls[0]
    arguments = json.loads(tool_call.function.arguments)
    country = arguments.get('country')    
    base_64 = create_image(country)
    response = {
        "role": "tool",
        "content": json.dumps({"new_language_country": country, "did_work": "The image was updated in the UI"}),
        "tool_call_id": tool_call.id
    }
    return response, base_64

with gr.Blocks() as ui:
    with gr.Row():
        chatbot = gr.Chatbot(height=500, type="messages")
        image_output = gr.Image(height=500)
    with gr.Row():
        entry = gr.Textbox(label="Chat with our Languages Teacher:")
    with gr.Row():
        clear = gr.Button("Clear")

    def do_entry(message, history):
        history += [{"role":"user", "content":message}]
        return "", history

    
    entry.submit(do_entry, inputs=[entry, chatbot], outputs=[entry, chatbot]).then(
        chat, inputs=chatbot, outputs=[chatbot, image_output])
        
    clear.click(lambda: None, inputs=None, outputs=chatbot, queue=False)

ui.launch(inbrowser=True)
    