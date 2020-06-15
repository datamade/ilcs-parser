from collections import OrderedDict

import ilcs_parser


def test_parse():
    assert ilcs_parser.parse('720-550/402-d') == [
        ('720', 'Chapter'),
        ('550', 'ActPrefix'),
        ('402', 'Section'),
        ('d', 'SubSection')
    ]


def test_tag():
    assert ilcs_parser.tag('720-550//402-d') == ilcs_parser.CitationTag([
        OrderedDict(
            [
                ('Chapter', '720'),
                ('ActPrefix', '550'),
                ('Section', '402'),
                ('SubSection', 'd')
            ]
        ),
        'Citation'
    ])


def test_tag_strip_parens():
    assert ilcs_parser.tag('720-550/402(d)') == ilcs_parser.CitationTag([
        OrderedDict(
            [
                ('Chapter', '720'),
                ('ActPrefix', '550'),
                ('Section', '402'),
                ('SubSection', 'd')
            ]
        ),
        'Citation'
    ])


def test_tag_complex():
    assert ilcs_parser.tag('625-5/11-501(a)(2) (tp337049) (att)') == ilcs_parser.CitationTag([
        OrderedDict(
            [
                ('Chapter', '625'),
                ('ActPrefix', '5'),
                ('Section', '11'),
                ('SubSection', '501 a 2'),
                ('AttemptedSuffix', 'att')
            ]
        ),
        'Citation'
    ])


def test_attempted_prefix():
    assert ilcs_parser.tag('720-5/8-4 625-5/11-501(a)(2)') == ilcs_parser.CitationTag([
        OrderedDict(
            [
                ('AttemptedChapter', '720'),
                ('AttemptedActPrefix', '5'),
                ('AttemptedSection', '8'),
                ('AttemptedSubSection', '4'),
                ('Chapter', '625'),
                ('ActPrefix', '5'),
                ('Section', '11'),
                ('SubSection', '501 a 2'),
            ]
        ),
        'Citation'
    ])


def test_tags_are_equal():
    tag_a = ilcs_parser.tag('720-550/402-d')
    tag_b = ilcs_parser.tag('720 550 402(d)')
    assert tag_a == tag_b
    assert tag_a in [tag_b]


def test_tags_are_not_equal():
    tag_a = ilcs_parser.tag('720-550/402-d(a)(1)')
    tag_b = ilcs_parser.tag('720 550 402.d')
    assert tag_a != tag_b
    assert tag_a not in [tag_b]


def test_tags_are_equal_attempted():
    tag_a = ilcs_parser.tag('720-5/8-4 625-5/11-501(a)(1)')
    tag_b = ilcs_parser.tag('625-5/11-501.a.1 (att)')
    assert tag_a == tag_b
    assert tag_a in [tag_b]


def test_tags_are_not_equal_attempted():
    tag_a = ilcs_parser.tag('720-5/8-4 625-5/11-501(a)(1)')
    tag_b = ilcs_parser.tag('625-5/11-501.a.1')
    assert tag_a != tag_b
    assert tag_a not in [tag_b]
