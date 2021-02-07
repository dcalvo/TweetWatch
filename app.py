import os
import requests
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
analyzer = SentimentIntensityAnalyzer()

from models import Result


@app.route('/', methods=['GET', 'POST'])
def index():
    errors = []
    results = []
    if request.method == "POST":
        # get url that the user has entered
        try:
            url = request.form['url']
            score = analyzer.polarity_scores(url)
            #r = requests.get(url)
            #print(r.text)
        except:
            errors.append(
                "Unable to get URL. Please make sure it's valid and try again."
            )
        if score:
            results.append((url, score))
            try:
                result = Result(
                    tweet=url,
                    sentiment=score
                )
                db.session.add(result)
                db.session.commit()
            except:
                errors.append("Unable to add item to database.")
    return render_template('index.html', errors=errors, results=results)



if __name__ == '__main__':
    app.run()