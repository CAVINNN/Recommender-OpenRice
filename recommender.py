import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer


class UserCF:

    def __init__(self, rating_data):
        self.__rating_data = rating_data

    def get_user_rating_average(self, user):
        user_ratings_sum = 0
        for rating in self.__rating_data[user].values():
            user_ratings_sum += rating
        return user_ratings_sum / len(self.__rating_data[user])

    def similarity_cosine(self, user1, user2):
        # Get related rating keys among two users
        related_rating_keys = list()
        for key in self.__rating_data[user2]:
            if key in self.__rating_data[user1]:
                related_rating_keys.append(key)
        # Accumulated sum of (r1 * r2)
        if len(related_rating_keys) != 0:
            users_mul_sum = 0
            for key in related_rating_keys:
                users_mul_sum += self.__rating_data[user1][key] * self.__rating_data[user2][key]
            # Sqrt of accumulated sum of (r1^2)
            user1_sq_sum_sqrt = 0
            for key in related_rating_keys:
                user1_sq_sum_sqrt += np.square(self.__rating_data[user1][key])
            user1_sq_sum_sqrt = np.sqrt(user1_sq_sum_sqrt)
            # Sqrt of accumulated sum of (r2^2)
            user2_sq_sum_sqrt = 0
            for key in related_rating_keys:
                user2_sq_sum_sqrt += np.square(self.__rating_data[user2][key])
            user2_sq_sum_sqrt = np.sqrt(user2_sq_sum_sqrt)
            return users_mul_sum / (user1_sq_sum_sqrt * user2_sq_sum_sqrt)
        else:
            return 0

    def similarity_pearson(self, user1, user2):
        # Get related rating keys among two users
        related_rating_keys = list()
        if len(self.__rating_data[user1]) >= len(self.__rating_data[user2]):
            for key in self.__rating_data[user1]:
                if key in self.__rating_data[user2]:
                    related_rating_keys.append(key)
        else:
            for key in self.__rating_data[user2]:
                if key in self.__rating_data[user1]:
                    related_rating_keys.append(key)
        # Accumulated sum of ((r1 - avg_u1) * (r2 - avg_u2))
        subavgs_mul_sum = 0
        for key in related_rating_keys:
            subavgs_mul_sum += (self.__rating_data[user1][key] - self.get_user_rating_average(self.__rating_data, user1)) * (
                    self.__rating_data[user2][key] - self.get_user_rating_average(self.__rating_data, user2))
        # Sqrt of accumulated sum of ((r1 - avg_u1)^2)
        user1_subavg_sq_sum_sqrt = 0
        for key in related_rating_keys:
            user1_subavg_sq_sum_sqrt += np.square(self.__rating_data[user1][key] - self.get_user_rating_average(self.__rating_data, user1))
        user1_subavg_sq_sum_sqrt = np.sqrt(user1_subavg_sq_sum_sqrt)
        # Sqrt of accumulated sum of ((r2 - avg_u2)^2)
        user2_subavg_sq_sum_sqrt = 0
        for key in related_rating_keys:
            user2_subavg_sq_sum_sqrt += np.square(self.__rating_data[user2][key] - self.get_user_rating_average(self.__rating_data, user2))
        user2_subavg_sq_sum_sqrt = np.sqrt(user2_subavg_sq_sum_sqrt)
        return subavgs_mul_sum / (user1_subavg_sq_sum_sqrt * user2_subavg_sq_sum_sqrt)

    def top_match_users(self, user, similarity_method):
        similar_users = list()
        for rating_user in self.__rating_data:
            if rating_user == user:
                continue
            else:
                similar_user = (similarity_method(rating_user, user), rating_user)
                similar_users.append(similar_user)
        similar_users.sort()
        similar_users.reverse()
        if similar_users[0][0] == 0:
            return []
        else:
            return similar_users

    def recommend(self, user, matched_users):
        # Items not rated(not viewed) by the user
        no_rating_items_set = set()
        for matched_user in matched_users:
            no_rating_items_set = no_rating_items_set | set(self.__rating_data[matched_user[1]].keys())
        no_rating_items_set = no_rating_items_set - set(self.__rating_data[user].keys())
        # User's average ratings
        user_rating_avg = self.get_user_rating_average(user)
        # Get recommended items with rating
        recommend_items = list()
        for item in no_rating_items_set:
            # Get Users who has rated the item
            evaluated_users = list()
            for matched_user in matched_users:
                if item in self.__rating_data[matched_user[1]]:
                    evaluated_users.append(matched_user)
            # Sum of similarity
            similarity_sum = 0
            for evaluated_user in evaluated_users:
                similarity_sum += evaluated_user[0]
            # Sum of similarity weighted average
            similarity_weighted_average = 0
            for evaluated_user in evaluated_users:
                subavg = self.__rating_data[evaluated_user[1]][item] - self.get_user_rating_average(evaluated_user[1])
                similarity_weighted_average += ((evaluated_user[0] * subavg) / similarity_sum)
            item_predict_rating = (user_rating_avg + similarity_weighted_average, item)
            recommend_items.append(item_predict_rating)
        recommend_items.sort()
        recommend_items.reverse()
        return recommend_items

    def get_recommend(self, user):
        match_users = list()
        for match_user in self.top_match_users(user, self.similarity_cosine):
            if match_user[0] > 0:
                match_users.append(match_user)
        return self.recommend(user, match_users)


