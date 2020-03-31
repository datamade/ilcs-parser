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
    assert ilcs_parser.tag('720-550//402-d') == (
        OrderedDict(
            [
                ('Chapter', '720'),
                ('ActPrefix', '550'),
                ('Section', '402'),
                ('SubSection', 'd')
            ]
        ),
        'Citation'
    )


def test_tag_complex():
    assert ilcs_parser.tag('625-5/11-501(a)(2) (tp337049) (att)') == (
        OrderedDict(
            [
                ('Chapter', '625'),
                ('ActPrefix', '5'),
                ('Section', '11'),
                ('SubSection', '501 (a) (2)'),
                ('Attempted', '(att)')
            ]
        ),
        'Citation'
    )
