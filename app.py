import os
from flask import Flask, render_template, request, jsonify
import requests
from openai import OpenAI
import logging
from dotenv import load_dotenv
import os

app = Flask(__name__)

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENAI_API_KEY")
)

load_dotenv()

@app.route("/", methods=["POST", "GET"])
def index():
    user_input = None
    if request.method == "POST":
        user_input = request.form.get("study_material")
        logging.info(f"User entered: {user_input}") 

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"status": "success", "input" : user_input})
        else:
            return render_template("index.html")
        
    completion = client.chat.completions.create(
    model="deepseek/deepseek-chat-v3-0324:free",
    messages=[
        {
        "role": "user",
        "content": "Give me 5 facts about the following " + user_input if user_input else "say 'No input provided'"
        }
    ]
    )
    logging.basicConfig(level=logging.INFO)
    logging.info(completion.choices[0].message.content)

    return render_template("index.html", user_input=user_input)

if __name__ == "__main__":
    app.run(debug=True)