import os
import random
import unicodedata

from flask import Flask, flash, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-only-secret-key")

PALABRAS = [
    "python", "flask", "servidor", "programa", "teclado", "pantalla",
    "variable", "funcion", "libreria", "ventana", "internet", "ordenador",
    "algoritmo", "database", "archivo", "carpeta", "sistema", "codigo",
]
MAX_INTENTOS = 6
ABECEDARIO = list("abcdefghijklmnñopqrstuvwxyz")

ETAPAS = [
    r"""
  +---+
  |   |
      |
      |
      |
      |
=========""",
    r"""
  +---+
  |   |
  O   |
      |
      |
      |
=========""",
    r"""
  +---+
  |   |
  O   |
  |   |
      |
      |
=========""",
    r"""
  +---+
  |   |
  O   |
 /|   |
      |
      |
=========""",
    r"""
  +---+
  |   |
  O   |
 /|\  |
      |
      |
=========""",
    r"""
  +---+
  |   |
  O   |
 /|\  |
 /    |
      |
=========""",
    r"""
  +---+
  |   |
  O   |
 /|\  |
 / \  |
      |
=========""",
]


def normalizar(texto):
    """Pasa a minúsculas y quita tildes, conservando la ñ."""
    texto = texto.lower().replace("ñ", "\0")
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return texto.replace("\0", "ñ")


def nueva_partida():
    session["palabra"] = random.choice(PALABRAS)
    session["adivinadas"] = []
    session["falladas"] = []


def estado_juego():
    palabra = session["palabra"]
    adivinadas = session["adivinadas"]
    falladas = session["falladas"]

    mostrada = " ".join(letra.upper() if letra in adivinadas else "_" for letra in palabra)
    intentos_restantes = MAX_INTENTOS - len(falladas)
    gano = all(letra in adivinadas for letra in palabra)
    perdio = intentos_restantes <= 0

    return {
        "mostrada": mostrada,
        "adivinadas": adivinadas,
        "falladas": falladas,
        "usadas": set(adivinadas) | set(falladas),
        "intentos_restantes": intentos_restantes,
        "max_intentos": MAX_INTENTOS,
        "gano": gano,
        "perdio": perdio,
        "terminado": gano or perdio,
        "palabra": palabra.upper(),
        "dibujo": ETAPAS[len(falladas)],
    }


@app.route("/")
def index():
    if "palabra" not in session:
        nueva_partida()
    return render_template("index.html", juego=estado_juego(), abecedario=ABECEDARIO)


@app.route("/adivinar", methods=["POST"])
def adivinar():
    if "palabra" not in session:
        nueva_partida()

    juego = estado_juego()
    if juego["terminado"]:
        return redirect(url_for("index"))

    letra = normalizar(request.form.get("letra", "").strip())

    if len(letra) != 1 or not letra.isalpha():
        flash("Ingresa una sola letra válida.")
    elif letra in juego["usadas"]:
        flash(f"Ya usaste la letra {letra.upper()}.")
    elif letra in session["palabra"]:
        session["adivinadas"] = session["adivinadas"] + [letra]
    else:
        session["falladas"] = session["falladas"] + [letra]

    return redirect(url_for("index"))


@app.route("/reiniciar")
def reiniciar():
    nueva_partida()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
