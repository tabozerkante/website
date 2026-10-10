
from flask import Flask, render_template, jsonify, request
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from urllib.error import HTTPError, URLError
import json

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/definition")
def get_definition():
    word = request.args.get("word", "").strip()

    if not word or len(word) > 100:
        return jsonify({"error": "Saisis un mot valide."}), 400

    params = urlencode({
        "action": "query",
        "format": "json",
        "prop": "extracts",
        "explaintext": 1,
        "redirects": 1,
        "titles": word
    })

    url = "https://fr.wiktionary.org/w/api.php?" + params

    req = Request(
        url,
        headers={"User-Agent": "LexiFrance/1.0 (learning project)"}
    )

    try:
        with urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode("utf-8"))

        pages = data.get("query", {}).get("pages", {})
        page = next(iter(pages.values()), {})

        if "missing" in page or not page.get("extract"):
            return jsonify({
                "error": "Aucune définition trouvée pour ce mot."
            }), 404

        return jsonify({
            "word": page.get("title", word),
            "definition": page["extract"],
            "source": "Wiktionnaire français"
        })

    except HTTPError as error:
        app.logger.exception("Erreur HTTP du dictionnaire")
        return jsonify({
            "error": f"Le dictionnaire a répondu avec le code {error.code}."
        }), 502

    except (URLError, TimeoutError):
        app.logger.exception("Erreur de connexion")
        return jsonify({
            "error": "Connexion impossible au dictionnaire. Vérifie Internet."
        }), 502

    except Exception:
        app.logger.exception("Erreur inattendue")
        return jsonify({
            "error": "Erreur interne. Consulte le terminal VS Code."
        }), 500


if __name__ == "__main__":
    app.run(debug=True)