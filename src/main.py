import asyncio

from flask import Flask, request, abort, jsonify

from hypercorn.config import Config
from hypercorn.asyncio import serve

from auth import requires_token
from artifact import Artifact

app = Flask(__name__)


@app.route('/artifacts', methods=['POST'])
@requires_token
async def create_artifact():
    json_data = request.get_json()

    for k in ['title', 'content']:
        if k not in json_data:
            abort(400, f'Missing required field {k}')
    
    a = Artifact(json_data['title'], json_data['content'])
    
    asyncio.create_task(a.save())

    return jsonify(a.to_dict(['id', 'token']))


@app.route('/artifacts/_<string:id>', methods=['GET'])
async def get_artifact(id: str):
    a = Artifact.load(id)

    if 'token' in request.args:
        if request.args['token'] == a.token:
            if request.content_type is not None:
                if 'text/html' in request.content_type:
                    return a.content
                elif 'application/json' in request.content_type:
                    return jsonify(a.to_dict())
                else:
                    return abort(400)
            else:
                return a.content
        else:
            abort(401, 'Invalid token.')
    else:
        abort(401, 'Missing token.')


@app.route('/artifacts/list', methods=['GET'])
@requires_token
async def get_artifact_list():
    if 'application/json' in request.content_type:
        return jsonify(await Artifact.get_artifacts())
    else:
        return abort(400)


if __name__ == '__main__':
    config = Config()
    config.bind = ['0.0.0.0:8001']

    asyncio.run(serve(app, config))