# -*- coding: utf-8 -*-
"""Contest crossword views."""
import itertools

from flask import (
    abort,
    Blueprint,
    flash,
    redirect,
    render_template,
    url_for,
)
from flask_login import login_required, current_user
from sqlalchemy.orm import (
    joinedload,
    load_only,
)

from pyxword_contest.contest.challenges import challenges_query
from pyxword_contest.contest.utils import set_request_contest, get_contest
from pyxword_contest.crossword.models import Crossword
from pyxword_contest.extensions import (
    db,
    limiter,
)
from pyxword_contest.user.models import User
from . import challenges
from .models import (
    ContestStage,
    ContestStageWinner,
    UserCrossword,
    UserStats,
)

blueprint = Blueprint('contest', __name__, static_folder='../static')


def next_challenge(query, contest_slug: str):
    """
    get next challenge redirect

    :param query: challenges query
    :param contest_slug: contest slug name
    :return: redirect to next challenge or score board
    """
    unsolved = query.options(
        load_only(UserCrossword.id)
    ).filter_by(solved=None).first()
    if unsolved:
        return redirect(url_for(
            'contest.challenge',
            contest_slug=contest_slug,
            pk=unsolved.id,
        ))
    else:
        flash(
            "You have completed all available challenges!",
            category='info',
        )
        return redirect(url_for(
            'contest.stats',
            contest_slug=contest_slug,
        ))


@blueprint.route('/<contest_slug>/challenges')
@blueprint.route('/<contest_slug>/challenges/<int:pk>')
@login_required
@limiter.limit('30/minute')
def challenge(contest_slug: str, pk: int = None):
    """Main crossword challenge."""
    contest = get_contest(contest_slug)
    db.session.expunge(contest)  # prevent reloading from db
    set_request_contest(contest)
    if not contest.active:
        flash(
            "Contest already ended, you can view results here",
            category='info',
        )
        return redirect(
            url_for('contest.stats', contest_slug=contest_slug)
        )

    user_challenges = challenges_query(contest.id, current_user.id)
    needed_challenges = (
        challenges.EXTRA_COUNT + 1 -
        user_challenges.filter_by(solved=None).count()
    )
    if needed_challenges > 0:
        challenges.generate(
            contest.id,
            current_user.id,
            how_many=needed_challenges,
        )

    if pk is None:
        return next_challenge(user_challenges, contest_slug)

    this_challenge = user_challenges.filter_by(id=pk).options(
        joinedload(UserCrossword.crossword).undefer(Crossword.description),
    ).first()
    if not this_challenge:
        abort(404)

    if this_challenge.solved:
        flash(
            f"You have solved \"{this_challenge.crossword.name}\", "
            f"congratulations!",
            category='info',
        )
        return next_challenge(user_challenges, contest_slug)

    remaining_challenges = user_challenges.filter(
        UserCrossword.id != pk,
    ).filter_by(
        solved=None,
    ).limit(challenges.EXTRA_COUNT).all()

    return render_template(
        'crossword/challenge.html',
        contest=contest,
        challenge=this_challenge,
        remaining_challenges=remaining_challenges,
        pk=pk,
    )


@blueprint.route('/<contest_slug>/stats')
def stats(contest_slug):
    """Hall of fame"""
    contest = get_contest(contest_slug)
    set_request_contest(contest)

    stages = [
        {
            'id': s.id,
            'name': s.name,
            'stats': [],
            'finish': s.finish,
        }
        for s in db.session.query(
            ContestStage
        ).filter_by(
            contest_id=contest.id,
        ).order_by(
            ContestStage.finish.desc()
        )
    ]

    for stage in stages:
        stage['stats'] = db.session.query(
            ContestStageWinner
        ).join(User).order_by(
            ContestStageWinner.score.desc()
        ).filter(
            ContestStageWinner.contest_stage_id == stage['id']
        ).all()

    winner_ids = list(sorted(set(
        itertools.chain.from_iterable(
            (u.id for u in s['stats'])
            for s in stages
        )
    )))

    contest_stats = db.session.query(
        UserStats,
    ).join(User).filter(
        UserStats.contest_id == contest.id,
        UserStats.user_id.notin_(winner_ids),
        User.display_name.isnot(None),
    ).order_by(
        UserStats.score.desc(),
    )

    top_score = contest_stats.first()

    top_stats = list(
        contest_stats.limit(10).all()
    )

    player_score = None
    if not current_user.is_anonymous and not any(
            current_user.id == stat.user_id for stat in top_stats
    ):
        player_score = contest_stats.filter(
            UserStats.user_id == current_user.id,
        ).first()

    return render_template(
        'public/stats.html',
        contest=contest,
        player_score=player_score,
        stages=stages,
        stats=top_stats,
        top_score=top_score,
    )


@blueprint.route('/<contest_slug>/rules')
def rules(contest_slug):
    """Hall of fame"""
    return render_template(
        'public/rules.html',
    )
