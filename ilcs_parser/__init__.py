#!/usr/bin/python
# -*- coding: utf-8 -*-

import pycrfsuite
import os
import re
import warnings
from collections import OrderedDict
import string

LABELS = [
    'Chapter',
    'ActPrefix',
    'Section',
    'SubSection',
    'Attempted'
]

PARENT_LABEL  = 'TokenSequence'               # the XML tag for each labeled string
GROUP_LABEL   = 'Collection'                  # the XML tag for a group of strings
NULL_LABEL    = 'Null'                        # the null XML tag
MODEL_FILE    = 'learned_settings.crfsuite'   # filename for the crfsuite settings file


try:
    TAGGER = pycrfsuite.Tagger()
    TAGGER.open(os.path.split(os.path.abspath(__file__))[0]+'/'+MODEL_FILE)
except IOError:
    TAGGER = None
    warnings.warn(
        'You must train the model (parserator train [traindata] [modulename]) '
        'to create the %s file before you can use the parse and tag methods' % MODEL_FILE
    )


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
    return list(zip(tokens, tags))


def tag(raw_string):
    tagged = OrderedDict()
    for token, label in parse(raw_string):
        tagged.setdefault(label, []).append(token)

    for token in tagged:
        component = ' '.join(tagged[token])
        component = component.strip(' ,;')
        tagged[token] = component

    return tagged


def tokenize(raw_string):
    if isinstance(raw_string, bytes):
        try:
            raw_string = str(raw_string, encoding='utf-8')
        except:
            raw_string = str(raw_string)

    # Replace back slashes with forward slashes
    raw_string = re.sub(r"\\", "/", raw_string)

    re_tokens = re.compile(r"""
        [(\"'\/]*\b[^\s\/,.;#&()-]+\b[)]*  # ['720-5/8-4(a)'] -> ['720', '5', '/8', '4', '(a)']
    """, re.VERBOSE | re.UNICODE)
    tokens = re_tokens.findall(raw_string)

    if not tokens:
        return []
    return tokens


def tokens2features(tokens):
    feature_sequence = [tokenFeatures(tokens[0])]
    previous_features = feature_sequence[-1].copy()

    for token in tokens[1:]:
        # set features for individual tokens (calling tokenFeatures)
        token_features = tokenFeatures(token)
        current_features = token_features.copy()

        # features for the features of adjacent tokens
        feature_sequence[-1]['next'] = current_features
        token_features['previous'] = previous_features

        token_features['succeeds.slash'] = token.startswith('/')
        feature_sequence[-1]['preceeds.slash'] = token_features['succeeds.slash']

        # DEFINE ANY OTHER FEATURES THAT ARE DEPENDENT UPON TOKENS BEFORE/AFTER
        # for example, a feature for whether a certain character has appeared previously in the token sequence

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
        'parenthetical': parenthetical(token),
        'attempted': token_clean in ['att', 'attempted'],
    }


def int_value(token):
    try:
        return int(token)
    except ValueError:
        return None


def parenthetical(token):
    re_parens = re.compile(r"\([^(]+\)")
    tokens = re_parens.findall(token)
    return tokens is not None


def digits(token):
    if token.isdigit():
        return 'all_digits'
    elif set(token) & set(string.digits):
        return 'some_digits'
    else:
        return 'no_digits'
