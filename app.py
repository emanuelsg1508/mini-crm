from flask import Flask, render_template_string, request, redirect, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "clave_secreta_super_segura"

META_MENSUAL = 5000
COMISION = 0.05  # 5%

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
<h2>Login Mini CRM PRO</h2>
<form method="POST">
Usuario:
<input name="username" required><br><br>
Contraseña:
<input name="password" type="password" required><br><br>
<button type="submit">Ingresar</button>
</form>
"""

dashboard_html = """
<h1>Mini CRM PRO</h1>
<h2>🏆 Top Vendedor: {{ top_vendedor }}</h2>
<a href="/logout">Cerrar sesión</a>

<hr>

<h3>📊 Meta Mensual: {{ meta }}</h3>
<p>Total Vendido: {{ total }}</p>
<p>Falta para la meta: {{ falta }}</p>
<p>Progreso: {{ progreso }}%</p>

<hr>

<h2>Registrar Venta</h2>
<form method="POST">
Cliente:
<input name="cliente" required><br><br>

Monto:
<input name="monto" type="number" step="0.01" required><br><br>

Empleado:
<select name="empleado">
<option>Carlos</option>
<option>Maria</option>
<option>Andres</option>
</select><br><br>

<button type="submit">Registrar Venta</button>
</form>

<hr>

<h3>Ranking</h3>
<ul>
{% for nombre, total in ranking %}
<li>{{ nombre }} - {{ total }}</li>
{% endfor %}
</ul>

<h3>Comisiones (5%)</h3>
<ul>
{% for nombre, valor in comisiones.items() %}
<li>{{ nombre }} - {{ valor }}</li>
{% endfor %}
</ul>
"""

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "1234":
            session["logged_in"] = True
            return redirect("/")
        else:
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

    comisiones = {}
    for nombre, total_vendido in ranking:
        comisiones[nombre] = round(total_vendido * COMISION, 2)

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
        progreso=progreso
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
