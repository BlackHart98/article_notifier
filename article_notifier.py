import requests
import smtplib
import typing as t
from bs4 import BeautifulSoup
from email.mime.text import MIMEText
from jinja2 import Environment, FileSystemLoader
from dataclasses import dataclass 
import json
import os
from dotenv import find_dotenv, load_dotenv
import time
import sys

DOTENV_PATH = find_dotenv()
load_dotenv(DOTENV_PATH)


EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

class Scraped:
    def __init__(self):
        pass
    
    def get_name(self):
        pass
    
    def _normalize(self, raw_result : t.List[t.Tuple[str, str, str]]) -> t.List[t.Dict[str, str]]:
        pass
    
    def scrape(self):
        return self

    def get_current_state(self) -> t.Dict[str, t.List[t.Dict[str, str]]]:
        pass
    

class BigThink(Scraped):
    _url : str = "https://bigthink.com/articles/"
    _raw_result : t.List[t.Tuple[str, str, str]] = []
    _current_state : t.List[t.Dict[str, str]] = []
    _new_articles : t.List[t.Dict[str, str]] = []
    
    def get_name(self):
        return "BigThink"
    
    def _normalize(self, raw_result : t.List[t.Tuple[str, str, str]]) -> t.List[t.Dict[str, str]]:
        current_state : t.List[t.Dict[str, str]] = []
        for item in raw_result:
            current_state += [{
                "title" : item[1],
                "link" : item[0],
                "summary" : item[2]}]
        return current_state
    
    def scrape(self):
        try:
            r = requests.get(self._url)
            self._raw_result = []
            soup : BeautifulSoup = BeautifulSoup(r.content, "html.parser")
            article_list = soup.find_all("article", {"class" : "card card-standard card-narrative"})
            for item in article_list:
                headline_class = item.find("div", class_="card-headline")
                key : str = headline_class.find("a")["href"]
                headline : str = "".join(headline_class.find("a").contents).strip()
                excerpt_class = item.find("div", class_="card-excerpt")
                excerpt = "".join(excerpt_class.contents).strip()
                self._raw_result += [(key, headline, excerpt)]
            self._current_state = self._normalize(self._raw_result)
            return self
        except:
            print(f"ERROR: Issues fetching from {self._url}")
            return self

    def get_current_state(self) -> t.Dict[str, t.List[t.Dict[str, str]]]:
        return {"bigthink": self._current_state}

def get_update(
    previous_state: t.Dict[str, t.List[t.Dict[str, str]]], 
    current_state: t.Dict[str, t.List[t.Dict[str, str]]]) -> t.Dict[str, t.List[t.Dict[str, str]]]:
    result : t.Dict[str, t.List[t.Dict[str, str]]] = {}
    for article in current_state:
        if article not in previous_state:
            result[article] = current_state[article]
        else:
            result[article] = []
            current_dict : t.Dict[str, t.Any] = {}
            previous_dict : t.Dict[str, t.Any] = {}
            for item in current_state[article]:
                current_dict[item["link"]] = item
                pass
            for item in previous_state[article]:
                previous_dict[item["link"]] = item
            for item in current_dict:
                if item not in previous_dict:
                    result[article] += [current_dict[item]]
    return result
    


def send_gmail_thread(sender_email, sender_password, recipient_email, updates : t.Dict[str, t.List[t.Dict[str, str]]]) -> None:
    try:
        alert_group = []
        for item in updates:
            alert_group += [{
                "name" : item, 
                "news" : updates[item],
            }]
        
        # print(alert_group)
        context = {"websites" : alert_group}
        environment = Environment(loader=FileSystemLoader("templates/"))
        template = environment.get_template('email_template.html')
        html_body = template.render(context)
        
        html_message = MIMEText(html_body, 'html')
        html_message['Subject'] = "MyReporter: News update!"
        html_message['From'] = sender_email
        html_message['To'] = recipient_email
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, html_message.as_string())
    except:
        print(f"ERROR: Could not send email to {recipient_email}")
        

if __name__ == "__main__":
    if (len(sys.argv) - 1 < 1) or (len(sys.argv) - 1 > 2):
        print("ERROR: Invalid command parameters, expect `python crawler.py <recipient_email> [--offset]`")
        sys.exit()
    offset = False
    if len(sys.argv) - 1 == 2:
        if sys.argv[2] != "--offset":
            print("ERROR: Invalid command parameters, expect `python crawler.py <recipient_email> [--offset]`")
            sys.exit()
        else:
            offset = True
    
    # websites  
    bigthink = BigThink()
    websites : Scraped = {bigthink}
    
    current_state = {}
    previous_state_in_mem = {}
    recipient = sys.argv[1]
    while True:
        for item in websites:
            print(f"INFO: Reviewing {item.get_name()}")
            current_state.update(item.scrape().get_current_state())
        updates = get_update(previous_state_in_mem, current_state)
        if not offset:
            all_empty: bool = True
            _updates = {}
            for key in updates:
                if len(updates[key]) > 0:
                    _updates[key] = updates[key]
                    all_empty = False
            if not all_empty:
                print("INFO: New articles found")
                print(f"INFO: Sending email thread to recipient: {recipient}")
                send_gmail_thread(EMAIL, PASSWORD, recipient, updates)
                print(f"INFO: Sent email to recipient: {recipient}")
        else:
            offset = False
        previous_state_in_mem = current_state
        time.sleep(60)