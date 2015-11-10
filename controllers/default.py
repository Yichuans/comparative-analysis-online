# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################

def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html
    """
    response.flash = "Welcome to web2py!"
    return dict(message=T('Hello World'))

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request,db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs must be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())


def show_request_vars():
    return dict(req_vars = request.vars, req_args = request.args, request = request)

def main():
    return dict()

def local():
    return locals()

def post():
    return request.post_vars

def add():
    result = 0
    for each in request.vars:
        result += float(request.vars[each])

    return result

def count():
    session.counter = (session.counter or 0) + 1
    return dict(counter=session.counter, now=request.now)

@request.restful()
def api():
    response.view = 'generic.'+request.extension

    def POST(*arg, **var):
        # return response.json({'inputvar':v1})
        return dict(**var)


    return locals()


# test to get geom as json from pgis database, asyncly
@request.restful()
def geoapi():
    from gluon.serializers import loads_json
    # response.view = 'generic.json'
    def GET(recid):
        ## the result is only part of the geojson
        rows = db(db.wwfgeom.recid == recid).select(db.wwfgeom.geom.st_asgeojson().with_alias('geom'))

        ## geojson need to be constructured
        features = [{"type": "Feature", "geometry": loads_json(row['geom'])} for row in rows]
        return response.json({"type": "FeatureCollection", "features": features})


    def POST(**geojson_dict):
        # geojson_dict is input from jquery, with its key the content


        response.view = 'generic.json'

        # python's own json utilities. json.dumps() converts a dictionary to json format string
        import json

        # loads_json converts a string of json to a python dict
        json_dict = loads_json(geojson_dict.keys()[0])

        # if en empty geojson is submitted
        if len(json_dict['features']) == 0:
            return 'No feature submitted'

        # for each geojson feature do a db insert
        for eachfeature in json_dict['features']:

            # each feature is a dict of keys: geometry, type and properties, of which geometry is of interest
            feature_dict = eachfeature['geometry']

            # ensure crs is included, by default WGS84
            feature_dict['crs'] = {'type': 'name', 'properties':{'name':'EPSG:4326'}}

            # dump in json format and construct sql to insert record
            sql = "INSERT INTO tempgeom (geom) VALUES (st_geomfromgeojson({!r}));".format(json.dumps((feature_dict)))

            # run queries
            db.executesql(sql)

        

        # return feature_list[0]
        return sql


    return locals()

def get_json():
    return dict()

def post_json():
    return dict()



# def get_geojson():
#     from gluon.serializers import loads_json

#     recid = request.args[0]
#     response.view = 'generic.json'

#     # only expect one row as result

#     ## through DAL
#     row = db(db.wwfgeom.recid == recid).select(db.wwfgeom.geom.st_asgeojson().with_alias('geom'))[0]
#     result = row['geom']

#     # ## direct sql, inject warning
#     # result =  db.executesql('SELECT st_asgeojson(geom) as geom FROM wwfgeom WHERE recid = %s LIMIT 1;'%(recid,), as_dict=True)[0]
#     # result = loads_json(result['geom'])

#     return result



