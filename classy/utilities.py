# standard libraries
pass
# third party libraries
pass
# first party libraries
pass

def copy_headers(source, destination):
    source_headers = source.headers.copy()
    destination.headers.update(source_headers)
    return destination