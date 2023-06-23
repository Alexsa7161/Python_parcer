import requests
import pandas as pd
import os
from sqlalchemy import create_engine
import warnings
warnings.simplefilter("ignore")
from lxml import etree
import smtplib
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import json
from bs4 import BeautifulSoup
import xml.etree.ElementTree as Xet
import zipfile
import csv
from transliterate import translit
import sqlalchemy
#mas - array of sites
#xpaths - paths to parsing
mas = ['https://cbr.ru/registries/123-fz/#a_72070','https://cbr.ru/registries/RSCI/activity_npf/#a_85257link','https://cbr.ru/registries/microfinance/#a_33636','https://www.cbr.ru/banking_sector/credit/FullCoList/','https://cbr.ru/PSystem/payment_system/?utm_source=w&utm_content=page#a_101477','https://www.cbr.ru/banking_sector/credit/cstat/']
xpaths = ['/html/body/main/div/div/div/div[2]/div/div[2]/div/div/a/span','/html/body/main/div/div/div/div[3]/div/div[2]/div/div/a/span','/html/body/main/div/div/div/div[6]/div/div[2]/div/div/a/span','/html/body/main/div/div/div/form/div/div/div/a/text()','/html/body/main/div/div/div/div[9]/div[2]/div/div[2]/div/div[1]/a/@href']

#save date into json
def save_date_to_json(date):
    json_file = 'downloaded_dates.json'
    downloaded_dates = {}
    if os.path.exists(json_file):
        with open(json_file, 'r') as file:
            downloaded_dates = json.load(file)

    downloaded_dates['date'] = date

    with open(json_file, 'w') as file:
        json.dump(downloaded_dates, file)

#get date from json
def get_saved_date_from_json():
    json_file = 'downloaded_dates.json'
    if os.path.exists(json_file):
        with open(json_file, 'r') as file:
            downloaded_dates = json.load(file)
            if 'date' in downloaded_dates:
                return downloaded_dates['date']
    return None

#checks whether the day in the file corresponds to the current one
dt = datetime.date.today().strftime("%Y-%m-%d")
saved_date = get_saved_date_from_json()
if not os.path.exists('downloaded_dates.json'):
    save_date_to_json(dt)
elif saved_date == dt:
    print("Файл уже загружен для текущей даты. Пропускаю скачивание.")
    exit()
else:
    save_date_to_json(dt)
folder_name = dt
if not os.path.exists(folder_name):
        os.makedirs(folder_name)
