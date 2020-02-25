# import necessary libraries
from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
import scrape_mars

# Create an instance of Flask
app = Flask(__name__)

# setup mongo connection
mongo = PyMongo(app, uri="mongodb://localhost:27017/mission_to_mars")

# create home route
@app.route("/")
def index():
    
    # query relevant data from mongodb
    latest_news = mongo.db.news.find_one()
    featured_img = mongo.db.featured.find_one()
    mars_weather = mongo.db.weather.find_one()
    hemispheres = list(mongo.db.hemispheres.find())
    
    return render_template("index.html", 
        latest_news = latest_news,
        featured_img = featured_img, 
        mars_weather = mars_weather, 
        hemispheres = hemispheres)

# create route that runs scrape function
@app.route("/scrape")
def scrape_route():
    
    scrape_mars.scrape()
    
    # Redirect back to home page
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)