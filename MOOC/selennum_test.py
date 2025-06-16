from selenium import webdriver
from selenium.webdriver.common.by import By
import csv
import time

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

def extract_course_name(driver):
    """提取课程名称"""
    course_name_element = driver.find_element(by=By.XPATH, value='//*[@id="g-body"]/div[1]/div[1]/div[1]/div[1]/div[2]/div[2]/div[1]/div[2]/div[1]/span[1]')
    return course_name_element.text.strip()

def save_to_csv(name, outline, filename):
    """将数据保存到 CSV 文件"""
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "outline"])  # 写入表头
        # 将所有大纲项用空格拼接成一个字符串
        outline_str = " ".join(outline)
        writer.writerow([name, outline_str])  # 写入数据

def main():
    driver = setup_driver()
    try:
        schoolSN = 'WHU'
        id = '1002332010'
        driver.get(f'https://www.icourse163.org/course/{schoolSN}-{id}')
        # 定位并点击 "展开全部" 按钮
        expand_button = driver.find_element(by=By.CSS_SELECTOR, value=".fold")  # 根据实际 HTML 结构调整选择器
        expand_button.click()
        # 提取课程名称
        course_name = extract_course_name(driver)
        # 提取课程大纲
        course_outline = extract_outline(driver)
        # 保存到 CSV 文件
        save_to_csv(name=course_name, outline=course_outline, filename="course_outline_test.csv")
        print(f"{course_name} 信息已保存完毕")
    finally:
        time.sleep(5)  # 等待 5 秒，观察结果
        driver.quit()

if __name__ == "__main__":
    main()