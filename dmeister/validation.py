from starlette.exceptions import HTTPException

from . import models


def validate_endpoints(endpoints, required_fields=None):
    if required_fields is None:
        required_fields = ['path']
    for e in endpoints:
        for f in required_fields:
            if not e.get(f):
                raise HTTPException(400, f"'{f}' is a required field for an endpoint")

        if 'methods' in required_fields or 'methods' in e:
            for m in e['methods']:
                if m.lower() not in models.ALLOWED_METHODS:
                    raise HTTPException(400, f"'{m}' is not a valid method")


def validate_patch_endpoints_request(request, body):
    _validate_request(request, body,
                      required_path_params=['name'],
                      required_body_fields=['endpoints'])
    validate_endpoints(body.get('endpoints'))


def validate_put_service_request(request, body):
    _validate_request(request, body,
                      required_path_params=['name'],
                      required_body_fields=['protocols', 'endpoints'])
    validate_endpoints(body.get('endpoints'), required_fields=['path', 'methods'])


def _validate_request(request, body, required_path_params, required_body_fields):
    for p in required_path_params:
        if p not in request.path_params:
            raise HTTPException(400, f"'{p}' is a required path parameter")

    for f in required_body_fields:
        if f not in body:
            raise HTTPException(400, f"'{f}' is a required field")
