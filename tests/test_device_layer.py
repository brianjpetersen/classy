# standard libraries
import os
import datetime
import json
import glob
# third party libraries
import rethinkdb
import delorean
import passlib.hash
# first party libraries
import classy
import tiny_id

DATA_PATH = 'data'
HASHED_PASSWORDS_BY_USERNAME = {'sigmatron-manufacturing':   '$5$rounds=110000$HbOdkzprjm5OvVyl$/jsD1OOlx6AoMglfBeSqDZdhIMImAanMhyrO7czNBw9',
                                'podimetrics-manufacturing': '$5$rounds=110000$P9P2gjDmtibD3ss6$zbNCE7fp84iy1JmFAicrVTXbxMS8EiVwPap0i82n1l/'}

class RethinkDBController(classy.Controller):

    def __init__(self, *args, **kwargs):
        super(RethinkDBController, self).__init__(*args, **kwargs)
        self.connection = rethinkdb.connect()
        self.database = rethinkdb.db('test')

    def before_response_returned(self):
        self.connection.close()

def authenticate(username, password):
    try:
        return passlib.hash.sha256_crypt.verify(password, HASHED_PASSWORDS_BY_USERNAME[username])
    except:
        return False

class Transmissions(RethinkDBController):

    def __init__(self, *args, **kwargs):
        super(Transmissions, self).__init__(*args, **kwargs)
        # setup rethinkdb table if it doesn't exist
        try:
            self.database.table_create('transmissions').run(self.connection)
        except:
            # table already exists
            pass
        finally:
            table = self.table = self.database.table('transmissions')

    @classy.authentication.Basic(authenticate)
    def delete(self, transmission_id=None):
        if transmission_id is None:
            try:
                self.table.delete().run(self.connection)
                filenames = [path for path in glob.glob('data/*') if os.path.isfile(path)]
                for filename in filenames:
                    os.remove(filename)
            except:
                raise classy.exceptions.HTTPNotFound
        elif transmission_id != 'rethinkdb_data':
            try:
                self.table.get(transmission_id).delete().run(self.connection)
                os.remove(os.path.join('data', transmission_id))
            except:
                raise classy.exceptions.HTTPNotFound

    @classy.authentication.Basic(authenticate)
    def get(self, transmission_id=None):
        if transmission_id is None:
            raw_after = self.request.params.get('after', datetime.datetime.min.isoformat())
            raw_before = self.request.params.get('before', datetime.datetime.max.isoformat())
            limit = self.request.params.get('limit', None)
            #
            after_datetime = delorean.parse(raw_after).datetime
            before_datetime = delorean.parse(raw_before).datetime
            # compose query
            when_received = rethinkdb.row['when_received']
            scans_between = when_received.during(after_datetime, before_datetime)
            plucked_values = lambda transmission: {'when': transmission['when_received'].to_iso8601(), 
                                                   'transmission_id': transmission['id']}
            descending_date_order = rethinkdb.desc('when_received')
            query = self.table.filter(scans_between).order_by(descending_date_order).map(plucked_values)
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
                with open(os.path.join(DATA_PATH, transmission_id), 'rb') as f:
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

    classy.serve(host='0.0.0.0',port=8080)