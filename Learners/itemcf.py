import pandas as pd
import random
import math
from operator import itemgetter

def getDatas(pivot=0.75):
    path = 'data/student_prediction.csv'
    data = pd.read_csv(path)

    students = data.iloc[:,0]
    labels = data.columns[1:-2]
    data = data.iloc[:, 1:-2]
    trainset, testset = {}, {}

    for row in range(data.shape[0]):
        for column in range(data.shape[1]):
            trainset.setdefault(students[row], {})
            testset.setdefault(students[row], {})
            if (random.random() < pivot):
                if data.iloc[row, column] >= 3:
                    data.iloc[row, column] = 1
                    trainset[students[row]][labels[column]] = 1
                else:
                    data.iloc[row, column] = 0
                    trainset[students[row]][labels[column]] = 0
            if (random.random() >= pivot):
                if data.iloc[row, column] >= 3:
                    data.iloc[row, column] = 1
                    testset[students[row]][labels[column]] = 1
                else:
                    data.iloc[row, column] = 0
                    testset[students[row]][labels[column]] = 0

    print('训练集、测试集划分成功!!!')
    return trainset,testset

# 计算课程之间的相似度
def clac_course_sim(trainset):
    course_popular = {}  # 课程观看次数
    course_count = {}  # 课程数量
    course_sim_matrix = {}
    for student, courses in trainset.items():
        for course in courses:
            if course not in course_popular:
                course_popular[course] = 0
            course_popular[course] += trainset[student][course]
    course_count = len(course_popular)
    # print('总计课程数量 = %d' % course_count)
    # print('course_popular:',course_popular)

    for student, courses in trainset.items():
        for c1 in courses:
            # 遍历该用户每件物品项
            for c2 in courses:
                if c1 == c2:
                    continue
                course_sim_matrix.setdefault(c1, {})
                course_sim_matrix[c1].setdefault(c2, 0)
                # 同一个用户，遍历到其他用户则加一
                if trainset[student][c1] == 1 & trainset[student][c2] == 1:
                    course_sim_matrix[c1][c2] += 1

    print('构建同现矩阵成功!')
    # print('course_sim_matrix_前:',course_sim_matrix)

    # 计算课程的相似度
    print('计算课程相似度...')

    for c1, related_courses in course_sim_matrix.items():
        for c2,count in related_courses.items():
            # 注意0向量的处理，即某电影的用户数为0
            if course_popular[c1] == 0 or course_popular[c2] == 0:
                course_sim_matrix[c1][c2] = 0
            else:
                course_sim_matrix[c1][c2] = count / math.sqrt(course_popular[c1] * course_popular[c2])
    print('计算相似度成功!')
    return course_sim_matrix
    # print('course_sim_matrix_后:',course_sim_matrix)

#学生未产生过行为的课程
def recommend(trainset,course_sim_matrix,student):
    K,N = 8,3   #相似课程，推荐课程数
    #学生student对课程的偏好值
    rank = {}
    #学生student产生过行为的课程，与课程item按照相似度从大到小排序，取与课程item相似度最大的K个物品
    courses_taken = {}
    for course, value in trainset[student].items():
        if value == 1:
            courses_taken[course] = value

    for course,value in courses_taken.items():
        #遍历与物品item最相似的前K个，获得这些物品以及相似分数
        for related_course,w in sorted(course_sim_matrix[course].items(),key=itemgetter(1),reverse=True)[:K]:
            if related_course in courses_taken:
                continue
            #计算user对related——course偏好值
            rank.setdefault(related_course,0)
            #通过与其相似物品对物品related——course的偏好值相乘并相加
            #排名的依据——>推荐课程与该课程的相似度（累计）*用户对自己上过课程的评分
            rank[related_course] += w*float(value)
    return sorted(rank.items(),key=itemgetter(1),reverse=True)[:N]

def evaluate(trainset,testset,course_count=30):
    print('正在计算中...')
    N=3
    #准确率和召回率
    hit = 0
    rec_count = 0
    test_count = 0
    #覆盖率
    all_rec_courses = set()
    for i,student in enumerate(trainset):
        test_courses = testset.get(student,{})
        rec_courses = recommend(trainset,course_sim_matrix,student)
        for course,w in rec_courses:
            if course in test_courses:
                hit += 1
            all_rec_courses.add(course)
        rec_count += N
        test_count += len(test_courses)

    precision = hit/(1.0*rec_count)
    recall = hit/(1.0*test_count)
    coverage = len(all_rec_courses)/(1.0*course_count)
    print('precision=%.4f\trecall=%.4f\tcoverage=%.4f'%(precision,recall,coverage))


trainset,testset = getDatas()
course_sim_matrix = clac_course_sim(trainset)
evaluate(trainset,testset)
print('trainset的STUDENT1：',trainset['STUDENT1'])

