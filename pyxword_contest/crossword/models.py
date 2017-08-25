# -*- coding: utf-8 -*-
"""User models."""
from sqlalchemy.orm import deferred

from pyxword_contest.database import (
    Column,
    db,
    Model,
    SurrogatePK,
)


class Crossword(SurrogatePK, Model):
    """Crossword challenge."""

    __tablename__ = 'crosswords'
    name = Column(db.String(80), nullable=False)
    score = Column(db.Float(), nullable=False, default=0)
    description = deferred(Column(db.Text(), nullable=True))
    """^ Markdown field"""
    body = deferred(Column(db.Text(), nullable=False))
    solution = deferred(Column(db.Text(), nullable=False))

    def __str__(self):
        return f'{super().__str__()}: {self.name}'
