#!/usr/bin/env python
# coding: utf-8

# In[176]:


import requests
from bs4 import BeautifulSoup
import json
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import pytz
from datetime import datetime


url = "https://houm.com/cl/propiedades/arriendo/ambos/metropolitana?pos=-33.437554,-70.650490,12.20&max_price=399997&parking_spaces=1"
result = requests.get(url)
src = result.content
soup = BeautifulSoup(src, 'lxml')


# In[177]:


tz=pytz.timezone('America/Santiago')
now = datetime.now(tz).strftime("%d/%m/%Y %H:%M:%S")


# In[216]:


with open('deptos.txt') as f:
    for line in f:
        print(line)
f.close()


# In[217]:


deptos_old = line.split(',')


# In[180]:


def string_formatter(string_in):
	str_low = string_in.lower()
	
	str_low1 = str_low.replace('á','a')
	str_low2 = str_low1.replace('é','e')
	str_low3 = str_low2.replace('í','i')
	str_low4 = str_low3.replace('ó','o')
	str_low5 = str_low4.replace('ú','u')
	str_low6 = str_low5.replace('ë','e')
	str_low7 = str_low6.replace('ü','u')
	str_low8 = str_low7.replace('ñ','n')
	str_low9 = str_low8.upper()
	
	str_def = str_low9
	return str_def.replace(' ','-')

def send_email(recipient,msg):

    user='maxpowermax6000@gmail.com'
    pwd='drums09='
    FROM = user
    TO = recipient
    message = msg

    html = """
    <html>
    <head>
    <style>
    .myDiv {
      background-color: #000000;
    }
    .msg {
      background-color: white;    
      text-align: center;
    }
    img {
      display: block;
      margin-left: auto;
      margin-right: auto;
    }

    p {
    display: inline-block; 
    text-align: left; 
    color:black;
    }

    </style>
    </head>
    <body>
    <div style="border-collapse: collapse;display: table;width: 100%;background-color:#000000;">
    <div class="col num4" style="display: table-cell; vertical-align: top; max-width: 320px; min-width: 268px; width: 271px;">
    <div style="border-top:0px solid transparent; border-left:0px solid transparent; border-bottom:0px solid transparent; border-right:0px solid transparent; padding-top:45px; padding-bottom:10px; padding-right: 5px; padding-left: 5px;">
    </div>
    </div>
    </div>

    <div class="msg" style="font-family:helvetica">
        <p>"""+message+"""
        </p>
    </div>
    </body>
    </html>
    """
    body = MIMEText(html, 'html')
    body["Subject"] = "Propiedades Houm {}".format(now)

    
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(user,pwd)
        server.sendmail(FROM, TO, body.as_string())
        server.close()
        print ('successfully sent the mail to {}'.format(TO))
    except Exception as e:
        
        print ("failed to send mail"+str(e))

    return


# In[181]:


data_raw = (str(soup).split("initialMapList")[1]).split('"uid"')


# In[182]:


deptos = []
for i in range(0,len(data_raw)):
    depto = '{'+'"uid"'+(data_raw[i][:-2]).strip()
    
    if (depto.find(',"defaultPos":') != -1):
        deptos.append(depto.split(',"defaultPos":')[0])
    
    if (depto.find('],"initialPropertyList":') != -1):
        deptos.append(depto.split('],"initialPropertyList":')[0])
    else:
        deptos.append(depto)


# In[218]:


# parse:
deptos_json = []
for j in range(0,len(deptos)):
    if j < len(deptos) - 1:
        if len(deptos[j]) > 9:
            if deptos[j][-1] == ']':
                deptos_json.append(json.loads(deptos[j][:-1]))
            if deptos[j][-1] != ']':
                deptos_json.append(json.loads(deptos[j]))

msg_mail=""
send_mail_status=False
for elem in deptos_json:
    id=elem['id']
    type=elem['type']
    address=elem['address']
    street_num=elem['street_number']
    comuna=elem['comuna']
    price=elem['price'][0]['value']
    currency=elem['price'][0]['currency']
    gc=elem['property_details'][0]['gc']
    m_constr=elem['property_details'][0]['m_construidos']
    m_terr=elem['property_details'][0]['m_terreno']
    dorm=elem['property_details'][0]['dormitorios']
    banos=elem['property_details'][0]['banos']
    estac=elem['property_details'][0]['estacionamientos']
    orientacion=elem['property_details'][0]['orientacion']
    url_ad="https://houm.com/cl/propiedades/arriendo/departamento/region-metropolitana/{}/{}".format(string_formatter(elem['comuna']).lower(),elem['id'])
    
    if price <= 390000 and estac>=1 and comuna in ['Santiago','Peñalolén','La Reina','Macul','Providencia',
            'Ñuñoa','La Florida'] and str(id) not in deptos_old:
        msg_mail = msg_mail+"""            ID Propiedad {} - Tipo: {}<br>
            Comuna: {}, Dirección: {} {}<br>
            Precio: ${}<br>
            Gastos Comunes: ${}<br>
            M2 construidos: {} m2<br>
            Dormitorios: {} - Baños: {} - Estacionamientos: {}<br>
            URL: {}<br>
            <br>""".format(id,type,comuna,address,street_num,price,gc,m_constr,dorm,banos,estac,url_ad)
        deptos_old.append(str(id))
        send_mail_status = True
        
# Replace the target string
filedata = str(deptos_old).replace("[","").replace("]","").replace(" ","").replace("'","")
# Write the file out again

#open the input file in write mode
fin = open("deptos.txt", "wt")
#overrite the input file with the resulting data
fin.write(filedata)
#close the file
fin.close()

if send_mail_status == True:
    mail_list = ['diego.vasquezcaro@gmail.com','eripaola@gmail.com']
    #send_email(mail_list,msg_mail)

