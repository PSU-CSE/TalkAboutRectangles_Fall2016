import nltk
from nltk import grammar, parse

cp = parse.load_parser('base_parse.fcfg', trace=1)

sent = 'the big blue box between the small red squares'

tokens = [x.lower() for x in sent.split()]
trees = cp.parse(tokens)
for line in trees:
    line.draw()
    #for word in line:
    #    word.draw()


"""

print('----------------')
for i, tree in enumerate(trees):
    for node in tree:
        for n in node:
            for nn in n:
                print(nn, "nn")
                if type(nn) != str:
                    print(nn.label().keys())
                    print(type(nn.label()["*type*"]), "label")
                    for nnn in nn:
                        print(nnn, "nnn")
                        if type(nnn) != str:
                            print(type(nnn.label()))
        print("==============")
    print(i)
    print(type(tree))
    print(tree)"""