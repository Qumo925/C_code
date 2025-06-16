from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import csv
import time
import os

def setup_driver():
    """配置并启动 Chrome 浏览器"""
    chrome_opt = webdriver.ChromeOptions()
    chrome_opt.binary_location = "D:\\Chrome\\chrome-win64\\chrome.exe"
    return webdriver.Chrome(options=chrome_opt)

def extract_outline(driver):
    """提取课程大纲内容"""
    outline_body = driver.find_element(by=By.CSS_SELECTOR, value=".outlineBody")
    paragraphs = outline_body.find_elements(by=By.TAG_NAME, value="p")
    # 定义需要过滤的关键词
    exclude_keywords = ["测试", "测验", "作业", "参考资料", "讨论", "本讲", "总结"]
    outline = []
    for p in paragraphs:
        spans = p.find_elements(by=By.TAG_NAME, value="span")
        if spans:
            # 提取所有 <span> 的文本内容，去重并拼接
            text = " ".join(dict.fromkeys(span.text.strip() for span in spans if span.text.strip()))
            # 过滤包含关键词的条目
            if text and not any(keyword in text for keyword in exclude_keywords):
                outline.append(text)
    return outline

    # # 如果方法1没提取到内容，尝试方法2
    # if not outline:
    #     try:
    #         chapters = driver.find_elements(By.CSS_SELECTOR, ".chapterName")
    #         outline = list(dict.fromkeys(
    #             chapter.text.strip()
    #             for chapter in chapters
    #             if chapter.text.strip()
    #         ))
    #         print("使用.chapterName选择器提取大纲")
    #     except Exception as e:
    #         print(f"方法2提取大纲时出错: {e}")

    return outline if outline else ["未提取到大纲内容"]

def extract_course_name(driver):
    """提取课程名称"""
    try:
        course_name_element = driver.find_element(By.XPATH, '//*[@id="g-body"]/div[1]/div[1]/div[1]/div[1]/div[2]/div[2]/div[1]/div[2]/div[1]/span[1]')
        return course_name_element.text.strip()
    except Exception as e:
        print(f"提取课程名称时出错: {e}")
        return "未知课程名称"

def save_to_csv(data, filename):
    """将数据保存到 CSV 文件"""
    # 检查文件是否存在，如果不存在则写入表头
    file_exists = os.path.isfile(filename)
    with open(filename, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["name", "outline"])  # 写入表头
        writer.writerow(data)  # 写入数据

def main():
    driver = setup_driver()
    num = 0
    try:
        # 读取 course_data.csv 文件
        with open("course_data.csv", "r", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            course_data = list(reader)

        # 遍历每个课程的 URL
        for course in course_data:
            num += 1
            url = course["url"]
            print(f"正在处理课程: {url}")
            driver.get(url)

            # 尝试查找并点击"展开全部"按钮（如果存在）
            try:
                expand_button = driver.find_element(By.CSS_SELECTOR, ".fold")
                expand_button.click()
            except NoSuchElementException:
                print("未找到'展开全部'按钮，继续执行")

            # 提取课程名称
            course_name = extract_course_name(driver)
            # 提取课程大纲
            course_outline = extract_outline(driver)
            # 将课程名称和大纲内容保存到 CSV 文件
            save_to_csv([course_name, "".join(course_outline)], "course_outlines.csv")
            print(f"{num}:{course_name} 大纲已保存完毕")

    finally:
        # 关闭浏览器
        time.sleep(5)
        driver.quit()

if __name__ == "__main__":
    main()