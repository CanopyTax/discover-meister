from copy import copy

import howard
from starlette.responses import JSONResponse
from starlette.requests import Request

from dmeister.validation import validate_put_service_request
from .dataaccess import serviceda, endpointda
from . import endpoints as endpoints_
from .models import Endpoint


async def get_services(request: Request):
    host = request.url.scheme + '://' + request.url.hostname
    results = await serviceda.get_services()
    for service in results:
        name = service['name']
        service['endpoints'] = f'{host}/services/{name}/endpoints'
    return JSONResponse({'services': results})


async def get_service(request: Request):
    host = request.url.scheme + '://' + request.url.hostname
    service_name = request.path_params.get('name')
    results = await serviceda.get_services(service_name=service_name)
    if results:
        service = results[0]
        service['endpoints'] = f'{host}/services/{service_name}/endpoints'
        return JSONResponse(service)
    else:
        return JSONResponse({'message': f'Service by the name {service_name} doesnt exist'},
                            status_code=404)


async def put_service(request: Request):
    body = await request.json()
    validate_put_service_request(request, body)

    host = request.url.scheme + '://' + request.url.hostname
    if request.url.port:
        host += str(request.url.port)

    service_name = request.path_params.get('name')
    protocols = body.get('protocols')
    endpoints = body.get('endpoints')
    meta = body.get('meta')

    endpoints_dictionary = {}
    for endpoint in endpoints:
        ep: Endpoint = howard.from_dict(endpoint, Endpoint)
        endpoints_dictionary[ep.stripped_path] = ep

    existing_endpoints = await endpoints_.get_existing_endpoints()

    service_existing_endpoints = {k: ep for k, ep in existing_endpoints.items()
                                  if ep.service == service_name}
    for k, ep in service_existing_endpoints.items():
        if k not in endpoints_dictionary:
            if ep.new_service:
                await _move_endpoint_to_new_service(ep)
            else:
                await endpointda.delete_endpoint(ep.stripped_path)

    taken_endpoints = []
    for stripped_path, ep in endpoints_dictionary.items():
        if stripped_path in existing_endpoints:
            existing_ep = existing_endpoints[stripped_path]
            if existing_ep.service == service_name:
                diff = copy(existing_ep)
                diff.path = ep.path
                diff.methods = ep.methods
                await endpointda.update_endpoint(diff)
            else:
                if existing_ep.locked:
                    taken_endpoints.append(ep.path)
                    continue
                elif existing_ep.new_service == service_name:
                    continue
                elif not existing_ep.new_service:
                    diff = copy(existing_ep)
                    diff.new_service = service_name
                    diff.locked = True

                    await endpointda.update_endpoint(diff)
                else:
                    taken_endpoints.append(ep.path)
                    continue
        else:
            ep.service = service_name
            await endpointda.add_endpoint(ep)

    if taken_endpoints:
        return JSONResponse({'message': 'failed to register existing paths',
                             'paths': taken_endpoints}, status_code=409)

    result = await serviceda.insert_service(service_name, protocols, meta)

    result['endpoints'] = f'{host}/services/{service_name}/endpoints'
    return JSONResponse(result)


async def delete_service(request: Request):
    service_name = request.path_params.get('name')
    results = await serviceda.get_services(service_name=service_name)
    if not results:
        return JSONResponse({'message': f'Service "{service_name}" not found'}, status_code=404)

    await serviceda.delete_service(service_name=service_name)
    return JSONResponse(status_code=204)


async def _move_endpoint_to_new_service(endpoint):
    diff = copy(endpoint)
    diff.deprecated = False
    diff.locked = True
    diff.toggle = ''
    diff.service = endpoint.new_service
    diff.new_service = ''

    await endpointda.update_endpoint(endpoint)
