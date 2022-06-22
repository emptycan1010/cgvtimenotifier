from xmlrpc.client import ResponseError
import requests
import telepot
import json
from datetime import date, timedelta
import time

tel = telepot.Bot("Token")
s = requests.session()
chann = ChatID
s.get(
    "https://m.cgv.co.kr/WebApp/Reservation/schedule.aspx?tc=0013&rc=01&ymd=20220624&fst=&fet=&fsrc="
)


def nextdate(num: int):
    text = (date.today() + timedelta(num)).strftime("%Y%m%d")
    return text


def makeurl(date: int):
    jsjs = {
        "strRequestType": "THEATER",
        "strUserID": "",
        "strMovieGroupCd": "",
        "strMovieTypeCd": "",
        "strPlayYMD": nextdate(date),
        "strTheaterCd": "0013",
        "strScreenTypeCd": "",
        "strRankType": "MOVIE",
    }
    return jsjs


def gettimetable(s: requests.Session, date: int):
    res = s.post(
        "https://m.cgv.co.kr/WebAPP/Reservation/Common/ajaxTheaterScheduleList.aspx/GetTheaterScheduleList",
        json=makeurl(date),
        headers={
            "Referer": "https://m.cgv.co.kr/WebApp/Reservation/schedule.aspx?tc=0013&rc=01&ymd="
            + nextdate(date)
            + "&fst=&fet=&fsrc=",
            "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Mobile Safari/537.36",
            "Accept-Language": "ko-KR,ko;q=0.9,ja-JP;q=0.8,ja;q=0.7,en-US;q=0.6,en;q=0.5",
            "X-Requested-With": "XMLHttpRequest",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Origin": "https://m.cgv.co.kr",
            "sec-ch-ua": '"Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
            "sec-ch-ua-platform": '"Android"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "sec-gpc": "1",
            "Host": "m.cgv.co.kr",
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "Content-Length": "173",
        },
    )
    return res


def loadtojson(res):
    try:
        res = res.text.replace("\\", "")[6 : len(res.text) - 2].replace(
            '"}]}}"}', '"}]}}'
        )
        res = json.loads(res)
    except:
        pass
    return res


def makelib(res: requests.Response, l: int):
    return [
        res["ResultSchedule"]["ScheduleList"][l]["MovieAttrNm"],
        res["ResultSchedule"]["ScheduleList"][l]["MovieNmKor"],
        res["ResultSchedule"]["ScheduleList"][l]["PlayStartTm"][:2]
        + ":"
        + res["ResultSchedule"]["ScheduleList"][l]["PlayStartTm"][2:]
        + " ~ "
        + res["ResultSchedule"]["ScheduleList"][l]["PlayEndTm"][:2]
        + ":"
        + res["ResultSchedule"]["ScheduleList"][l]["PlayEndTm"][2:],
    ]


library = {}
for i in range(1, 31):
    res = loadtojson(gettimetable(s, i))
    result = []
    try:
        for l in range(len(res["ResultSchedule"]["ScheduleList"])):
            if "IMAX" in res["ResultSchedule"]["ScheduleList"][l]["MovieAttrNm"]:
                result.append(makelib(res, l))
    except:
        pass
    library[nextdate(i)] = result
print(library)
print("Initialize Complete")
while True:
    for l in range(1, 31):
        # time.sleep(0.5)
        res = loadtojson(gettimetable(s, l))
        result = []
        txt = ""
        try:
            for i in range(len(res["ResultSchedule"]["ScheduleList"])):
                if "IMAX" in res["ResultSchedule"]["ScheduleList"][i]["MovieAttrNm"]:
                    result.append(makelib(res, i))
        except:
            pass

        try:
            if len(result) != len(library[nextdate(l)]):
                print(result)
                text = ""
                txt = ""
                for i in range(len(result)):
                    txt = (
                        txt
                        + result[i][0]
                        + " "
                        + result[i][1]
                        + "\n"
                        + result[i][2]
                        + "\n"
                    )
                for i in range(len(library[nextdate(l)])):
                    text = (
                        text
                        + library[nextdate(l)][i][0]
                        + " "
                        + library[nextdate(l)][i][1]
                        + "\n"
                        + library[nextdate(l)][i][2]
                        + "\n"
                    )
                tel.sendMessage(
                    chann,
                    nextdate(l)[:4]
                    + "년 "
                    + nextdate(l)[4:6]
                    + "월 "
                    + nextdate(l)[6:]
                    + "일\n"
                    + text
                    + "\n"
                    + txt,
                )
                print(library)
                library[nextdate(l)] = result
        except:
            library[nextdate(l)] = []
    time.sleep(5)
