import yake

sourcefile = open("Extraction.txt", "w")
for line in open("Requirements.txt"):
    text = line
    print(text, file=sourcefile)
    kw_extractor = yake.KeywordExtractor(top=10, stopwords=set(line.strip() for line in open('SmartStopword.txt')))
    keywords = kw_extractor.extract_keywords(text.lower())
    keywords = sorted(keywords, key=lambda x: x[1], reverse=True)
    for kw, v in keywords:
        print("Keyphrase: ", kw, ": score", v, file=sourcefile)
    print("\n", file=sourcefile)

sourcefile.close()
