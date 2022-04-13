# CST8267- Advance Database Project
# Section: 350
# Semester: 22W
# Professor: Taghreed Altamimi
# Student name: Jing Zhao
# Student ID: 040994750
# Student Email: zhao0224@algonquinlive.com
# Project: MongoDB database flask display data writing by Python

import pandas as pd
from flask import Flask, redirect, url_for, render_template, request, session, flash, json
from application.controller import Controller
from application.models import Record
import plotly.express as px
import json
import plotly


app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'


@app.route("/")
@app.route("/home/")
def home():
    return render_template("index.html")


@app.route("/display")
def display():
    c = Controller()
    dt = c.get_all()
    return render_template("display.html", data=dt)


@app.route("/search", methods=["POST", "GET"])
def search():
    if request.method == "GET":
        return render_template("search.html")

    if request.method == "POST":
        incident_number = request.form["incident_number"]
        incident_type = request.form["incident_type"]
        reported_date = request.form["reported_date"]
        pop_center = request.form["pop_center"]
        province = request.form["province"]
        company = request.form["company"]
        substance = request.form["substance"]
        significant = request.form["significant"]
        category = request.form["category"]
        c = Controller()
        db = c.db_connect()
        col = db['pipeline']
        results = list(col.find({"$or": [
            {"Incident Number": incident_number},
            {"Incident Types": incident_type},
            {"Reported Date": reported_date},
            {"Nearest Populated Centre": pop_center},
            {"Province": province},
            {"Company": company},
            {"Substance": substance},
            {"Significant": significant},
            {"What happened category": category}
        ]}, {'Incident Number': 1, 'Incident Types': 1, 'Reported Date': 1, 'Nearest Populated Centre': 1,
             'Province': 1, 'Company': 1, 'Substance': 1, 'Significant': 1, 'What happened category': 1,
             '_id': 0}))
        json.dumps(results, default=object)
        session['res'] = results
        return redirect(url_for("searchresult"))


@app.route('/searchresult', methods=["POST", "GET"])
def searchresult():
    results = session.get('res', None)
    if results is None:
        flash("There is no matching record in database")
    return render_template("searchresult.html", results=results)


@app.route("/add", methods=["POST", "GET"])
def add():
    if request.method == "GET":
        return render_template("add.html")
    if request.method == "POST":
        incident_number = request.form["incident_number"]
        incident_type = request.form["incident_type"]
        reported_date = request.form["reported_date"]
        pop_center = request.form["pop_center"]
        province = request.form["province"]
        company = request.form["company"]
        substance = request.form["substance"]
        significant = request.form["significant"]
        category = request.form["category"]

        record = Record(
            incident_num=incident_number,
            incident_typ=incident_type,
            report_date=reported_date,
            nearest_centre=pop_center,
            province=province,
            company=company,
            substance=substance,
            significant=significant,
            category=category,
        )
        c = Controller()
        db = c.db_connect()
        col = db['pipeline']
        inc_num_in_db = c.record_eixsing_to_insert(incident_number)
        col.insert_one(record.asdict())
        return redirect("/display")


@app.route("/<string:inc_num>/update", methods=["POST", "GET"])
def update(inc_num):
    if request.method == "GET":
        c = Controller()
        db = c.db_connect()
        col = db['pipeline']
        results = col.find_one({"Incident Number": inc_num},
                               {'Incident Number': 1, 'Incident Types': 1, 'Reported Date': 1,
                                'Nearest Populated Centre': 1,
                                'Province': 1, 'Company': 1, 'Substance': 1, 'Significant': 1,
                                'What happened category': 1,
                                '_id': 0})
        return render_template("update.html", results=results)

    if request.method == "POST":
        incident_number = request.form["incident_number"]
        incident_type = request.form["incident_type"]
        reported_date = request.form["reported_date"]
        pop_center = request.form["pop_center"]
        province = request.form["province"]
        company = request.form["company"]
        substance = request.form["substance"]
        significant = request.form["significant"]
        category = request.form["category"]

        record = Record(
            incident_num=incident_number,
            incident_typ=incident_type,
            report_date=reported_date,
            nearest_centre=pop_center,
            province=province,
            company=company,
            substance=substance,
            significant=significant,
            category=category,
        )
        c = Controller()
        c.db_connect()
        c.update_record(record)
        flash("Record updated successfully!")
    return redirect("/display")


@app.route("/chart")
def chart():
    c = Controller()
    inc_num_year = c.incident_per_year()
    year = []
    inc_num = []
    for inc in inc_num_year:
        year.append(inc[0])
        inc_num.append(inc[1])
    df_new = pd.DataFrame({'Incident Per Year': inc_num, 'Reported Year': year})
    fig1 = px.bar(df_new, x='Reported Year', y='Incident Per Year', orientation="v")

    fig1.update_layout(
        width=1100,
        height=700,
    )
    graph1JSON = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template("chart.html", title="Chart", graph1JSON=graph1JSON)


@app.route("/<string:inc_num>/delete", methods=["POST", "GET"])
def delete(inc_num):
    if request.method == "POST":
        c = Controller()
        c.db_connect()
        c.delete_record(inc_num)
        return redirect("/search")
    return render_template("delete.html")


if __name__ == "__main__":
    app.run(debug=True)
