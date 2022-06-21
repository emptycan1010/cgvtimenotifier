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


def nextdate(num):
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
            + "&fst=&fet=&fsrc="
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


def makelib(res, l):
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
                    + "[시간표 변경]\n"
                    + text
                    + " --> "
                    + "\n"
                    + txt,
                )
                print(library)
                library[nextdate(l)] = result
        except:
            library[nextdate(l)] = []
    time.sleep(5)
