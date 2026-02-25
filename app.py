from flask import Flask, render_template_string, request, redirect
import sqlite3
import os

app = Flask(__name__)

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

html = """
<h1>Mini CRM PRO</h1>

<h2>Registrar Venta</h2>
<form method="POST">
    Cliente: <input name="cliente" required><br>
    Monto: <input name="monto" type="number" step="0.01" required><br>
    Empleado:
    <select name="empleado">
        <option>Carlos</option>
        <option>Maria</option>
        <option>Andres</option>
    </select><br>
    <button type="submit">Registrar</button>
</form>

<hr>

<h2>Resumen</h2>
<p><strong>Total Ventas:</strong> {{ total }}</p>

<h2>Ranking Empleados</h2>
<ul>
{% for nombre, total in ranking %}
<li>{{ nombre }} - {{ total }}</li>
{% endfor %}
</ul>
<h2>Comisiones (10%)</h2>
<ul>
{% for nombre, valor in comisiones.items() %}
<li>{{ nombre }} - {{ valor }}</li>
{% endfor %}
</ul>
<hr>

<h2>Historial de Ventas</h2>
<table border="1">
<tr>
<th>Cliente</th>
<th>Monto</th>
<th>Empleado</th>
</tr>
{% for v in ventas %}
<tr>
<td>{{ v[1] }}</td>
<td>{{ v[2] }}</td>
<td>{{ v[3] }}</td>
</tr>
{% endfor %}
</table>
"""

@app.route("/", methods=["GET", "POST"])
def home():
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
    comisiones[nombre] = round(total_vendido * 0.10, 2)

    conn.close()

return render_template_string(
    html,
    ventas=ventas,
    total=total,
    ranking=ranking,
    comisiones=comisiones
)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
