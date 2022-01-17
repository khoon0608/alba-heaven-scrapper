import os
import csv
import math
import requests
from bs4 import BeautifulSoup

os.system("clear")
alba_url = "http://www.alba.co.kr"

global number_completed
number_completed = 0

def find_superbrand_links():
  result = requests.get(alba_url)
  soup = BeautifulSoup(result.text, 'html.parser')
  companys_links_list = soup.select('div#MainSuperBrand > ul.goodsBox > li.impact')
  for company_links in companys_links_list:
    apply_links = company_links.find_all('a',{'class':'brandHover'})
    for apply_link in apply_links:
      global number_completed
      print(number_completed)
      print(apply_link)
      company_url = apply_link['href']
      company_url_result = requests.get(company_url)
      company_url_soup = BeautifulSoup(company_url_result.text, 'html.parser')
      company_title = apply_link.select_one('span.company > strong').string.replace("/","")
      print(company_title)
      lastpage = find_superbrand_info_lastpage(company_url_soup, company_title)
      jobs_info = find_superbrand_info_container(lastpage, company_url, company_title)
      save_to_file_by_company(jobs_info, company_title)
      number_completed += 1 
  return 0
# 1 

def find_superbrand_info_lastpage(soup, company_title):
  job_count = soup.select_one('div#NormalInfo > p.jobCount > strong')
  if (job_count):
    count = int(job_count.string.replace(",",""))
  else:
    list_count = soup.select_one('div#NormalInfo > p.listCount > strong')
    count = int(list_count.string.replace(",",""))
  lastpage = math.ceil(count / 50)
  return lastpage
# 4

def find_info(container, url):
  place = container.find('td',{'class':'local'}).get_text()
  title = container.select_one('td.title > a > span.company').get_text().strip().replace("/","")
  working_time = container.select_one('td.data').get_text()
  methods_of_payment_wage = container.select_one('span.payIcon').get_text()
  payment_wage = container.select_one('span.number').get_text()
  pay = f'{methods_of_payment_wage} {payment_wage}원'
  date_ = container.select_one('td.regDate').get_text()
  return{
    "place" : place.replace('\xa0', " "),
    "title" : title,
    "time" : working_time,
    "pay" : pay,
    "date" : date_
  }
# 6

def find_superbrand_info_container(lastpage, main_url, company_title):
  jobs_info=[];
  for page in range(lastpage):
    url = f'{main_url}job/brand/?page={page + 1}'
    result = requests.get(url)
    print(f'{company_title} {page + 1}page scrapping...')
    soup = BeautifulSoup(result.text, 'html.parser')
    info_containers = soup.select('div#NormalInfo > table > tbody > tr:not(.summaryView)')
    for info_container in info_containers:
      job_info = find_info(info_container, url)
      jobs_info.append(job_info)
  return jobs_info
# 5

def save_to_file_by_company(jobs_info, company):
  file = open(f'csvfolder/{company}.csv', mode = "w")
  writer = csv.writer(file)
  writer.writerow(["place", "title", "time", "pay", "date"])
  for job_info in jobs_info:
    job_info_values = job_info.values()
    list_job_info = list(job_info_values)
    writer.writerow(list_job_info)



links_list = find_superbrand_links()
print(number_completed)
print("END")