from starlette.responses import JSONResponse
from starlette.requests import Request

from .dataaccess import endpointda


async def get_all_endpoints(request: Request):
    results = await endpointda.get_endpoints()
    return JSONResponse({'endpoints': results})


async def get_endpoints_for_service(request: Request):
    service_name = request.path_params.get('name')
    results = await endpointda.get_endpoints(service_name=service_name)
    if results:
        return JSONResponse(results[0])
    else:
        return JSONResponse({'message': f'Service by the name {service_name} doesnt exist'},
                            status_code=404)
