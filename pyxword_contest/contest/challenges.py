""""
Contest business logic
"""

import arrow
import yaml
from acrossword.crossword import dumps
from flask import current_app
from sqlalchemy import literal

from pyxword_contest.contest.models import UserStats
from pyxword_contest.crossword.utils import create_crossword
from pyxword_contest.extensions import db, cache
from .models import (
    ContestInitialCrosswords,
    UserCrossword,
)

EXTRA_COUNT = 3
"""how many extra challenges should we have for the player"""


def sync_initial_challenges(contest_id, user_id) -> int:
    # FIXME low priority but this is suboptimal - queries could be smarter

    initial_challenges = db.session.query(
        ContestInitialCrosswords
    ).filter_by(
        contest_id=contest_id,
    ).order_by(
        ContestInitialCrosswords.order.asc(),
    ).all()

    created = 0
    for ch in initial_challenges:
        if not db.session.query(literal(True)).filter(
            UserCrossword.query.filter_by(
                user_id=user_id,
                contest_id=contest_id,
                crossword_id=ch.crossword_id,
            ).exists()
        ).scalar():
            db.session.add(UserCrossword(
                user_id=user_id,
                contest_id=contest_id,
                crossword_id=ch.crossword_id,
            ))
            created += 1

    db.session.commit()
    return created


@cache.memoize(timeout=180)
def load_words(glossary_path: str):
    with open(glossary_path) as f:
        words = yaml.load(f)['glossary'].split()
    return frozenset(words)


def generate(contest_id, user_id, how_many: int):
    created = sync_initial_challenges(contest_id, user_id)

    if created < how_many:
        current_level = db.session.query(UserCrossword).filter_by(
            contest_id=contest_id,
            user_id=user_id,
        ).count()
        words = load_words(current_app.config['GLOSSARY_PATH'])
        for i in range(how_many - created):
            crossword = create_crossword(
                words=words,
                max_words=10 + (current_level + i) * 2,
            )
            db.session.add(crossword)
            db.session.commit()
            db.session.add(UserCrossword(
                user_id=user_id,
                contest_id=contest_id,
                crossword_id=crossword.id,
            ))
            db.session.commit()


def challenges_query(contest_id, user_id):
    user_challenges = db.session.query(UserCrossword).filter_by(
        contest_id=contest_id,
        user_id=user_id,
    ).order_by(
        UserCrossword.id.asc(),
    )
    return user_challenges


def get_or_create_user_stats(user_id: int, contest_id: int) -> UserStats:
    user_stats = db.session.query(UserStats).filter_by(
        user_id=user_id,
        contest_id=contest_id,
    ).first()
    if user_stats is None:
        user_stats = UserStats(
            contest_id=contest_id,
            score=0.0,
            user_id=user_id,
        )
        db.session.add(user_stats)
    return user_stats


def solved(challenge: UserCrossword):
    """
    Mark challenge as solved, count score.
    At this point we trust the contest is indeed running.

    :param challenge:
    :return:
    """
    challenge.solved = arrow.utcnow()

    user_stats = get_or_create_user_stats(
        user_id=challenge.user_id,
        contest_id=challenge.contest_id,
    )
    user_stats.score += challenge.crossword.score

    db.session.commit()
