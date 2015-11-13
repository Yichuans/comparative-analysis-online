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
REALMBIOME_GEOM = 'realmbiome_geom'

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
    tempid = len(db().select(db['tempgeom'].id)) + 1

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
        return None

    else:
        return str(tempid) + '\n' + fullsql

def intersection(tempid, tab=REALMBIOME_GEOM):
    db = current.db

    # get query object: a simple test intersection!!!
    intersect_query = db.tempgeom.geom.st_intersects(db[tab].geom)
    select_tempid_query = (db.tempgeom.tempid == tempid)

    # return rows of distinct bids
    rows = db(intersect_query & select_tempid_query).select(db[tab].bid, distinct = True)
    return rows

# insert this to the `result` table and update `intersect_taken`
def update_intersect_taken(tempid, tab=REALMBIOME):
    db = current.db
    # IMPLEMENT NEEDED
