###### YO
import os

from mediapipe.tasks import python
from mediapipe.tasks.python import text

# wget -O embedder.tflite -q https://storage.googleapis.com/mediapipe-models/text_embedder/bert_embedder/float32/1/bert_embedder.tflite

class Text2Vec:
    def __init__(self):
        l2_normalize = True  # @param {type:"boolean"}
        quantize = False  # @param {type:"boolean"}
        cwd = os.getcwd()
        base_options = python.BaseOptions(model_asset_path=  cwd+'/model/embedder.tflite')
        self.options = text.TextEmbedderOptions(base_options=base_options, l2_normalize=l2_normalize, quantize=quantize)
        self.dimension = 512
        pass

    def embedding_func(self, *args, **kwargs):
        if not args:
            raise ValueError("No word provided for embedding.")
        # Use it
        with text.TextEmbedder.create_from_options(self.options) as embedder:
            result = embedder.embed(args[0])  # returns a 300-dim vector
            return result.embeddings[0].embedding


if __name__ == '__main__':
    word2vec = Text2Vec()
    print(len(word2vec.embedding_func("hello world! HUIAWHGFI AWGAUIWHGA AWUHGAWIUGA WGUIAHWGIUAW GAWUGHAWIUGA WGUIAWHGIUAWHGIUAWGN").embeddings.pop().embedding))

######


