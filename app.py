from flask import Flask, render_template, request
import requests

app = Flask(__name__)

@app.route("/", methods=["POST", "GET"])
def index():
    user_input = None
    if request.method == "POST":
        user_input = request.form.get("study_material")
        print(f"User entered: {user_input}") 
    return render_template("index.html", user_input=user_input)

if __name__ == "__main__":
    app.run(debug=True)