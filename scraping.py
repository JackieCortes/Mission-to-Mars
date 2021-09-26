# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
import datetime as dt
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

def scrape_all():
# Set up Splinter
    # Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)
    
    news_title, news_paragraph = mars_news(browser)
    
    # Run all scraping functions and store results in a dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now()
    }

    # Stop webdriver and return data
    browser.quit()
    return data
    

def mars_news(browser):
    #Scrape Mars News

    # Visit the mars nasa news site
    #url = 'https://redplanetscience.com'
    url = 'https://data-class-mars.s3.amazonaws.com/Mars/index.html'
    browser.visit(url)
    # Optional delay for loading the page & we're searching for elements 
    #with a specific combination of tag (div) and attribute (list_text)
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')
    
    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')

        #slide_elem.find('div', class_='content_title')

        # Use the parent element to find the first `a` tag and save it as `news_title`
        news_title = slide_elem.find('div', class_='content_title').get_text()
        #news_title

        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()
        #news_p
    except AttributeError:
        return None, None
    
    return news_title, news_p


# ### Featured Images
def featured_image(browser):
    # Visit URL where the images are
    #url = 'https://spaceimages-mars.com'
    url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        # Find the relative image url, img tag is nested within this HTML 
        #.get('src') pulls the link to the image.
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')
        #"img_url_rel" is going to give you a partial link
    except AttributeError:
        return None

    # Use the base URL to create an absolute URL
    #img_url = f'https://spaceimages-mars.com/{img_url_rel}'
    img_url = f'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/{img_url_rel}'
    
    return img_url

#To scrape a complete table instead of each row
def mars_facts():
    # Add try/except for error handling
    try:
    
        #Creation of new DataFrame from the HTML table. 
        #The Pandas function read_html()searches for and returns a list of tables
        # (HTML). By index of 0, Pandas pulls the 1st table it encounters, 
        #or the 1st item in the list. Then, it turns the table into a DataFrame.
        #df = pd.read_html('https://galaxyfacts-mars.com')[0]
        df = pd.read_html('https://data-class-mars-facts.s3.amazonaws.com/Mars_Facts/index.html')[0]
    except BaseException:
        return None
    
    #we assign columns to the new DataFrame for additional clarity.
    df.columns=['Description', 'Mars', 'Earth']
    #By using the .set_index()we're turning the Description column into df's index
    #inplace=True means the updated index remains in place.
    #without having to reassign the DataFrame to a new variable.
    df.set_index('Description', inplace=True)
    #df

    #convert our DataFrame back into HTML, easily with Pandas
    #return df.to_html()
    return df.to_html(classes="table table-striped")

#browser.quit()
if __name__ == "__main__":

    # If running as script, print scraped data
    print(scrape_all())
