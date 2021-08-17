from flask import Flask, render_template, request
from flaskr import records, matchups, scores, blowouts

app=Flask(__name__)

@app.route('/')
def home():
    app.route('/')
    return render_template("home.html")

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
    playoffs = 'playoffs' in request.form or None
    blowouts = request.form["radioAnswer"] == 'blowouts'
    count = request.form['count'] or 10
    resp = matchups.results(start_year, end_year, playoffs, count, blowouts)
    return render_template("matchups.html", result=resp)

@app.route('/individual-seasons', methods=['POST'])
def list_seasons():
    start_year = request.form['startyear'] or None
    end_year = request.form['endyear'] or None
    count = request.form['count'] or 10
    best = request.form["radioAnswer"] == 'best'
    resp = scores.best_and_worst_seasons(start_year, end_year, count, best)
    return render_template("seasons.html", result=resp)

@app.route('/individual-weeks', methods=['POST'])
def list_weeks():
    start_year = request.form['startyear'] or None
    end_year = request.form['endyear'] or None
    playoffs = 'playoffs' in request.form or None
    count = request.form['count'] or 10
    best = request.form["radioAnswer"] == 'best'
    resp = scores.best_and_worst_weeks(start_year, end_year, playoffs, count, best)
    return render_template("weeks.html", result=resp)

@app.route('/yearly-blowouts', methods=['POST'])
def list_blowouts():
    start_year = request.form['startyear'] or None
    end_year = request.form['endyear'] or None
    playoffs = 'playoffs' in request.form or None
    resp = blowouts.by_year(start_year, end_year, playoffs)
    return render_template("blowouts.html", result=resp)

if __name__=="__main__":
    app.run(debug=True)
