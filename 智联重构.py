import requests
from bs4 import BeautifulSoup
import csv
import pandas as pd
import re
import time
import random

cityId=538#城市代码，538为上海，489为全国，北京为530
pageSize=60#数量
industry=10100#行业代码，https://fe-api.zhaopin.com/c/i/sou/base-data?CityId=489&init=false，访问这个接口可以看行业代码
page=0#起始页
end=100#终止页面，接口一共提供了上亿条数据，根据需求选择
start=0#起始数据
kw='c'#搜索关键字
jobName=[]#标题
positionURL=[]#链接
company=[]#公司
workingExp=[]#工作经验
city=[]#城市
salary=[]#薪资
sameitem=0#重复条目

headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
}

def getHtmlJson(url):
    try:
        r=requests.get(url,headers=headers)
        r.raise_for_status()
        r.encoding=r.apparent_encoding
        return r.json()
    except:
        return 'error'

def getData():
    global page,start,sameitem
    while  True:
        start=page*60
        try:
            url = 'https://fe-api.zhaopin.com/c/i/sou?start=' + str(start) + '&pageSize=' + str(pageSize) + '&cityId=' + str(
                cityId) + '&industry=' + str(
                industry) + '&workExperience=-1&education=-1&companyType=-1&employmentType=-1&jobWelfareTag=-1&kw=' + kw + '&kt=3'

            result=getHtmlJson(url)
            date=result['data']['results']
            if len(result['data']['results']) == 0 or page==end:
                break
            print('getting page %d' % (page + 1))
            for i in date:
                if i['jobName'] in jobName and i['company']['name']in company:#过滤重复
                    sameitem+=1
                    continue

                jobName.append(i['jobName'])
                company.append(i['company']['name'])
                positionURL.append(i['positionURL'])
                workingExp.append(i['workingExp']['name'])
                salary.append(i['salary'].replace('K','000'))
                city.append(i['city']['display'])

            page+=1
            #time.sleep(2*random.random())
            if page>1:
                if page%50==0:
                    time.sleep(100*random.random())
        except:
            print('hold process')
            time.sleep(600)
            continue

def calculateAver():#平均工资计算函数，可注释掉
    global salaryPer,salaryTotal
    salaryPer=0
    salaryTotal=0
    for i in salary:
        if '.' in i:
            each = re.findall(r'[0-9]+', i)
            each1 = each[0] + each[1][:3]
            if len(each)==3:
                each2=each[2]
            else:
                each2 = each[2] + each[3][:3]
            salaryPer=(int(each1)+int(each2))/2
            continue

        each=re.findall(r'[0-9]+',i)
        try:
            if len(each)==2:
                salaryPer=(int(each[0])+int(each[1]))/2
            if len(each)==1:
                continue
            else:
                salaryPer=10000
        except:
            print(each)
            break

        salaryTotal=salaryPer+salaryTotal

    return salaryTotal


if __name__ == '__main__':
    getData()
    calculateAver()
    print(len(jobName))
    print('重复条目有：%d'%sameitem)
    salaryAverage=salaryTotal/len(salary)
    print('平均工资为：%f'%salaryAverage)
    #
    #字典中的key值即为csv中列名
    dataframe = pd.DataFrame({'标题':jobName,'地址':city,'工资':salary,'公司':company,'工作经验':workingExp,'链接':positionURL})
    # #将DataFrame存储为csv,index表示是否显示行名，default=True
    dataframe.to_csv("jobinfo.csv",index=False,sep=',')
