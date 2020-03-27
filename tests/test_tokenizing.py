from ilcs_parser import tokenize


def test_commas():
    assert tokenize('foo,bar') == ['foo', 'bar']


def test_periods():
    assert tokenize('foo.bar') == ['foo', 'bar']


def test_spaces():
    assert tokenize('foo bar') == ['foo', 'bar']
    assert tokenize('foo  bar') == ['foo', 'bar']
    assert tokenize('foo bar ') == ['foo', 'bar']
    assert tokenize(' foo bar') == ['foo', 'bar']


def test_forward_slashes():
    assert tokenize('foo/bar') == ['foo', '/bar']


def test_back_slashes():
    assert tokenize('foo\\bar') == ['foo', '/bar']


def test_parens():
    assert tokenize('foobar(a)') == ['foobar', '(a)']
    assert tokenize('foobar(a)(b)') == ['foobar', '(a)', '(b)']


def test_hyphens():
    assert tokenize('foo-bar-baz') == ['foo', 'bar', 'baz']
