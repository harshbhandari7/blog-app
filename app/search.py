'''
    The idea is to keep all the Elasticsearch code in this module.
    The rest of the application will use the functions in this new module to access the index and
    will not have direct access to Elasticsearch. This is important, because if one day we need to
    switch to a different engine, then all we  need to do is rewrite the functions in this module,
    and the application will continue to work as before.
'''

from flask import current_app

def add_to_index(index, model):
    if not current_app.elasticsearch:
        return
    
    payload = {}
    for field in model.__searchable__:
        payload[field] = getattr(model, field)
    
    current_app.elasticsearch.index(index=index, id=model.id, body=payload)

def remove_from_index(index, model):
    if not current_app.elasticsearch:
        return
    
    current_app.elasticsearch.delete(index=index, id=model.id)

def query_index(index, query, page, per_page):
    if not current_app.elasticsearch:
        return [], 0
    
    search_results = current_app.elasticsearch.search(
        index=index,
        body={
            'query': { 'multi_match': { 'query': query, 'fields': ['*'] } },
            'from': (page - 1) * per_page, 
            'size': per_page
        }
    )

    ids = [int(hit['_id']) for hit in search_results['hits']['hits']]

    # returns ids of all the search results and total no. of results
    return ids, search_results['hits']['total']['value']
