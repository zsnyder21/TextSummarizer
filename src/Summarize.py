import pandas as pd 
import numpy as np
import pickle as pkl
from nltk.corpus import brown, stopwords
from nltk.cluster.util import cosine_distance
from operator import itemgetter 


class Summarize_dis:
    def __init__(self, stopwords=None) -> None:
        if stopwords is None:
            stopwords = []

        self.stopwords = stopwords
        
    
    def pagerank(self, A, eps=0.0001, d=0.85):
        P = np.ones(len(A)) / len(A)
        while True:
            new_P = np.ones(len(A)) * (1 - d) / len(A) + d * A.T.dot(P)
            delta = abs(new_P - P).sum()
            if delta <= eps:
                return new_P
            P = new_P

    def sentence_similarity(self, sent1, sent2):

        sent1 = list(map(lambda x: x.lower(), sent1))
        sent2 = list(map(lambda x: x.lower(), sent2))

        all_words = list(set(sent1+sent2))

        vector1 = np.zeros(len(all_words))
        vector2 = np.zeros(len(all_words))


        for w in sent1:
            if w in self.stopwords:
                continue
            vector1[all_words.index(w)] += 1

        for w in sent2:
            if w in self.stopwords:
                continue
            vector2[all_words.index(w)] += 1

        return 1 - cosine_distance(vector1, vector2)



 
 
    def build_similarity_matrix(self, sentences):
        # Create an empty similarity matrix
        S = np.zeros((len(sentences), len(sentences)))
    
    
        for idx1 in range(len(sentences)):
            for idx2 in range(len(sentences)):
                if idx1 == idx2:
                    continue
    
                S[idx1][idx2] = self.sentence_similarity(sentences[idx1], sentences[idx2])
    
        # normalize the matrix row-wise
        for idx in range(len(S)):
            S[idx] /= S[idx].sum()
    
        return S

    def textrank(self, sentences, top_n=5):
        """
        sentences = a list of sentences [[w11, w12, ...], [w21, w22, ...], ...]
        top_n = how may sentences the summary should contain
        stopwords = a list of stopwords
        """
        S = self.build_similarity_matrix(sentences) 
        sentence_ranks = self.pagerank(S)
    
        # Sort the sentence ranks
        ranked_sentence_indexes = [item[0] for item in sorted(enumerate(sentence_ranks), key=lambda item: -item[1])]
        selected_sentences = sorted(ranked_sentence_indexes[:top_n])
        summary = itemgetter(*selected_sentences)(sentences)
        return summary
    

if __name__ == "__main__":
    x = Summarize_dis()

    '''df = pd.read_pickle("/Users/andrewargaez/TextSummarizer/data/comments.pkl")
    df.index = range(len(df))
    sentences = [x.split(".") for x in list(df.reindex(df["CommentBody"].map(len).sort_values(ascending=False).index)["CommentBody"].values[:1])]
    sentences = [list(map(lambda x: x.split(), sentence)) for sentence in sentences]
    sentences = [x for x in sentences[0] if x]
    print(type(sentences))
    '''
    
    sentences = brown.sents('ca01')
    print(sentences)

    for idx, sentence in enumerate(x.textrank(sentences)):
        print("%s. %s" % ((idx + 1), ' '.join(sentence)))