class ItemCF:

    def __init__(self, rating_data):
        self.__rating_data = rating_data

    def get_item_rating_average(self, item):
        item_ratings_sum = 0
        item_ratings_len = 0
        for user_key in self.__rating_data:
            for item_key in self.__rating_data[user_key]:
                if item_key == item:
                    item_ratings_len += 1
                    item_ratings_sum += self.__rating_data[user_key][item_key]
        return item_ratings_sum / item_ratings_len

    def similarity_cosine(self, item1, item2):
        items_mul_sum = 0
        item1_sq_sum_sqrt = 0
        item2_sq_sum_sqrt = 0
        for user_key in self.__rating_data:
            if item1 in self.__rating_data[user_key] and item2 in self.__rating_data[user_key]:
                items_mul_sum += self.__rating_data[user_key][item1] * self.__rating_data[user_key][item2]
                item1_sq_sum_sqrt += np.square(self.__rating_data[user_key][item1])
                item2_sq_sum_sqrt += np.square(self.__rating_data[user_key][item2])
        if item1_sq_sum_sqrt != 0 and item2_sq_sum_sqrt != 0:
            item1_sq_sum_sqrt = np.sqrt(item1_sq_sum_sqrt)
            item2_sq_sum_sqrt = np.sqrt(item2_sq_sum_sqrt)
            return items_mul_sum / (item1_sq_sum_sqrt * item2_sq_sum_sqrt)
        else:
            return 0

    def similarity_pearson(self, item1, item2):
        subavgs_mul_sum = 0
        item1_subavg_sq_sum_sqrt = 0
        item2_subavg_sq_sum_sqrt = 0
        for user_key in self.__rating_data:
            if item1 in self.__rating_data[user_key] and item2 in self.__rating_data[user_key]:
                subavgs_mul_sum += (self.__rating_data[user_key][item1] - self.get_item_rating_average(item1)) * (
                        self.__rating_data[user_key][item2] - self.get_item_rating_average(item2))
                item1_subavg_sq_sum_sqrt += np.square(
                    self.__rating_data[user_key][item1] - self.get_item_rating_average(item1))
                item2_subavg_sq_sum_sqrt += np.square(
                    self.__rating_data[user_key][item2] - self.get_item_rating_average(item2))
        item1_subavg_sq_sum_sqrt = np.sqrt(item1_subavg_sq_sum_sqrt)
        item2_subavg_sq_sum_sqrt = np.sqrt(item2_subavg_sq_sum_sqrt)
        return subavgs_mul_sum / (item1_subavg_sq_sum_sqrt * item2_subavg_sq_sum_sqrt)

    def top_match_items(self, item, similarity_method):
        items_set = set()
        for user_key in self.__rating_data:
            items_set = items_set | set(self.__rating_data[user_key].keys())
        similar_items = list()
        for match_item in items_set:
            if match_item == item:
                continue
            else:
                similar_item = (similarity_method(item, match_item), match_item)
                similar_items.append(similar_item)
        similar_items.sort()
        similar_items.reverse()
        if similar_items[0][0] == 0:
            return []
        else:
            return similar_items

    def recommend(self, item, matched_items):
        # Users who do not rated(not viewed) the item
        no_rating_user_list = list()
        for user_key in self.__rating_data:
            if item not in self.__rating_data[user_key]:
                no_rating_user_list.append(user_key)
        item_rating_avg = self.get_item_rating_average(item)
        recommend_users = list()
        for no_rating_user in no_rating_user_list:
            evaluated_items = list()
            for matched_item in matched_items:
                if matched_item[1] in self.__rating_data[no_rating_user]:
                    evaluated_items.append(matched_item)
            similarity_sum = 0
            for evaluated_item in evaluated_items:
                similarity_sum += evaluated_item[0]
            similarity_weighted_average = 0
            for evaluated_item in evaluated_items:
                subavg = self.__rating_data[no_rating_user][evaluated_item[1]] - self.get_item_rating_average(
                    evaluated_item[1])
                similarity_weighted_average += ((evaluated_item[0] * subavg) / similarity_sum)
            user_predict_rating = (item_rating_avg + similarity_weighted_average, no_rating_user)
            recommend_users.append(user_predict_rating)
        recommend_users.sort()
        recommend_users.reverse()
        return recommend_users

    def get_recommend(self, item):
        match_items = list()
        for match_item in self.top_match_items(item, self.similarity_cosine):
            if match_item[0] > 0:
                match_items.append(match_item)
        return self.recommend(item, match_items)


