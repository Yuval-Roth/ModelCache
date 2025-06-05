###### YO
import gensim.downloader as api

# Download and load the model (this may take time and space ~1.5GB)
model = api.load("word2vec-google-news-300")

class Word2Vec:
    def __init__(self):
        pass

    def embedding_func(self, *args, **kwargs):
        if not args:
            raise ValueError("No word provided for embedding.")
        # Use it
        vector = model[args[0]]  # returns a 300-dim vector
        return vector
        # similarity = model.similarity("computer", "keyboard")
        # print(similarity)


if __name__ == '__main__':
    word2vec = Word2Vec()
    word2vec.embedding_func()

######