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
    """提取课程大纲内容 - 只提取章节名称"""
    try:
        # 查找所有章节元素
        chapters = driver.find_elements(By.CSS_SELECTOR, ".chapterName")
        # 提取章节文本并去重
        outline = list(dict.fromkeys(chapter.text.strip() for chapter in chapters if chapter.text.strip()))
        return outline
    except Exception as e:
        print(f"提取大纲时出错: {e}")
        return []


def extract_course_name(driver):
    """提取课程名称"""
    course_name_element = driver.find_element(by=By.XPATH, value='//*[@id="g-body"]/div[1]/div[1]/div[1]/div[1]/div[2]/div[2]/div[1]/div[2]/div[1]/span[1]')
    return course_name_element.text.strip()

def save_to_csv(name, outline, filename):
    """将数据保存到 CSV 文件"""
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "outline"])  # 写入表头
        # 将所有章节用空格拼接成一个字符串
        outline_str = " ".join(outline)
        writer.writerow([name, outline_str])  # 写入数据


def main():
    driver = setup_driver()
    try:
        schoolSN = 'NENU'
        id = '1207124814'
        driver.get(f'https://www.icourse163.org/course/{schoolSN}-{id}')
        # 定位并点击 "展开全部" 按钮
        expand_button = driver.find_element(by=By.CSS_SELECTOR, value=".fold")  # 根据实际 HTML 结构调整选择器
        expand_button.click()
        # 提取课程名称
        course_name = extract_course_name(driver)
        print(f"课程名称: {course_name}")
        # 提取课程大纲（章节名称）
        course_outline = extract_outline(driver)
        print(f"提取到章节: {course_outline}")
        # 保存到 CSV 文件
        save_to_csv(name=course_name, outline=course_outline, filename="course_outline_test.csv")
        print(f"{course_name} 信息已保存完毕")

    except Exception as e:
        print(f"程序运行出错: {e}")
    finally:
        time.sleep(5)  # 等待 5 秒，观察结果
        driver.quit()


if __name__ == "__main__":
    main()