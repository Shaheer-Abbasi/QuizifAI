import os
from flask import Flask, render_template, request, jsonify
import requests
from openai import OpenAI
import logging

app = Flask(__name__)
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",
)

@app.route("/", methods=["POST", "GET"])
def index():
    completion = client.chat.completions.create(
    model="deepseek/deepseek-chat-v3-0324:free",
    messages=[
        {
        "role": "user",
        "content": "When did Napoleon Bonaparte become Emperor of the French?"
        }
    ]
    )
    logging.basicConfig(level=logging.INFO)
    logging.info(completion.choices[0].message.content)
    
    user_input = None
    if request.method == "POST":
        user_input = request.form.get("study_material")
        logging.info(f"User entered: {user_input}") 

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"status": "success", "input" : user_input})
        else:
            return render_template("index.html")
    return render_template("index.html", user_input=user_input)

if __name__ == "__main__":
    app.run(debug=True)