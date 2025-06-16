import csv
import json
import requests

# 创建 CSV 文件并写入列名
with open('course_data.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
    writer = csv.writer(csvfile)
    fields = ['name', 'teacherName', 'schoolName', 'schoolSN', 'id', 'url']  # 只保留需要的字段
    writer.writerow(fields)

# 定义获取课程信息的 URL
twourl = "https://www.icourse163.org/web/j/mocSearchBean.searchCourseCardByChannelAndCategoryId.rpc?csrfKey=9ddd9641afce4905aa429bf754db5b1b"

# 请求头
headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Cache-Control": "no-cache",
    "Content-Length": "192",
    "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
    "Cookie": "NTESSTUDYSI=9ddd9641afce4905aa429bf754db5b1b; EDUWEBDEVICE=7a18a0d811e443da8466a956d9571abd; Hm_lvt_77dc9a9d49448cf5e629e5bebaa5500b=1714007316; __yadk_uid=lxVu0GBpcgHrjnjdBP4LXojZlFfwpS4n; WM_NI=4G7PWoEQ02m4%2BvueYIsLLEdVSrkmtq2QbnYz6oN0vU7DuVNiljn7xkLMqPibUCA0Y3KTw4e3PffcgFfwwieW1RRmO7vvCHyP7%2FfjlmJia7I03OR%2FMP0xMocc%2FWmx3lHnckU%3D; WM_NIKE=9ca17ae2e6ffcda170e2e6ee91e159a5adb6b5f162b1a88aa6d15f968b9e86d83eb0bc83dae67dbc8699a6db2af0fea7c3b92af899f9b1d665878f00d3f040e9aabb86dc43b19484a6e75e91aea58ef77bf28fae8fdc72f6b182d1f55ff59cbbb7cd63b0b6a2d8fb619093bfb1ec6a979d8fd1dc39898cb9d5e83994baaa84e64ea6a9b98ae85df38e9e8ece3db6aa8da9fc5cf5f1aa8bef678ab7afd8cc3cf1919ed0d05cf4a88390e269ed89a399b2688cb2ad8cd837e2a3; WM_TID=uZLSXz1D89ZBAUAUVQKFu0YZ91x1YWRD; Hm_lpvt_77dc9a9d49448cf5e629e5bebaa5500b=1714009886",
    "Edu-Script-Token": "9ddd9641afce4905aa429bf754db5b1b",
    "Origin": "https://www.icourse163.org",
    "Pragma": "no-cache",
    "Referer": "https://www.icourse163.org/channel/2001.htm?cate=-1&subCate=-1",
    "Sec-Ch-Ua": '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
    "Sec-Ch-Ua-Mobile": "?1",
    "Sec-Ch-Ua-Platform": "Android",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.289 Mobile Safari/537.36"
}

# 定义要爬取的课程类别 ID（计算机类别的 ID）
categoryChannelId = 3002  # 计算机类别的 ID
pageIndex = 1  # 当前页码
categoryId = -1  # 未知参数，固定为 -1
num = 0
# 循环爬取课程信息
while True:
    # 设置请求参数
    data = {
        "mocCourseQueryVo": '{categoryId:' + str(categoryId) + ',categoryChannelId:' + str(categoryChannelId) + ','
                             'orderBy:0,stats:30,pageIndex:' + str(pageIndex) + ',pageSize:20,shouldConcatData:true}'
    }

    try:
        # 发送请求
        response = requests.post(twourl, data=data, headers=headers)
        response.raise_for_status()  # 检查请求是否成功
        parsed_course_data = json.loads(response.text)

        # 遍历课程数据
        for item in parsed_course_data['result']['list']:
            course = item.get('mocCourseBaseCardVo')
            if course:
                # 只获取需要的字段
                name = course.get('name', '')
                teacherName = course.get('teacherName', '')
                schoolName = course.get('schoolName', '')
                schoolSN = course.get('schoolSN', '')
                id = course.get('id', '')
                url = f"https://www.icourse163.org/course/{schoolSN}-{id}"
                num += 1
                # 写入 CSV 文件
                with open('course_data.csv', 'a', newline='', encoding='utf-8-sig') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow([name, teacherName, schoolName, schoolSN, id, url])
                    # 打印写入的数据
                    print(f"{num} name: {name}, teacherName: {teacherName}, schoolName: {schoolName}, schoolSN:{schoolSN}, id:{id}, url:{url}")

        # 检查是否还有下一页
        if pageIndex >= parsed_course_data["result"]["query"]["totlePageCount"]:
            break
        pageIndex += 1  # 翻页

    except Exception as e:
        print(f"请求失败: {e}")
        break

print("爬取结束")