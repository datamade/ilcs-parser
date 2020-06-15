#!/usr/bin/python
# -*- coding: utf-8 -*-

import pycrfsuite
import os
import re
import warnings
from collections import OrderedDict
import string

# Labels are based on the Illinois Compiled Statutes numbering scheme:
# https://ilga.gov/commission/lrb/lrbnew.htm#ILCS
# SubSection and the Attempted labels are included even though they are not
# technically part of the spec, since it's often useful to compare these tokens

LABELS = [
    'AttemptedChapter',
    'AttemptedActPrefix',
    'AttemptedSection',
    'AttemptedSubSection',
    'Chapter',
    'ActPrefix',
    'Section',
    'SubSection',
    'AttemptedSuffix'
]
ATTEMPTED_LABELS = [label for label in LABELS if label.startswith('Attempted')]
CITATION_LABELS = [label for label in LABELS if not label.startswith('Attempted')]

PARENT_LABEL  = 'Citation'
GROUP_LABEL   = 'CitationCollection'
NULL_LABEL    = 'Null'
MODEL_FILE    = 'learned_settings.crfsuite'


try:
    TAGGER = pycrfsuite.Tagger()
    TAGGER.open(os.path.split(os.path.abspath(__file__))[0]+'/'+MODEL_FILE)
except IOError:
    TAGGER = None
    warnings.warn(
        'You must train the model (parserator train [traindata] [modulename]) '
        'to create the %s file before you can use the parse and tag methods' % MODEL_FILE
    )


class CitationTag(tuple):
    def __hash__(self):
        return hash(tuple(self.get_hashable_rep()))

    def __eq__(self, other):
        return (
            self.__class__ == other.__class__ and
            self.get_hashable_rep() == other.get_hashable_rep()
        )

    @property
    def is_attempted(self):
        return any(self[0].get(label) for label in ATTEMPTED_LABELS)

    def get_hashable_rep(self):
        hashable_rep = [self[0].get(label) for label in CITATION_LABELS]
        hashable_rep.append(bool(self.is_attempted))
        return tuple(hashable_rep)


def strip_semantic_punctuation(token):
    """
    Given a string token, remove its semantic puncutation (slashes).
    """
    stripped_token = re.sub(r"/", "", token)
    return stripped_token


def parse(raw_string):
    if not TAGGER:
        msg = '\nMISSING MODEL FILE: %s\n' % MODEL_FILE
        msg += (
            'You must train the model before you can use the parse and tag '
            'methods\nTo train the model annd create the model file, run:\n'
            'parserator train [traindata] [modulename]'
        )
        raise IOError(msg)

    tokens = tokenize(raw_string)
    if not tokens:
        return []

    features = tokens2features(tokens)

    tags = TAGGER.tag(features)

    tokens = [strip_semantic_punctuation(token) for token in tokens]

    return list(zip(tokens, tags))


def tag(raw_string):
    tagged = OrderedDict()
    for token, label in parse(raw_string):
        tagged.setdefault(label, []).append(token)

    for token in tagged:
        component = ' '.join(tagged[token])
        component = component.strip(' ,;')
        tagged[token] = component

    citation_type = 'Citation'

    return CitationTag([tagged, citation_type])


def tokenize(raw_string):
    if isinstance(raw_string, bytes):
        try:
            raw_string = str(raw_string, encoding='utf-8')
        except:
            raw_string = str(raw_string)

    # Replace back slashes with forward slashes
    raw_string = re.sub(r"\\", "/", raw_string)

    # Remove any instances of the string "ILCS"
    raw_string = re.sub(r"ilcs", " ", raw_string, flags=re.IGNORECASE)

    # Remove instances of stray IDs formatted like "(tp337049)"
    raw_string = re.sub(r"\(tp[^\)]+\)", " ", raw_string, flags=re.IGNORECASE)

    re_tokens = re.compile(r"""
        [\/]*\b[^\s\/,;#&()-]+  # ['720-5.0/8-4(a)'] -> ['720', '5.0', '/8', '4', 'a']
    """, re.VERBOSE | re.UNICODE)
    tokens = re_tokens.findall(raw_string)

    return tokens if tokens else []


def tokens2features(tokens):
    # Record the number of tokens, since early tokens in longer strings tend to
    # refer to Attempted charges.
    num_tokens = len(tokens)
    first_feature = tokenFeatures(tokens[0])
    first_feature['num.tokens'] = num_tokens

    feature_sequence = [tokenFeatures(tokens[0])]
    previous_features = feature_sequence[-1].copy()

    for token in tokens[1:]:
        # set features for individual tokens (calling tokenFeatures)
        token_features = tokenFeatures(token)
        token_features['num.tokens'] = num_tokens
        current_features = token_features.copy()

        # features for the features of adjacent tokens
        feature_sequence[-1]['next'] = current_features
        token_features['previous'] = previous_features

        token_features['succeeds.slash'] = token.startswith('/')
        feature_sequence[-1]['preceeds.slash'] = token_features['succeeds.slash']

        feature_sequence.append(token_features)
        previous_features = current_features

    if len(feature_sequence) > 1:
        # these are features for the tokens at the beginning and end of a string
        feature_sequence[0]['rawstring.start'] = True
        feature_sequence[-1]['rawstring.end'] = True
        feature_sequence[1]['previous']['rawstring.start'] = True
        feature_sequence[-2]['next']['rawstring.end'] = True

    else:
        # a singleton feature, for if there is only one token in a string
        feature_sequence[0]['singleton'] = True

    return feature_sequence


def tokenFeatures(token):
    # Strip any non-word characters for a "clean" representation
    token_clean = re.sub(r'(^[\W]*)|([^.\w]*$)', '', token.lower())

    return {
        'digits': digits(token),
        'letter': len(token_clean) == 1 and token_clean in string.ascii_lowercase,
        'integer.value': int_value(token),
        'length': len(token),
        'attempted': token_clean in ['att', 'attempted'],
    }


def int_value(token):
    try:
        return int(token)
    except ValueError:
        return 0


def digits(token):
    if token.isdigit():
        return 'all_digits'
    elif set(token) & set(string.digits):
        return 'some_digits'
    else:
        return 'no_digits'
