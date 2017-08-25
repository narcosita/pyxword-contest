# -*- coding: utf-8 -*-
"""User models."""
import arrow
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import deferred
from sqlalchemy_utils import ArrowType

from pyxword_contest.database import (
    Column,
    db,
    Model,
    reference_col,
    relationship,
    SurrogatePK,
)


class Contest(SurrogatePK, Model):
    """Crossword challenge."""

    __tablename__ = 'contests'
    name = Column(db.String(150), nullable=False)
    slug = Column(db.String(20), nullable=False, unique=True)
    description = Column(db.Text(), nullable=True)
    """^ Markdown field"""
    start = Column(ArrowType(), nullable=True, default=None)
    end = Column(ArrowType(), nullable=True, default=None)

    rules = Column(db.Text(), nullable=True)
    """^ Markdown field"""

    @property
    def active(self):
        if not self.start:
            return False

        now = arrow.utcnow()
        return self.start <= now and (not self.end or now < self.end)

    def __str__(self):
        return f'{super().__str__()}: {self.slug}'


class ContestStage(SurrogatePK, Model):
    """Crossword challenge."""

    __tablename__ = 'contests_stages'
    name = Column(db.String(150), nullable=False)
    finish = Column(ArrowType(), nullable=True, default=None)

    contest_id = reference_col('contests', nullable=False)
    contest = relationship('Contest', backref='stages')

    __table_args__ = (
        UniqueConstraint('contest_id', 'name'),
    )


class ContestStageWinner(SurrogatePK, Model):
    """Crossword challenge."""

    __tablename__ = 'contests_stage_winners'
    user_id = reference_col('users', nullable=False)
    user = relationship('User', backref='contest_stage_wins')

    score = Column(db.Float(), nullable=False)

    contest_stage_id = reference_col('contests_stages', nullable=False)
    contest_stage = relationship('ContestStage', backref='winners')

    __table_args__ = (
        UniqueConstraint('contest_stage_id', 'user_id'),
    )


class UserCrossword(SurrogatePK, Model):
    user_id = reference_col('users', nullable=False)
    user = relationship('User')

    contest_id = reference_col('contests', nullable=False)
    contest = relationship('Contest')

    crossword_id = reference_col('crosswords', nullable=False)
    crossword = relationship('Crossword', lazy='joined')

    solved = Column(ArrowType(), nullable=True, default=None)
    solution = deferred(Column(db.Text(), nullable=True, default=True))

    __table_args__ = (
        UniqueConstraint('user_id', 'contest_id', 'crossword_id'),
    )


class UserStats(SurrogatePK, Model):
    """Crossword challenge."""

    __tablename__ = 'user_stats'
    user_id = reference_col('users', nullable=False)
    user = relationship('User', backref='stats')

    contest_id = reference_col('contests', nullable=False)
    contest = relationship('Contest', backref='stats')

    score = Column(db.Float(), nullable=False, default=0.0)

    __table_args__ = (
        UniqueConstraint('contest_id', 'user_id'),
    )


class ContestInitialCrosswords(SurrogatePK, Model):
    __tablename__ = 'contest_crossword'
    contest_id = reference_col('contests', nullable=False)
    contest = relationship('Contest', backref='initial_crosswords')

    crossword_id = reference_col('crosswords', nullable=False)
    crossword = relationship('Crossword')

    order = Column(db.Integer(), nullable=False, default=0)

    __table_args__ = (
        UniqueConstraint('contest_id', 'crossword_id'),
        UniqueConstraint('contest_id', 'order'),
    )
