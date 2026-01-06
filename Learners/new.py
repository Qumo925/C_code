import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
from opencc import OpenCC
import numpy as np
import matplotlib.pyplot as plt

class Get_data:
    def __init__(self):
        self.path_1 = 'junyi/junyi_Exercise_table.csv'               #课程数据
        self.path_2 = 'junyi/junyi_ProblemLog_original.csv'          #用户交互数据
        self.encoding = 'UTF-8-SIG'
        self.nrows = 50000

    def Get_Exercise_Name(self):
        df = pd.read_csv(self.path_1,encoding=self.encoding)
        exercise_name = {}
        cc = OpenCC('t2s')    #繁体->简体
        for row in df.values:
            exercise_name[row[0]] = cc.convert(row[-3])
        exercise_name["parabola_intuition_1"] = "抛物线直觉 1"
        return exercise_name

    def Get_Problemlog(self,exercise_names):
        df = pd.read_csv(self.path_2,encoding=self.encoding,nrows=self.nrows)
        user_log = {}
        # print(df.values)
        for row in df.values:
            if row[0] in user_log:
                user_log[row[0]].add(exercise_names[row[1]])
            else:
                user_log[row[0]] = {exercise_names[row[1]]}
        return user_log

    def topic_mode(self):
        df = pd.read_csv(self.path_2, encoding=self.encoding,nrows=self.nrows)
        points_earned = df['points_earned'].tolist()
        bins = [0 , 75 , 120 , 160 , 200 , 225]
        labels = ['不及格' , '及格' , '中' , '良' , '优']
        "0-75 75-120 120-160 160-200 200-225"
        hist, _ = np.histogram(points_earned, bins=bins)
        plt.figure(figsize=(8, 8))
        plt.pie(hist, labels=labels, autopct='%1.1f%%')
        plt.title('Points Earned Distribution')
        plt.show()

if __name__ == '__main__':
    data = Get_data()
    exercise_names = data.Get_Exercise_Name()
    user_log = data.Get_Problemlog(exercise_names)
    data.topic_mode()

