from starlette.responses import JSONResponse
from starlette.requests import Request

from .dataaccess import serviceda, endpointda


async def get_services(request: Request):
    results = await serviceda.get_services()
    return JSONResponse({'services': results})


async def get_service(request: Request):
    service_name = request.path_params.get('name')
    results = await serviceda.get_services(service_name=service_name)
    if results:
        return JSONResponse(results[0])
    else:
        return JSONResponse({'message': f'Service by the name {service_name} doesnt exist'},
                            status_code=404)


async def put_service(request: Request):
    body = await request.json()
    service_name = body.get('name')
    protocols = body.get('protocols')
    endpoints = body.get('endpoints')
    squad = body.get('squad')
    meta = body.get('meta')

    if not service_name:
        return JSONResponse({'message': "'name' is a required field"}, status_code=400)

    if not protocols:
        return JSONResponse({'message': "'protocols' is a required field"}, status_code=400)

    if not endpoints:
        return JSONResponse({'message': "'endpoints' is a required field"}, status_code=400)

    existing_endpoints = await endpointda.get_endpoints(internal_data=True)
    endpoint_dictionary = {}
    for endpoint in existing_endpoints:
        endpoint_dictionary[endpoint['path']] = endpoint

    taken_endpoints = []
    for ep in endpoints:
        if ep['path'] in endpoint_dictionary:
            existing_ep = endpoint_dictionary[ep['path']]
            if existing_ep['service'] == service_name:
                continue
            else:
                if existing_ep['locked']:
                    taken_endpoints.append(ep['path'])
                    continue
                elif existing_ep['new_service'] == service_name:
                    continue
                elif existing_ep['new_service'] is None:
                    return JSONResponse({'message': 'taking over routes is not yet supported'}, status_code=400)
                else:
                    taken_endpoints.append(ep['path'])
                    continue
        else:
            await endpointda.add_endpoint(ep['path'], ep['methods'], service_name)

    if taken_endpoints:
        return JSONResponse({'message': 'failed to register existing paths',
                             'paths': taken_endpoints}, status_code=409)

    results = await serviceda.insert_service(service_name, protocols, squad, meta)
    return JSONResponse(results[0])
