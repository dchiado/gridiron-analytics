from flask import Flask, render_template, request
from flaskr import records, matchups, scores

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

@app.route('/scores', methods=['POST'])
def list_scores():
    start_year = request.form['startyear'] or None
    end_year = request.form['endyear'] or None
    playoffs = 'playoffs' in request.form or None
    best = request.form["radioAnswer"] == 'best'
    resp = scores.relative_to_league(start_year, end_year, playoffs, best)
    return render_template("scores.html", result=resp)

if __name__=="__main__":
    app.run(debug=True)
