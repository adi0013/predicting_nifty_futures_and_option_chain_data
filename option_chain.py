import time
from datetime import date
from datetime import datetime
import requests
import json
import pandas as pd
import pymysql
from sqlalchemy import create_engine
from configparser import ConfigParser
import os

z=1
dfs={}

x=1
y=1
c=1


url = 'https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY'

headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'}

response = requests.get(url, headers=headers)



response_text_p = response.text

json_object_p = json.loads(response_text_p)


e_date_p = json_object_p['records']['expiryDates']

for i in range(len(e_date_p)):
    exp = e_date_p[i]
    today = date.today()
    folder_path = f'C:/xampp/htdocs/Internship_Code/Storage/Excel/{exp}/{today}'
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    else:
        print(f"Folder '{today}' already exists.")
    
    
    y2=str(y)
    gr_name='Hour'+y2

    config = ConfigParser()
    config.read("config.ini")
    dexcel = config.get('Paths','excelpath')
    efile = f'{exp}/{today}/{gr_name}.xlsx'
    file_epath = os.path.join(dexcel,efile)
    with pd.ExcelWriter(file_epath) as writer:




        for y in range(1,7):
        
            for z in range(1,21):

                z2=str(z)
                sh_name='Sheet'+z2
                #gr_name='Group'+z2

                try:
                    url = 'https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY'

                    headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'}

                    response = requests.get(url, headers=headers)



                    response_text = response.text

                    json_object = json.loads(response_text)

                    with open("Options.json","w") as outfile:
                        outfile.write(response_text)

                    e_date = json_object['records']['expiryDates']

                    oc_data = {}
                    data = json_object['records']['data']
                    for ed in e_date:
                        oc_data[ed]={"CE":[],"PE":[]}
                        for di in range(len(data)):
                            if data[di]['expiryDate']==ed:
                                if 'CE' in data[di].keys() and data[di]['CE']['expiryDate']==ed:
                                    oc_data[ed]['CE'].append(data[di]['CE'])
                                else:
                                    oc_data[ed]['CE'].append("-")
                                if 'PE' in data[di].keys() and data[di]['PE']['expiryDate']==ed:
                                    oc_data[ed]['PE'].append(data[di]['PE'])
                                else:
                                    oc_data[ed]['PE'].append("-")

                    #to delete extra keys from the table
                    for k in oc_data.keys():
                        for i in range(len(oc_data[k]['CE'])):
                            if oc_data[k]['CE'][i] != '-':
                                del oc_data[k]['CE'][i]["expiryDate"]
                                del oc_data[k]['CE'][i]["underlying"]
                                del oc_data[k]['CE'][i]["identifier"]
                            
                            if oc_data[k]['PE'][i] != '-':
                                del oc_data[k]['PE'][i]["expiryDate"]
                                del oc_data[k]['PE'][i]["underlying"]
                                del oc_data[k]['PE'][i]["identifier"]

                    
                    l_oc = []

                    p = datetime.now()
                    

                    for j in range(len(e_date)):
                        
                        expiry_date = e_date[j]
                        keys_to_exclude = [
                        'pchangeinOpenInterest',
                        'totalBuyQuantity',
                        'totalSellQuantity',
                        'underlyingValue',
                        'pChange'
                        
                        ]
                        
                        oc_data_dt = oc_data[expiry_date]
                        CE = list(oc_data_dt['CE'])
                        PE = list(oc_data_dt['PE'])

                        for i in range(len(CE)):
                            if CE[i]!='-':
                                for key in keys_to_exclude:
                                    del CE[i][key]
                            if PE[i]!='-':
                                for key in keys_to_exclude:
                                    del PE[i][key]

                        def set_decimal(x):
                            return('%.2f' % x).rstrip('0').rstrip('.')
                        
                        

                        
                        seq = 0
                        for i in range(len(CE)):
                            l_ce=[]
                            l_pe=[]
                            seq = seq + 1
                    
                            if CE[i]!='-':
                                sp = CE[i]['strikePrice']
                                l_ce = [
                                    e_date[j],
                                    seq,
                                    CE[i]['openInterest'],
                                    CE[i]['changeinOpenInterest'],
                                    CE[i]['totalTradedVolume'],
                                    CE[i]['impliedVolatility'],
                                    CE[i]['lastPrice'],
                                    set_decimal(CE[i]['change']),
                                    CE[i]['bidQty'],
                                    CE[i]['bidprice'],
                                    CE[i]['askPrice'],
                                    CE[i]['askQty'],
                                    sp
                                    ]
                            else:
                                l_ce = list([e_date[j],seq,'-','-','-','-','-','-','-','-','-','-',sp])
                                
                            if PE[i]!='-':
                                l_pe = [
                                    PE[i]['bidQty'],
                                    PE[i]['bidprice'],
                                    PE[i]['askPrice'],
                                    PE[i]['askQty'],
                                    set_decimal(PE[i]['change']),
                                    PE[i]['lastPrice'],
                                    PE[i]['impliedVolatility'],
                                    PE[i]['totalTradedVolume'],
                                    PE[i]['changeinOpenInterest'],
                                    PE[i]['openInterest'],
                                    p
                                    
                                    
                        
                                ]
                            else:
                                l_pe = list(['-','-','-','-','-','-','-','-','-','-',p])
                    
                            l_oc_t = l_ce + l_pe
                            l_oc_t[:] = [x if x != 0 else 0 for x in l_oc_t]
                            l_oc.append(l_oc_t)
                            

                    oc_col = ['expiry','sequence','c_OI','c_chng_OI','c_volume','c_iv','c_ltp','c_chng','c_bid_Qty','c_bid','c_ask','c_ask_Qty','strike','p_bid_Qty','p_bid','p_ask','p_ask_Qty','p_chng','p_ltp','p_iv','p_volume','p_chng_OI','p-OI','current']
                    ex_col = ['expiry']
                    pd.set_option('display.max_rows',None)
                    df = pd.DataFrame(l_oc)
                    df.columns = oc_col
                    df2 = pd.DataFrame(e_date)
                    df2.columns = ex_col

                    dcon = config.get('engineobj','enginepath')
                    
                    engine = create_engine(dcon)
                    df.to_sql('option_chain',engine,if_exists='replace',index=False)
                    df.to_sql('option_storage',engine,if_exists='append',index =False)
                    df2.to_sql('expiry_date',engine,if_exists='replace',index =False)
                    
                    time.sleep(10)
                    print("Excecuted")
                    
                    dfs[z]=df

                    t = time.localtime()
                    current_time = time.strftime("%H:%M:%S", t)
                    sheet_name = f'Sheet {current_time}'
                    invalid_chars = "/\?*[]:"
                    for char in invalid_chars:
                        sheet_name = sheet_name.replace(char, "_")

                    # truncate the sheet name if it exceeds 31 characters
                    sheet_name = sheet_name[:31]
                    
                    #with pd.ExcelWriter("C:\\Users\\dell\\OneDrive\\Desktop\\temp5.xlsx") as writer:
                    df.to_excel(writer,sheet_name=sheet_name,index=False)

                    c2=str(c)
                    jr_name=f'json {current_time}'

                    for char in invalid_chars:
                        jr_name = jr_name.replace(char, "_")

                    # truncate the sheet name if it exceeds 31 characters
                    jr_name = jr_name[:31]

                    folder_path2 = f'C:/xampp/htdocs/Internship_Code/Storage/Json/{today}'
                    if not os.path.exists(folder_path2):
                        os.makedirs(folder_path2)

                    djson = config.get('Paths','jsonpath')
                    jfile = f'{today}/{jr_name}.json'
                    file_jpath=os.path.join(djson,jfile)

                    df.to_json(file_jpath)
                
                    print(z)
                    z=z+1
                    c=c+1
                    

                except:
                    print("problem with script or manual exit")


            

    
