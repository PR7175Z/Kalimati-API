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
    initial_url = "https://kalimatimarket.gov.np/price"
    lang_url = "https://kalimatimarket.gov.np/lang/en"

    #start a session
    session = requests.Session()

    #Get the first URL
    response = session.get(initial_url)

    if response.status_code == 200:
        #Navigate to the second URL
        response_lang = session.get(lang_url)

        if response_lang.status_code == 200:
            soup = BeautifulSoup(response_lang.content, 'html.parser')

            table = soup.find('table', id='commodityPriceParticular')
            
            if table:
                tbody = table.find('tbody')
                
                if tbody:
                    vegdict = {}
                    rows = tbody.find_all('tr')

                    for row in rows:
                        cells = row.find_all('td')
                        if len(cells) >= 5:
                            name_raw = cells[0].get_text(strip=True)
                            unit = cells[1].get_text(strip=True)
                            min_price = cells[2].get_text(strip=True)
                            max_price = cells[3].get_text(strip=True)
                            avg_price = cells[4].get_text(strip=True)

                            name_cleaned = re.sub(r'\((.*?)\)', r'-\1', name_raw)
                            name_cleaned = re.sub(r'\s+', '-', name_cleaned)

                            vegdict[name_cleaned] = {
                                'name': name_raw,
                                'unit': unit,
                                'min': min_price,
                                'max': max_price,
                                'avg': avg_price
                            }

                    return vegdict
                else:
                    return HTTPException(status_code = 404, detail = str('tbody not found in table'))
            else:
                return HTTPException(status_code = 404, detail = str('table not found'))
        else:
            return HTTPException(status_code = 404, detail = str(f"Failed to fetch the language-specific page. Status code: {response_lang.status_code}"))
    else:
        return HTTPException(status_code = 404, detail = str(f"Failed to fetch the page. Status code: {response.status_code}"))