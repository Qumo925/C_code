import csv

def merge_files(course_outlines_file, course_data_file, output_file):
    # 读取 course_outlines.csv 文件
    with open(course_outlines_file, "r", encoding="utf-8") as f:
        outlines_reader = csv.reader(f)
        outlines_data = list(outlines_reader)  # 读取所有行

    # 读取 course_data.csv 文件
    with open(course_data_file, "r", encoding="utf-8") as f:
        data_reader = csv.reader(f)
        data_data = list(data_reader)  # 读取所有行

    # 确保两个文件的行数一致
    if len(outlines_data) != len(data_data):
        print("错误：两个文件的行数不一致！")
        return

    # 合并数据
    merged_data = []
    empty_outline_count = 0  # 统计 outline 列为空的数量
    for i in range(len(data_data)):
        # 跳过表头行
        if i == 0:
            merged_data.append(["name", "teacherName", "schoolName", "outline"])  # 新的表头
            continue
        # 合并每一行，只保留需要的列
        outline = outlines_data[i][1]  # 获取 outline 列
        if not outline:  # 如果 outline 为空
            empty_outline_count += 1
        merged_data.append([
            data_data[i][0],  # name
            data_data[i][1],  # teacherName
            data_data[i][2],  # schoolName
            outline  # outline
        ])

    # 保存合并后的数据到 data_final.csv 文件
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(merged_data)

    print(f"合并后的数据已保存到 {output_file} 文件中")
    print(f"outline 列为空的数量: {empty_outline_count}")

if __name__ == "__main__":
    # 文件路径
    course_outlines_file = "course_outlines.csv"
    course_data_file = "course_data.csv"
    output_file = "data_final.csv"

    # 合并文件
    merge_files(course_outlines_file, course_data_file, output_file)