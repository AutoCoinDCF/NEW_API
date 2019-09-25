# coding=utf-8
# Author: YuSH
# Date: 2019-9-3
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.cluster import MiniBatchKMeans
import numpy as np


class OperatorDoc():
    def __init__(self):
        pass
    def text_clustering(self, text_dict, class_num):
        """cluster text docs
        Args:
            text_dict: {doc id: doc content}
            class_num: the number of class
        Returns:
            cluster_result: The cluster result saved as a dict.
                            The format is {cluster id: [doc id, ...], cluster id: [doc id, ...], ...}
                            The length of this list is class_num.
                            Each cluster id is a integer from 0 to class_num - 1.
                            Each list in the value of cluster_result
                            contains the doc ids which are in the same cluster.
            keywords:       A dict saved top 5 keywords of each cluster.
                            The format is {cluster id: [word1, ..., word5], ...}
                            Each cluster id is a integer from 0 to class_num - 1.
                            And the importance of word1 > word2 > word3 > word4 > word5
            center_doc:     A dict saved the center doc of each cluster.
                            The format is {cluster id: doc id, ...}
                            Each cluster id is a integer from 0 to class_num - 1.
        """

        def word2fea(docs_content_set):
            """Change word to features by TF-IDF"""
            tv = TfidfVectorizer(binary=False, decode_error='ignore', stop_words='english', norm='l2')
            return tv.fit_transform(docs_content_set).toarray()

        def cluster(fea):
            """Clustering by features"""
            assert len(doc_id) == len(fea)
            km = MiniBatchKMeans(n_clusters=class_num) if len(fea) > 100 else KMeans(n_clusters=class_num)
            km.fit(fea)
            doc_class = km.predict(fea)
            assert len(doc_id) == len(doc_class)
            res = [[] for _ in range(class_num)]
            for doc_index in range(len(doc_id)):
                res[int(doc_class[doc_index])].append(doc_index)
            return res

        def get_keywords(doc_words_set):
            """Get keywords a doc set
            Args:
                doc_words_set: The words of docs which in whole doc set
            Return:
                keywords: The top-5 keywords
            """
            word_tf = {}
            word_idf = {}
            for words in doc_words_set:
                solved_word = set()
                for word in words:
                    word_tf[word] = word_tf.get(word, 0.0) + 1.0
                    if word not in solved_word:
                        solved_word.add(word)
                        word_idf[word] = word_idf.get(word, 0.0) + 1.0

            word_weight = {word: word_tf[word] * np.log(float(len(doc_words)) / word_idf[word])
                           for word in word_tf.keys()}

            words, weight = zip(*word_weight.items())

            indices = np.argsort(np.array(weight) * -1)

            return [words[word_index] for word_index in indices[:5]]

        def get_center_doc_index(doc_fea_set, indices):
            """Get center doc index of a doc set
            Args:
                doc_fea_set: The features of docs which in whole doc set
                indices: The indices of used doc
            Return:
                doc id: Id of the center doc
            """
            cluster_fea_set = [doc_fea_set[doc_index] for doc_index in indices]
            center_fea = np.sum(cluster_fea_set, axis=0)
            tmp = np.array(cluster_fea_set) - center_fea
            distance = np.sum(tmp*tmp, axis=1)

            assert len(distance) == len(indices)

            doc_index = np.argmin(distance)

            return indices[doc_index]

        def resolve_data(content):
            def _get_useless_word(wordset):
                word_tf = {}
                for item in wordset:
                    for w in item:
                        word_tf[w] = word_tf.get(w, 0) + 1
                useless_word = set()
                delete_tf = 0
                while (len(word_tf) - len(useless_word)) * len(content) > 1e9:
                    delete_tf += 1
                    # print("increase delete tf from %d to %d" % (delete_tf-1, delete_tf))
                    for w, t in word_tf.items():
                        if t == delete_tf:
                            useless_word.add(w)

                # print("solved %d - %d = %d cases" % (
                #     len(word_tf),
                #     len(useless_word),
                #     len(word_tf)-len(useless_word)))

                return useless_word

            words = [c.rstrip("\n").split(" ") for c in content]
            uw = _get_useless_word(words)

            for doc_index in range(len(content)):
                content[doc_index] = " ".join([w for w in words[doc_index] if w not in uw])
            return content

        assert class_num > 1

        cluster_result = {cluster_id: None for cluster_id in range(class_num)}
        keywords = {cluster_id: None for cluster_id in range(class_num)}
        center_doc = {cluster_id: None for cluster_id in range(class_num)}

        doc_id, doc_content = zip(*text_dict.items())
        doc_id = list(doc_id)
        doc_content = [c.rstrip("\n") for c in doc_content]
        doc_content = resolve_data(doc_content)

        doc_words = [c.split(" ") for c in doc_content]
        doc_features = word2fea(doc_content)
        # print("solved features")

        cluster_ids = cluster(doc_features)
        # print("solved clustering")

        for i in range(class_num):
            cluster_focus_ids = cluster_ids[i]
            # solve cluster_result
            ids = [doc_id[doc_index] for doc_index in cluster_focus_ids]
            cluster_result[i] = ids
            # solve keywords
            cluster_word_set = [doc_words[doc_index] for doc_index in cluster_focus_ids]
            keywords[i] = get_keywords(cluster_word_set)
            # solve center doc
            center_doc[i] = doc_id[get_center_doc_index(doc_features, cluster_focus_ids)]

        return cluster_result, keywords, center_doc


if __name__ == "__main__":
    docs = {}
    with open("../data/mq2007/doc_set") as f:
        index = 0
        for line in f.readlines():
            docs["doc_%d" % index] = line.rstrip("\n")
            index += 1
            if index > 90:
                break

    cs, kw, cd = OperatorDoc().text_clustering(docs, 5)
    print(cs)
    print(kw)
    print(cd)