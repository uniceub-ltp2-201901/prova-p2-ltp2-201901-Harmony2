from flask import Flask
from flask import render_template
from flask import redirect
from flask import request
import requests
import mysql.connector


db = mysql.connector.connect(host="localhost", user="root", password="root")
cursor = db.cursor()

cursor.execute("USE url")


app = Flask(__name__)

def validate_url(url):
    r = requests.get(url)
    if r.status_code == 200:
        return True
    else:
        return False


@app.route("/")
def home():
    return render_template("home.html")

@app.route("/top")
def top():
    cursor.execute("SELECT counter, id FROM urls")
    a = cursor.fetchall()
    a = sorted(a, key=lambda x: x[0], reverse=True)
    return render_template("top.html", a=a)


@app.route("/test")
def red_test():
    return redirect("https://www.youtube.com/watch?v=5B0H-5cLkEo")

@app.route("/shorten", methods=["post", "get"])
def shorten():
    if request.method == "POST":
        full_url = request.form.get('full_url')
        cursor.execute("INSERT INTO urls (url, counter) VALUES ('%s', 0)"%full_url)
        db.commit()
        cursor.execute("SELECT MAX(id) FROM urls")
        url_id = cursor.fetchall()[0][0]
    else:
        return render_template("unauth.html")
    return render_template("short.html", full_url=full_url, url_id=url_id)

@app.route("/<url_id>")
def red(url_id):
    cursor.execute("select url from urls where id = %s;"%url_id)
    try:
        full_url = cursor.fetchall()[0][0]
    except:
        return render_template("unauth.html", error="Not a valid url")
    if validate_url(full_url):            
        cursor.execute("select counter from urls where id = %s;"%url_id)
        counter = cursor.fetchall()[0][0]
        counter += 1
        cursor.execute("UPDATE urls SET counter = %s WHERE id = '%s'"%(counter, url_id))
        print("UPDATE urls SET counter = %s WHERE id = '%s'"%(counter, url_id))
        db.commit()
        return redirect(full_url)
    else:
        return render_template("unauth.html", error="not a valid url")

if __name__ == "__main__":
    app.run(debug=False,host="0.0.0.0")