class ContentBased:

    def __init__(self, rating_data, item_names, texts):
        self.__rating_data = rating_data
        vectorizer = TfidfVectorizer()
        tf_idf = vectorizer.fit_transform(texts).toarray()
        items_tfidf_dic = {}
        for index in range(len(tf_idf)):
            name = item_names[index]
            items_tfidf_dic[name] = tf_idf[index]
        self.__tfidf_dic = items_tfidf_dic

    def similarity_cosine(self, item1, item2):
        if len(item1) == len(item2):
            features_length = len(item1)
        else:
            print('Error in similarity_cosine, len(item1) not equals to len(item2)')
            return 0
        items_mul_sum = 0
        for feature_index in range(features_length):
            items_mul_sum += item1[feature_index] * item2[feature_index]
        item1_sq_sum_sqrt = 0
        for feature_index in range(features_length):
            item1_sq_sum_sqrt += np.square(item1[feature_index])
        item1_sq_sum_sqrt = np.sqrt(item1_sq_sum_sqrt)
        item2_sq_sum_sqrt = 0
        for feature_index in range(features_length):
            item2_sq_sum_sqrt += np.square(item2[feature_index])
        item2_sq_sum_sqrt = np.sqrt(item2_sq_sum_sqrt)
        return items_mul_sum / (item1_sq_sum_sqrt * item2_sq_sum_sqrt)

    def get_recommend(self, user):

        # Get sorted user rated list (high -> low)
        user_rating_list = list()
        for key in self.__rating_data[user]:
            rating_tuple = (self.__rating_data[user][key], key)
            user_rating_list.append(rating_tuple)
        user_rating_list.sort()
        user_rating_list.reverse()

        # Calculate similarity_cosine between fav_item and all other items
        fav_item = user_rating_list[0][1]
        recommend_list = list()
        for item_name in self.__tfidf_dic:
            if item_name != fav_item:
                tup = (self.similarity_cosine(self.__tfidf_dic[fav_item],
                                              self.__tfidf_dic[item_name]), item_name)
                recommend_list.append(tup)
        recommend_list.sort()
        recommend_list.reverse()

        # Get items which similarity_cosine > 0
        recommend_items = list()
        for item in recommend_list:
            # if item[0] > 0:
            recommend_items.append(item)

        return recommend_items
