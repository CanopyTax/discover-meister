import re
import urllib.parse

from starlette.requests import Request
from starlette.responses import JSONResponse

from dmeister.validation import validate_patch_endpoints_request
from .dataaccess import endpointda


async def get_all_endpoints(request: Request):
    path = request.query_params.get('path')
    from_db = await endpointda.get_endpoints()

    if path:
        search_term = urllib.parse.unquote(path)
        results = _filter_endpoints(search_term, from_db)
    else:
        results = from_db
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
    body = await request.json()
    validate_patch_endpoints_request(request, body)

    service_name = request.path_params.get('name')
    endpoints = body.get('endpoints')

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

    results = await endpointda.get_endpoints()

    tree = _create_tree(results)
    dictionary = _create_dictionary(results)

    path_to_endpoints_dict = {}
    for p in paths:
        path_to_endpoints_dict[p] = _resolve_path(p, tree, dictionary)

    return JSONResponse(path_to_endpoints_dict)


# Supports wildcards before . : / $
def _replace_wildcards_with_regex(path):
    return re.sub(re.compile(r"({.*?}([/:.]|$))"), _replacement_func, path)


def _replacement_func(obj):
    match = obj.group(0)
    if match.endswith(('/', ':', '.')):
        return f'([^/:.]*){match[-1]}'
    else:
        return '([^/:.]*)'


def _filter_endpoints(search_term, endpoints):
    if search_term[0] == '/':
        search_term = search_term[1:]
    len_parts = len(search_term.split('/'))
    results = []
    # Will attempt to first find endpoints that contain the search term exactly
    next_generators = [[search_term]]
    for n in range(-1, len_parts - 1):
        """
        In each iteration n thereafter, a set is generated containing regular expressions that will match paths
        containing any of the possible combinations of the search term split by '/' and n parts replaced by
        wildcards. For example if the search term is 'A/B/C' the first iteration would produce the regex set [
        '*/B/C', # 'A/*/C', 'A/B/*'] and so on... Each new set of regular expressions is generated using the
        previous set.
        """
        check_patterns, next_generators = _get_next_search_iteration(n, search_term, len_parts, next_generators)
        for e in endpoints:
            to_match = e['path']
            match = False
            for p in check_patterns:
                if p.match(to_match):
                    match = True
            if match:
                results.append(e)
        """
        Before the next iteration, the set of endpoints is compared to the set of regular expressions to find any
        matches. If any are found the loop is broken and the results are returned.
        """
        if len(results) > 0:
            break

    return sorted(results, key=lambda e: _sort_by_path_hierarchy(e, search_term))


def _get_next_search_iteration(iteration, search_term, num_search_parts, generators):
    if iteration < 0:
        return [re.compile(r'^.*' + search_term + '.*$')], [[search_term]]

    regex_patterns = []
    next_generators = []

    for li in generators:
        if iteration == 0:
            num_generators_to_use = num_search_parts - iteration
        else:
            num_generators_to_use = len(li) - 1

        repl_start_list = num_search_parts - num_generators_to_use
        repl_start = repl_start_list
        for pattern_idx in range(min(num_generators_to_use, len(li))):
            pattern = li[pattern_idx]
            new_generators = []
            for r in range(repl_start, num_search_parts):
                generator = _rep_n(pattern, r)
                search_pattern = r'^.*' + generator.replace('***', '{[^/]*}') + '.*$'
                regex_patterns.append(re.compile(search_pattern))
                new_generators.append(generator)
            next_generators.append(new_generators)
            repl_start += 1

    return regex_patterns, next_generators


def _rep_n(s, n, spl='/'):
    parts = s.split(spl)
    result = ''
    for x in range(len(parts)):
        # only match paths where the first part matches so dont replace first part with regex
        if x == n and not x == 0:
            result += '***'
        else:
            result += parts[x]
        if not x == len(parts) - 1:
            result += '/'

    return result


def _sort_by_path_hierarchy(endpoint, search_term):
    path = endpoint['path']
    index = path.find(search_term)
    return path.count('/', 0, index)


def _create_tree(endpoints):
    tree = {}
    for e in endpoints:
        path = e['path'].strip('/')
        sub = tree
        for portion in path.split('/'):
            portion = re.sub(re.compile(r'{.*?}'), '{}', portion)
            if sub.get(portion, None) is None:
                sub[portion] = {}
            sub = sub[portion]
    return tree


def _create_dictionary(endpoints):
    dictionary = {}
    for e in endpoints:
        path = re.sub(re.compile(r'{.*?}'), '{}', e['path'])
        dictionary[path] = e
    return dictionary


def _resolve_path(path, tree, endpoint_dictionary):
    lookup_path = ''
    sub = tree
    path = path.strip('/')
    for part in path.split('/'):
        portion = part
        if sub.get(part, None) is None:
            portion = '{}'
            if ':' in part:
                portion += ':' + part.split(':')[1]
        if sub.get(portion, None) is None:
            return None
        lookup_path += '/' + portion
        sub = sub[portion]
    return endpoint_dictionary.get(lookup_path, None)
