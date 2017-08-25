from flask import Blueprint
from flask_restful import Api

from pyxword_contest.extensions import csrf_protect
from .resources.challenges import (
    ChallengeResource,
    ChallengesResource,
)

contest_api_blueprint = Blueprint(
    'contest_api', __name__, url_prefix='/api/<contest_slug>',
)

contest_api = Api(contest_api_blueprint)

contest_api.add_resource(
    ChallengesResource, '/challenges', endpoint='Challenges',
)
contest_api.add_resource(
    ChallengeResource, '/challenges/<int:pk>', endpoint='Challenge',
)

# disable CSRF for API
csrf_protect.exempt(contest_api_blueprint)
