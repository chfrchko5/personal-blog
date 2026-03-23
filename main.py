from flask import Flask, render_template, request
from flask_basicauth import BasicAuth
import json
import datetime

guest_file = "guest.html"
admin_file = "admin.html"
article_file = "article.html"
articles_json = "blog/articles.json"

app = Flask(__name__)

# basic authentication thing to get into admin page
app.config['BASIC_AUTH_USERNAME'] = 'admin'
app.config['BASIC_AUTH_PASSWORD'] = '123'

basic_auth = BasicAuth(app)

# home/guest page is the default thats loaded
# shows all the articles inside articles.json file
# with an option to go into the admin dashboard
@app.route("/")
def guest_page():
    articles = []
    with open(articles_json, 'r') as f:
        articles = json.load(f)
        f.close()
    return render_template(guest_file, articles = articles)

@app.route("/article/<id>")
def article(id):
    articles = []
    with open(articles_json, 'r') as f:
        articles = json.load(f)

    for article in articles:
        if article['id'] == id:
            return article
        
    return render_template(article_file, one_article = article)

# admin dashboard, log in via username and password
# is used to add, edit, and delete articles
@app.route("/admin")
@basic_auth.required
def admin_page():
    articles = []
    with open(articles_json, 'r') as f:
        articles = json.load(f)
        f.close()
    return render_template(admin_file, articles = articles)

# a page thats accessible from the admin page
# used to add a new article into the articles.json file
@app.route("/admin/new")
def new_article():
    return render_template("admin_things/admin_new.html")

@app.route("/admin/new", methods=["POST"])
def create_new_article():
    title = request.form["title"]
    content = request.form["content"]

    with open(articles_json, 'r') as f:
        articles = json.load(f)

    if articles:
        next_id = max(id["id"] for id in articles) + 1
    else:
        next_id = 1

    article = {
        "id": next_id,
        "title": title,
        "date": str(datetime.datetime.now().strftime("%m-%d-%Y")),
        "content": content
    }

    articles.append(article)

    with open(articles_json, 'w') as f:
        json.dump(articles, f, indent=4)

    return {"message": "Article saved"}


if __name__ == "__main__":
    app.run(debug=True)