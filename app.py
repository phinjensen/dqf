from flask import Flask, abort, render_template, request, session
import json
import os
import sqlite3
import time
import uuid

from flask.wrappers import Response

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
app.jinja_env.policies["json.dumps_kwargs"] = {"ensure_ascii": False}
app.secret_key = b"6b6055679699d0bde49c7a333c24f601c79779cb673d61447719ecacfedd399a"


def get_db_connection():
    conn = sqlite3.connect("dqf.db")
    conn.row_factory = sqlite3.Row
    return conn


def get_db_id(cur):
    return cur.execute("SELECT last_insert_rowid()").fetchone()["last_insert_rowid()"]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload_batch", methods=["GET", "POST"])
def upload_batch():
    if request.method == "GET":
        return render_template("upload_batch.html")
    elif request.method == "POST":
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO batches (source_lang, target_lang) VALUES ('en', 'tr')"
            )
            batch_id = get_db_id(cur)
            batch_key = uuid.uuid4()
            cur.execute(
                "INSERT INTO batch_keys VALUES (?, ?)", (str(batch_key), batch_id)
            )

            file = request.files["file"]
            headers = file.readline().strip().decode("utf8").split("\t")[1:]
            header_ids = []
            for header in headers:
                cur.execute("INSERT INTO translators (name) VALUES (?)", (header,))
                header_ids.append(cur.lastrowid)
            for line in file.readlines():
                line = line.strip()
                source, *translations = line.decode("utf8").split("\t")
                cur.execute(
                    "INSERT INTO sentences (batch_id, source) VALUES (?, ?)",
                    (batch_id, source),
                )
                sentence_id = get_db_id(cur)
                cur.executemany(
                    "INSERT INTO translations (source_id, translator_id, translation) VALUES (?, ?, ?)",
                    [
                        (sentence_id, header_ids[i], translation)
                        for i, translation in enumerate(translations)
                    ],
                )
        return f"Success! Your key: {batch_key}"


@app.route("/dqf", methods=["GET", "POST"])
def dqf():
    if "key" not in request.args:
        abort(400)
    if request.method == "GET":
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT id, source
                FROM sentences
                WHERE batch_id=(
                    SELECT batch_id FROM batch_keys WHERE key=?
                )
                """,
                (request.args["key"],),
            )

            sentences = []
            for sentence in cur.fetchall():
                cur.execute(
                    """
                    SELECT translation, translator_id
                    FROM translations
                    WHERE source_id=?
                    """,
                    (sentence["id"],),
                )
                sentences.append(
                    {
                        "id": sentence["id"],
                        "source": sentence["source"],
                        "translations": {
                            t["translator_id"]: t["translation"] for t in cur.fetchall()
                        },
                    }
                )

            return render_template(
                "dqf.html",
                sentences=sentences,
                translators=sentences[0]["translations"].keys(),
            )
    elif request.method == "POST":
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT id, source
                FROM sentences
                WHERE batch_id=(
                    SELECT batch_id FROM batch_keys WHERE key=?
                )""",
                (request.args["key"],),
            )
            body = request.get_json()
            if not body:
                abort(400)
            for result in body:
                for key, rank in result["result"].items():
                    cur.execute(
                        "INSERT INTO rankings (translation_id, batch_key, rank) VALUES ((SELECT id FROM translations WHERE source_id=? AND translator_id=?), ?, ?)",
                        (result["id"], key, request.args["key"], rank),
                    )
            return ""


@app.route("/results", methods=["GET"])
def results():
    if "key" not in request.args:
        abort(400)
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, source
            FROM sentences
            WHERE batch_id=(
                SELECT batch_id FROM batch_keys WHERE key=?
            )
            """,
            (request.args["key"],),
        )
        results = []
        for sentence in cur.fetchall():
            cur.execute(
                """
                SELECT
                    rankings.rank,
                    translations.translation,
                    translators.name
                FROM rankings
                JOIN translations ON translations.id=rankings.translation_id
                JOIN translators ON translators.id=translations.translator_id
                WHERE rankings.batch_key=? AND translations.source_id=?;
                """,
                (request.args["key"], sentence["id"]),
            )
            results.append(
                {
                    "source": sentence["source"],
                    **{t["name"]: t["rank"] for t in cur.fetchall()},
                }
            )

        result = "{}\n{}".format(
            "\t".join(results[0].keys()),
            "\n".join(["\t".join(map(str, r.values())) for r in results]),
        )
        return Response(
            result,
            mimetype="text/csv",
            headers={"Content-Disposition": 'attachment; filename="results.csv"'},
        )
