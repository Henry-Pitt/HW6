from flask import Flask, jsonify, request
from newsapi import NewsApiClient
import json

#key control
newsapi = NewsApiClient(api_key='cada455bce2244539fc16cd419f815f3')

#page control

# EB looks for an 'application' callable by default.
application = Flask(__name__)

@application.route('/')
def homepage():
    return application.send_static_file('home.html')

@application.route('/mycss.css')
def styleFile():
    return application.send_static_file('mycss.css')

@application.route('/myjs.js')
def jsFile():
    return application.send_static_file('myjs.js')

@application.route('/wordcloud')
def getwordCloud():
    news = newsapi.get_top_headlines(page_size = 100 ,language='en')
    words = {}

    for article in news['articles']:
        title = article['title']
        #print(title)
        for word in title.split():
            word = word.split(':')[0]
            word = word.lower()
            if word in words:
                words[word] +=1
            else:
                words[word] =1
    
    try:
        stopwords = open('stopwords_en.txt','r').read().splitlines()
    except:
        application.logger.info('can not find \'stopwords_en.txt\'! ')
    somesigne = {"-","|"} #extra word

    for key in stopwords:
        if key in words.keys():
            words.pop(key)
    for key in somesigne:
        if key in words.keys():
            words.pop(key)

    sorted_x = sorted(words.items(), key=lambda kv: kv[1],reverse=True)
    guiyi = sorted_x[0][1]-sorted_x[29][1]
    # (min - max) => (10-40)


    words = []
    for iteam in sorted_x[:30]:
        words.append({"word" : iteam[0],"times":iteam[1],"Nor":int(10+(iteam[1]-sorted_x[29][1])/guiyi * 20)})
        
    ans={}
    ans["words"] = words
    return jsonify(ans)


   

@application.route('/headline')
def getHeading():
    headline = newsapi.get_top_headlines(language='en')
    #get the top 5 news that include image, title and description
    cnt = 0
    ans = []
    for article in headline['articles']:
        if 'title' not in article.keys() or 'description' not in article.keys() or 'urlToImage' not in article.keys():
            continue
        if article['title'] =='' or article['description'] =='' or article['urlToImage'] =='':
            continue 
        tmp={"title":article['title'],"description":article['description'],"imageurl":article['urlToImage'],"url":article['url']}
        ans.append(tmp)
        cnt +=1
        if cnt == 5:
            break
    # tmp = {}
    # tmp["articles"]=ans

    return jsonify({'articles': ans})

@application.route('/sourcenews')
def getsourcenews():
    news = newsapi.get_top_headlines(language='en',sources='cnn,fox-news')
    cnn=[]
    fox=[]
    ans={}
    cnn_count = 0
    fox_count = 0
    for article in news['articles']:
        if 'title' not in article.keys() or 'description' not in article.keys() or 'urlToImage' not in article.keys():
            continue
        if article['title'] =='' or article['description'] =='' or article['urlToImage'] =='':
            continue 
        #fetch cnn
        if article["source"]['id'] == "cnn" and cnn_count<4:
            tmp={"title":article['title'],"description":article['description'],"imageurl":article['urlToImage'],"url":article['url']}
            cnn.append(tmp)
            cnn_count +=1
        #fetch fox
        if article["source"]['id'] == "fox-news" and fox_count<4:
            tmp={"title":article['title'],"description":article['description'],"imageurl":article['urlToImage'],"url":article['url']}
            fox.append(tmp)
            fox_count +=1
    ans["CNN"]=cnn
    ans["FOX"]=fox

    return jsonify(ans)

@application.route('/getsource')
def getsource():
    cate = request.args.get("cat",None)
    if( not cate or cate =='all'):
        allsource = newsapi.get_sources(language ='en',
                                    country = 'us'
        )
    else:
        allsource = newsapi.get_sources(language ='en',
                                    country = 'us',
                                    category = cate
    )
    ans = {}
    tmp={}
    atmp = []
    for each in allsource['sources']:
        tmp={"name":each['name'],"id":each['id'] }
        atmp.append(tmp)
    ans["sources"] = atmp;
    return jsonify(ans)

@application.route('/search')
def getquery():
    keyword = request.args.get("keyword",None)
    from1 = request.args.get("from",None)
    to1 = request.args.get("to",None)
    sour = request.args.get("sour",None)
    try:
        if(sour == 'all' or sour == None):
            news = newsapi.get_everything( q = keyword,
                                from_param = from1,
                                to = to1,
                                language = 'en',
                                sort_by = 'publishedAt',
                                page_size = 30
        )
        else:
            news = newsapi.get_everything( q = keyword,
                                    sources = sour,
                                    from_param = from1,
                                    to = to1,
                                    language = 'en',
                                    sort_by = 'publishedAt',
                                    page_size = 30
            )
        #filter 
        tmp1=[]
        for each in news['articles']:
            if each['author'] =='' or each['description'] =='' or each['publishedAt'] ==''or each['source']['name'] ==''or each['title'] ==''or each['url'] ==''or each['urlToImage'] =='':
                continue 
            if not each['author']  or not each['description']  or not each['publishedAt'] or not each['source']['name'] or not each['title'] or not each['url'] or not each['urlToImage'] :
                continue
            if each['author'] =='null' or each['description'] =='null' or each['publishedAt'] =='null'or each['source']['name'] =='null'or each['title'] =='null'or each['url'] =='null'or each['urlToImage'] =='null':
                continue 
            tmp={"author":each['author']}
            tmp['description']=each['description']
            text = each['description'].split(' ')
            # hanle extend words
            newtext = ""
            tcnt=0
            spacelimit = 100
            while len(newtext) <spacelimit:
                newtext = newtext + text[tcnt] +" "
                tcnt = tcnt +1
                if tcnt >= len(text):
                    break
            if newtext[-2] ==',' or newtext[-2] =='-' or newtext[-2] =='.' or newtext[-2] =='!':
                newtext=newtext[:-2] +" "
            
            newtext = newtext[:-1]  + "..."
            if len(each['description']) < spacelimit:
                tmp['description2'] = each['description']
            else:
                tmp['description2'] = newtext
            date = each['publishedAt'].split('-')
            newdate = date[1][:2]+ '/' + date[2][:2] +'/'+date[0][:4]
            tmp['publishedAt'] = newdate
            
            tmp['source']=each['source']['name']
            tmp['title']=each['title']
            tmp['url']=each['url']
            tmp['urlToImage']=each['urlToImage']
            tmp1.append(tmp)
    except Exception as e:
        return jsonify({"error":e.get_message()})

    return jsonify({'news': tmp1})


# run the application.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run()

