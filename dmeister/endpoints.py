import re

from starlette.requests import Request
from starlette.responses import JSONResponse

from .dataaccess import endpointda


async def get_all_endpoints(request: Request):
    results = await endpointda.get_endpoints()
    return JSONResponse({'endpoints': results})


async def get_endpoints_for_service(request: Request):
    service_name = request.path_params.get('name')
    results = await endpointda.get_endpoints(service_name=service_name)
    if results:
        return JSONResponse({'endpoints': results})
    else:
        return JSONResponse({'message': f'Service by the name {service_name} doesnt exist'},
                            status_code=404)


async def patch_endpoints_for_service(request: Request):
    service_name = request.path_params.get('name')
    body = await request.json()
    endpoints = body.get('endpoints')
    if not endpoints:
        return JSONResponse({'message': "'endpoints' is a required field"})
    existing_endpoints = await endpointda.get_endpoints(internal_data=True)
    endpoints_dictionary = {}
    for endpoint in existing_endpoints:
        endpoints_dictionary[endpoint['path']] = endpoint

    results = []
    for ep in endpoints:
        if ep['path'] not in endpoints_dictionary:
            path = ep['path']
            return JSONResponse({'message': f'endpoint with path {path} does not exist'},
                                status_code=404)
        else:
            existing_ep = endpoints_dictionary[ep['path']]
            if not existing_ep['service'] == service_name:
                if not existing_ep.get('new_service') == service_name:
                    return JSONResponse({'message': 'cannot PATCH an endpoint owned by another service'},
                                        status_code=400)
                ep = await endpointda.update_endpoint(ep['path'],
                                                      existing_ep['service'],
                                                      toggle=ep.get('toggle'))
                results.append(ep)
            ep = await endpointda.update_endpoint(ep['path'],
                                                  service_name,
                                                  locked=ep.get('locked'),
                                                  deprecated=ep.get('deprecated'))
            results.append(ep)

    return JSONResponse({'endpoints': results})


async def search_endpoints(request: Request):
    body = await request.json()
    paths = body.get('paths')
    if not paths:
        return JSONResponse({'message': "'paths' is a required field"}, status_code=400)

    results = await endpointda.get_endpoints(paths)

    path_pattern_dict = {}
    for row in results:
        path = row['path']
        path_pattern_dict[path] = re.compile(_replace_wildcards_with_regex(path))

    possible_endpoints_dict = {}
    for path in paths:
        possible_endpoints_dict[path] = []

    for row in results:
        for path in paths:
            matches = path_pattern_dict[row['path']].match(path)
            if matches:
                possible_endpoints_dict[path].append(row)

    path_to_endpoints_dict = {}
    for path in paths:
        endpoint = None
        possible_endpoints = possible_endpoints_dict[path]
        if len(possible_endpoints) == 1:
            endpoint = possible_endpoints[0]
        elif len(possible_endpoints) > 1:
            for e in possible_endpoints:
                if path == e['path']:
                    endpoint = e
        path_to_endpoints_dict[path] = endpoint

    return JSONResponse(path_to_endpoints_dict)


# Supports wildcards before . : / $
def _replace_wildcards_with_regex(path):
    return re.sub(re.compile(r"({.*?}([/:.]|$))"), _replacement_func, path)


def _replacement_func(obj):
    match = obj.group(0)
    if match.endswith(('/', ':', '.')):
        return f'([^/:.]*){match[-1]}'
    else:
        return '([^/:.]*$)'
