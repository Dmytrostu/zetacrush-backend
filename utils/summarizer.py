import argparse
from collections import Counter
import random

d={w for w in open("dict").read().split("\n")[:2500]}
j={
    "bet",
    "wager",
    "gamble",
    "pray",
    "suicide",
    "kill",
    "catch",
    "oust",
    "coup",
    "death",
    "crash",
    "died",
    "rape",
    "die",
    "murder",
    "jail",
    "assault",
    "lost",
    "battle",
    "hit",
    "strike",
    "shoot",
    "fight",
    "bleed",
    "stab",
    "burn",
    "kiss",
    "celebrate",
    "overcome",
    "surrender",
    "yell",
    "shout",
    "escape",
    "sex",
    "negotiation",
    "deal",
    "court"
    "marry"
    "married"
    "divorce"
    "divorced"
    "desperate",
    "loser",
}

def get_chr_sen(s,char):
    x=s.index(char)
    q=s[x-70:x+110].replace("\n"," ")
    return " ".join(q.split(" ")[1:-1])

def get_easter_egg(s,m):
    x=s.index("first")
    f=s[x-300:x+400]
    while not any(_m in f for _m in m):
        s=s[x+5:]
        x=s.index("first")
        f=s[x+300+random.randint(0,100):x+1400]
    return " ".join(f.split(" ")[1:-1])

def main(f):
    #s=open(f).read()
    s=open(f,encoding="latin-1").read()
    words=s.split(" ")
    t=[]
    last=None
    imp=[]
    l=10
    for i in range(len(words)):
        if words[i][:1] in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            if last:
                last.append(words[i])
            else:
                last=[words[i]]
        else:
            if last:
                t.append(" ".join(last))
                last=None
            else:
                t.append(words[i])
        for _j in j:
            if words[i].startswith(_j) and i<l:
                imp.append(" ".join(words[i-28:i+35]))
                l=i+60
            else:
                l=i+1

    x=[]
    for m in Counter(t).most_common():
        w=m[0]
        if w[:1] in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            w=w.rstrip(",").rstrip(".").rstrip(";").rstrip("\n").rstrip("!").rstrip("?")
            if w.lower() not in d and\
                "gutenberg" not in w.lower() and\
                "\n" not in w and\
                w not in x and\
                "_" not in w and\
                "’" not in w and\
                "'" not in w and\
                "I" not in w.split(" ") and\
                "But" not in w.split(" ") and\
                "So" not in w.split(" ") and\
                len(w)>0:
                x.append(w)
    print("\n\n*******************************************************************")
    print("\nThe main characters/places/things in this book are:\n")
    print("*******************************************************************\n\n")
    for m in x[:25]:
        print("######################")
        print(m)
        print("######################")
        print(get_chr_sen(s,m))
        print("~~~~~~~~~~~~~~~~~~~~~~")
        pass
    print("\n\n*******************************************************************")
    print("Synopsis:\n")
    print("*******************************************************************\n\n")
    for _imp in imp:
        p=_imp.replace("\n"," ")
        for _m in x[:25]:
            if _m in p and random.randint(0,2)>0:
                print(p)
                print("\n")
                break

    print("\n\n*******************************************************************")
    print("Easter Egg:\n")
    print("*******************************************************************\n\n")
    print(get_easter_egg(s,x[:25]))

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--f")
    args=parser.parse_args()
    main(args.f)