#passing through the links
for i in range(len(mas)):
    url = mas[i]
    if (i != 5):
        response = requests.get(url)
        html = response.text
        tree = etree.HTML(html)
        excel_link = tree.xpath(xpaths[i])


    if i == 5 or excel_link:
        if (i!=5):
            excel_link = excel_link[0].getparent().get('href')
            excel_url = "https://cbr.ru" + excel_link
            excel_response = requests.get(excel_url)
        if url == 'https://cbr.ru/registries/123-fz/#a_72070':
            # create or open file for audit
            with open(get_saved_date_from_json()+"\\fin_reestr_"+get_saved_date_from_json()+".xlsx", "wb") as file:
                file.write(excel_response.content)
        elif url == 'https://cbr.ru/registries/RSCI/activity_npf/#a_85257link':
            with open(get_saved_date_from_json()+"\\reestr_licenzii_"+get_saved_date_from_json()+".xlsx", "wb") as file:
                file.write(excel_response.content)
        elif url == 'https://cbr.ru/registries/microfinance/#a_33636':
            with open(get_saved_date_from_json()+"\\reestr_lombardov_"+get_saved_date_from_json()+".xlsx", "wb") as file:
                file.write(excel_response.content)
        elif url == 'https://www.cbr.ru/banking_sector/credit/FullCoList/888888888':
            # site with many links in one
            with open(get_saved_date_from_json()+"\\credit_organization_"+get_saved_date_from_json()+".xlsx", "wb") as file:
                file.write(excel_response.content)
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")
            table = soup.find("table")
            rows = table.find_all("tr")
            df = {'firm_name' : [],
                  'BIC' : [],
                  'adr_ust' : [],
                  'fakt_adr' : [],
                  'Idx' : []
                  }
            mas_d = []
            df_res = pd.DataFrame(df)
            m = 0
            for row in rows:
                # check the "a" tag in html markup
                columns = row.find_all("a")
                row_data = [column.get('href') for column in columns]
                for link in row_data:  #for link in site
                    link = 'https://www.cbr.ru' + link
                    response = requests.get(link)
                    soup1 = BeautifulSoup(response.text, "lxml")
                    inf = soup1.find("div", attrs= {"class" : "org_info"})
                    rows1 = inf.find_all("div", attrs= {"class": "coinfo_item_text col-md-13 offset-md-1"})  #necessary information
                    cols = inf.find_all("div", attrs= {"class": "coinfo_item_title col-md-9"})
                    if cols[0].text != 'Полное фирменное наименование' or cols[5].text != 'БИК' or cols[6].text != 'Адрес из устава' or cols[7].text != 'Адрес фактический':
                        # index
                        m = m+1
                        df_res +=['','','','',m]
                        continue
                    for j in range(0,8):
                        if j ==0 or j== 5 or j == 6 or j == 7:
                            mas_d.append(rows1[j].text)
                    mas_d.append(m)
                    # insert into dataframe array
                    df_res = pd.concat([pd.DataFrame([mas_d], columns=df_res.columns), df_res], ignore_index=True)
                    mas_d.clear()
            df1 = pd.DataFrame(pd.read_excel(
                get_saved_date_from_json() + "\\credit_organization_" + get_saved_date_from_json() + ".xlsx",
                skiprows=2))
            df1 = pd.concat([df1, df_res], axis=1, join='inner')
            df1.drop([0, 1], inplace=True)
            df1.columns = ['ccode', 'oldctbank', 'newctbank', 'csname', 'cnamer', 'oldcopf', 'newcopf', 'cregnum',
                          'oldcregnr', 'newcregn', 'cdreg', 'lic', 'strcuraddr', 'ogrn','poln_name','BIC','adr_ust','fakt_adr','Idx']
            df1.to_csv(get_saved_date_from_json() + "\\credit_organization_" + get_saved_date_from_json() + ".csv",
                      index=False, sep='%')
            engine = create_engine('postgresql://alex:alexsa7161@localhost:5432/postgres')
            file = os.path.dirname(
                os.path.abspath(
                    __file__)) + '\\' + get_saved_date_from_json() + '\\' + 'credit_organization_' + get_saved_date_from_json() + '.csv'
            xl = pd.read_csv(
                get_saved_date_from_json() + '\\credit_organization_' + get_saved_date_from_json() + '.csv',
                delimiter='%')
            table_name = 'credit_organization'
            Dtype = {
                "BIC": sqlalchemy.types.VARCHAR(length=9)
            }
            # export to db
            xl.to_sql(table_name, con=engine, if_exists='replace', index=False, index_label=True,dtype=Dtype)
        elif url == 'https://cbr.ru/PSystem/payment_system/?utm_source=w&utm_content=page#a_101477':
            with open(get_saved_date_from_json()+'\\BIC_sprav_'+get_saved_date_from_json()+'.zip', "wb") as file:
                file.write(excel_response.content)
            # .zip_file_open
            with zipfile.ZipFile(get_saved_date_from_json()+'\\BIC_sprav_'+get_saved_date_from_json()+'.zip', 'r') as zip_file:
                zip_file.extractall(get_saved_date_from_json()+'\\')
            cols = ["NameP", "Rgn","DateIn","PtType","Srvcs","XchType","UID","PrntBIC","AccountCBRBIC","Idx"]
            rows = []
            #parcing .xml file to .csv
            tree = Xet.parse(get_saved_date_from_json()+'\\'+str.replace(get_saved_date_from_json(),'-','')+'_ED807_full.xml')
            root = tree.getroot()
            try:
                m = 0
                for i in root:
                    num = 0
                    t = False
                    AccountCBRBIC = i.attrib['BIC']
                    for j in i:
                        try:
                            if 'ParticipantInfo' in j.tag:
                                num += 1
                                NameP = j.attrib['NameP']
                                Rgn = j.attrib['Rgn']
                                DateIn = j.attrib['DateIn']
                                PtType = j.attrib['PtType']
                                Srvcs = j.attrib['Srvcs']
                                XchType = j.attrib['XchType']
                                UID = j.attrib['UID']
                                if j.attrib.__contains__('PrntBIC'):
                                    PrntBIC = j.attrib['PrntBIC']
                                else:
                                    PrntBIC = " "
                            elif 'RstrList' in j.tag:
                                t = True
                            elif 'Accounts' in j.tag:
                                num +=1
                                if (num != 2):
                                    m += 1
                                    NameP = ''
                                    Rgn = ''
                                    DateIn = ''
                                    PtType = ''
                                    Srvcs = ''
                                    XchType = ''
                                    UID = ''
                                    PrntBIC = ''
                                    rows.append({"NameP": NameP,
                                                 "Rgn": Rgn,
                                                 "DateIn": DateIn,
                                                 "PtType": PtType,
                                                 "Srvcs": Srvcs,
                                                 "XchType": XchType,
                                                 "UID": UID,
                                                 "PrntBIC": PrntBIC,
                                                 "AccountCBRBIC": AccountCBRBIC,
                                                 "Idx" : m
                                                 })
                                    break
                                else:
                                    m += 1
                                    rows.append({"NameP": NameP,
                                                 "Rgn": Rgn,
                                                 "DateIn": DateIn,
                                                 "PtType": PtType,
                                                 "Srvcs": Srvcs,
                                                 "XchType": XchType,
                                                 "UID": UID,
                                                 "PrntBIC": PrntBIC,
                                                 "AccountCBRBIC": AccountCBRBIC,
                                                 "Idx": m
                                                 })
                                    break
                            else:
                                continue
                        except: break
            except ValueError: continue
            df = pd.DataFrame(rows, columns=cols)
            df.columns = ['NameP', 'Rgn', 'DateIn', 'PtType', 'Srvcs', 'XchType', 'UID','PrntBIC','AccountCBRBIC','Idx']
            df.to_csv(get_saved_date_from_json()+'\\BIC_sprav_'+get_saved_date_from_json()+'.csv', index=False, sep='%')
            engine = create_engine('postgresql://alex:alexsa7161@localhost:5432/postgres')
            file = os.path.dirname(
                os.path.abspath(__file__)) +'\\'+ get_saved_date_from_json()+'\\' + 'BIC_sprav_' + get_saved_date_from_json() + '.csv'
            xl = pd.read_csv(get_saved_date_from_json()+'\\BIC_sprav_' + get_saved_date_from_json() + '.csv', delimiter='%')
            table_name = 'BIC_sprav_dop'
            Dtype = {
                "NameP": sqlalchemy.types.VARCHAR(length=200),
                "Rgn": sqlalchemy.types.INTEGER(),
                "DateIn": sqlalchemy.types.DATE(),
                "PtType": sqlalchemy.types.INTEGER(),
                "Srvcs" : sqlalchemy.types.INTEGER(),
                "XchType": sqlalchemy.types.INTEGER(),
                "UID": sqlalchemy.types.VARCHAR(length=10),
                "PrntBIC": sqlalchemy.types.VARCHAR(length=10),
                "AccountCBRBIC": sqlalchemy.types.VARCHAR(length=20),
                "Idx" : sqlalchemy.types.INTEGER()
            }
            xl.to_sql(table_name, con=engine, if_exists='replace', index=False, index_label=True,dtype=Dtype)
        print("Файл успешно загружен.")
    if url == 'https://cbr.ru/registries/123-fz/#a_72070':
        pdxl = pd.ExcelFile(get_saved_date_from_json()+"\\fin_reestr_"+get_saved_date_from_json()+".xlsx")
        for name in pdxl.sheet_names:
            df = pd.DataFrame(pd.read_excel(get_saved_date_from_json()+"\\fin_reestr_"+get_saved_date_from_json()+".xlsx",skiprows=2,sheet_name=name))
            df.drop(df.columns[0], axis=1, inplace=True)
            df.drop([0, 1], inplace=True)
            mas_s = []
            for i in range(len(df.columns)):
                mas_str = df.columns[i].split(' ')
                if (len(mas_str) ==1):
                    if (len(mas_str[0])<4):
                        res = mas_str[0]
                    else:
                        res = mas_str[0][0:3]
                elif ( len(mas_str[0])>4 and len(mas_str[1])>4):
                    res = mas_str[0][0:4]+mas_str[1][0:4]
                elif (len(mas_str[0])<4 and len(mas_str[1])<4):
                    res = mas_str[0]+mas_str[1]
                elif ( len(mas_str[0])>4):
                    res = mas_str[0][0:4]+mas_str[1]
                elif (len(mas_str[1])>4):
                    res = mas_str[0]+mas_str[1][0:4]
                mas_s.append(translit(res,language_code='ru', reversed=True))
            df.columns = mas_s
            df.to_csv(get_saved_date_from_json()+"\\fin_reestr_"+name+get_saved_date_from_json()+".csv",index=False,sep='%')
            engine = create_engine('postgresql://alex:alexsa7161@localhost:5432/postgres') #connection to db
            file = os.path.dirname(os.path.abspath(__file__))+'\\'+get_saved_date_from_json()+'\\'+'fin_reestr_'+name+get_saved_date_from_json()+'.csv'
            xl = pd.read_csv(get_saved_date_from_json()+'\\fin_reestr_'+name+get_saved_date_from_json()+'.csv',delimiter='%')
            table_name = 'fin_reestr_'+name
            xl.to_sql(table_name, con=engine, if_exists='replace', index=False, index_label=True)
    elif url == 'https://cbr.ru/registries/RSCI/activity_npf/#a_85257link':
        df = pd.DataFrame(pd.read_excel(get_saved_date_from_json()+"\\reestr_licenzii_" + get_saved_date_from_json() + ".xlsx", skiprows=2))
        df.drop(df.columns[0], axis=1, inplace=True)
        df.drop([0, 1], inplace=True)
        df.columns = ['polnnaim', 'sokrnaim', 'nomlicenz', 'datvid', 'inn', 'ogrn', 'adresurliz', 'telef', 'adressait','uchastzastrlic','uchastpravuchast']
        df.to_csv(get_saved_date_from_json()+"\\reestr_licenzii_" + get_saved_date_from_json() + ".csv", index=False, sep='%')
        engine = create_engine('postgresql://alex:alexsa7161@localhost:5432/postgres')
        file = os.path.dirname(os.path.abspath(__file__)) + '\\' +get_saved_date_from_json()+'\\'+ 'reestr_licenzii_' + get_saved_date_from_json() + '.csv'
        xl = pd.read_csv(get_saved_date_from_json()+'\\reestr_licenzii_' + get_saved_date_from_json() + '.csv', delimiter='%')
        table_name = 'reestr_licenzii'
        xl.to_sql(table_name, con=engine, if_exists='replace', index=False, index_label=True)
    elif url == 'https://cbr.ru/registries/microfinance/#a_33636':
        df = pd.DataFrame(pd.read_excel(get_saved_date_from_json()+"\\reestr_lombardov_" + get_saved_date_from_json() + ".xlsx", skiprows=2))
        df.drop(df.columns[0], axis=1, inplace=True)
        df.drop([0, 1], inplace=True)
        mas_s = []
        for i in range(len(df.columns)):
            mas_str = df.columns[i].split(' ')
            if (len(mas_str) == 1):
                if (len(mas_str[0]) < 4):
                    res = mas_str[0]
                else:
                    res = mas_str[0][0:3]
            elif (len(mas_str[0]) > 4 and len(mas_str[1]) > 4):
                res = mas_str[0][0:4] + mas_str[1][0:4]
            elif (len(mas_str[0]) < 4 and len(mas_str[1]) < 4):
                res = mas_str[0] + mas_str[1]
            elif (len(mas_str[0]) > 4):
                res = mas_str[0][0:4] + mas_str[1]
            elif (len(mas_str[1]) > 4):
                res = mas_str[0] + mas_str[1][0:4]
            mas_s.append(translit(res, language_code='ru', reversed=True))
        df.columns = mas_s
        df.to_csv(get_saved_date_from_json()+"\\reestr_lombardov_" + get_saved_date_from_json() + ".csv", index=False, sep='%')
        engine = create_engine('postgresql://alex:alexsa7161@localhost:5432/postgres')
        file = os.path.dirname(
            os.path.abspath(__file__)) + '\\' +get_saved_date_from_json()+'\\'+ 'reestr_lombardov_' + get_saved_date_from_json() + '.csv'
        xl = pd.read_csv(get_saved_date_from_json()+'\\reestr_lombardov_' + get_saved_date_from_json() + '.csv', delimiter='%')
        table_name = 'reestr_lombardov'
        xl.to_sql(table_name, con=engine, if_exists='replace', index=False, index_label=True)
    elif url == 'https://www.cbr.ru/banking_sector/credit/cstat/':
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table")
        rows = table.find_all("tr")
        with open(get_saved_date_from_json() + "\\kol_char"+get_saved_date_from_json()+".csv", "w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file, delimiter=";")
            column_mapping = {
                "Регион": "reg",
                "Наименование КО": "naimko",
                "Рег. № КО": "regko",
                "Головные офисы": "golofic",
                "Филиалы": "filial",
                "Допофисы": "dopof",
                "Всего подразделений": "vsego"
            }
            header_row = table.find("thead").find_all("th")
            header_data = [column_mapping.get(header.get_text().strip(), "") for header in header_row]
            writer.writerow(header_data)
            for row in rows:
                columns = row.find_all("td")
                row_data = [column.get_text().strip() for column in columns]
                writer.writerow(row_data)
        engine = create_engine('postgresql://alex:alexsa7161@localhost:5432/postgres')
        file = os.path.dirname(
            os.path.abspath(
                __file__)) + '\\' + get_saved_date_from_json() + '\\' + 'credit_organization_' + get_saved_date_from_json() + '.csv'
        xl = pd.read_csv(get_saved_date_from_json() + "\\kol_char"+get_saved_date_from_json()+".csv",delimiter=';')
        table_name = 'kol_char'
        print("Файл успешно загружен.")
        xl.to_sql(table_name, con=engine, if_exists='replace', index=False, index_label=True)
files = [get_saved_date_from_json()+'\\BIC_sprav_'+get_saved_date_from_json()+'.csv',get_saved_date_from_json()+'\\reestr_licenzii_' + get_saved_date_from_json() + '.csv',
         get_saved_date_from_json()+'\\reestr_lombardov_' + get_saved_date_from_json() + '.csv',
         get_saved_date_from_json() + "\\kol_char"+get_saved_date_from_json()+".csv",get_saved_date_from_json()+'\\fin_reestr_ССД' + get_saved_date_from_json() + '.csv',
         get_saved_date_from_json() + "\\fin_reestr_НПФ"+get_saved_date_from_json()+".csv",get_saved_date_from_json()+'\\fin_reestr_МФО' + get_saved_date_from_json() + '.csv',
         get_saved_date_from_json() + "\\fin_reestr_Ломбарды"+get_saved_date_from_json()+".csv",get_saved_date_from_json()+'\\fin_reestr_Исключенные ФО' + get_saved_date_from_json() + '.csv',
         get_saved_date_from_json() + "\\fin_reestr_КПК"+get_saved_date_from_json()+".csv",get_saved_date_from_json()+'\\fin_reestr_Кредитные организации' + get_saved_date_from_json() + '.csv']


#sending email

sender_email = "alexsa716151@mail.ru"
receiver_email = "alexsa7161@gmail.com"
message = MIMEMultipart()
message["From"] = sender_email
message['To'] = receiver_email
message['Subject'] = "report_files"
for f in files:
    attachment = open(f, 'rb')
    obj = MIMEBase('application', 'octet-stream')
    obj.set_payload((attachment).read())
    encoders.encode_base64(obj)
    obj.add_header('Content-Disposition', "attachment; filename= " + str(f).replace(get_saved_date_from_json(),'',1))
    message.attach(obj)
my_message = message.as_string()
email_session = smtplib.SMTP('smtp.mail.ru',587)
email_session.starttls()
email_session.login(sender_email,'6us2daX7HvhDaRDszzFh')
email_session.sendmail(sender_email,receiver_email,my_message)
email_session.quit()
print("Сообщение было отправлено")