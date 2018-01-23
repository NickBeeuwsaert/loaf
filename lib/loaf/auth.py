import argparse
from wsgiref.simple_server import make_server
from urllib.parse import urljoin, urlencode
import logging
import json

from pyramid.config import Configurator
from pyramid.response import Response
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPSeeOther
import requests
import toml

from . import JSONType


@view_config(route_name='index')
def index(request):
    config = request.registry.settings['config']

    client_config = config['client']

    endpoint = client_config.get('endpoint', 'https://slack.com/api/')

    location = urljoin(endpoint, '/oauth/authorize')

    return HTTPSeeOther(f"""{location}?{urlencode({
        'client_id': client_config['id'],
        'scope': 'client',
        'redirect_uri': request.route_url('authorize')
    })}""")


@view_config(route_name='authorize', renderer='json')
def authorize(request):
    settings = request.registry.settings
    config = settings['config']
    client_config = config['client']
    endpoint = client_config.get('endpoint', 'https://slack.com/api/')

    response = requests.post(
        urljoin(endpoint, 'oauth.access'),
        data=dict(
            client_id=client_config['id'],
            client_secret=client_config['secret'],
            code=request.params['code'],
            redirect_uri=request.route_url(request.matched_route.name)
        )
    ).json()

    with open(settings['output'], 'w+') as fp:
        json.dump({
            **config,
            'team': [
                *config.get('team', []),
                {
                    'name': response['team_name'],
                    'token': response['access_token']
                }
            ]
        }, fp, indent=4)

    return response


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', default='config.json', type=JSONType)
    parser.add_argument('-o', '--output', default='config.json')
    parser.add_argument('-H', '--host', default='127.0.0.1')
    parser.add_argument('-p', '--port', default=6543, type=int)
    args = parser.parse_args()

    config = Configurator(settings=vars(args))
    config.scan(__name__)
    config.add_route('index', '/')
    config.add_route('authorize', '/oauth')

    print(f'Running on http://{args.host}:{args.port}/')
    app = config.make_wsgi_app()
    server = make_server(args.host, args.port, app)
    server.serve_forever()


if __name__ == '__main__':
    main()
