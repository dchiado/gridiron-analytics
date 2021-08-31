import io
import base64
from flask_material import Material
from flask_scss import Scss
from flask import Flask, render_template, request
from flaskr import records, matchups, scores, blowouts, favorite_players
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

app = Flask(__name__)
Material(app)
Scss(app, static_dir='flaskr/static', asset_dir='flaskr/assets')
app.debug = True


@app.route('/')
def home():
    app.route('/')
    return render_template("home.html")


@app.route('/seasons-form')
def seasons_form():
    app.route('/seasons-form')
    return render_template("seasons-form.html")


@app.route('/matchups-form')
def matchups_form():
    app.route('/matchups-form')
    return render_template("matchups-form.html")


@app.route('/drafts-form')
def drafts_form():
    app.route('/drafts-form')
    return render_template("drafts-form.html")


@app.route('/records', methods=['POST'])
def list_records():
    start_year = request.form['startyear']
    end_year = request.form['endyear']
    resp = records.list(start_year, end_year)
    return render_template("records.html", result=resp)


@app.route('/matchups', methods=['POST'])
def list_matchups():
    start_year = request.form['startyear'] or None
    end_year = request.form['endyear'] or None
    playoffs = 'margins-playoffs' in request.form or None
    print(request.form)
    blowouts = request.form["radio"] == 'blowouts'
    count = request.form['count'] or 10
    resp = matchups.results(start_year, end_year, playoffs, count, blowouts)
    return render_template("matchups.html", result=resp)


@app.route('/individual-seasons', methods=['POST'])
def list_seasons():
    start_year = request.form['startyear'] or None
    end_year = request.form['endyear'] or None
    count = request.form['count'] or 10
    best = request.form["radio"] == 'best-seasons'
    resp = scores.best_and_worst_seasons(start_year, end_year, count, best)
    return render_template("seasons.html", result=resp)


@app.route('/individual-weeks', methods=['POST'])
def list_weeks():
    start_year = request.form['startyear'] or None
    end_year = request.form['endyear'] or None
    playoffs = 'weeks-playoffs' in request.form or None
    count = request.form['count'] or 10
    best = request.form["radio"] == 'best-weeks'
    resp = scores.best_and_worst_weeks(
        start_year, end_year, playoffs, count, best
    )
    return render_template("weeks.html", result=resp)


@app.route('/yearly-blowouts', methods=['POST'])
def list_blowouts():
    start_year = request.form['startyear'] or None
    end_year = request.form['endyear'] or None
    playoffs = 'blowouts-playoffs' in request.form or None
    resp = blowouts.by_year(start_year, end_year, playoffs)

    plot_blowouts = [
        sub["blowout_count"] for sub in resp.values()
        if "blowout_count" in sub.keys()
    ]
    plot_scores = [
        sub["average_score"] for sub in resp.values()
        if "average_score" in sub.keys()
    ]
    years = list(resp.keys())
    fig = Figure()
    ax = fig.subplots()
    ax.plot(years, plot_blowouts, color='blue', label="Blowouts")
    ax.tick_params(axis='y', labelcolor='blue')
    ax.set_ybound(lower=0, upper=max(plot_blowouts) + 1)
    ax.set_yscale('linear')

    ax2 = ax.twinx()
    ax2.plot(years, plot_scores, color='red', label="Average Score")
    ax2.tick_params(axis='y', labelcolor='red')

    fig.legend()

    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    pngImage = io.BytesIO()
    FigureCanvas(fig).print_png(pngImage)
    pngImageB64String = "data:image/png;base64,"
    pngImageB64String += base64.b64encode(pngImage.getvalue()).decode('utf8')

    return render_template(
        "blowouts.html", result=resp, plot=pngImageB64String
    )


@app.route('/favorite-picks', methods=['POST', 'GET'])
def favorite_picks():
    resp = favorite_players.top_drafted()
    return render_template("favorites.html", result=resp)


if __name__ == "__main__":
    app.run(debug=True)
