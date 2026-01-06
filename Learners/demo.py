import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
from opencc import OpenCC
import numpy as np
import math

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

    def User_Exercise_Matrix(self,exercise_names):
        df = pd.read_csv(self.path_2, encoding=self.encoding, nrows=self.nrows)
        user_exercise_matrix = pd.pivot_table( df,
            values='points_earned',
            index='user_id',
            columns='exercise',
            fill_value=0
        )
        user_exercise_matrix.columns = [exercise_names[col] for col in user_exercise_matrix.columns]  #替换exercise语言,英->中
        transposed_matrix = user_exercise_matrix.T    #转置矩阵
        item_similarity_matrix = cosine_similarity(transposed_matrix)  # 计算项目之间的余弦相似度
        user_similarity_matrix = cosine_similarity(user_exercise_matrix)  # 计算用户之间的余弦相似度
        # 将相似度矩阵转换为DataFrame，方便查看和使用
        item_similarity = pd.DataFrame(item_similarity_matrix, index=transposed_matrix.index,
                                     columns=transposed_matrix.index)
        user_similarity = pd.DataFrame(user_similarity_matrix, index=user_exercise_matrix.index,
                                       columns=user_exercise_matrix.index)
        return user_exercise_matrix, item_similarity, user_similarity

    def Item_Recommendation(self, user_id, item_similarity, user_exercise_matrix, num=5):
        if user_id not in user_exercise_matrix.index:
            return f"没有找到这个用户: {user_id}"
        user_ratings = user_exercise_matrix.loc[user_id]
        existing_ratings = user_ratings[user_ratings.ne(0)].index.tolist()  #使用布尔索引找到非零评分的索引,转换为整数列表
        scores = item_similarity.dot(user_ratings.values.reshape(-1, 1))
        # 将已经交互过的项目设为0，不推荐
        if not scores.empty:
            # 将用户已经评分的项目名称转换为scores的索引
            existing_ratings_index = [user_exercise_matrix.columns.get_loc(exercise) for exercise in existing_ratings]
            scores.iloc[existing_ratings_index] = 0
            item_recommendations = scores.sort_values(by=scores.columns[0], ascending=False).head(num).index
        else:
            item_recommendations = []
        return existing_ratings,item_recommendations.tolist()  # 返回列表形式的推荐结果

    def User_Recommendation(self, user_id, user_similarity, user_exercise_matrix, num=5):
        if user_id not in user_exercise_matrix.index:
            return f"没有找到这个用户: {user_id}"
        user_ratings = user_exercise_matrix.loc[user_id]
        existing_ratings = user_ratings[user_ratings.ne(0)].index.tolist()
        n = len(existing_ratings)
        scores_dict = {}  # 使用字典来累积评分

        user_index = user_exercise_matrix.index.get_loc(user_id)     #用户的索引位置
        user_similarity_scores = user_similarity.iloc[user_index]
        # 将当前用户相似度设为0，不推荐
        user_similarity_scores.loc[user_id] = 0
        # 获取相似用户的索引
        similar_users = user_similarity_scores.sort_values(ascending=False).head(15).index
        for sim in similar_users:
            user_ratings = user_exercise_matrix.loc[sim]
            existing_ratings = user_ratings[user_ratings.ne(0)]  # 非零评分的项目
            for exercise, rating in existing_ratings.items():
                if exercise not in scores_dict:
                    scores_dict[exercise] = rating
                else:
                    scores_dict[exercise] += rating  # 累加相似用户的评分
        # 将字典转换为Series并排序
        scores = pd.Series(scores_dict)
        user_recommendations = scores.sort_values(ascending=False).head(num+n).index[n:].tolist()
        return user_recommendations

    def SVD_Recommendation(self, user_id, user_exercise_matrix, num=5):
        user_exercise_matrix_np = user_exercise_matrix.values
        svd = TruncatedSVD(n_components=user_exercise_matrix.shape[1])
        # 分解用户-项目矩阵
        svd.fit(user_exercise_matrix_np)
        if user_id not in user_exercise_matrix.index:
            return f"没有找到这个用户: {user_id}"
        else:
            # 获取目标用户的交互向量
            user_ratings = user_exercise_matrix.loc[user_id].values
            # 使用 SVD 模型进行预测
            user_ratings_pred = svd.transform(user_ratings.reshape(1, -1))
            # 获取预测评分最高的项目索引
            top_indices = np.argsort(-user_ratings_pred[0])
            # 返回推荐的项目索引
        return list(user_exercise_matrix.columns[top_indices[:num]])

if __name__ == '__main__':
    data = Get_data()
    user_id = 247372
    exercise_names = data.Get_Exercise_Name()
    user_exercise_matrix,item_similarity,user_similarity= data.User_Exercise_Matrix(exercise_names)   #用户交互矩阵、项目相似度矩阵、用户相似度矩阵
    print('用户id序列：',user_exercise_matrix.index)
    exercise_history,item_recommendations = data.Item_Recommendation(user_id, item_similarity, user_exercise_matrix)
    print('用户曾经交互记录：',exercise_history)
    print('项目协同过滤推荐结果:', item_recommendations)
    user_recommendations = data.User_Recommendation(user_id, user_similarity, user_exercise_matrix)
    print('用户协同过滤推荐结果:', user_recommendations)
    svd_recommendations = data.SVD_Recommendation(user_id, user_exercise_matrix)
    print('模型协同过滤推荐结果:', svd_recommendations)

