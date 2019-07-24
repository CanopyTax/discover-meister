import os
import pathlib
import secrets
from json import JSONDecodeError

import uvicorn
from asyncpgsa import pg
from starlette.applications import Starlette
from starlette.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import HTMLResponse, JSONResponse
from starlette.middleware.authentication import AuthenticationMiddleware
from sentry_asgi import SentryMiddleware
import sentry_sdk

from . import services, health, endpoints
from .security import GoogleAuthBackend


DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
LOCAL_DEV = os.getenv('IS_LOCAL', 'false').lower() == 'true'
GOOGLE_ID = os.getenv('GOOGLE_ID')
GOOGLE_SECRET = os.getenv('GOOGLE_SECRET')
GOOGLE_ORG = os.getenv('GOOGLE_ORG')
COOKIE_NAME = os.getenv('COOKIE_NAME', 'dmeister-auth')
COOKIE_KEY = os.getenv('COOKIE_KEY') or secrets.randbits(60)
POSTGRES_URL = os.getenv('DATABASE_URL', 'localhost')
POSTGRES_USERNAME = os.getenv('DATABASE_USER', 'postgres')
POSTGRES_PASSWORD = os.getenv('DATABASE_PASS', 'password')
POSTGRES_DB_NAME = os.getenv('DATABASE_DB_NAME', 'postgres')
POSTGRES_MIN_POOL_SIZE = int(os.getenv('DATABASE_MIN_POOL_SIZE', '2'))
POSTGRES_MAX_POOL_SIZE = int(os.getenv('DATABASE_MAX_POOL_SIZE', '4'))
SENTRY_URL = os.getenv('SENTRY_URL')
ENV_NAME = os.getenv('ENV_LOCATION', 'local')


if (not LOCAL_DEV) and None in (GOOGLE_ID, GOOGLE_SECRET, GOOGLE_ORG):
    raise ValueError('GITHUB_ID, GITHUB_SECRET or GITHUB_ORG'
                     ' environment variables are missing')


async def pg_init():
    await pg.init(
        user=POSTGRES_USERNAME,
        password=POSTGRES_PASSWORD,
        host=POSTGRES_URL,
        database=POSTGRES_DB_NAME,
        min_size=POSTGRES_MIN_POOL_SIZE,
        max_size=POSTGRES_MAX_POOL_SIZE,
    )


def init():
    app = Starlette()

    @app.on_event("startup")
    async def async_setup():
        await pg_init()

    @app.exception_handler(JSONDecodeError)
    async def bad_json(request, exc):
        return JSONResponse({'reason': 'invalid json', 'details': str(exc)}, status_code=400)

    # auth stuff
    auth = GoogleAuthBackend(GOOGLE_ID, GOOGLE_SECRET, GOOGLE_ORG)
    app.add_middleware(AuthenticationMiddleware,
                       backend=auth,
                       on_error=auth.on_error)

    app.add_middleware(SessionMiddleware, session_cookie=COOKIE_NAME,
                       secret_key=COOKIE_KEY, https_only=not LOCAL_DEV,
                       max_age=2 * 24 * 60 * 60)  # 2 days

    # sentry stuff
    sentry_sdk.init(dsn=SENTRY_URL, environment=ENV_NAME)
    app.add_middleware(SentryMiddleware)

    async def index_html(request):
        static = pathlib.Path('dmeister/static/index.html')
        return HTMLResponse(static.read_text())

    app.add_route('/api/services', services.get_services, methods=['GET'])
    app.add_route('/api/services/{name}', services.get_service, methods=['GET'])
    app.add_route('/api/services/{name}', services.put_service, methods=['PUT'])
    app.add_route('/api/endpoints', endpoints.get_all_endpoints, methods=['GET'])
    app.add_route('/api/endpoints:search', endpoints.search_endpoints, methods=['POST'])
    app.add_route('/api/services/{name}/endpoints', endpoints.get_endpoints_for_service, methods=['GET'])
    app.add_route('/api/services/{name}/endpoints', endpoints.patch_endpoints_for_service, methods=['PATCH'])
    app.add_route('/heartbeat', health.get_health)
    app.add_route('/', index_html)

    app.mount('/public/', app=StaticFiles(directory='dmeister/static/public'), name='static')

    @app.exception_handler(404)
    async def serve_index_on_unknown_routes(request, exc):
        if request.url.path.startswith('/api'):
            return JSONResponse({'message': 'not found'}, status_code=404)
        else:
            return await index_html(request)

    @app.exception_handler(400)
    async def handle_malformed_request(request, exc):
        return JSONResponse({'message': exc.detail}, status_code=400)

    return app


def main(app=None):
    # setup
    if app is None:
        app = init()

    kwargs = {}
    if LOCAL_DEV:
        kwargs['reload'] = True
    else:
        kwargs['workers'] = 2

    uvicorn.run(app, host='0.0.0.0', http='h11', port=8080, headers=[('Server', 'dmeister')],
                proxy_headers=True, **kwargs)


if __name__ == '__main__':
    main()
