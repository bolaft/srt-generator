#!/usr/bin/python3

import re
import random

from optparse import OptionParser

# These mappings can get fairly large -- they're stored globally to
# save copying time.

# (tuple of words) -> {dict: word -> number of times the word appears following the tuple}
# Example entry:
#    ('eyes', 'turned') => {'to': 2.0, 'from': 1.0}
# Used briefly while first constructing the normalized mapping
tempMapping = {}

# (tuple of words) -> {dict: word -> *normalized* number of times the word appears following the tuple}
# Example entry:
#    ('eyes', 'turned') => {'to': 0.66666666, 'from': 0.33333333}
mapping = {}

# Contains the set of words that can start sentences
starts = []


# We want to be able to compare words independent of their capitalization.
def fixCaps(word):
    # Ex: "FOO" -> "foo"
    if word.isupper() and word != "I":
        word = word.lower()
        # Ex: "LaTeX" => "Latex"
    elif word[0].isupper():
        word = word.lower().capitalize()
        # Ex: "wOOt" -> "woot"
    else:
        word = word.lower()
    return word


# Tuples can be hashed; lists can't.  We need hashable values for dict keys.
# This looks like a hack (and it is, a little) but in practice it doesn't
# affect processing time too negatively.
def toHashKey(lst):
    return tuple(lst)


# Returns the contents of the file, split into a list of words and
# (some) punctuation.
def wordlist(filename):
    f = open(filename, 'r')
    wordlist = [fixCaps(w) for w in re.findall(r"[\w']+|[.,!?;]", f.read())]
    f.close()
    return wordlist


# Self-explanatory -- adds "word" to the "tempMapping" dict under "history".
# tempMapping (and mapping) both match each word to a list of possible next
# words.
# Given history = ["the", "rain", "in"] and word = "Spain", we add "Spain" to
# the entries for ["the", "rain", "in"], ["rain", "in"], and ["in"].
def addItemToTempMapping(history, word):
    global tempMapping
    while len(history) > 0:
        first = toHashKey(history)
        if first in tempMapping:
            if word in tempMapping[first]:
                tempMapping[first][word] += 1.0
            else:
                tempMapping[first][word] = 1.0
        else:
            tempMapping[first] = {}
            tempMapping[first][word] = 1.0
        history = history[1:]


# Building and normalizing the mapping.
def buildMapping(wordlist, markovLength):
    global tempMapping
    starts.append(wordlist[0])
    for i in range(1, len(wordlist) - 1):
        if i <= markovLength:
            history = wordlist[: i + 1]
        else:
            history = wordlist[i - markovLength + 1: i + 1]
        follow = wordlist[i + 1]
        # if the last elt was a period, add the next word to the start list
        if history[-1] == "." and follow not in ".,!?;":
            starts.append(follow)
        addItemToTempMapping(history, follow)
    # Normalize the values in tempMapping, put them into mapping
    for first, followset in tempMapping.items():
        total = sum(followset.values())
        # Normalizing here:
        mapping[first] = dict([(k, v / total) for k, v in followset.items()])


# Returns the next word in the sentence (chosen randomly),
# given the previous ones.
def next(prevList):
    sum = 0.0
    retval = ""
    index = random.random()
    # Shorten prevList until it's in mapping
    while toHashKey(prevList) not in mapping:
        prevList.pop(0)
    # Get a random word from the mapping, given prevList
    for k, v in mapping[toHashKey(prevList)].items():
        sum += v
        if sum >= index and retval == "":
            retval = k
    return retval


def genSentence(markovLength, start):
    # Start with a random "starting word"
    if start:
        sent = start.strip().capitalize()
        prevList = start.split(" ")
        curr = prevList[-1]

        # if curr not in starts:
        #     curr = random.choice(starts)
        #     sent += " " + curr
        #     prevList.append(curr)
    else:
        curr = random.choice(starts)
        sent = curr.capitalize()
        prevList = [curr]

    # Keep adding words until we hit a period
    while (curr not in "."):
        curr = next(prevList)
        prevList.append(curr)
        # if the prevList has gotten too long, trim it
        if len(prevList) > markovLength:
            prevList.pop(0)
        if (curr not in ".,!?;"):
            sent += " "  # Add spaces between words (but not punctuation)
        sent += curr
    return sent[0].upper() + sent[1:].lower()

mapped = False


def generate_sentence(filename, markovLength, sentenceLength, start):
    global mapped
    if not mapped:
        buildMapping(wordlist(filename), markovLength)
        mapped = True
    generated_sentence = ""

    i = 0
    if sentenceLength:
        while len(generated_sentence.split(" ")) != sentenceLength:
            generated_sentence = genSentence(markovLength, start)
            i += 1
            if i > 1000:
                break
    else:
        generated_sentence = genSentence(markovLength, start)

    return(generated_sentence)


def parse_args():
    """
    Parses command line options and arguments
    """
    op = OptionParser(usage="usage: %prog [opts] corpus_file start_chain")

    op.add_option(
        "-n", "--ngrams",
        dest="ngrams",
        type="int",
        default=2,
        help="number of ngrams")

    return op.parse_args()


# Launch
if __name__ == "__main__":
    options, arguments = parse_args()

    if len(arguments) != 2:
        print("This script takes exactly 2 arguments. Use --help for more details.")
    else:
        print(generate_sentence(arguments[0], options.ngrams, False, arguments[1]))
