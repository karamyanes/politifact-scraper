import bs4 as bs
import os 
import pandas as pd
import json
import re



path = "/data/crawled_data/fakenews-data-fresh-crawl/snopes"
listOfFiles = list()
for (dirpath, dirnames, filenames) in os.walk(path):
    listOfFiles += [os.path.join(dirpath, file) for file in filenames]

date_mapper = ["January", "February", "March", "April", "May", "June", "July", "August",
              "September", "October", "November", "December"]

def date_format(d):
    dates = d.split()
    for c, ds in enumerate(date_mapper):
        if ds == dates[1]:
            dates[1] = str(c+1)
            break

    return dates[2] + "-" + dates[1] + "-" + dates[0] #YYYY-MM-DD


def parse_snopes(file):
    res = {}

    #The minimum to work
    try:
        soup = bs.BeautifulSoup(file, 'html.parser')

        claim = soup.find('div', {"class" : "claim"})
        claim = claim.find("p").get_text(strip=True).replace("\xa0","").strip()
        article_body = soup.find('div', {"class" : "content"})
        doc = []
        for p in article_body.findAll('p'):
            doc.append(p.get_text().replace("\xa0","").strip())

        if len(doc) < 1 or len(claim) < 1:
            return None
        
        doc = ' '.join(doc)
        doc = re.sub(' +', ' ', doc).replace("\n","").replace("\t","") #Remove weird spacing
        label = soup.find('div', {"class" : "rating"}).find("h5").get_text(strip=True)
        res["label"] = label
        res["claim"] = claim
        res["doc"] = doc
    except:
        return None

    #author info
    try:
        factchecker = soup.find('a', {"class" : "author"}).get_text(strip=True)
        published = soup.find('li', {"class" : "date-published"}).findAll("span")[-1].get_text(strip=True)
        published = date_format(published) #YYYY-MM-DD
        res["factchecker"] = factchecker
        res["published"] = published
    except:

        res["factchecker"] = None
        res["published"] = None

        
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
        topics = [soup.find('ol', {"class" : "breadcrumb"}).findAll('li')[-2].get_text(strip=True)]
        #Add additional topics if available
        try:
            tags = soup.find('ul', {"class" : "tags"})
            for tag in tags.findAll('li'):
                topic = tag.get_text(strip=True)
                topics.append(topic)
        except:
            pass
        res["topic"] = topics
    except:
        res["topic"] = None
        
    
    #Source info
    try:
        source_body = soup.find('div', {"class" : "citations"})
        source_res = []
        for p in source_body.findAll("li"):
            info = p.find("p").get_text(strip=True).replace("\xa0","")
            info =  re.sub(' +', ' ', info).replace("\n","").replace("\t","") #Remove weird spacing
            source_res.append({
                "description": info
            })
        res["sources"] = source_res
    except:
        res["sources"] = None
        
    #Split decisions
    extra_description = None
    if res["label"] == 'Mostly True' or res["label"] == 'Mostly False' or res["label"] == 'Mixture':
        try:
            whats_true = soup.find('div', {"class" : "whats-true"}).find('p').get_text().strip()
            whats_false = soup.find('div', {"class" : "whats-false"}).find('p').get_text().strip()
            extra_description = {
                "whats_true": whats_true,
                "whats_false": whats_false
            }
        except:
            pass
    res["extra_description"] = extra_description
    return res


def create_snopes(files, limit=None):
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
            f = open(file, "r")
            html = f.read()
            f.close()
            res = parse_snopes(html)
            if res and res["claim"] not in scraped_claims:
                scraped_claims.append(res["claim"])
            else:
                continue
            res_df.append(res)
    return res_df


df = create_snopes(listOfFiles)

with open('snopes.json', 'w+') as f:
    json.dump(df, f, indent=4)
