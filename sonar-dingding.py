# coding=utf-8

import os
import time
import json
import jenkins
import requests
from requests.auth import HTTPDigestAuth

projectKey = os.getenv("JOB_NAME")

def sendding(url,content,title):
    pagrem = {
        "msgtype": "link",
        "link": {
            'title':title,
            "text": content,
            'messageUrl':'https://sonarqube.xxx.xxx/dashboard?id='+projectKey
        }
    }

    headers = {
        'Content-Type': 'application/json'
    }

    # 发送消息
    requests.post(url, data=json.dumps(pagrem), headers=headers)

def notification():
    webhook='https://oapi.dingtalk.com/robot/send?access_token=xxx'
    sonarurl='http://sonarqube.xxx.xxx/api/qualitygates/project_status?projectKey='+projectKey
    s = requests.Session()
    s.auth = ('user', 'pass')
    r = s.get(sonarurl)

    result = json.loads(r.text)
    print result
    coverage = 0

    for item in result['projectStatus']['conditions']:
        if item['metricKey']=="new_coverage":
            coverage = item['actualValue']
    code_reslut=  "coverage: " + coverage + "%"

    sendding(url=webhook, content=code_reslut, title=projectKey)


if __name__=="__main__":
    # 等待10秒,确保SonarQube刷新结果
    time.sleep(9)
    notification()