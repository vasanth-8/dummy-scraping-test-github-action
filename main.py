import requests
from bs4 import BeautifulSoup as bs
import os
import re
from email.message import EmailMessage
import ssl
import smtplib
import logging

# from dotenv import load_dotenv
# load_dotenv()

logging.basicConfig(filename='logs.log',level=logging.INFO,format='%(asctime)s - %(message)s')

cert_path=os.path.join(os.path.dirname(__file__),'combined.crt')
headers={'Accept-Language':'en-US,en;q=0.9','User-Agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"}
req=requests.Session()
req.headers=headers
req.verify=cert_path if os.path.exists(cert_path) else False

response=""
try:
    url="https://aucoe.annauniv.edu/"
    response=req.get(url+'rank_details_overall.php')
except:
    try:
        url="http://14.139.161.113/"
        response=req.get(url+'rank_details_overall.php')
    except Exception as e1:
        logging.info(f"error - {e1}")

if response.status_code==200:
    soup=bs(response.content,'html.parser')
    x=soup.select('ul[class="cd-accordion cd-accordion--animated margin-top-lg margin-bottom-lg"] li[class="cd-accordion__item cd-accordion__item--has-children"] ul[class="cd-accordion__sub cd-accordion__sub--l1"] li[class="cd-accordion__item cd-accordion__item--has-children"]')
    xx=""
    for z in x[::-1]:
        if '2022' in z.text:
            xx=z
            break
    
    stop = open('stop.txt','r').read()

    if xx and not stop:
        y=xx.text
        yy=re.search(r'20\d{2}',y).group()
        fi=xx.find_all('a',{'class':'cd-accordion__label cd-accordion__label--icon-img'})
        pdfugurl=""
        for zz in fi:
            if 'ug' in zz['href'].lower():
                pdfugurl=url+zz['href']
                break
        else:
            pdfgurl=url+fi[0]['href']
            
        file_data = req.get(pdfugurl).content
        file_name = pdfugurl.split('/')[-1]

        sender_email=os.environ["SENDER_MAIL"]
        email_password=os.environ["PASSWORD"]
        receiver_email=[os.environ["RECEIVER1"],os.environ["RECEIVER2"]]
        subjet=f"AU Rank List for {yy} is Out!!!!"
        body=f"link for UG rank list {yy}\n\n{pdfugurl}"
        em=EmailMessage()
        em['From']=sender_email
        em['To']=receiver_email
        em['subject']=subjet
        
        try:
            em.set_content(body)
            em.add_attachment(file_data, maintype='application', subtype = 'octet-stream', filename=file_name)
            context=ssl.create_default_context()
            with smtplib.SMTP_SSL('smtp.gmail.com',465,context=context) as smtp:
                smtp.login(sender_email,email_password)
                smtp.sendmail(sender_email,receiver_email,em.as_string())
                with open('stop.txt','w') as filew:
                    filew.write("stop")
                logging.info(f"MAIL SENT")
        except Exception as e2:
            logging.info(f"error - {e2}")
    else:
        logging.info("not found")
else:
    logging.info("connection error")
