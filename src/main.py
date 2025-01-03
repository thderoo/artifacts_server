import asyncio
import os

from flask import Flask, request, abort, jsonify, render_template

from hypercorn.config import Config
from hypercorn.asyncio import serve

from auth import requires_token
from artifact import Artifact

app = Flask(__name__, template_folder='../templates/')


@app.route('/artifacts', methods=['POST'])
@requires_token
async def create_artifact():
    json_data = request.get_json()
    
    a = Artifact(json_data['title'], json_data['content'])
    
    asyncio.create_task(a.save())

    return jsonify(a.to_dict(['id', 'token']))


@app.route('/artifacts/_<string:id>', methods=['GET'])
async def get_artifact(id: str):
    a = Artifact.load(id)

    if 'token' in request.args:
        if request.args['token'] == a.token:
            if 'source' in request.args:
                return a.content

            if request.accept_mimetypes is not None:
                best_match = request.accept_mimetypes.best_match(['text/html', 'application/json'])

                if best_match == 'text/html':
                    return render_template('index.html', id=a.id, token=a.token, title=a.title)
                elif best_match == 'application/json':
                    if 'only_modified_at' in request.args:
                        return jsonify(a.to_dict(['modified_at']))
                    else:
                        json_artifact = a.to_dict()

                        if 'rendered' in request.args:
                            json_artifact['content'] = render_template('frame_content.html', content=json_artifact['content'])

                        return jsonify(json_artifact)
                else:
                    return abort(400)
            else:
                return render_template('index.html', id=a.id, token=a.token, title=a.title)
        else:
            abort(401, 'Invalid token.')
    else:
        abort(401, 'Missing token.')


@app.route('/artifacts/_<string:id>', methods=['POST'])
@requires_token
async def edit_artifact(id: str):
    json_data = request.get_json()
    
    a = Artifact.load(id)
    a.edit(**json_data)
    await a.save()

    return '', 200


@app.route('/artifacts/list', methods=['GET'])
@requires_token
async def get_artifact_list():
    return jsonify(await Artifact.get_artifacts())


if __name__ == '__main__':
    config = Config()
    config.bind = ['0.0.0.0:443']
    config.certfile = 'cert/cert.pem'
    config.keyfile = 'cert/key.pem'

    os.makedirs('artifacts', exist_ok=True)

    asyncio.run(serve(app, config))
