from .models import Gist

DATETIME_PREFIXES = ('created_at', 'updated_at')


def is_datetime_param(param):
    for prefix in DATETIME_PREFIXES:
        if param.startswith(prefix):
            return True
    return False


def get_operator(comparison):
    return {
        'lt': '<',
        'lte': '<=',
        'gt': '>',
        'gte': '>=',
    }[comparison]
    


def build_query(**kwargs):
    query = 'SELECT * FROM gists'
    values = {}
    filters = []

    for param, value in kwargs.items():
        if is_datetime_param(param):
            if '__' in param:
                attribute, comparison = param.split('__')
                operator = get_operator(comparison)
                filters.append(f"datetime({attribute}) {operator} datetime(:{param})")
            else:
                filters.append(f"datetime({param}) = datetime(:{param})")
        else:
            filters.append(f"{param} = :{param}")
        values[param] = value

    if filters:
        query += ' WHERE ' + ' AND '.join(filters)

    return query, values

def search_gists(db_connection, **kwargs):
    query, params = build_query(**kwargs)
    cursor = db_connection.execute(query, params)
    results = []
    for gist in cursor:
        results.append(Gist(gist))
    return results