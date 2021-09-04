import io
import base64
import os
from flask_material import Material
from flask_scss import Scss
from flask import Flask, render_template, request
from flaskr import standings, matchups, scores, blowouts, favorite_players
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from flask import send_from_directory

app = Flask(__name__)
Material(app)
Scss(app, static_dir='flaskr/static', asset_dir='flaskr/assets')
app.debug = True


@app.route('/')
def home():
    app.route('/')
    return render_template("home.html")


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')


@app.route('/bests-and-worsts')
def bests_and_worsts_form():
    app.route('/bests-and-worsts')
    return render_template("bests-worsts-form.html")


@app.route('/standings', methods=['POST', 'GET'])
def all_time_standings():
    resp = standings.list()
    return render_template("standings.html", result=resp)


@app.route('/favorite-picks', methods=['POST', 'GET'])
def favorite_picks():
    resp = favorite_players.top_drafted()
    return render_template("favorites.html", result=resp)


@app.route('/matchups', methods=['POST'])
def list_matchups():
    start_year = request.form['startyear'] or None
    end_year = request.form['endyear'] or None
    playoffs = 'margins-playoffs' in request.form or None
    blowouts = request.form["matchup-radio"] == 'blowouts'
    count = request.form['count'] or 10
    resp = matchups.results(start_year, end_year, playoffs, count, blowouts)
    return render_template("matchups.html", result=resp)


@app.route('/individual-seasons', methods=['POST'])
def list_seasons():
    start_year = request.form['startyear'] or None
    end_year = request.form['endyear'] or None
    count = request.form['count'] or 10
    best = request.form['seasons-radio'] == 'best-seasons'
    resp = scores.best_and_worst_seasons(start_year, end_year, count, best)
    return render_template('seasons.html', result=resp)


@app.route('/individual-weeks', methods=['POST'])
def list_weeks():
    print('request', request.form)
    start_year = request.form['startyear'] or None
    end_year = request.form['endyear'] or None
    playoffs = 'weeks-playoffs' in request.form or None
    count = request.form['count'] or 10
    best = request.form["week-scores-radio"] == 'best-weeks'
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


if __name__ == "__main__":
    app.run(debug=True)
