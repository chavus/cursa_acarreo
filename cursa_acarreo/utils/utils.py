def nonify_dict(dict):
    for key in dict:
        if dict[key] == '':
            dict[key] = None
    return dict
