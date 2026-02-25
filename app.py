from flask import Flask

app = Flask(__name__, static_url_path='', static_folder='.')

@app.route("/")
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Mini CRM</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                text-align: center;
                margin-top: 50px;
                background-color: #f4f4f4;
            }
            img {
                margin-top: 20px;
            }
            h1 {
                color: #333;
            }
        </style>
    </head>
    <body>
        <h1>Mini CRM</h1>
        <img src="/logo.jpeg" width="180">
        <p>Bienvenido al sistema</p>
    </body>
    </html>
    """

if __name__ == "__main__":
    app.run(debug=True)
