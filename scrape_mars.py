def scrape():
    # import dependencies
    from bs4 import BeautifulSoup
    from splinter import Browser
    from splinter.exceptions import ElementDoesNotExist
    import requests
    import pymongo
    import pandas as pd

    # setup mongo connection
    conn = "mongodb://localhost:27017"
    client = pymongo.MongoClient(conn)
    
    # establish database
    db = client.mission_to_mars
    
    # set up splinter
    executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
    browser = Browser('chrome', **executable_path, headless = False)

    # URL of page to be scraped
    url = 'https://mars.nasa.gov/news/'

    # retrieve page with the requests module
    response = requests.get(url)

    # create bs object; parse with html
    soup = BeautifulSoup(response.text, 'html.parser')

    # find all div with class slide, store them in result set
    results = soup.find_all('div', class_ = 'slide')

    # create empty list to store dictionaries
    mars_news = []

    # loop through all slides, store relevant content
    for result in results:

        # create empty dict to store article data
        article_data = {}

        # scrape article title
        title = result.find('div', class_='content_title').text
        # remove leading/trailing spaces
        title = title.strip()

        # scrape article description
        desc = result.find('div', class_='rollover_description_inner').text
        # remove leading/trailing spaces
        desc = desc.strip()

        # print article data
        print('-----------------')
        print(title)
        print(desc)

        # store data in dictionary to be appended to list
        article_data = {
            'news_title': title,
            'news_p': desc
        }

        mars_news.append(article_data)
        
    # drop existing collection
    db.news.drop()

    # insert data
    db.news.insert_many(mars_news)

    
    
    # set url to scrape image
    base_url = 'https://www.jpl.nasa.gov'
    img_search_url = f'{base_url}/spaceimages/?search=&category=Mars'

    # use splinter to visit url
    browser.visit(img_search_url)

    # set html from browser
    html = browser.html

    # create soup object, parse with html
    soup = BeautifulSoup(html, 'html.parser')

    # find anchor with image link
    results = soup.find_all('a', class_='button fancybox')

    # find href from result
    img_href = results[0]['data-fancybox-href']

    # build url from href and base url
    featured_img_url = f'{base_url}{img_href}'
    
    # drop existing collection
    db.featured.drop()

    # insert data
    db.featured.insert_one({"featured_img_url": featured_img_url})

    
    
    # url of twitter page to scrape
    twitter = 'https://twitter.com/marswxreport?lang=en'

    # retrieve page with the requests module
    response = requests.get(twitter)

    # create bs object; parse with html
    soup = BeautifulSoup(response.text, 'html.parser')

    # find all div with class js-tweet-text-container, store them in result set
    results = soup.find_all('div', class_ = 'js-tweet-text-container')

    # get the top result (most recent tweet), and pull the text inside the paragraph element
    mars_weather = results[0].find('p').text
    
    # drop existing collection
    db.weather.drop()

    # insert data
    db.weather.insert_one({'weather': mars_weather})

    
    
    # url of facts page to scrape
    space_facts = 'https://space-facts.com/mars/'

    # retrieve page with the requests module
    response = requests.get(space_facts)

    # create bs object; parse with html
    soup = BeautifulSoup(response.text, 'html.parser')

    # find all tables, store them in result set
    results = soup.find_all('table')

    # get the top result, and read the data into a pandas table
    table = results[0]

    table = pd.read_html(str(table))

    # read_html returns a list, use index to store the table as a df
    mars_facts = table[0]

    # print out html code for table
    print(mars_facts.to_html(header = False))

    
    
    # create list of hemisphere names
    hemispheres = ['Cerberus',
                  'Schiaparelli',
                  'Syrtis Major',
                  'Valles Marineris']

    # initialize list to store all hemisphere data
    hemisphere_data = []

    for hemisphere in hemispheres:

        # intialize dictionary to store individual hemisphere data
        current_hemisphere = {}

        # set starting point
        hemisphere_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'

        # use splinter to visit url
        browser.visit(hemisphere_url)

        # navigate to hemisphere page
        browser.click_link_by_partial_text(hemisphere)

        # set html from browser
        html = browser.html

        # create soup object, parse with html
        soup = BeautifulSoup(html, 'html.parser')

        # find div that contains image link, remove it from list
        results = soup.find('div', class_ = 'wide-image-wrapper')

        # pull the href from the first anchor inside the div to get image link
        img_url = results.find('a')['href']

        # find div that contains page title
        results = soup.find('div', class_ = 'content')

        # pull the text from the header
        long_title = results.find('h2').text

        # remove 'Enhanced' or 'Unenhanced' from the text
        title = long_title.replace(' Enhanced', '')

        # add data to dictionary
        current_hemisphere['title'] = title
        current_hemisphere['img_url'] = img_url

        hemisphere_data.append(current_hemisphere)
        
    # drop existing collection
    db.hemispheres.drop()

    # insert data
    db.hemispheres.insert_many(hemisphere_data)
    
    # quit browser
    browser.quit()