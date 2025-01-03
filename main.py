import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import re
import time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins = ['*'],
    allow_credentials = True,
    allow_methods = ['*'],
    allow_headers = ['*']
)

@app.get('/veg')
def veg():
    url = "https://kalimatimarket.gov.np/lang/en"

    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        tbody = soup.find('tbody')
        if tbody:
            vegdict = {}
            texts = [tag.get_text(strip=True) for tag in tbody.find_all('tr') if tag.get_text(strip=True)]

            for x in texts:
                item = x.split('Rs')
                new_text = re.sub(r'\((.*?)\)', r'-\1', item[0])
                t = re.sub(r'\s+', '-', new_text)

                if t not in vegdict:
                    vegdict[t] = {'name': '', 'min': '', 'max': '', 'avg': ''}

                vegdict[t]['name'] = item[0].strip() 
                vegdict[t]['min'] = item[1].strip() 
                vegdict[t]['max'] = item[2].strip() 
                vegdict[t]['avg'] = item[3].strip() 

            return vegdict
        else:
            return HTTPException(status_code = 404, detail = str('Not found'))
    else:
        return HTTPException(status_code = 404, detail = str('Failed to fetch the page'))