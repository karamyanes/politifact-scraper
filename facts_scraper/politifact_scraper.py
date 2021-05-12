import bs4 as bs
import os 
import json
import re

path = "politifact/www.politifact.com/"

# Get the list of all files in directory tree at given path
listOfFiles = list()
for (dirpath, dirnames, filenames) in os.walk(path):
    listOfFiles += [os.path.join(dirpath, file) for file in filenames]


date_mapper = ["January", "February", "March", "April", "May", "June", "July", "August",
              "September", "October", "November", "December"]

def date_format(d):
    dates = []
    first = True
    for i in d.split():
        if first:
            for c, ds in enumerate(date_mapper):
                if ds == i:
                    dates.append(str(c+1)) 
                    break
            first = False
        else:
            dates.append(i.replace(",","").strip())
    return dates[2] + "-" + dates[0] + "-" + dates[1] #YYYY-MM-DD


def parse_politifact(file):
    res = {}

    #The minimum to work
    try:
        soup = bs.BeautifulSoup(file, 'html.parser')
        stat_box = soup.find('section', {"class" : "o-stage"})
        
        claim = stat_box.find('div', {"class" : "m-statement__quote"}).get_text(strip=True).replace("\xa0","").strip()
        article_body = soup.find('article', {"class" : "m-textblock"})
        doc = []
        for p in article_body.findAll('p'):
            doc.append(p.get_text().replace("\xa0","").strip())

        if len(doc) < 1 or len(claim) < 1:
            return None
        doc = ' '.join(doc)
        doc = re.sub(' +', ' ', doc).replace("\n","").replace("\t","") #Remove weird spacing

        res["claim"] = claim
        res["doc"] = doc
        
        label = stat_box.find('div', {"class" : "m-statement__meter"}).find('img', {"class" : "c-image__original"})["alt"]
        res["label"] = label
    except:
        return None

    #author info
    try:
        author_info = soup.find('div', {"class" : "m-author__content"})
        factchecker = author_info.find('a').get_text(strip=True)
        published = author_info.find('span').get_text(strip=True)
        published = date_format(published) #Change date format

        res["factchecker"] = factchecker
        res["published"] = published
    except:

        res["factchecker"] = None
        res["published"] = None

    #Speaker
    try:
        speaker = stat_box.find('a', {"class" : "m-statement__name"}).get_text(strip=True)
        res["speaker"] = speaker
    except:
        res["speaker"] = None

    #Statement info
    try:
        stated_on  = stat_box.find('div', {"class" : "m-statement__desc"}).get_text(strip=True)\
        .split("on")[1].split("in")[0]

        stated_in = stat_box.find('div', {"class" : "m-statement__desc"}).get_text(strip=True)\
        .split("on")[1].split("in")[1].replace(":","").strip()

        res["date_stated"] = date_format(stated_on)
        res["stated_in"] = stated_in
    except:
        res["date_stated"] = None
        res["stated_in"] = None


    #URL
    try:
        url = None
        for tag in soup.find_all("meta"):
            if tag.get("property", None) == "og:url":
                url = tag.get("content", None)
        res["url"] = url
    except:
        res["url"] = None


    #Topics
    try:
        tags = stat_box.find('ul', {"class" : "m-list--horizontal"})
        topics = []
        for tag in tags.findAll('li'):
            topic = tag.find("span").get_text(strip=True)
            topics.append(topic)
        res["topic"] = topics
    except:
        res["topic"] = None


    #Source info
    try:
        source_body = soup.find('article', {"class" : "m-superbox__content"})
        source_res = []
        for p in source_body.findAll("p"):
            source_desc = p.get_text(strip=True)
            source_link = None
            try:
                source_link = p.find("a", href=True)["href"]
                if len(source_link) > 5:
                    source_link = source_link
            except:
                source_link = None

            source_res.append({
                "description": source_desc,
                "link": source_link
            })
        res["sources"] = source_res
    except:
        res["sources"] = None


    #Summary box
    try:
        summary_box = soup.find('div', {"class" : "short-on-time"})
        summary = []
        for p in summary_box.findAll("p"):
            summary.append(p.get_text().strip())

        if len(summary) < 1:
            res["summary"] = None
        else:
            summary = ' '.join(summary)
            summary = re.sub(' +', ' ', summary).replace("\n","").replace("\t","") #Remove weird spacing
            res["summary"] = summary
    except:
        res["summary"] = None

    return res

def create_politifact(files, limit=None):
    scraped_claims = []
    res_df = []
    count = 0
    for file in files:
        if limit:
            if count > limit:
                break
        if count % 2000 == 0:
            print("Done with ", count)
        if file[-5::]=='.html':
            count += 1
            f = open(file, "r", encoding="utf8")
            html = f.read()
            f.close()
            res = parse_politifact(html)
            if res and res["claim"] not in scraped_claims:
                scraped_claims.append(res["claim"])
            else:
                continue
            res_df.append(res)
    return res_df


df = create_politifact(listOfFiles)

with open('politifact.json', 'w+', encoding="utf8") as f:
    json.dump(df, f, indent=4)
