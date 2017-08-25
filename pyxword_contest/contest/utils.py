import arrow
from flask import request
from sqlalchemy.orm import load_only
from werkzeug import exceptions

from pyxword_contest.contest.models import Contest
from pyxword_contest.extensions import db


def set_request_contest(contest):
    request.contest = contest


def get_request_contest():
    return getattr(request, 'contest', None)


def get_active_contest():
    now = arrow.utcnow()
    contest = Contest.query.filter(
        Contest.start <= now,
        Contest.start.isnot(None),
    ).order_by(
        Contest.start.desc(),
        # Contest.end.desc().nullsfirst() would be better but breaks sqlite
        Contest.end.is_(None).desc(),
        Contest.end.desc(),
        Contest.id.desc(),
    ).options(
        load_only('slug')
    ).first()
    return contest


def get_contest(slug):
    contest = db.session.query(Contest).filter_by(slug=slug).first()
    if not contest:
        raise exceptions.NotFound('No such contest')
    return contest
