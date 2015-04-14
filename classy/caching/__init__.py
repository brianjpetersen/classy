# standard libraries
pass
# third party libraries
pass
# first party libraries
pass

"""
if self.cache:
    etag_hash = hash((file_iterator.last_modified,
                      file_iterator.content_length,
                      self.filename))
    self.response.etag = str(etag_hash)
    self.response.conditional_response = True
    self.response.last_modified = file_iterator.last_modified
"""