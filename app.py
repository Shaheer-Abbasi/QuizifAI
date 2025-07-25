from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

@app.route("/", methods=["POST", "GET"])
def index():
    user_input = None
    if request.method == "POST":
        user_input = request.form.get("study_material")
        print(f"User entered: {user_input}") 

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"status": "success", "input" : user_input})
        else:
            return render_template("index.html")
    return render_template("index.html", user_input=user_input)

if __name__ == "__main__":
    app.run(debug=True)