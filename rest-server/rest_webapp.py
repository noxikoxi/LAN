#!/usr/bin/python3
# -*- coding: UTF-8 -*-

plik_bazy = './osoby.sqlite'

import re, sqlite3
from urllib.parse import parse_qs

class OsobyApp:
    def __init__(self, environment, start_response):
        """
        Constructor needed by wsgi server
        """
        self.env = environment
        self.start_response = start_response
        self.status = '200 OK'
        self.headers = [('Content-Type', 'text/html; charset=UTF-8')]
        self.content = b''

    def __iter__(self):
        """
        Needed by wsgi server, iterates through request
        """
        try:
            self.route()
        except sqlite3.Error as e:
            s = 'SQLite error: ' + str(e)
            self.failure('500 Internal Server Error', s)
        n = len(self.content)
        self.headers.append(('Content-Length', str(n)))
        self.start_response(self.status, self.headers)
        yield self.content

    def failure(self, status, detail=None):
        """
        Adds failure status and creates html document with announcement about it occurring
        """
        self.status = status
        s = '<html>\n<head>\n<title>' + status + '</title>\n</head>\n'
        s += '<body>\n<h1>' + status + '</h1>\n'
        if detail is not None:
            s += '<p>' + detail + '</p>\n'
        s += '</body>\n</html>\n'
        self.content = s.encode('UTF-8')

    def route(self):
        """
        Handle routing of the request
        """
        if self.env['PATH_INFO'].startswith('/osoby'):
            self.handle_osoby()
            return
        elif self.env['PATH_INFO'].startswith('/psy'):
            self.handle_psy()
            return
        else:
            self.failure('404 Not Found')

    def handle_osoby(self):
        """
        Handle request to table osoby
        """
        if self.env['PATH_INFO'] == '/osoby':
            self.handle_table(table_name="osoby")
            return
        elif self.env['PATH_INFO'] == '/osoby/search':
            query_dict = {k: v[0] for k, v in parse_qs(self.env['QUERY_STRING']).items()}
            self.handle_table(table_name="osoby", filters=query_dict)
            return

        m = re.search('^/osoby/(?P<id>[0-9]+)$', self.env['PATH_INFO'])
        if m is not None:
            self.handle_row(m.group('id'), table_name="osoby")
            return

        self.failure('404 Not Found')

    def handle_psy(self):
        """
            Handle request connected with dogs
        """
        if self.env['PATH_INFO'] == '/psy':
            self.handle_table(table_name="psy")
            return
        if self.env['PATH_INFO'].startswith('/psy/rasy'):
            m = re.search('^/psy/rasy/(?P<nazwa>[a-zA-Z]+)$', self.env['PATH_INFO'])
            if m is not None:
                self.handle_rasy(nazwa=m.group('nazwa'))
            elif self.env['PATH_INFO'] == "/psy/rasy":
                self.handle_rasy()
            else:
                self.failure('404 Not Found')
            return
        elif self.env['PATH_INFO'] == '/psy/search':
            query_dict = {k: v[0] for k, v in parse_qs(self.env['QUERY_STRING']).items()}
            self.handle_table(table_name="psy", filters=query_dict)
            return

        m = re.search('^/psy/(?P<id>[0-9]+)$', self.env['PATH_INFO'])
        if m is not None:
            self.handle_row(m.group('id'), table_name="psy")
            return

        self.failure('404 Not Found')

    def handle_row(self, id, table_name="osoby"):
        """
        Handle request to a row in the table
        """
        colnames, rows = self.sql_select(table_name=table_name, filters={"id": id})
        # To update/delete a resource it must exist
        if len(rows) == 0:
            self.failure("404 Not Found", detail="Record does not exist")
            return

        if self.env['REQUEST_METHOD'] == 'GET':
            self.status = "200 OK"
            self.send_rows(colnames, rows)
        elif self.env['REQUEST_METHOD'] == 'PUT':
            colnames, vals = self.read_tsv()

            if not self.check_valid_request(table_name, colnames, vals, "PUT"):
                self.failure("400 Bad Request", detail="Request is not valid, check your columns' names")
            else:
                q = f'UPDATE {table_name} SET '
                q += ', '.join([c + ' = ?' for c in colnames])
                q += ' WHERE id = ' + id
                self.sql_modify(q, vals)
                colnames, rows = self.sql_select(table_name=table_name, filters={"id": id})
                self.status = "200 OK"
                self.send_rows(colnames, rows)
        elif self.env['REQUEST_METHOD'] == 'DELETE':
            if not self.check_delete(table_name, id):
                self.failure("400 Bad Request", detail="Cannot delete row with id " + id)
            else:
                q = f'DELETE FROM {table_name} WHERE id = ' + str(id)
                self.sql_modify(q)
                self.status = "200 OK"
                self.send_message("Deleted Resource")
        else:
            self.failure('501 Not Implemented')

    def handle_rasy(self, nazwa=None):
        """
        Handle request to /psy/rasy
        """
        if self.env['REQUEST_METHOD'] == 'GET':
            if nazwa is not None:
                colnames, rows = self.sql_select(table_name="rasy", filters={"nazwa": nazwa})
            else:
                colnames, rows = self.sql_select(table_name="rasy")
            if len(rows) > 0:
                self.status = "200 OK"
                self.send_rows(colnames, rows)
            else:
                self.failure("404 Not Found", detail="No records found")
        elif self.env['REQUEST_METHOD'] == 'POST':
            colnames, vals = self.read_tsv()
            if len(colnames) != 1 or colnames[0] != "nazwa":
                self.failure("400 Bad Request", detail="Request is not valid, check your columns' names")
                return

            cols, rows = self.sql_select(table_name="rasy")
            race = [r[0] for r in rows]
            if vals[0] in race:
                self.failure("400 Bad Request", detail="Request is not valid, cannot duplicate values")
                return
            q = f'INSERT INTO "rasy" VALUES (?)'
            self.sql_modify(q, vals)
            colnames, rows = self.sql_select(table_name="rasy")
            if len(rows) > 0:
                self.status = "201 Created"
                self.send_rows(colnames, rows)
            else:
                self.failure("500 Internal Server Error", detail="Failed to create record")
        elif nazwa is not None and self.env['REQUEST_METHOD'] == 'DELETE':
            cols, rows = self.sql_select(table_name="psy", columns="DISTINCT rasa")
            used_race = [r[0] for r in rows]
            if nazwa in used_race:
                self.failure("400 Bad Request", detail="Cannot delete raced used in table psy")
            else:
                q = f'DELETE FROM "rasy" WHERE nazwa = "{nazwa}"'
                self.sql_modify(q)
                self.status = "200 OK"
                self.send_message("Deleted Resource")
        else:
            self.failure('501 Not Implemented')

    def send_message(self, content):
        self.content = content.encode()
        self.headers = [('Content-Type', "text/plain")]

    def handle_table(self, table_name="osoby", filters=None):
        """
        Handle request to table
        """
        if self.env['REQUEST_METHOD'] == 'GET':
            colnames, rows = self.sql_select(table_name=table_name, filters=filters)
            if len(rows) > 0:
                self.status = "200 OK"
                self.send_rows(colnames, rows)
            else:
                self.failure("404 Not Found", detail="No records found")
        elif self.env['REQUEST_METHOD'] == 'POST':
            colnames, vals = self.read_tsv()
            if not self.check_valid_request(table_name, colnames, vals, "POST"):
                self.failure("400 Bad Request", detail="Request is not valid, check your columns' names")
            else:
                q = f'INSERT INTO {table_name} (' + ', '.join(colnames) + ') VALUES ('
                q += ', '.join(['?' for _ in vals]) + ')'
                id = self.sql_modify(q, vals)
                colnames, rows = self.sql_select(table_name=table_name, filters={"id": id})
                if len(rows) > 0:
                    self.status = "201 Created"
                    self.send_rows(colnames, rows)
                else:
                    self.failure("500 Internal Server Error", detail="Failed to create record")
        else:
            self.failure('501 Not Implemented')

    def check_valid_request(self, table_name, colnames, vals, method):
        """
        Checks request for POST/PUT (if columns names are valid)
        """
        valid_columns = self.get_colnames(table_name)
        valid_columns.remove("id")
        if len(colnames) != len(set(colnames)):  # Repetitions
            return False

        if method == "POST":
            if table_name in "psy":
                valid_columns.remove("wlasciciel_id")
                colnames = [v for v in colnames if v != "wlasciciel_id"]

            if len(valid_columns) != len(colnames):
                return False

        for column in colnames:
            if column not in valid_columns:
                return False

        # Checks Values (Integrity)
        if table_name == "psy":
            if not self.check_add_dog(colnames, vals):
                return False

        return True

    def check_delete(self, table_name, id):
        if table_name == "osoby":
            if not self.check_remove_person(id):
                return False

        return True

    def check_add_dog(self, colnames, vals):
        """
        Checks integrity on post request to table psy
        A dog with invalid race cannot be added to the table

        return True if dog can be added, False otherwise
        """

        _, rows = self.sql_select(table_name="rasy", columns="DISTINCT nazwa")
        race = [r[0] for r in rows]
        for i, val in enumerate(colnames):
            if val == "rasa":
                if vals[i] not in race:
                    return False
                break

        return True

    def check_remove_person(self, id):
        """
        Checks integrity on delete request to table osoby
        A person cannot be deleted if possesses a dog

        :return True if person can be deleted, False otherwise
        """
        _, rows = self.sql_select(table_name="psy", columns="DISTINCT wlasciciel_id")
        dog_owners = [r[0] for r in rows]
        if int(id) in dog_owners:
            return False

        return True

    def read_tsv(self):
        f = self.env['wsgi.input']
        n = int(self.env['CONTENT_LENGTH'])
        raw_bytes = f.read(n)
        lines = raw_bytes.decode('UTF-8').splitlines()
        colnames = lines[0].split('\t')
        vals = lines[1].split('\t')
        return colnames, vals

    def send_rows(self, colnames, rows):
        s = '\t'.join(colnames) + '\n'
        for row in rows:
            s += '\t'.join([str(val) for val in row]) + '\n'
        self.content = s.encode('UTF-8')
        self.headers = [('Content-Type',
                         'text/tab-separated-values; charset=UTF-8')]

    def get_colnames(self, table_name="osoby"):
        conn = sqlite3.connect(plik_bazy)
        crsr = conn.cursor()
        query = f'SELECT * FROM {table_name} LIMIT 1'
        crsr.execute(query)
        names = [d[0] for d in crsr.description]
        crsr.close()
        conn.close()
        return names

    def sql_select(self, table_name="osoby", filters=None, columns="*"):
        valid_columns = self.get_colnames(table_name)
        conn = sqlite3.connect(plik_bazy)
        crsr = conn.cursor()
        query = f'SELECT {columns} FROM {table_name}'
        if filters:
            query += f' WHERE '
            for index, key in enumerate(filters.keys()):
                if key not in valid_columns:  # Invalid Filter
                    return valid_columns, []

                query += f'{key}="{str(filters[key])}"'
                if index < (len(filters.keys()) - 1):  # And won't be added at the end of filters
                    query += ' AND '
        crsr.execute(query)
        colnames = [d[0] for d in crsr.description]
        rows = crsr.fetchall()
        crsr.close()
        conn.close()
        return colnames, rows

    def sql_modify(self, query, params=None):
        conn = sqlite3.connect(plik_bazy)
        crsr = conn.cursor()
        if params is None:
            crsr.execute(query)
        else:
            crsr.execute(query, params)
        rowid = crsr.lastrowid  # Row id
        crsr.close()
        conn.commit()
        conn.close()
        return rowid


if __name__ == '__main__':
    from wsgiref.simple_server import make_server

    port = 8000
    httpd = make_server('', port, OsobyApp)
    print('Listening on port %i, press ^C to stop.' % port)
    httpd.serve_forever()
