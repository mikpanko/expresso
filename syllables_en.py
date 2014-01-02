import re

###
### Fallback syllable counter
###
### This is based on the algorithm in Greg Fast's perl module
### Lingua::EN::Syllable.
### https://github.com/nltk/nltk_contrib/blob/master/nltk_contrib/readability/syllables_en.py
###
### Slightly modified by Mikhail Panko (2014)
###

specialSyllables_en = """tottered 2
chummed 1
peeped 1
moustaches 2
shamefully 3
messieurs 2
satiated 4
sailmaker 4
sheered 1
disinterred 3
propitiatory 6
bepatched 2
particularized 5
caressed 2
trespassed 2
sepulchre 3
flapped 1
hemispheres 3
pencilled 2
motioned 2
poleman 2
slandered 2
sombre 2
etc 4
sidespring 2
mimes 1
effaces 2
mr 2
mrs 2
ms 1
dr 2
st 1
sr 2
jr 2
truckle 2
foamed 1
fringed 2
clattered 2
capered 2
mangroves 2
suavely 2
reclined 2
brutes 1
effaced 2
quivered 2
h'm 1
veriest 3
sententiously 4
deafened 2
manoeuvred 3
unstained 2
gaped 1
stammered 2
shivered 2
discoloured 3
gravesend 2
60 2
lb 1
unexpressed 3
greyish 2
unostentatious 5"""

fallback_cache = {}

fallback_subsyl = ["cial", "tia", "cius", "cious", "gui", "ion", "iou", "sia$", ".ely$"]

fallback_addsyl = ["ia", "riet", "dien", "iu", "io", "ii",
                   "[aeiouy]bl$", "mbl$",
                   "[aeiou]{3}",
                   "^mc", "ism$",
                   "(.)(?!\\1)([auy])\\2l$",  # "(.)(?!\\1)([aeiouy])\\2l$"
                   "[^l]llien",
                   "^coad.", "^coag.", "^coal.", "^coax.",
                   "(.)(?!\\1)[gq]ua(.)(?!\\2)[aeiou]",
                   "dnt$"]


# Compile our regular expressions
fallback_subsyl_re = [re.compile(expr) for expr in fallback_subsyl]
fallback_addsyl_re = [re.compile(expr) for expr in fallback_addsyl]


def _normalize_word(word):
    return word.strip().lower()


# Read our syllable override file and stash that info in the cache
for line in specialSyllables_en.splitlines():
    line = line.strip()
    if line:
        toks = line.split()
        assert len(toks) == 2
        fallback_cache[_normalize_word(toks[0])] = int(toks[1])


def count(word):
    word = _normalize_word(word)

    if not word:
        return 0

    # Check for a cached syllable count
    count0 = fallback_cache.get(word, -1)
    if count0 > 0:
        return count0

    # Remove final silent 'e'
    if word[-1] == "e":
        word = word[:-1]

    # Count vowel groups
    count0 = 0
    prev_was_vowel = 0
    for c in word:
        is_vowel = c in ("a", "e", "i", "o", "u", "y")
        if is_vowel and not prev_was_vowel:
            count0 += 1
        prev_was_vowel = is_vowel

    # Add & subtract syllables
    for r in fallback_addsyl_re:
        if r.search(word):
            count0 += 1
    for r in fallback_subsyl_re:
        if r.search(word):
            count0 -= 1

    # Cache the syllable count
    fallback_cache[word] = count0

    return count0