# coding=utf-8

import os
import re
import time
import json
import jenkins
import requests
import xml.etree.ElementTree as ET
import commands

projectKey = os.getenv("SERVICE")
#projectKey = 'wisdomclass-interaction'

def sendding_link(url,content,title):
    pagrem = {
        "msgtype": "link",
        "link": {
            'title':title,
            "text": content,
            'messageUrl':'https://sonarqube.xxx.xxx/dashboard?id=zhkt.wisdomclass.'+projectKey
        }
    }

    headers = {
        'Content-Type': 'application/json'
    }

    # 发送消息
    requests.post(url, data=json.dumps(pagrem), headers=headers)

def sendding_text(url,content):
    pagrem = {
        "msgtype": "text",
        "text": {
            "content": content,
        }
    }

    headers = {
        'Content-Type': 'application/json'
    }

    # 发送消息
    requests.post(url, data=json.dumps(pagrem), headers=headers)


def notification():
    webhook='https://oapi.dingtalk.com/robot/send?access_token=xxx'
    jacoco_report = '/var/lib/jenkins/workspace/job_name/' + projectKey + '/target/jacoco-ut/jacoco.xml'
    jacoco_list = []
    jacoco_dict = {}

    tree = ET.parse(jacoco_report)
    root = tree.getroot()
    for child in root:
        if child.tag == 'counter':
            jacoco_list.append(child.attrib)
    
    for item in jacoco_list:
        jacoco_dict[item['type']] = str(float(item['covered'])/(float(item['covered'])+float(item['missed']))*100)+'%'

    
    surefire_report_all = 'cd /var/lib/jenkins/workspace/job_name/' + projectKey + '/target/surefire-reports/; cat cn.susoncloud.wisdomclass.*.txt > cn.susoncloud.wisdomclass.all'
    surefire_report = '/var/lib/jenkins/workspace/job_name/' + projectKey + '/target/surefire-reports/cn.susoncloud.wisdomclass.all'
    surefire_dict = {'Tests run': 0, 'Skipped': 0, 'Failures': 0, 'Errors': 0}
    commands.getoutput(surefire_report_all)

    f = open(surefire_report)
    for line in f.readlines():                          #依次读取每行
        if line.startswith('Tests run'):       #判断是否是空行或注释行
            for surefire in line.split(','):
                if surefire.startswith(' Time elapsed'):
                    continue
                surefire_dict[surefire.split(':')[0].strip()] = surefire_dict[surefire.split(':')[0].strip()] + int(surefire.split(':')[1])
    f.close()
    reslut = "LINE: " + jacoco_dict['LINE'] + "\nBRANCH: " + jacoco_dict['BRANCH'] + "\nTests run: " + str(surefire_dict['Tests run']) + ", Skipped: " + str(surefire_dict['Skipped']) +", Failures: " + str(surefire_dict['Failures']) + ", Errors: " + str(surefire_dict['Errors'])
    #print reslut

    sendding_link(url=webhook, content=reslut, title=projectKey)

    if surefire_dict['Skipped'] > 0 or surefire_dict['Failures'] > 0 or surefire_dict['Errors'] > 0:
        f = open(surefire_report)
        sendding_text(url=webhook, content=f.read())
        f.close()


if __name__=="__main__":
    notification()

