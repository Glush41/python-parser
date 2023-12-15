from flask import Flask, render_template

from database import sort_desc
from database import sort_asc

app = Flask(__name__)


@app.route('/')
def main_page():
    return 'Привет, если хочешь увидить таблицу по возрастанию цены ghjghghhghg добавь "/asc" к URL. Если по убыванию - "/desc"'


@app.route("/desc")
def first_page():
    answers = sort_desc()
    return render_template("index.html", answer=answers)


@app.route("/asc")
def second_page():
    answers = sort_asc()
    return render_template("index2.html", answer=answers)
