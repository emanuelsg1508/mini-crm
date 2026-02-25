from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return """
    <h1>Mini CRM</h1>
    <img src="/static/logo.jpeg" width="200">
    """

if __name__ == "__main__":
    app.run(debug=True)
