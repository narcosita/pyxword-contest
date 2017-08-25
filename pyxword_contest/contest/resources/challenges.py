"""
Challenges API resources
"""
import random

from flask import url_for, Response, request
from flask_apispec import MethodResource, doc
from flask_login import login_required, current_user
from flask_restful import Resource, abort
from sqlalchemy.orm import load_only, joinedload
from werkzeug import exceptions

from pyxword_contest.contest import challenges
from pyxword_contest.contest.challenges import challenges_query
from pyxword_contest.contest.models import UserCrossword
from pyxword_contest.contest.utils import (
    get_contest,
    set_request_contest,
)
from pyxword_contest.crossword.models import Crossword
from pyxword_contest.crossword.utils import clean, compare
from pyxword_contest.extensions import (
    db,
    limiter,
)


class ChallengesResource(Resource, MethodResource):
    method_decorators = [
        login_required,
        limiter.limit('10/minute'),
    ]

    @doc(
        summary='Gets list of available challenges',
        responses={
            200: {'description': 'Success'},
        },
    )
    def get(self, contest_slug):
        contest = get_contest(contest_slug)
        db.session.expunge(contest)  # prevent reloading from db
        set_request_contest(contest)
        if not contest.active:
            raise abort(400, message="Contest already ended")

        available_challenges = challenges_query(
            contest.id, current_user.id
        ).filter_by(
            solved=None,
        )

        limit = challenges.EXTRA_COUNT + 1

        needed_challenges = limit - available_challenges.count()
        if needed_challenges > 0:
            challenges.generate(
                contest.id,
                current_user.id,
                how_many=needed_challenges,
            )

        available_challenges = available_challenges.options(
            load_only(UserCrossword.id),
        ).limit(limit)

        return [
            url_for(
                'contest_api.Challenge',
                contest_slug=contest_slug,
                pk=ch.id,
            )
            for ch in available_challenges
        ]


class ChallengeResource(Resource, MethodResource):
    method_decorators = [
        login_required,
        limiter.limit('60/minute'),
    ]

    def get_object(self, contest_slug, pk):
        contest = get_contest(contest_slug)
        db.session.expunge(contest)  # prevent reloading from db
        set_request_contest(contest)
        if not contest.active:
            raise exceptions.BadRequest("Contest already ended")

        user_challenges = challenges_query(contest.id, current_user.id)
        this_challenge = user_challenges.filter_by(id=pk).options(
            joinedload(UserCrossword.crossword).undefer(Crossword.description),
        ).first()
        if not this_challenge:
            abort(404)

        if this_challenge.solved:
            raise exceptions.Gone("Challenge already solved")

        return this_challenge

    @doc(
        summary='Get challenge',
        responses={
            200: {'description': "Success"},
        },
    )
    def get(self, contest_slug: str, pk: int):
        this_challenge = self.get_object(contest_slug, pk)

        return Response(
            clean(this_challenge.crossword.body),
            mimetype='text/plain',
        )

    @doc(
        summary='Submit solution challenge',
        responses={
            204: {'description': "Solution was correct"},
        },
    )
    def put(self, contest_slug: str, pk: int):
        this_challenge = self.get_object(contest_slug, pk)
        try:
            submitted_solution = request.data.decode('utf-8')
        except UnicodeDecodeError:
            submitted_solution = ''
        this_challenge.solution = clean(submitted_solution)

        diff = compare(
            this_challenge.solution,
            this_challenge.crossword.solution
        )
        if diff == 0:
            challenges.solved(this_challenge)

            return Response(
                'Success!',
                status=204,
            )

        todo = this_challenge.crossword.body.count('*')
        error = 10
        misses = int(diff / todo * 100) + random.randint(-error, error)
        if misses < 1:
            misses = 1
        elif misses > 100:
            misses = 100

        db.session.commit()
        abort(422, message=(
            f'This is not valid solution, '
            f'try something else (around {100-misses}% was correct '
            f'+-{error}%)'
        ))
