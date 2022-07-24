#!python3

# pip3  install selenium 
# install driver for chromium from https://selenium-python.readthedocs.io/installation.html#drivers
# https://chromedriver.storage.googleapis.com/index.html?path=97.0.4692.71/

# featrues: 
# - get: ordered products, price, orderdate
# - page down counter lazy loading
# - export to csv
# TODO:
# - product url

filename = "amazon.csv"
#https://www.amazon.de/gp/your-account/order-history/ref=ppx_yo_dt_b_pagination_4_5?ie=UTF8&orderFilter=year-2022&search=&startIndex=40
# https://www.amazon.de/gp/your-account/order-history/ref=ppx_yo_dt_b_pagination_3_4?ie=UTF8&orderFilter=year-2022&search=&startIndex=30
#orderurl = "https://www.amazon.de/gp/your-account/order-history?orderFilter=year-2022&ref_=ppx_yo2ov_dt_b_filter_all_y2022"
#orderurl = "https://www.amazon.de/gp/your-account/order-history/ref=ppx_yo_dt_b_pagination_4_5?ie=UTF8&orderFilter=year-2022&search=&startIndex=40"
orderurl = "https://www.amazon.de/gp/your-account/order-history?orderFilter=year-2021"
printurl = "https://www.amazon.de/gp/css/summary/print.html/ref=oh_aui_ajax_invoice?ie=UTF8&orderID="
# https://www.amazon.de/gp/css/summary/print.html/ref=oh_aui_ajax_invoice?ie=UTF8&orderID=302-6899278-5865937
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time 

# cookies on overview page
oc = ordercookie = "BESTELLUNG AUFGEGEBEN"
pc = pricecookie = "SUMME"
onc = ordernrcookie = "BESTELLNR"
dc = deliveredcookie = "Zugestellt"
bc = buyagaincookie = "Nochmals kaufen"

# cookies in order
odc = orderdatecookie = "Bestellung aufgegeben am"
articlc = "Bestellte Artikel"
curencyc = "EUR" 
nrc = "Exemplar(e) von: "

def getOrderNr(content):
    i = content.find(onc)
    onstr = content[i:i+40].split('\n')[0]  # cut off a bit
    nstr = onstr.split(' ')[1]
    return nstr , i+40             # remove currency

def isDelivered(content):
    # is delivered if this order cookie is folloed by a delivered cookie before the next order cookie
    dc1 = -1
    oc1 = content[:30].find(oc)
    if oc1 == 0:
        dc1 = content[:400].find(dc)
    return dc != -1

def getprice(content):
    pi = content.find(pc)
    cpstr = content[pi:pi+30].split('\n')[1]  # cut off a bit
    pstr = cpstr.split(' ')[1]                # remove currency

    # replace german decimalcomma
    pstr = pstr.replace(',','.')

    price = float(pstr)
    return price

def getDesc(content):
    dc1 = -1
    oc0 = content[:30].find(oc)
    if oc0 != 0:
        return None # not aligned; maybe even exception 
    oc1 = content[1:].find(oc) # this should match only for the next order if there is one -1 or >>0
    
def getNrPriceArticle(invoicetext,url,onr, f=None):
    res = []

    # search for orders in Text
    offset = 0
    content = invoicetext

    odi = invoicetext.find(odc)
    orderdate = invoicetext[odi+len(odc)+2:].split("\n")[0]

    idx = content.find(articlc)
    
    while idx != -1: 
        # we have an order
        offset += idx
        content = content[idx:] # shift buffer so it starts 

        #onr = getOrderNr(content)

        nri = content.find(nrc)

        nr =  int(content[nri-min(5,nri):nri].split('\n')[1])
        
        article = content[nri+len(nrc):].split('\n')[0]
        article.strip(';')

        ci = content.find(curencyc)
        cil = content[ci:].find('\n')
        
        pstr = content[ci:ci+cil].split(' ')[1]
        pstr = pstr.replace(',','.')
        price = float(pstr)

        logline = f"{orderdate};\t {onr};\t {nr};\t {price};\t {article};\t {url}; \n"
        print(logline[:-1]) # print to screen
        if f: 
            f.write(logline)
        res.append((nr,price,article))
       
        # prepare next loop
        ismore =  content[ci+cil:].find(nrc) 

        if ismore > -1:
            idx = ci+cil
        else: 
            idx = -1
    return res


def findOrder(maxorders=1000000):

    driver = webdriver.Chrome("./chromedriver")


    driver.get(orderurl)
    input("Login in chrome and press enter here to continue ...")

    f = open(filename,'w')

    time.sleep(1)

    body = driver.find_element_by_tag_name("body") # TODO: resolve deprecation
 
    #    time.sleep(0.5)

    text = body.text

    # search for orders in Text
    offset = 0
    content = text

    invoiceurls = []
    allpages = False

    idx = content.find(ordercookie)
    
    while maxorders > 0: 
        while idx != -1: 
            # we have an order
            offset += idx
            content = content[idx:] # shift buffer so it starts with the order

            onr, idx = getOrderNr(content)

            # now get invoice 
            url = printurl+onr
            print(url)
            if url not in invoiceurls: 
                invoiceurls.append((url,onr))
                allpages = False
                maxorders-=1
                if maxorders <= 0:
                    allpages = True
                    break
            else:
                allpages = True
                # TODO: improve this part by a working last page check


            # check if ther is another order 
            idx = content[idx:].find(ordercookie)

        # press next button
        if not allpages:
            nextB = driver.find_element_by_class_name('a-last')
            nextB.click()

            body = driver.find_element_by_tag_name("body") # TODO: resolve deprecation
            #    time.sleep(0.5)
            text = body.text
            content = text
            idx = content.find(ordercookie)
            if idx == -1 : 
                break
        else: 
            break

    for url,onr in invoiceurls:
    
        print(f"get invioce from {url}")
        driver.get(url)

        # get invioce text
        invoicebody = driver.find_element_by_tag_name("body") # TODO: resolve deprecation
        invoicetext = invoicebody.text
        nrPriceaArticles = getNrPriceArticle(invoicetext,url,onr,f)
        

        #if isDelivered(content): 
        #    price = getprice(content)
        #    desc = getDesc(content)

    f.close()
    print(f"No more orders found after position {offset}")


findOrder(2)


print("Done")
