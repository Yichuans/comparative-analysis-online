# -*- coding: utf-8 -*-

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## reload modules when changes are made
from gluon.custom_import import track_changes
track_changes(True)

## make sure db is accessibe in user define db
from gluon import current

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

if not request.env.web2py_runtime_gae:
    ## if NOT running on Google App Engine use SQLite or other DB
    # db = DAL('sqlite://storage.sqlite')
    db = DAL('postgres://postgres:gisintern@localhost/postgis', migrate=False)
    current.db = db
else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore')
    ## store sessions and tickets there
    session.connect(request, response, db = db)
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
# response.generic_patterns = ['*'] if request.is_local else []
response.generic_patterns = ['*']
## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'

#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import Auth, Crud, Service, PluginManager, prettydate
auth = Auth(db, hmac_key=Auth.get_or_create_key())
crud, service, plugins = Crud(db), Service(), PluginManager()

## create all tables needed by auth if not custom tables
auth.define_tables()

## configure email
mail=auth.settings.mailer
mail.settings.server = 'logging' or 'smtp.gmail.com:587'
mail.settings.sender = 'you@gmail.com'
mail.settings.login = 'username:password'

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

## if you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, write your domain:api_key in private/janrain.key
from gluon.contrib.login_methods.rpx_account import use_janrain
use_janrain(auth,filename='private/janrain.key')

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################

## === RESULTS
# intersection table holding result of user geometry vs other base layers
db.define_table('result',
    Field('tempid', 'integer'),
    Field('baselayer', 'text'),
    Field('bid', 'text')
)

# db.executesql('CREATE INDEX ')

# this table checks if an intersection has been done before
db.define_table('intersect_taken',
    Field('tempid', 'integer'),
    Field('baselayer', 'text'))


## === REALM-BIOME
# pre-authored realmbiome result table for WH
db.define_table('realmbiome',
    Field('tid', 'integer'),
    Field('bid', 'text'),
    Field('seg_area', 'double'),
    Field('theme_area', 'double'),
    Field('base_area', 'double'))

    # lookup table for realmbiome
db.define_table('realmbiome_lookup',
    Field('bid', 'text'),
    Field('name', 'text'))


# pre-authored KBA
db.define_table('kba',
    Field('tid', 'integer'),
    Field('bid', 'text'),
    Field('seg_area', 'double'),
    Field('theme_area', 'double'),
    Field('base_area', 'double'))

    # lookup table for KBA
db.define_table('kba_lookup',
    Field('bid', 'text'),
    Field('name', 'text'))

# pre-authored HS
db.define_table('hs',
    Field('tid', 'integer'),
    Field('bid', 'text'),
    Field('seg_area', 'double'),
    Field('theme_area', 'double'),
    Field('base_area', 'double'))


## === WH
# world heritage attribute table
db.define_table('wh',
    Field('wdpaid', 'integer'),
    Field('unesid', 'integer'),
    Field('en_name', 'text'),
    Field('fr_name', 'text'),
    Field('country', 'text'),
    Field('criteria', 'text')
    )

## === GEOMETRIES
# WWF realmbiome
db.define_table('realmbiome_geom',
    Field('bid', 'text'),
    Field('geom', 'geometry()'))

# KBA 
db.define_table('kba_geom',
    Field('bid', 'text'),
    Field('geom', 'geometry()'))

# Biodiv hotspot
db.define_table('hs_geom',
    Field('bid', 'text'),
    Field('geom', 'geometry()'))

# temporary table holding user submitted geometry
db.define_table('tempgeom',
    Field('tempid', 'integer'),
    Field('geom', 'geometry()'))

# WH
db.define_table('whgeom',
    Field('wdpaid', 'integer'),
    Field('geom', 'geometry()'))


## ===== INDEX ======= run once only
# db.executesql('CREATE INDEX whgeom_idx ON whgeom USING GIST(geom)')
# db.executesql('CREATE INDEX tempgeom_idx ON tempgeom USING GIST(geom)')
# db.executesql('CREATE INDEX realmbiome_geom_idx ON realmbiome_geom USING GIST(geom)')
# db.executesql('CREATE INDEX kba_geom_idx ON kba_geom USING GIST(geom)')
# db.executesql('CREATE INDEX hs_geom_idx ON hs_geom USING GIST(geom)')

# # non spatial
# db.executesql('CREATE UNIQUE INDEX wh_wdpaid_idx ON wh (wdpaid)')
# db.executesql('CREATE UNIQUE INDEX kba_lookup_bid_idx ON kba_lookup (bid)')
# db.executesql('CREATE UNIQUE INDEX realmbiome_lookup_bid_idx ON realmbiome_lookup (bid)')

