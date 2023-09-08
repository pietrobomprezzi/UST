
import pandas as pd
import requests

#insert here the path to the dataset we want to check
filepath = 'C:/Users/pietr/Downloads/Ukraine_Support_Tracker_Release_13.xlsx'

df = pd.read_excel(filepath, sheet_name='Bilateral Assistance, MAIN DATA')

#for now checking only source 1
colchecklist = ['Source of Aid 1', 'Source of Aid 2', 'Source of Aid 3', 'Source of Aid 4']


def requester(string,identifier):
    #can play around with this
    headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Mobile Safari/537.36'}
    try:
        resp = requests.head(string,headers=headers, timeout=60)
        if resp.status_code < 400:
            output={'error':'no','id':identifier,'link':string}
        else:
            output={'error':'YES','id':identifier,'link':string}
            #to do: more detailed errors
    except requests.exceptions.RequestException:
        output={'error':'some other error','id':identifier,'link':string}
    return output

#------Start
#check
sources_by_date = df.groupby(['ID','Announcement Date'])['Source of Aid 1'].nunique()
#collapse at the ID-date level? not really a necessary thing but if correct would halve the time of the script
df.drop_duplicates(subset=['ID','Announcement Date'],keep='first',inplace=True)

#loopity-loop 
dict_list = [requester(i,x) for i,x in zip(df['Source of Aid 1'],df['ID'])]

finaldf = pd.DataFrame.from_dict(dict_list)

finaldf.to_excel('output/check_pdfs.xlsx')


#notes:
#australia seems to be problematic..probably server issues specific to the country? 

