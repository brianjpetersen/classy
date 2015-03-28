# standard libraries
import os
import datetime
import json
# third party libraries
import rethinkdb
import delorean
# first party libraries
import classy
import tiny_id

DATA_PATH = 'data'

class RethinkDBController(classy.Controller):

    def before_handler_called(self):
        self.connection = rethinkdb.connect()

    def before_response_returned(self):
        self.connection.close()

class Transmissions(RethinkDBController):

    def before_handler_called(self):
        super(Transmissions, self).before_handler_called()
        database = self.database = rethinkdb.db('test')
        try:
            database.table_create('transmissions').run(self.connection)
        except:
            pass
        finally:
            table = self.table = database.table('transmissions')

    def get(self, scan_id=None):
        if scan_id is None:
            raw_after = self.request.params.get('after', datetime.datetime.min.isoformat())
            raw_before = self.request.params.get('before', datetime.datetime.max.isoformat())
            limit = self.request.params.get('limit', None)
            #
            after_datetime = delorean.parse(raw_after).datetime
            before_datetime = delorean.parse(raw_before).datetime
            # compose query
            when_received = rethinkdb.row['when_received']
            scans_between = when_received.during(after_datetime, before_datetime)
            pluck_function = lambda transmission: {'when': transmission['when_received'].to_iso8601(), 
                                                   'scan_id': transmission['id']}
            descending_date_order = rethinkdb.desc('when_received')
            query = self.table.filter(scans_between).order_by(descending_date_order).map(pluck_function)
            try:
                limit = int(limit)
                query = query.limit(limit)
            except TypeError:
                pass
            results = list(query.run(self.connection))
            # return results
            self.response.content_type = 'application/json'
            return json.dumps(list(results))
        else:
            try:
                with open(os.path.join(DATA_PATH, scan_id), 'rb') as f:
                    raw_transmission = f.read()
            except IOError:
                raise classy.exceptions.HTTPNotFound
            # return result
            self.response.content_type = 'application/octet-stream'
            return raw_transmission

    def post(self):
        raw_transmission = self.request.body
        # persist data
        try:
            transmission_id = tiny_id.random.generate(10)
            when_received = delorean.Delorean().datetime
            with open(os.path.join(DATA_PATH, transmission_id), 'wb') as f:
                f.write(raw_transmission)
            transmission_data = {'id': transmission_id, 'when_received': when_received}
            self.table.insert(transmission_data).run(self.connection)
            response = chr(0)
        except:
            response = chr(1)
        # setup response
        self.response.content_type = 'application/octet-stream'
        return response

class Root(classy.Controller):
    
    transmissions = Transmissions

    def get(self):
        return 'Welcome to Podimetrics\' temporary Device Layer deployment for motherboard testing.' 

app = classy.application
app.add_route('/', Root)

if __name__ == '__main__':

    classy.serve(port=8080)