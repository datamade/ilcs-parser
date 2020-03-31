# ilcs-parser

Probabilistic parser for tagging data that references the Illinois Compiled Statutes (ILCS).

## Installation

Install with `pip`:

```
pip install git+https://github.com/datamade/ilcs-parser.git
```

## Development

Local development requires an installation of Python.

Install development requirements:

```
pip install -e .[tests]
```

Train the model:

```
parserator train training/labeled.xml ilcs_parser
```

Parse away!

### Running tests

Run the tests:

```
pytest
```

All tests should pass.
