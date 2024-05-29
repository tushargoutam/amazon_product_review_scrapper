from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import logging
import pymongo
logging.basicConfig(filename="scrapper.log" , level=logging.INFO)

app = Flask(__name__)

@app.route("/", methods = ['GET'])
def homepage():
    return render_template("index.html")

@app.route("/review" , methods = ['POST' , 'GET'])
def index():
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ","")
            amazon_url = "https://www.amazon.in/s?k=" + searchString
            uClient = uReq(amazon_url)
            amazonPage = uClient.read()
            uClient.close()
            amazon_html = bs(amazonPage, "html.parser")
            bigboxes = amazon_html.find_all("div",{"class":"sg-col-20-of-24 s-result-item s-asin sg-col-0-of-12 sg-col-16-of-20 sg-col s-widget-spacing-small sg-col-12-of-16"})
            reviews = []
            filename = searchString + ".csv"
            fw = open(filename, "w")
            headers = "Product, Customer Name, Rating, Heading, Comment \n"
            fw.write(headers)
            for box in bigboxes:
                productLink = "https://www.amazon.in" + box.a['href']
                prodRes = requests.get(productLink)
                prodRes.encoding='utf-8'
                prod_html = bs(prodRes.text, "html.parser")
                commentboxes = prod_html.find_all('div',{"class":"a-section review aok-relative"})
                for commentbox in commentboxes:
                    try:
                        #name.encode(encoding='utf-8')
                        name = commentbox.find('span',{"class":"a-profile-name"}).text

                    except:
                        logging.info("name")

                    try:
                        #rating.encode(encoding='utf-8')
                        rating = commentbox.find('i',{'class':'a-icon a-icon-star a-star-5 review-rating'}).text


                    except:
                        rating = 'No Rating'
                        logging.info("rating")

                    try:
                        #commentHead.encode(encoding='utf-8')
                        commentHead = commentbox.find('a',{'class':"a-size-base a-link-normal review-title a-color-base review-title-content a-text-bold"}).find('span',{'class':''}).text

                    except:
                        commentHead = 'No Comment Heading'
                        logging.info(commentHead)
                    try:
                        #custComment.encode(encoding='utf-8')
                        custComment = commentbox.find('div',{"class":"a-expander-content reviewText review-text-content a-expander-partial-collapse-content"}).span.text 
                    except Exception as e:
                        logging.info(e)

                    mydict = {"Product": searchString, "Name": name, "Rating": rating, "CommentHead": commentHead,
                            "Comment": custComment}
                    reviews.append(mydict)
            try:
                pymongo_client = pymongo.MongoClient("mongodb+srv://pwskills:pwskills@cluster0.sgaahcs.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
                db = pymongo_client['scrap_data']
                rev_data = db['review_scrap_data']
                rev_data.insert_many(reviews)
            except:
                logging.info("Can't Save")

            logging.info("log my final result {}".format(reviews))
            return render_template('result.html', reviews=reviews[0:(len(reviews)-1)])
        except Exception as e:
            logging.info(e)
            return 'something is wrong'
    # return render_template('results.html')

    else:
        return render_template('index.html')


if __name__=="__main__":
    app.run(host="0.0.0.0")