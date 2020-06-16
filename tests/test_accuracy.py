import os

import pytest
from lxml import etree

import ilcs_parser


def test_accuracy():
    with open(os.path.join(os.path.dirname(__file__), 'labeled.xml')) as fobj:
        tree = etree.parse(fobj)

    successes, failures = [], []
    for citation in tree.getroot():
        raw_citation = None
        confirmed_citation_parts = []

        for element in citation:
            if element.tag == 'RawString':
                raw_citation = element.text
            else:
                # Strip semantic punctuation
                element_text = ilcs_parser.strip_semantic_punctuation(element.text)
                confirmed_citation_parts.append((element_text, element.tag))

        parsed_citation = ilcs_parser.parse(raw_citation)

        if parsed_citation == confirmed_citation_parts:
            successes.append((raw_citation, parsed_citation))
        else:
            failures.append((raw_citation, parsed_citation, confirmed_citation_parts))

    accuracy = len(successes) / (len(successes) + len(failures))
    THRESHOLD = 0.95

    if accuracy > THRESHOLD:
        print('Accuracy meets {0:.0%} threshold: {1:.0%}'.format(
            THRESHOLD,
            accuracy
        ))
    else:
        msg = 'Accuracy does not meet {0:.0%} threshold: {1:.1%}'.format(
            THRESHOLD,
            accuracy
        )
        msg += '\n\nFailing examples:\n\n'
        for raw_citation, parsed_citation, true_citation in failures:
            msg += '\n'.join([
                '* {}'.format(raw_citation),
                '\tParsed citation: {}'.format(parsed_citation),
                '\tTrue citation:   {}'.format(true_citation),
                '\n'
            ])
        pytest.fail(msg)
