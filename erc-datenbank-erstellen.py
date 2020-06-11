#!/usr/bin/env python
# coding: utf-8


from bs4 import BeautifulSoup
import requests
import pandas as pd
import re
     
liste_neu =[]

for i in range(0,110): # 109 Seiten à Einträge 
    url = "https://erc.europa.eu/projects-figures/erc-funded-projects/results?items_per_page=100&page=" +str(i)
    main_url = url
    req = requests.get(main_url)
    soup = BeautifulSoup(req.text, "html.parser")
    
    # Methode prettify von BS4 anwenden, html Parser
    text = soup.prettify()
    
    
    y = soup.find_all("div", "views-row")
    for j in y:
        a = j.get_text()
        liste_neu.append(a)
        
# Die einzelnen Einträge aufsplitten.
for y in range(0, len(liste_neu)):
    t = liste_neu[y]
    t = re.sub(r"Project acronym ","", t)
    t = re.sub(r"Project ","###", t)

    ### hier Wenn-Bedingung, falls kein PI vorhanden
    if(t.count("(PI)") == 1):
        t = re.sub(r"Researcher [(]PI[)] ","###", t)
    else:
        t = re.sub(r"Host Institution [(]HI[)] ","### Kein Eintrag \n ###", t)

    t = re.sub(r"Host Institution [(]HI[)] ","###", t)
    t = re.sub(r"Call Details","###", t)
    t = re.sub(r"\n \r\n  Summary\r\n\n\r\n  (.)*", "", t)
    t = re.sub(r" Summary", "###", t)
    t = re.sub("Max ERC Funding", "###", t)
    t = re.sub(" €", "", t)
    t = re.sub("Duration", "", t)
    t = re.sub("Start date: ", "###", t)
    t = re.sub(", End date: ", "###", t)
    t = re.sub("# ","#", t)
    t = re.sub(" #","#", t)
    
    # some cleanup: überflüssige Leerzeichen und so weiter raus.
    t = re.sub("\r\n\n\r\n", "", t)
    t = re.sub("\n ", "", t)
    t = re.sub("\n", "", t)
    t = re.sub(" \r\n ", "", t)
    t = re.sub("\r","",t)       
    liste_neu[y]=t
    
# So, jetzt bauen wir uns einen Dataframe.
df_ERC = pd.DataFrame(liste_neu)
df_ERC.columns = ["Alles"]
new = df_ERC["Alles"].str.split("###", expand=True)
df_ERC["akronym"] = new[0]
df_ERC["titel"] = new[1]
df_ERC["PI"] = new[2]
df_ERC["HI"] = new[3]
df_ERC["details"] = new[4]
df_ERC["summary"] = new[5]
df_ERC["funding"] = new[6]
df_ERC["start"]=new[7]
df_ERC["end"]=new[8]
df_ERC.drop(columns=["Alles"], inplace=True)
df_ERC.columns = df_ERC.columns.str.strip()


for i in range(0,len(df_ERC["details"])):
    temp_str =df_ERC["details"][i]
    temp_str = re.sub(r"\s[(].*[)]","", temp_str)
    temp_str = re.sub(r"-\D*_\d*","", temp_str)
    temp_str = re.sub("ERC-","", temp_str)
    temp_str = re.sub(", ",",", temp_str)
    temp_str = re.sub("-\D*","", temp_str)
    df_ERC["details"][i] = temp_str

new = df_ERC["details"].str.split(",", expand=True)
df_ERC["grant_kategorie"] = new[0]
df_ERC["fach"] = new[1]
df_ERC["jahr_call"] = new[2]
df_ERC.drop(columns=["details"], inplace=True)

print(df_ERC)

# als JSON speichern
df_ERC.to_json("/home/jan/Dokumente/erc-alle.json")

# In CSV-Tabelle exportieren 
df_ERC.to_csv("/home/jan/Dokumente/erc-alle.csv", index = False)
