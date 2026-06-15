from normalization import load_pipeline

def loadNormalizer():
    return load_pipeline("gladia-3", language="en")

def normalize(text="", pipeline=None):
    if not pipeline or pipeline is None:
        return text
    return pipeline.normalize(text)

if __name__ == "__main__":
    pipeline = loadNormalizer()
    text =  normalize("It's $50 at 3:00PM — you know, roughly.", pipeline=pipeline)
    print(text)