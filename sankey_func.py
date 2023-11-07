def get_sankey(data,path,value_col):
    sankey_data = {
    'label':[],
    'source': [],
    'target' : [],
    'value' : []
    }
    counter = 0
    while (counter < len(path) - 1):
        for parent in data[path[counter]].unique():
            sankey_data['label'].append(parent)
            for sub in data[data[path[counter]] == parent][path[counter+1]].unique():
                sankey_data['source'].append(sankey_data['label'].index(parent))
                sankey_data['label'].append(sub)
                sankey_data['target'].append(sankey_data['label'].index(sub))
                sankey_data['value'].append(data[data[path[counter+1]] == sub][value_col].sum())
                
        counter +=1
    return sankey_data