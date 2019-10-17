from starlette.responses import JSONResponse
from starlette.requests import Request

from dmeister.validation import validate_put_service_request
from .dataaccess import serviceda, endpointda


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
        endpoints_dictionary[endpoint['path']] = endpoint

    existing_endpoints = await endpointda.get_endpoints(internal_data=True)
    existing_endpoints_dict = {}
    for endpoint in existing_endpoints:
        existing_endpoints_dict[endpoint['path']] = endpoint

    service_existing_endpoints = await endpointda.get_endpoints(service_name=service_name, internal_data=True)
    for ep in service_existing_endpoints:
        if ep['path'] not in endpoints_dictionary:
            if ep['new_service']:
                await _move_endpoint_to_new_service(ep['path'], ep['new_service'], ep['methods'])
            else:
                await endpointda.delete_endpoint(ep['path'])

    taken_endpoints = []
    for ep in endpoints:
        if ep['path'] in existing_endpoints_dict:
            existing_ep = existing_endpoints_dict[ep['path']]
            if existing_ep['service'] == service_name:
                await endpointda.update_endpoint(ep['path'], service_name, methods=ep['methods'])
            else:
                if existing_ep['locked']:
                    taken_endpoints.append(ep['path'])
                    continue
                elif existing_ep['new_service'] == service_name:
                    continue
                elif existing_ep['new_service'] is None:
                    await endpointda.update_endpoint(ep['path'],
                                                     existing_ep['service'],
                                                     new_service=service_name,
                                                     locked=True)
                else:
                    taken_endpoints.append(ep['path'])
                    continue
        else:
            await endpointda.add_endpoint(ep['path'], ep['methods'], service_name)

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


async def _move_endpoint_to_new_service(path, service, methods):
    await endpointda.update_endpoint(path, service,
                                     methods=methods,
                                     deprecated=False,
                                     locked=True,
                                     toggle=None,
                                     new_service=None)
