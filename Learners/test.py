import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
from opencc import OpenCC
import numpy as np

def Normalize(scores):
    if not isinstance(scores, dict):
        raise ValueError("scores must be a dictionary")

    max_score = max(scores.values())
    min_score = min(scores.values())
    # 避免除以零的情况
    if max_score == min_score:
        return {exercise: 0 for exercise in scores}
    normalized_scores = {exercise: (score - min_score) / (max_score - min_score) for exercise, score in
                         scores.items()}
    return normalized_scores

class Get_data:
    def __init__(self):
        self.path_1 = 'junyi/junyi_Exercise_table.csv'  # 课程数据
        self.path_2 = 'junyi/junyi_ProblemLog_original.csv'  # 用户交互数据
        self.encoding = 'UTF-8-SIG'
        self.nrows = 50000

    def Get_Exercise_Name(self):
        df = pd.read_csv(self.path_1, encoding=self.encoding)
        exercise_name = {}
        cc = OpenCC('t2s')  # 繁体->简体
        for row in df.values:
            exercise_name[row[0]] = cc.convert(row[-3])
        exercise_name["parabola_intuition_1"] = "抛物线直觉 1"
        return exercise_name

    def Get_Problemlog(self, exercise_names):
        df = pd.read_csv(self.path_2, encoding=self.encoding, nrows=self.nrows)
        user_log = {}
        for row in df.values:
            if row[0] in user_log:
                user_log[row[0]].add(exercise_names[row[1]])
            else:
                user_log[row[0]] = {exercise_names[row[1]]}
        return user_log

    def User_Exercise_Matrix(self, exercise_names):
        df = pd.read_csv(self.path_2, encoding=self.encoding, nrows=self.nrows)
        user_exercise_matrix = pd.pivot_table(df,
            values='points_earned',
            index='user_id',
            columns='exercise',
            fill_value=0
        )
        user_exercise_matrix.columns = [exercise_names[col] for col in user_exercise_matrix.columns]  # 替换exercise语言,英->中
        transposed_matrix = user_exercise_matrix.T  # 转置矩阵
        item_similarity_matrix = cosine_similarity(transposed_matrix)  # 计算项目之间的余弦相似度
        user_similarity_matrix = cosine_similarity(user_exercise_matrix)  # 计算用户之间的余弦相似度
        item_similarity = pd.DataFrame(item_similarity_matrix, index=transposed_matrix.index,
                                     columns=transposed_matrix.index)
        user_similarity = pd.DataFrame(user_similarity_matrix, index=user_exercise_matrix.index,
                                       columns=user_exercise_matrix.index)
        return user_exercise_matrix, item_similarity, user_similarity

    def Item_Recommendation(self, user_id, item_similarity, user_exercise_matrix):
        if user_id not in user_exercise_matrix.index:
            return {}, "没有找到这个用户: {}".format(user_id)
        user_ratings = user_exercise_matrix.loc[user_id]
        existing_ratings = user_ratings[user_ratings.ne(0)].index.tolist()  # 使用布尔索引找到非零评分的索引，转换为列表
        scores = item_similarity.dot(user_ratings.values.reshape(-1, 1))  # 计算所有项目的得分
        scores = pd.Series(scores.values.flatten(), index=user_exercise_matrix.columns)  # 将 DataFrame 转换为 Series
        existing_ratings_index = [user_exercise_matrix.columns.get_loc(exercise) for exercise in existing_ratings]
        scores.iloc[existing_ratings_index] = 0  # 将已经交互过的项目得分设为0，不推荐
        normalized_scores = Normalize(scores.to_dict())
        return normalized_scores, existing_ratings

    def User_Recommendation(self, user_id, user_similarity, user_exercise_matrix):
        if user_id not in user_exercise_matrix.index:
            return "没有找到这个用户: {}".format(user_id)
        scores_dict = {}  # 使用字典来累积评分
        user_index = user_exercise_matrix.index.get_loc(user_id)  # 用户的索引位置
        user_similarity_scores = user_similarity.iloc[user_index]
        user_similarity_scores.loc[user_id] = 0  # 将当前用户相似度设为0，不推荐
        similar_users = user_similarity_scores.sort_values(ascending=False).head(15).index
        for sim in similar_users:
            user_ratings = user_exercise_matrix.loc[sim]
            existing_ratings = user_ratings[user_ratings.ne(0)]  # 非零评分的项目
            for exercise, rating in existing_ratings.items():
                if exercise not in scores_dict:
                    scores_dict[exercise] = rating
                else:
                    scores_dict[exercise] += rating  # 累加相似用户的评分
        user_ratings = user_exercise_matrix.loc[user_id]
        existing_ratings = user_ratings[user_ratings.ne(0)].index.tolist()
        for exercise in existing_ratings:
            scores_dict[exercise] = 0
        normalized_scores = Normalize(scores_dict)
        return normalized_scores

    def SVD_Recommendation(self, user_id, user_exercise_matrix):
        user_exercise_matrix_np = user_exercise_matrix.values
        svd = TruncatedSVD(n_components=user_exercise_matrix.shape[1])
        svd.fit(user_exercise_matrix_np)
        if user_id not in user_exercise_matrix.index:
            return None, "没有找到这个用户: {}".format(user_id)
        else:
            user_ratings = user_exercise_matrix.loc[user_id].values
            user_ratings_pred = svd.transform(user_ratings.reshape(1, -1))
            top_indices = np.argsort(-user_ratings_pred[0])
            scores = user_ratings_pred[0][top_indices]  # 获取所有项目的评分
            # 将列名和对应的分数组合成字典
            score_dict = dict(zip(user_exercise_matrix.columns[top_indices], scores))
            # 归一化分数
            normalized_scores = Normalize(score_dict)  # 归一化
            return normalized_scores

    def Combined_Recommendation(self, user_id, item_similarity, user_similarity, user_exercise_matrix,
                                num=5, item_weight=0.35, user_weight=0.25, svd_weight=0.4):
        if user_id not in user_exercise_matrix.index:
            return "没有找到这个用户: {}".format(user_id)
        item_scores, _ = self.Item_Recommendation(user_id, item_similarity, user_exercise_matrix)
        print('item_scores:',item_scores)
        user_scores = self.User_Recommendation(user_id, user_similarity, user_exercise_matrix)
        print('user_scores:',user_scores)
        svd_scores = self.SVD_Recommendation(user_id, user_exercise_matrix)
        print('svd_scores:',svd_scores)
        all_scores = {}
        for exercise, score in item_scores.items():
            if isinstance(score, (int, float)):  # 确保 score 是数值类型
                all_scores[exercise] = score * item_weight
        for exercise, score in user_scores.items():
            if isinstance(score, (int, float)):  # 确保 score 是数值类型
                all_scores[exercise] = all_scores.get(exercise, 0) + score * user_weight
        for exercise, score in svd_scores.items():
            if isinstance(score, (int, float)):  # 确保 score 是数值类型
                all_scores[exercise] = all_scores.get(exercise, 0) + score * svd_weight
        combined_recommendations = sorted(all_scores.items(), key=lambda x: x[1], reverse=True)[:num]
        print('all_scores:',combined_recommendations)
        return [item[0] for item in combined_recommendations]

if __name__ == '__main__':
    data = Get_data()
    user_id = 247372
    exercise_names = data.Get_Exercise_Name()
    user_exercise_matrix, item_similarity, user_similarity = data.User_Exercise_Matrix(exercise_names)
    print('用户id序列：', user_exercise_matrix.index)
    combined_recommendations = data.Combined_Recommendation(user_id, item_similarity, user_similarity, user_exercise_matrix)
    print('最终推荐结果:', combined_recommendations)
