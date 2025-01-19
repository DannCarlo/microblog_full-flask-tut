from flask import current_app

def add_to_index(index, model):
    if not current_app.elasticsearch:
        return
    payload = {}
    for field in model.__searchable__:
        payload[field] = getattr(model, field)
    current_app.elasticsearch.index(index=index, id=model.id, document=payload)

def remove_from_index(index, model):
    if not current_app.elasticsearch:
        return
    current_app.elasticsearch.delete(index=index, id=model.id)

def query_index(index, query, page, per_page):
    if not current_app.elasticsearch:
        return [], 0
    search = current_app.elasticsearch.search(
        index=index,
        query={'multi_match': {'query': query, 'fields': ['*']}},
        from_=(page - 1) * per_page,
        size=per_page)
    ids_data = dict()
    for hit in search['hits']['hits']:
        if hit["_score"] in ids_data:
            ids_data[hit["_score"]].append(hit["_id"])
        else:
            ids_data[hit["_score"]] = [hit["_id"]]

    # ids = [int(hit['_id']) for hit in search['hits']['hits']]
    # scores = [int(hit['_scores']) for hit in search['hits']['hits']]
    return ids_data, search['hits']['total']['value']