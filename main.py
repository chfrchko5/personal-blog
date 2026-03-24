from flask import Flask, render_template, request
from flask_basicauth import BasicAuth
import json
import datetime
import os

guest_file = "guest.html"
admin_file = "admin.html"
article_file = "article.html"
articles_json = "blog/articles.json"

app = Flask(__name__)

# basic authentication thing to get into admin page
app.config['BASIC_AUTH_USERNAME'] = 'admin'
app.config['BASIC_AUTH_PASSWORD'] = '123'

basic_auth = BasicAuth(app)

# before launching server, create file or pass
try:
    with open(articles_json, 'x') as file:
        file.write("[]")
except FileExistsError:
    print("File already exists. Content not overwritten.")

# home/guest page is the default thats loaded
# shows all the articles inside articles.json file
# with an option to go into the admin dashboard
@app.route("/")
def guest_page():
    articles = []

    if not os.path.exists(articles_json):
        with open(articles_json, 'w') as f:
            json.dump([], f)

    if os.stat(articles_json).st_size == 0:
        with open(articles_json, 'w') as f:
            json.dump([], f)

    with open(articles_json, 'r') as f:
        articles = json.load(f)
        f.close()
    return render_template(guest_file, articles = articles)

# an endpoint with <id> variable that takes the id of the article pressed on the site
# opens up a new page with only that specific article
@app.route("/article/<int:id>")
def article(id):
    articles = []
    with open(articles_json, 'r') as f:
        articles = json.load(f)

    for article in articles:
        if article['id'] == id:
            return render_template(article_file, one_article=article)
        
    return "Article not found", 404

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
@app.route("/admin/new", methods=["GET", "POST"])
def new_article():
    with open(articles_json, 'r') as f:
        articles = json.load(f)

    if request.method == "POST":
        if articles:
            next_id = max(id["id"] for id in articles) + 1
        else:
            next_id = 1

        article = {
            "id": next_id,
            "title": request.form["title"],
            "date": str(datetime.datetime.now().strftime("%m-%d-%Y")),
            "content": request.form["content"]
        }

        articles.append(article)

        with open(articles_json, 'w') as f:
            json.dump(articles, f, indent=4)
        
        return {"message": "Article saved"}

    return render_template("admin_things/admin_new.html")

# takes an id of the article to perform edits on
@app.route("/admin/edit/<int:id>", methods=["GET", "POST"])
def edit_article(id):
    with open(articles_json, 'r') as f:
        articles = json.load(f)

    for article in articles:
        if article['id'] == id:
            if request.method == "POST":
                article['title'] = request.form["new_title"]
                article['content'] = request.form["new_content"]
                article['date_edited'] = datetime.datetime.now().strftime("%m-%d-%Y")

                with open(articles_json, 'w') as f:
                    json.dump(articles, f, indent=4)

                return {"message": "Article edited"}

            return render_template(
                "admin_things/admin_edit.html",
                one_article=article
            )

    return "Article not found", 404

# takes an id of the article deletes it then saves the file
@app.route("/admin/delete/<int:id>", methods=["POST"])
def delete_article(id):
    with open(articles_json, 'r') as f:
        articles = json.load(f)

    new_articles = [d for d in articles if d.get('id') != id]

    with open(articles_json, "w") as f:
        json.dump(new_articles, f, indent=4)
    
    return {"message": "Article deleted"}

if __name__ == "__main__":
    app.run(debug=True)