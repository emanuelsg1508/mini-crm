from flask import Flask, render_template_string, request, redirect, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "clave_secreta_super_segura"

META_MENSUAL = 5000
COMISION = 0.05  # 5%

VENDEDORES = ["Jeronimo", "Emanuel", "Julian"]

def init_db():
    conn = sqlite3.connect("crm.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente TEXT,
            monto REAL,
            empleado TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

login_html = """
<!DOCTYPE html>
<html>
<head>
<style>
body {
    background: black;
    color: gold;
    font-family: Arial;
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
}
.login-box {
    background: #111;
    padding: 40px;
    border-radius: 10px;
    width: 300px;
    text-align: center;
}
input {
    width: 100%;
    padding: 8px;
    margin: 10px 0;
}
button {
    width: 100%;
    padding: 10px;
    background: gold;
    border: none;
    color: black;
    font-weight: bold;
    cursor: pointer;
}
</style>
</head>
<body>
<div class="login-box">
<h2>Imperium G</h2>
<form method="POST">
<input name="username" placeholder="Usuario" required>
<input name="password" type="password" placeholder="Contraseña" required>
<button type="submit">Ingresar</button>
</form>
</div>
</body>
</html>
"""

dashboard_html = """
<!DOCTYPE html>
<html>
<head>
<style>
body {
    font-family: Arial;
    background-color: black;
    color: gold;
    margin: 0;
    padding: 30px;
}

.container {
    max-width: 1000px;
    margin: auto;
}

.logo {
    text-align: center;
}

.logo img {
    width: 180px;
}

.card {
    background: #111;
    padding: 20px;
    border-radius: 10px;
    margin-top: 20px;
}

button {
    background: gold;
    color: black;
    padding: 10px;
    border: none;
    cursor: pointer;
    border-radius: 5px;
    font-weight: bold;
}

input, select {
    width: 100%;
    padding: 8px;
    margin-top: 5px;
    background: #222;
    color: gold;
    border: 1px solid gold;
}

.progress-bar {
    background: #333;
    border-radius: 10px;
    overflow: hidden;
    margin-top: 10px;
}

.progress-fill {
    height: 20px;
    background: gold;
    width: {{ progreso }}%;
    text-align: center;
    color: black;
    font-weight: bold;
}
</style>
</head>
<body>

<div class="container">

<div class="logo">
<img src="/static/logo.png" alt="Imperium G Logo">
<h1>Imperium G - CRM</h1>
</div>

<div class="card">
<h2>🏆 Top Vendedor: {{ top_vendedor }}</h2>
<a href="/logout" style="color: gold;">Cerrar sesión</a>
</div>

<div class="card">
<h3>Meta Mensual: ${{ meta }}</h3>
<p>Total Vendido: ${{ total }}</p>
<p>Falta: ${{ falta }}</p>
<div class="progress-bar">
<div class="progress-fill">{{ progreso }}%</div>
</div>
</div>

<div class="card">
<h3>Registrar Venta</h3>
<form method="POST">
<label>Cliente</label>
<input name="cliente" required>

<label>Monto</label>
<input name="monto" type="number" step="0.01" required>

<label>Empleado</label>
<select name="empleado">
{% for vendedor in vendedores %}
<option>{{ vendedor }}</option>
{% endfor %}
</select>

<br><br>
<button type="submit">Registrar Venta</button>
</form>
</div>

<div class="card">
<h3>Ranking</h3>
<ul>
{% for nombre, total in ranking %}
<li>{{ nombre }} - ${{ total }}</li>
{% endfor %}
</ul>

<h3>Comisiones (5%)</h3>
<ul>
{% for nombre, valor in comisiones.items() %}
<li>{{ nombre }} - ${{ valor }}</li>
{% endfor %}
</ul>
</div>

</div>
</body>
</html>
"""

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == "admin" and request.form["password"] == "1234":
            session["logged_in"] = True
            return redirect("/")
        return "Credenciales incorrectas"
    return login_html

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/", methods=["GET", "POST"])
def home():
    if not session.get("logged_in"):
        return redirect("/login")

    conn = sqlite3.connect("crm.db")
    c = conn.cursor()

    if request.method == "POST":
        cliente = request.form["cliente"]
        monto = float(request.form["monto"])
        empleado = request.form["empleado"]

        c.execute(
            "INSERT INTO ventas (cliente, monto, empleado) VALUES (?, ?, ?)",
            (cliente, monto, empleado)
        )
        conn.commit()
        return redirect("/")

    c.execute("SELECT * FROM ventas")
    ventas = c.fetchall()

    total = sum(v[2] for v in ventas)

    ranking_dict = {}
    for v in ventas:
        ranking_dict[v[3]] = ranking_dict.get(v[3], 0) + v[2]

    ranking = sorted(ranking_dict.items(), key=lambda x: x[1], reverse=True)

    comisiones = {nombre: round(total * COMISION, 2) for nombre, total in ranking}
    top_vendedor = ranking[0][0] if ranking else "Nadie aún"

    falta = max(META_MENSUAL - total, 0)
    progreso = round((total / META_MENSUAL) * 100, 2) if META_MENSUAL > 0 else 0

    conn.close()

    return render_template_string(
        dashboard_html,
        total=total,
        ranking=ranking,
        comisiones=comisiones,
        top_vendedor=top_vendedor,
        meta=META_MENSUAL,
        falta=falta,
        progreso=progreso,
        vendedores=VENDEDORES
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
