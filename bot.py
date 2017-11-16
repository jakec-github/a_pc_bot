import bs4 as bs
import urllib.request
from time import strftime
import praw
import config

def newyorker():
    try:
        today = strftime("%A, %B %d")
        page = urllib.request.urlopen("http://newyorker.com/cartoons").read()
        soup = bs.BeautifulSoup(page, "lxml")
        link = soup.find("a", itemprop="image url").get("href")

        return {
            "link" : link,
            "source" : "The New Yorker",
            "origin" : "USA",
            "testing" : False
        }
    except Exception as e:

        return {
            "issue" : "New Yorker Exception: " + str(e)
        }

def independent():
    try:
        page = urllib.request.urlopen("http://independent.co.uk/").read()
        soup = bs.BeautifulSoup(page, "lxml")
        all_titles = soup.find_all("h2", class_="gallery-title")
        print ("All titles: " + str(all_titles))
        for n in range(0,len(all_titles)):
            if all_titles[n].text == "Daily cartoon":
                title = all_titles[n]
                break
        siblings = []

        for sibling in title.next_siblings:
            siblings.append(sibling)

        link = siblings[1].ul.li["data-original"]

        return {
            "link" : link,
            "source" : "The Independent",
            "origin" : "UK",
            "testing" : False
        }
    except Exception as e:

        return {
            "issue" : "Independent Exception: " + str(e)
        }

def guardian():
    try:
        page = urllib.request.urlopen("https://www.theguardian.com/uk/commentisfree").read()
        soup = bs.BeautifulSoup(page, "lxml")
        span = soup.find("span", text="cartoons")
        elements = []

        for element in span.next_elements:
            elements.append(element)

        div = elements[5]
        link = div.find("a", class_="fc-item__link").get("href")
        link = link + "#img-1"

        return {
            "link" : link,
            "source" : "The Guardian",
            "origin" : "UK",
            "testing" : False
        }
    except Exception as e:

        return {
            "issue" : "Guardian Exception: " + str(e)
        }

#USA Today cartoons are cut off versions. May have to find an alternative link
def usatoday():
    try:
        page = urllib.request.urlopen("https://www.usatoday.com/opinion/cartoons").read()
        soup = bs.BeautifulSoup(page, "lxml")
        cartoon_slider = "https://www.usatoday.com" + soup.find("a", class_="load-story").get("href")
        page = urllib.request.urlopen(cartoon_slider).read()
        soup = bs.BeautifulSoup(page, "lxml")
        link = soup.find("img", class_="gallery-photo").get("src")

        #this is also triggered if the link is the same because there is no new comic. duh!
        link_end = link.split("USATODAY/USATODAY")[1]
        for n in range(0, len(posted)):
            if link_end in posted[n]:
                return {
                    "issue" : "USA Today: Link altered. Cartoon unchanged"
                }


        return {
            "link" : link,
            "source" : "USA Today",
            "origin" : "USA",
            "testing" : False
        }
    except Exception as e:

        return {
            "issue" : "USA Today Exception: " + str(e)
        }

def get_saved_data():
    with open("posted.txt", "r") as f:
        posted = f.read()
        posted = posted.split("\n")
    return posted

def bot_login():
    r = praw.Reddit(username = config.username,
                password = config.password,
                client_id = config.client_id,
                client_secret = config.client_secret,
                user_agent = "Political Cartoon Bot v0.1")
    return r

def run_bot(r):

    for n in range(0, len(sources)):
        source = sources[n]
        if "link" in source.keys():
            title = source["source"] + " | " + strftime("%A, %B %d") + " | " + source["origin"]
            if source["link"] not in posted:
                if source["testing"] == False:
                    r.subreddit("politicalcartoons").submit(title, url=source["link"])
                    with open("posted.txt", "a") as f:
                        f.write(source["link"] + "\n")
                    print (title)
                else:
                    r.subreddit("test").submit(title, url=source["link"])
                    with open("posted.txt", "a") as f:
                        f.write(source["link"] + "\n")
                    print ("TESTING: " + title)
            else:
                print (source["source"] + " already posted")
        else:
            print (source["issue"])
            with open("error_log.txt", "a") as f:
                f.write(strftime("%c") + source["issue"] + "\n")

    with open("log.txt", "a") as f:
        f.write("Program run at: " + strftime("%c") + "\n")

r = bot_login()

posted = get_saved_data()
sources = [newyorker(), independent(), guardian(), usatoday()]

run_bot(r)
