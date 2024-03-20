import google.generativeai as genai

def send_message(message):
    api_key = "AIzaSyCNE0vxDN07f_cOQaoJ04Hf8xebD-CPfUs"

    genai.configure(api_key=api_key)

    model = genai.GenerativeModel('gemini-pro')

    chat = model.start_chat()

    response = chat.send_message(message)

    return response.text