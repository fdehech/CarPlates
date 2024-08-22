import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from requests import get as get
from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/<Type>")
def Latest(Type):
    load_dotenv()
    url = os.getenv('URL')
    html = get(url).text
    soup = BeautifulSoup(html, 'html.parser').find("div", class_='cms-prose')
    C1="mx-1 flex justify-around rounded-[7px] border-2 border-white py-3 text-[30px] text-white"
    C2=C1+" flex-row-reverse"
    TUN = soup.find('span', class_=C1).get_text(strip=True)
    RS = soup.find('span' , class_=C2).get_text(strip=True)
    MC = (soup.find_all('span', class_=C2)[5]).get_text(strip=True)    
    IT = soup.find_all('span' , class_=C2)[1].get_text(strip=True)
    REM = soup.find_all('span' , class_=C2)[2].get_text(strip=True)
    TRAC = soup.find_all('span' , class_=C2)[3].get_text(strip=True)
    AA = soup.find_all('span' , class_=C2)[4].get_text(strip=True)
    ES = soup.find_all('span' , class_=C2)[1].get_text(strip=True)
    if (Type.upper() in ['TU','TUN']):
        Data={
            'TUN':TUN[:3]+' TUN '+TUN[7:]
        }

    elif (Type.upper() == 'RS' ):
        Data={
            'RS': 'RS '+RS[3:]
        }

    elif (Type.upper() in ['MOTO','MC']):
        Data = {
            'MC':'MOTO '+MC[3:]
        }
    elif (Type.upper() =="ALL"):
        Data = {
            'TUN':['Immatriculation Normale',TUN[:3]+' TU '+TUN[7:]],
            'RS':['Régime Suspensif','RS '+RS[3:]],
            'MC':['Motocyclette','MOTO '+MC[3:]],
            'IT':['Immatriculation Temporaire','IT ' +IT[3:]],
            'REM':['Véhicule Remorqué','REM ' +REM[3:]],
            'TRAC':['Tracteur ','TRAC ' +TRAC[4:]],
            'AA':['Appareil Agricole','AA ' +AA[3:]],
            'ES':['Engins Spéciaux','ES ' +ES[3:]]
        }

    return jsonify(Data),200



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)