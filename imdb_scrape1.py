import requests
import io
import csv
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from multiprocessing import Pool
import time
from selenium.webdriver.chrome.options import Options
import zipfile
from functools import partial

PATH="C:\Program Files (x86)\chromedriver.exe"

    #JUST RETURNS THE SOUPIFIED CONTENT OF THAT URL BY USING LXML PARSER
def GET_SOUP(my_url):
    url = my_url
    response = requests.get(url)
    html = response.content
    soup = BeautifulSoup(html, features='lxml')
    return soup

    #SCRAPE THE CONTENT OF THAT URL BY REPEATEDLY FINDING THE LOAD MORE BUTTON
def scrapeData(url):
        listOfComments=[]

        driver_options = Options()
        driver_options.add_argument("--no-sandbox")
        driver_options.add_argument("--start-maximized")
        # driver_options.add_extension('proxy_auth_plugin.zip')

        driver = webdriver.Chrome(PATH, options=driver_options)


        driver.get(url)

        count = 0
        while True:
            try:
                loadMoreButton = driver.find_element_by_id("load-more-trigger")
                time.sleep(0.1)
                loadMoreButton.click()
                count = 0
                time.sleep(0.1)
            except Exception as e:
                count += 1
                if count == 20:
                    break

        soup_3=BeautifulSoup(driver.page_source, features="lxml")

        for item in soup_3.findAll('div', attrs={'class': 'review-container'}):
            try:
                headComment = item.find('div', attrs={'class': 'lister-item-content'}).find('a').text.replace('\n', '')
            except Exception as e:
                headComment = ""

            try:
                mainComment = item.find('div', attrs={'class': 'text show-more__control'}).text.replace('\n', '')
            except Exception as e:
                mainComment = ""

            try:
                commentRating = item.find('span', attrs={'class': 'rating-other-user-rating'}).find('span').text
            except Exception as e:
                commentRating = ""

            listOfComments.append([headComment, mainComment, commentRating])

        driver.quit()
        return [url, listOfComments]

    #GET THE FINAL URL USED FOR SCRAPING THE DATA FROM THE MAIN PAGE BY GETTING INTO EACH MOVIE
    #THERE ARE SUCH HUNDRED MAIN PAGES CONTAINING HUNDRED MOVIES EACH
def getURLs(url):
        soup=GET_SOUP(url)
        table = soup.find('div', attrs={'class': 'lister-list'})

        listofMovieUrls=[]
        for row in table.findAll('div', attrs={'class': 'lister-item mode-detail'}):
            startTime = time.time()
            print("Work under progress! Please do not interfere with the system")

            try:
                rating = row.find('span', attrs={'class': 'ipl-rating-star__rating'}).text.replace('\n', '')
            except Exception as e:
                rating = ""

            try:
                title = row.find('h3', attrs={'class': 'lister-item-header'}).find('a').text.replace('\n', '')
            except Exception as e:
                title = ""

            try:
                url_2="https://www.imdb.com"+row.find('h3', attrs={'class': 'lister-item-header'}).find('a').get("href")
            except Exception as e:
                continue

            soup_2=GET_SOUP(url_2)

            try:
                url_3="https://www.imdb.com" + soup_2.find('div', attrs={'class': 'user-comments'}).findAll('a')[4].get("href")
            except Exception as e:
                continue

            listofMovieUrls.append({url_3: (title, rating)})
            driver_options = Options()
            driver_options.add_argument("--start-maximized")
            # driver_options.add_extension('proxy_auth_plugin.zip')

        print("page completed")
        return listofMovieUrls
if __name__ == '__main__':
    

    # manifest_json = """
    # {
    #     "version": "1.0.0",
    #     "manifest_version": 2,
    #     "name": "Chrome Proxy",
    #     "permissions": [
    #         "proxy",
    #         "tabs",
    #         "unlimitedStorage",
    #         "storage",
    #         "<all_urls>",
    #         "webRequest",
    #         "webRequestBlocking"
    #     ],
    #     "background": {
    #         "scripts": ["background.js"]
    #     },
    #     "minimum_chrome_version":"22.0.0"
    # }
    # """

    # background_js = """
    # var config = {
    #         mode: "fixed_servers",
    #         rules: {
    #           singleProxy: {
    #             scheme: "http",
    #             host: "202.141.80.24",
    #             port: parseInt(3128)
    #           },
    #           bypassList: ["foobar.com"]
    #         }
    #       };

    # chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

    # function callbackFn(details) {
    #     return {
    #         authCredentials: {
    #             username: "gulat170123030",
    #             password: "FTS6C3kq"
    #         }
    #     };
    # }

    # chrome.webRequest.onAuthRequired.addListener(
    #             callbackFn,
    #             {urls: ["<all_urls>"]},
    #             ['blocking']
    # );
    # """


    


    # pluginfile = 'proxy_auth_plugin.zip'

    # with zipfile.ZipFile(pluginfile, 'w') as zp:
    #     zp.writestr("manifest.json", manifest_json)
    #     zp.writestr("background.js", background_js)

    mainUrl = "https://www.imdb.com/list/ls057823854/"
    url = "https://www.imdb.com/list/ls057823854/?sort=list_order,asc&st_dt=&mode=detail&page="

    FinalList=[]
    listOfUrls=[]
    listOfUrls.append(mainUrl)

    numPages = 1
    # GETTING THOSE HUNDRED MAIN PAGES
    for i in range(1, numPages):
    	listOfUrls.append(url+str(i))

    numCores = 4

    parProcess = Pool(numCores)
    result = parProcess.map(getURLs, listOfUrls)    # List of list of dicionaries
    # LIST OF LIST OF DICTIONARY WHERE [DICTIONARY CONTAINS (FINAL URL --> MOVIE NAME & RATING OF THE MOVIE ITSELF)], [ONE LIST IS THOSE 100 MOVIE ON A SINGLE PAGE]
    #[OUTER LIST IS BASICALLY FOR THOSE 100 MAIN PAGES]
    FinalList=[]
    finalDict = {}
    num = 0
    for i in result:
        for j in i:
            for k in j:
                finalDict[k] = j[k]
                FinalList.append(k)

    print(FinalList)
    print(len(FinalList))
    parProcesses = [Pool(numCores), Pool(numCores), Pool(numCores), Pool(numCores)]
    # numMovies = 4
    numMovies = len(FinalList)
    for i in range(0, 4):
        # parProcess2 = Pool(numCores)
        result2 = parProcesses[i].map(scrapeData, FinalList[(numMovies*i)//4:(numMovies*(i+1))//4])
        # movie = [url, listOfComments]
        for movie in result2:
            movieName = finalDict[movie[0]][0]
            movieRating = finalDict[movie[0]][1]
            # print(movieName)
            print("C:\\Users\\Ritwik\\Documents\\Scraping\\"+movieName.replace(' ', '_').replace('"', '_').replace('/', '_')+"_"+str(movieRating)+".tsv")
            with io.open("C:\\Users\\Ritwik\\Documents\\Scraping\\"+movieName.replace(' ', '_').replace('"', '_').replace('/', '_')+"_"+str(movieRating)+".tsv", "w", encoding="utf-8") as outfile:
            # outfile = open("C:/data/"+movieName.replace(' ', '_').replace('"', '_').replace('/', '_')+"_"+str(movieRating)+".tsv", "w")
                writer = csv.writer(outfile, delimiter='\t', lineterminator='\n')
                writer.writerow(['Comment Head','Comment Body', 'Comment Rating'])
                writer.writerows(movie[1])