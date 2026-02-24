from flask import Flask, render_template_string, request, redirect
import sqlite3

app = Flask(__name__)

# Crear base de datos si no existe
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

empleados = {
    "Carlos": 0,
    "Maria": 0,
    "Andres": 0
}

html = """
<h1>Mini CRM Web PRO</h1>

<form method="POST">
    Cliente: <input name="cliente"><br>
    Monto: <input name="monto"><br>
    <button type="submit">Registrar Venta</button>
</form>

<h2>Ventas Registradas</h2>
<ul>
{% for v in ventas %}
<li>{{v[1]}} - {{v[2]}} - {{v[3]}}</li>
{% endfor %}
</ul>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    conn = sqlite3.connect("crm.db")
    c = conn.cursor()

    if request.method == "POST":
        cliente = request.form["cliente"]
        monto = float(request.form["monto"])

        empleado = min(empleados, key=empleados.get)
        empleados[empleado] += monto

        c.execute("INSERT INTO ventas (cliente, monto, empleado) VALUES (?, ?, ?)",
                  (cliente, monto, empleado))
        conn.commit()
        return redirect("/")

    c.execute("SELECT * FROM ventas")
    ventas = c.fetchall()
    conn.close()

    return render_template_string(html, ventas=ventas)

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
