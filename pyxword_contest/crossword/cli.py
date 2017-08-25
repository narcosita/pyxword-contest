import collections
import os.path
import pathlib

import click
import sys
import yaml
from flask import current_app
from flask.cli import with_appcontext
from slugify import slugify

from pyxword_contest.crossword.utils import clean


class MultilineStrDumper(yaml.Dumper):
    """
    We need to override default behavior which is NOT to use or even allow
    block representation for multiline strings.
    PyYAML seems to parse them fine if they start with a non-whitespace
    character, so that will be our criteria here for `allow_block`.
    """

    def represent_str(self, data):
        kwargs = {}
        if '\n' in data:
            kwargs['style'] = '|'
        return self.represent_scalar('tag:yaml.org,2002:str', data, **kwargs)

    def analyze_scalar(self, scalar: str):
        analysis = super().analyze_scalar(scalar)
        """type: yaml.emitter.ScalarAnalysis"""
        if isinstance(scalar, str) and not scalar[:1].isspace():
            analysis.allow_block = True
        return analysis


MultilineStrDumper.add_representer(str, MultilineStrDumper.represent_str)


class CustomDumper(MultilineStrDumper):
    pass


# borrowed from `rtyaml`
def ordered_dict_serializer(self, data):
    return self.represent_mapping('tag:yaml.org,2002:map', data.items())


CustomDumper.add_representer(collections.OrderedDict, ordered_dict_serializer)

# required indent marker, see comment in `MultilineStrDumper`
INDENT_MARKER = '|indent\n'
INDENTED_FIELDS = ['body', 'solution']


def crossword_to_yaml(
    c: 'pyxword_contest.crossword.models.Crossword',
    stream=None,
):
    kwargs = {
        'name': c.name,
        'body': INDENT_MARKER + clean(c.body),
        'solution': INDENT_MARKER + clean(c.solution),
        'score': c.score,
        'description': c.description,
    }

    filtered_kwargs = {
        field: val
        for field, val in kwargs.items()
        if val is not None
    }

    return yaml.dump(
        # we use ordered dict so yaml doesn't mess with our order
        # which is preserved in normal dict by Python 3.6
        collections.OrderedDict(filtered_kwargs),
        stream=stream,
        Dumper=CustomDumper,
    )


def crossword_from_yaml(
    stream
) -> dict:
    kwargs = yaml.load(stream=stream)
    for indented in INDENTED_FIELDS:
        if indented in kwargs:
            val = kwargs[indented]
            if val.startswith(INDENT_MARKER):
                kwargs[indented] = val[len(INDENT_MARKER):]

    return kwargs


@click.group()
def crossword():
    """Do some crossword stuff!."""
    pass


@crossword.command()
@click.argument(
    'directory',
    type=click.Path(exists=True, file_okay=False),
)
@with_appcontext
def dump(directory):
    """Dumps crosswords from database into directory."""
    from .models import Crossword  # noqa
    for c in Crossword.query:
        filename = f'{c.id:0>5}_{slugify(c.name)}.yaml'
        with open(
            os.path.join(directory, filename),
            'w',
        ) as f:
            crossword_to_yaml(c, stream=f)


@crossword.command()
@click.argument(
    'directory',
    type=click.Path(exists=True, file_okay=False),
)
@with_appcontext
def load(directory):
    """Loads crosswords from directory into database."""
    from .models import Crossword  # noqa

    db = current_app.extensions['sqlalchemy'].db
    for path in sorted(pathlib.Path(directory).glob('**/*.yaml')):
        with open(path, 'r') as f:
            c_kwargs = crossword_from_yaml(f)
            updated = db.session.query(Crossword).filter_by(
                name=c_kwargs['name'],
            ).update(c_kwargs)
            if not updated:
                db.session.add(Crossword(**c_kwargs))
            db.session.commit()
