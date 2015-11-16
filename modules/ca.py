from gluon import current
# db = current.db

# base unit id, such as a biome name/id
BID = 'bid'

# theme unit id, such as wdpaid 
TID = 'tid'

# pre-authored result
REALMBIOME = 'realmbiome'

# theme layers
WH = 'wh'

# geometry 
GEOM_EXTENSION = '_geom'
REALMBIOME_GEOM = REALMBIOME + GEOM_EXTENSION
WH_GEOM = WH +GEOM_EXTENSION

TEMPGEOM = 'tempgeom'
# result tables
INTERSECT_TAKEN = 'intersect_taken'
RESULT = 'result'

### -------------------- experiment functions -----------------------------
def _get_tids_by_bid(bid, tab=REALMBIOME):
    # this function finds in the wh-wwf table wdpaid for WH
    if db.has_key(tab):
        # get intersection table object
        base_table = db[tab]

        # select rows
        rows = db(base_table[BID]==bid).select(base_table[TID])

        # return a list of wdpa ids for WH
        if len(rows.records) >0:
            return [row[TID] for row in rows]
        else:
            return list()

    else:
        raise Exception('Table {} does not exist'.format(tab))
        # return list()

def _get_wh_content_by_wdpaid(tid):
    if db.has_key(WH):
        # check if wh table exists
        wh = db[WH]

        # the WH table is a one-one relation table
        # return the row object
        return db(wh['wdpaid']==tid).select().first()

    else:
        raise Exception('Table {} does not exist'.format(tab))


### ------------------------- main functions ------------------------------
def get_geom_as_json_by_uid(uid, tab_geom=TEMPGEOM):
    from gluon.serializers import loads_json

    db = current.db

    if tab_geom == TEMPGEOM:
        table_id = 'tempid'
    elif tab_geom == REALMBIOME_GEOM:
        table_id = 'bid'
    elif tab_geom == WH_GEOM:
        table_id = 'wdpaid'
    else:
        # raise Exception('Invalid geom table {}'.format(tab_geom))
        return False

    # get geom rows
    rows = db(db[tab_geom][table_id] == uid).select(db[tab_geom].geom.st_asgeojson().with_alias('geom'))

    ## geojson need to be constructured
    features = [{"type": "Feature", "geometry": loads_json(row['geom'])} for row in rows]
    result = {"type": "FeatureCollection", "features": features}

    return result


def get_wh_rows_by_bid(bid, tab=REALMBIOME):
    db = current.db
    # input bid and return multiple rows of WH content
    # this should be more efficient than one by one
    if db.has_key(WH) and db.has_key(tab):
        wh = db[WH]
        base_table = db[tab]

        # make a join between the two tables
        rows = db((wh['wdpaid']==base_table[TID])& (base_table[BID]==bid)).select(wh.ALL)

        return rows
    else:
        raise Exception('Table {} or {} does not exist'.format(WH, tab))

def insert_temp_geom(geojson_dict):
    # from gluon import current
    # this is required as a module level variable is instantiated and won't change when thread in pool is destroyed
    # but db still referring to it. therefore it needs to be inside the function
    db = current.db

    import json
    from gluon.serializers import loads_json

    # loads_json converts a string of json to a python dict
    # geojson_dict is input from jquery, with its key the content
    json_dict = loads_json(geojson_dict.keys()[0])

    # if en empty geojson is submitted
    if len(json_dict['features']) == 0:
        return 'No feature submitted'

    # get a unique id
    tempid = len(db().select(db.tempgeom.id)) + 1

    try:
    # for each geojson feature do a db insert
        fullsql = ''

        for eachfeature in json_dict['features']:

            # each feature is a dict of keys: geometry, type and properties, of which only geometry is of interest
            feature_dict = eachfeature['geometry']

            # ensure crs is included, by default WGS84
            feature_dict['crs'] = {'type': 'name', 'properties':{'name':'EPSG:4326'}}

            # dump in json format and construct sql to insert record
            sql = "INSERT INTO tempgeom (tempid, geom) VALUES ({}, st_geomfromgeojson({!r}));".format(tempid, json.dumps((feature_dict)))

            fullsql += sql + '\n'
            # run queries
            db.executesql(sql)

    except Exception as e:
        print e
        return False

    #     # debug
    # else:
    #     return str(tempid) + '\n' + fullsql
    else:
        return tempid

# get bids 
def get_bids_by_tempid(tempid, tab=REALMBIOME):
    db = current.db

    # query
    select_query = (db.result.tempid == tempid) & (db.result.baselayer == tab)

    rows = db(select_query).select(db.result.bid)

    return [row.bid for row in rows]

# main process function to run intersection
def run_intersection(tempid, tab=REALMBIOME):
    db = current.db

    # if tempgeom not found
    if len(db(db.tempgeom.tempid == tempid).select(db.tempgeom.id)) == 0:
        raise Exception('no geometry found by id {}'.format(tempid))

    def intersection(tempid, tab_geom=REALMBIOME_GEOM):
        ## db = current.db

        # get query object: a simple test intersection!!!
        intersect_query = db.tempgeom.geom.st_intersects(db[tab_geom].geom)
        select_tempid_query = (db.tempgeom.tempid == tempid)

        # return rows of distinct bids
        rows = db(intersect_query & select_tempid_query).select(db[tab_geom].bid, distinct = True)
        return rows

    # update `intersect_taken`
    def update_intersect_taken(tempid, tab=REALMBIOME):
        ## db = current.db

        try: # insert
            db.intersect_taken.insert(tempid = tempid, baselayer=tab)

            # except models, vies and controllers, this is needed explicitly in order to commit change
            db.commit()

        except Exception as e:
            print e
            return False

        else:
            return True


    def has_intersect_taken(tempid, tab=REALMBIOME):
        ## db = current.db

        # query
        select_query = (db.intersect_taken.tempid == tempid) & (db.intersect_taken.baselayer == tab)

        # select 
        rows = db(select_query).select()
        if len(rows)==0:
            return False

        else:
            return True

    # insert this to the `result` table 
    def insert_intersect_result(tempid, rows, tab=REALMBIOME):
        ## db = current.db

        try:
            # insert
            for row in rows:
                db.result.insert(tempid = tempid, baselayer=tab, bid=row[BID])

            db.commit()

        except Exception as e:
            print e 
            return False
        else:
            return True

    # if already had intersection
    if has_intersect_taken(tempid, tab):
        return 'Intersection was done before, do nothing'

    else:
        # has not had intersection
        tab_geom = tab + GEOM_EXTENSION        
        rows = intersection(tempid, tab_geom)
            # intersect successful
        if insert_intersect_result(tempid, rows, tab):
                # update intersection taken table
            if update_intersect_taken(tempid, tab):
                return 'Intersection complete'

        return 'Error occurred during the intersection'


## serialise result in HTML
def div_wh_row(whrow):
    # still needs a picture element

    from gluon.html import *
    whname = P(whrow.en_name, _class='site-name')
    whcountry = P(whrow.country, _class='country')
    whcrit = P(whrow.criteria, _class='crit')
    unescolink = A('UNESCO WHC site page', _href='http://whc.unesco.org/en/list/'+ str(whrow.unesid))
    wdpalink = A('ProtectedPlanet page', _href='http://www.protectedplanet.net/'+str(whrow.wdpaid))

    div = DIV(whname, whcountry, whcrit, unescolink, wdpalink, _class='wh-div')
    return div


## ======== TEST =========
# ca.run_intersection(15)
# ca.get_bids_by_tempid(22)
# ca.get_wh_rows_by_bid('PA-4')



