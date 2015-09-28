import os


def debug_msg(message, display):
    '''
    This function takes a string and a boolean (display) that says whether to
    print the string or not.
    '''
    if display:
        print(message)


def contruct_image_label(run, version):

    catalog_number = 'None'
    if run['catalog_prefix']:
        if 'IP' in run['unique_id']:  # Special fix for Yale
            catalog_number = run['catalog_prefix']+' '+run['unique_id'].split('.')[1]
        else:
            catalog_number = run['catalog_prefix']+' '+run['unique_id']

    text = []
    text.append('%4.2f %s per pixel | Age and Source:  %s from %s'
                % (run['units_per_pixel'], run['unit'], run['age'], run['source']))
    this_line = 'Processed at '+run['location']

    if run['author']:
        this_line += ' by '+run['author']
    this_line += ' (Catalog Number: %s)' % catalog_number

    text.append(this_line)
    text.append('CODE VERSION: %s, PROCESSED ON: %s' % (version, run['timestamp']))
    text.append('Threshold of %4.2f and size filter of %d - %d %s'
                % (run['threshold'], run['minimumSize'], run['maximumSize'], run['unit']))
    text.append('Directory: %s' % run['subdirectory'])

    return text
