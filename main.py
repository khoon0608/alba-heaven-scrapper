import os
import csv
import math
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import shutil
import time

start = time.time()

os.system("clear")
alba_url = "http://www.alba.co.kr"

if(os.path.exists("csvfolder")):
  shutil.rmtree("csvfolder")
if(os.path.exists("zero_count_csvfolder")):
  shutil.rmtree("zero_count_csvfolder")
os.mkdir("csvfolder")
os.mkdir("zero_count_csvfolder")
# 실행할 때 마다 폴더를 생성, 만약 폴더가 있다면 지우고 생성

global index
global zero_info_companies
zero_info_companies = []


def find_superbrand_scrap():
  result = requests.get(alba_url)
  soup = BeautifulSoup(result.text, 'html.parser')
  companys_links_list = soup.select('div#MainSuperBrand > ul.goodsBox > li.impact')
  companies_list=[]
  for company_links in companys_links_list:
    companies_list.append(companys_links_list)
    apply_links = company_links.find_all('a',{'class':'brandHover'})
    for apply_link in apply_links:
      take_and_save_jobs_info(apply_link)

  return 0
      

def take_and_save_jobs_info(apply_link):
  company_url = apply_link['href']
  company_url_result = requests.get(company_url)
  company_url_soup = BeautifulSoup(company_url_result.text, 'html.parser')
  company_title = apply_link.select_one('span.company > strong').string.replace("/","")
  lastpage = find_superbrand_info_lastpage(company_url_soup)
  if (lastpage == 0):
    jobs_info = []
    save_to_file_by_company(jobs_info, company_title, company_url)
    print("\n", f"|{company_title} 0건이므로 스크랩 제외|", "\n")
  else:
    print("\n", f"[START {company_title}]", "\n")
    jobs_info = find_superbrand_info(lastpage, company_url, company_title)
    save_to_file_by_company(jobs_info, company_title, company_url)
    print("\n", f"[END {company_title}]", "\n")
  return 0




def find_superbrand_info_lastpage(soup):
  job_count = soup.select_one('div#NormalInfo > p.jobCount > strong')
  if (job_count):
    count = int(job_count.string.replace(",",""))
  else:
    list_count = soup.select_one('div#NormalInfo > p.listCount > strong')
    count = int(list_count.string.replace(",",""))
  lastpage = math.ceil(count / 50)
  return lastpage

def find_info(container):
  place_info = container.find('td',{'class':'local'}).get_text().replace('\xa0', " ")
  title_info = container.select_one('td.title > a > span.company').get_text().strip().replace("/","")
  time_info = container.select_one('td.data').get_text()
  methods_of_payment_wage = container.select_one('span.payIcon').get_text()
  payment_wage = container.select_one('span.number').get_text()
  pay_info = f'{methods_of_payment_wage} {payment_wage}원'
  date_info = container.select_one('td.regDate').get_text()
  return{
    "place" : place_info,
    "title" : title_info,
    "time" : time_info,
    "pay" : pay_info,
    "date" : date_info
  }

def find_superbrand_info(lastpage, main_url, company_title):
  jobs_info=[];
  for page in range(lastpage):
    if(main_url[7:10] == "www"):
      url = f'{main_url}/?page={page+1}'
    else:
      url = f'{main_url}job/brand/?page={page + 1}'
    result = requests.get(url)
    print(f'{company_title} {page + 1}page scrapping...')
    soup = BeautifulSoup(result.text, 'html.parser')
    info_containers = soup.select('div#NormalInfo > table > tbody > tr:not(.summaryView)')
    # 여기에 멀티프로세싱 추가할 것..아마
    for info_container in info_containers:
      job_info = find_info(info_container)
      jobs_info.append(job_info)
  return jobs_info

def save_to_file_by_company(jobs_info, company, company_url):
  now = datetime.now()

  if(len(jobs_info) == 0):
    global zero_info_companies
    zero_info_companies.append(company)
    file = open(f'zero_count_csvfolder/{company}.csv', mode = "w")
    writer = csv.writer(file)
    writer.writerow([company_url])
    writer.writerow([f'{int(now.strftime("%H")) + 9}:{now.strftime("%M")}:{now.strftime("%S")}'])
    writer.writerow([f'{now.strftime("%Y")}-{now.strftime("%m")}-{now.strftime("%d")}'])
    writer.writerow([f'{len(jobs_info)}건'])
  # job_info가 없으면 실행
  
  else:
    file = open(f'csvfolder/{company}.csv', mode = "w")
    writer = csv.writer(file)
    writer.writerow([f'{int(now.strftime("%H")) + 9}:{now.strftime("%M")}:{now.strftime("%S")}'])
    writer.writerow([f'{now.strftime("%Y")}-{now.strftime("%m")}-{now.strftime("%d")}'])
    writer.writerow([f"총 {len(jobs_info)}건"])
    writer.writerow(["index", "place", "title", "time", "pay", "date"])
    global index
    index = 0
    for job_info in jobs_info:
      index = 1 + index
      job_info_values = job_info.values()
      list_job_info = list(job_info_values)
      list_job_info.insert(0, index)
      writer.writerow(list_job_info)
  # job_info가 있으면 실행
  return 0


find_superbrand_scrap()
# 실행
if(len(zero_info_companies) != 0):
  for zero_info_company in zero_info_companies:
    print(f"\n{zero_info_company}는 채용정보가 0건 입니다.\n")
# 채용정보가 없는 회사가 존재하면 회사이름 출력 
print("END")
# 종료 
print(f"소요시간은 { math.ceil((time.time() - start)/60)}분입니다." )
# 소요시간 출력