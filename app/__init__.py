"""
Akasha: QianjunZhou, AidanWong, IvanGontchar, JasonChao
SoftDev
P02: Makers Makin' It, Act I
2025-01-09
Time Spent: 1
"""

#----------------------------------------------------------------------------------------------------------------

from flask import Flask, flash, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
import os
import datetime
import string
import random
import uuid
import json
import re
from CustomModules import api_modules, db_modules

db_modules.create_database()

app = Flask(__name__)
app.secret_key = "secret hehe"
#app.secret_key = os.urandom(32)

#----------------------------------------------------------------------------------------------------------------

# Landing Page
@app.route('/', methods = ['GET', 'POST'])
def landing():
    if 'username' in session:
        return render_template("landing.html", logged_in = True, username = session['username'])
    return render_template("landing.html", logged_in = False)

#----------------------------------------------------------------------------------------------------------------

# Function to update random username on register page
def updateusername():
    global lastusername
    lastusername = uuid.uuid4()
    return 0

# Authentication Page
@app.route('/auth', methods = ['GET', 'POST'])
def auth():
    if 'username' in session:
        return redirect(url_for('landing'))
    if request.method == 'POST':
        username = lastusername
        password = request.form['password']
        #for i in password:
        #    for k in username:
        #        if i == k:
        #            return render_template("auth.html", Username = lastusername)
        actualusername = lastusername.hex
        #print(lastusername.hex)
        for i in password:
            for k in actualusername:
                if i == k:
                    return render_template("auth.html", Username = lastusername, messages = "Your password cannot contain any parts of your username")
        if(request.form.get('checkbox1') == "on"):
            return render_template("auth.html", Username = lastusername, messages = "Please don't disagree to the terms and conditions")
        if(request.form.get('checkbox2') == None):
            return render_template("auth.html", Username = lastusername, messages = "Please agree to the terms and conditions")
        #print(request.form.get('checkbox1'))
        #print(request.form.get('checkbox2'))
        realage = request.form.get('ages').split("+")
        if(int(realage[0]) < 18):
            return render_template("auth.html", Username = lastusername, messages = "Please have a parent make an account for you since you are underaged")

        result = db_modules.add_user(actualusername, password)
        if (result == "Username already exists"):
            return render_template("auth.html", Username = lastusername, messages = result)
        session['username'] = username
        return redirect(url_for('landing'))
    updateusername()
    return render_template("auth.html", Username = lastusername)

# Login function
@app.route("/login", methods = ['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('landing'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        result = db_modules.login_user(username, password)
        if (result == "Login successful"):
            session['username'] = username
            return redirect(url_for('landing'))
        return render_template("login.html", messages = result)
    return render_template("login.html")

@app.route("/profile")
def profile():
    if 'username' in session:
        return render_template("profile.html", username = session['username'])
    return redirect(url_for('profile'))

# Logout page
@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect(url_for('landing'))

#----------------------------------------------------------------------------------------------------------------

# Classic game mode game page
@app.route("/game")
def game():
    if 'username' in session:
        return render_template("game.html", logged_in = True, username = session['username'])
    return render_template("game.html")

# Function to get data for classic game mode
@app.route("/getGameInfo")
def getGameInfo():
    word1 = api_modules.getRandomSearch()
    word2 = api_modules.getRandomSearch()

    word1Amount = api_modules.getSearchVolume(word1)
    word2Amount = api_modules.getSearchVolume(word2)

    x = {'word1': word1, 'count1': word1Amount, 'word2': word2, 'count2': word2Amount}
    return jsonify(x)

#----------------------------------------------------------------------------------------------------------------

x = "goofy setup" #ignore this please its goofy

@app.route("/game2")
def game2():
    global x
    x = getGameInfo2()
    return render_template("game2.html", mainData = x)

@app.route("/getGameInfo2")
def getGameInfo2():
    result = api_modules.randomCategory('celebrity')

    if not result or not isinstance(result, list): # Quick error handling
        print("No data available or result is not a list.")
        return

    randomAmount = random.randint(3, 7) # Make it actually random

    information = []
    for i in result:
        for k in range(randomAmount):
            imputed = False
            if (random.randint(0, 29) == 5):
                imputed = True
                information.append({
                    'name': i['name'].replace(" ", "_"),
                    'net_worth': i['net_worth']
                    }
                )
            if imputed:
                break
    #print(information)
    while (len(information) > 5):
        information.pop()
    #print(information)
    return information

@app.route("/getGameInfoJson")
def getGameInfoJson():
    return jsonify(x)

#----------------------------------------------------------------------------------------------------------------

# Define the upload folder path
UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')

# Set the upload folder configuration
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Make sure the folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route("/thub")
def thub():
    if 'username' in session:
        return render_template("thub.html", logged_in = True)
    return render_template("thub.html")

@app.route("/tcreate", methods=['GET', 'POST'])
def tcreate():
    if request.method == "POST":
        tournamentName = request.form.get("tournamentName")
        description = request.form.get("tournamentDescription", "")

        topics = []
        for i in range(1, 9):
            topic = f"topic{i}"
            image = f"image{i}"

            if topic in request.form:
                topicName = request.form[topic]
                image_file = request.files.get(image)
                if image_file:
                    # Ensure the upload folder exists
                    imagePath = os.path.join(app.config['UPLOAD_FOLDER'], image_file.filename)
                    image_file.save(imagePath)
                    topics.append((topicName, imagePath))

        # Add the tournament to the database
        db_modules.add_tournament(tournamentName, description, topics)

        flash("Tournament created successfully!")
        return redirect(url_for("thub"))

    return render_template("tcreate.html")
            

#----------------------------------------------------------------------------------------------------------------

# Game description
@app.route("/gdesc")
def gdesc():
    return render_template("gdesc.html")

if __name__ == "__main__":
    app.debug = True
    app.run()
