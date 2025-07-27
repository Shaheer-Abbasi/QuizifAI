import os
from flask import Flask, render_template, request, jsonify
import requests
from openai import OpenAI
from google import genai
import logging
from dotenv import load_dotenv
import os

app = Flask(__name__)

#client = OpenAI(
#    base_url="https://openrouter.ai/api/v1",
#    api_key=os.getenv("OPENAI_API_KEY")
#)
#completion = client.chat.completions.create(
#        model="tencent/hunyuan-a13b-instruct:free",
#        messages=[
#            {
#            "role": "user",
#            "content": "Give me 5 facts about the following. Format your answer in a python string array. " + user_input if user_input else "say 'No input provided'"
#            }
#        ]
#        )

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY"),
)

load_dotenv()

@app.route("/", methods=["POST", "GET"])
def index():
    ai_response = None
    user_input = None
     
    if request.method == "POST":
        user_input = request.form.get("study_material")
        logging.info(f"User entered: {user_input}") 

        response = client.models.generate_content(
            model="gemma-3n-e2b-it",
            contents="Give me 1 fact about the following. Format your answer in a python string array: " + user_input if user_input else "say 'No input provided'",
        )
        
        logging.basicConfig(level=logging.INFO)
        logging.info(response.text)

        ai_response = response.text if response and hasattr(response, 'text') else "No response from AI"
        logging.info(f"AI response: {ai_response}")

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"status": "success", "input" : user_input}, {"ai_response": ai_response})
        else:
            return render_template("index.html")
   
    return render_template("index.html", user_input=user_input, ai_response=ai_response)

if __name__ == "__main__":
    app.run(debug=True)