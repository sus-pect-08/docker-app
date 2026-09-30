import os
import time
import pymysql
from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)

# Legge le configurazioni dalle variabili d'ambiente di Docker
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "rootpassword")
DB_NAME = os.getenv("DB_NAME", "testdb")

def get_connection():
    # Attende che MySQL sia pronto ad accettare connessioni
    connection = None
    for i in range(10):
        try:
            connection = pymysql.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME,
                cursorclass=pymysql.cursors.DictCursor
            )
            return connection
        except Exception as e:
            print(f"Tentativo di connessione fallito, riprovo tra 3 secondi... ({e})")
            time.sleep(3)
    return None

def init_db():
    """Inizializza la tabella se non esiste"""
    connection = get_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS utenti (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        nome VARCHAR(100) NOT NULL,
                        creato_il TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
            connection.commit()
        finally:
            connection.close()

# Template HTML con Bootstrap per una UI pulita e moderna
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <title>Gestione Utenti MySQL</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light py-5">
    <div class="container" style="max-width: 700px;">
        <h1 class="mb-4 text-center">Gestione Utenti</h1>
        
        <!-- Form per inserire un nuovo utente -->
        <div class="card shadow-sm mb-4">
            <div class="card-body">
                <h5 class="card-title">Aggiungi Nuovo Utente</h5>
                <form action="/add" method="POST" class="row g-3">
                    <div class="col-8">
                        <input type="text" name="nome" class="form-control" placeholder="Nome e cognome" required>
                    </div>
                    <div class="col-4">
                        <button type="submit" class="btn btn-primary w-100">Salva</button>
                    </div>
                </form>
            </div>
        </div>

        <!-- Tabella con la lista degli utenti -->
        <div class="card shadow-sm">
            <div class="card-body">
                <h5 class="card-title mb-3">Utenti Registrati</h5>
                <table class="table table-striped">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Nome</th>
                            <th>Creato il</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for row in utenti %}
                        <tr>
                            <td>{{ row['id'] }}</td>
                            <td>{{ row['nome'] }}</td>
                            <td>{{ row['creato_il'] }}</td>
                        </tr>
                        {% else %}
                        <tr>
                            <td colspan="3" class="text-center text-muted">Nessun utente presente nel database.</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</body>
</html>
"""

@app.route("/")
def index():
    """Pagina principale che mostra la lista degli utenti"""
    connection = get_connection()
    utenti = []
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM utenti ORDER BY id DESC")
                utenti = cursor.fetchall()
        finally:
            connection.close()
    return render_template_string(HTML_TEMPLATE, utenti=utenti)

@app.route("/add", methods=["POST"])
def add_user():
    """Rotta per gestire l'inserimento dal form"""
    nome = request.form.get("nome")
    if nome:
        connection = get_connection()
        if connection:
            try:
                with connection.cursor() as cursor:
                    cursor.execute("INSERT INTO utenti (nome) VALUES (%s)", (nome,))
                connection.commit()
            finally:
                connection.close()
    return redirect(url_for("index"))

if __name__ == "__main__":
    init_db()
    # Avvia il server Flask sulla porta 5000
    app.run(host="0.0.0.0", port=5000, debug=True)