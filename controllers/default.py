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
    from ca import insert_temp_geom
    # response.view = 'generic.json'
    def GET(recid):
        ## the result is only part of the geojson
        rows = db(db.wwfgeom.recid == recid).select(db.wwfgeom.geom.st_asgeojson().with_alias('geom'))

        ## geojson need to be constructured
        features = [{"type": "Feature", "geometry": loads_json(row['geom'])} for row in rows]
        return response.json({"type": "FeatureCollection", "features": features})


    def POST(**geojson_dict):
        response.view = 'generic.json'

        #
        tempid = insert_temp_geom(geojson_dict)

        # debugging purposes
        if tempid:
            return 'success, id {}'.format(tempid)

        else:
            return 'failed to post json'


    return locals()

def get_json():
    return dict()

def post_json():
    return dict()


# for production
def welcome():
    # this is the landing page
    return dict()

def comparative_analysis():
    # this is the page showing the result of the comparative analysis
    return dict()

def submit_boundary():
    # this is the page to submit a drawn polygon
    return dict()



