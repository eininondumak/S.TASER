import os, sys
import argparse
import sqlite3 as sqlite
import re
import json
import xml.etree.ElementTree as ET
import time
import folium
from datetime import datetime
from urllib.parse import urlparse, parse_qs

def datafromSQL(path, file, flag):
    path = os.path.join(path, file)

    try:
        conn = sqlite.connect(path)
    except sqlite.Error as e:
        print(f"SQLite error: {e} {file}", path)
        return -1

    cursor = conn.cursor()

    try:
        if flag == 1:
            cursor.execute(
                "SELECT datetime(createdDate/1000, 'unixepoch') as time, deviceId, name, label, integration from DeviceDomain where integration like '%bleD2D%';")
        elif flag == 2:
            cursor.execute("SELECT infoList, pluginId from FmeAppData;")
        elif flag == 3:
            cursor.execute(
                "SELECT datetime(timestamp/1000, 'unixepoch') as time, mnId, setupId,displayName, brandName from EasySetupIconDb;")
        elif flag == 4:
            cursor.execute(
                "SELECT datetime(timestamp/1000, 'unixepoch') as time, processName, tag, title, description from PersistentLogDomain where title like 'getupdateddata' and (tag = 'DeviceResource' or tag = 'DataLayerDataBaseContentProviderOnCore');")
        elif flag == 5:
            cursor.execute(
                "SELECT datetime(timestamp/1000, 'unixepoch') as time, deviceId, capabilityId, stringifyValue from BleDeviceCapabilityStatusDomain;")
        elif flag == 6:
            cursor.execute("SELECT settings_key from insettings where settings_key like 'tag_owner_guid%';")
        elif flag == 7:
            cursor.execute(
                "SELECT deviceId, datetime(start/1000, 'unixepoch') as start, datetime(end/1000, 'unixepoch') as end, count, latitude, longitude, address from item_history;")
        elif flag == 8:
            cursor.execute(
                "SELECT encDeviceId, datetime(date/1000, 'unixepoch') as date, history from EncLocationHistory;")
        
        desc = cursor.description
        column_names = [col[0] for col in desc]
        data = [dict(zip(column_names, row)) for row in cursor.fetchall()]
        conn.close()

        return data

    except sqlite.Error as e:
        print(f"SQLite error: {e} {file}", path)
        conn.close()
        return -1

def insert_into_tag_activity(cursor, data):
    cursor.execute('''
        INSERT INTO tagActivity (timestamp, uuid, infotype, name, info, source, raw)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', data)

def parse_DeviceData(cursor, path, file):
    devicedata_result = datafromSQL(path, file, 1)
    if devicedata_result == -1 or not devicedata_result:
        return

    data_result = []
    for item in devicedata_result:
        integration = parse_integration(item['integration'])
        insert_into_tag_activity(cursor, (item['time'], item['deviceId'], 'Registered', item['label'], \
        integration['vendor']['mnId'] + ", " + integration['vendor']['setupId'] + ", " + integration['vendor']['modelName'] + ", " + integration['identifier'], file, \
            json.dumps({'timestamp':item['time'], 'uuid':item['deviceId'], 'name':item['label'], 'integration':integration})))

def parse_Fme(cursor, path, file):
    fme_result = datafromSQL(path, file, 2)
    if fme_result == -1 or not fme_result:
        return

    infoList = parse_infoList(fme_result[0]['infoList'])
    for info in infoList:
        insert_into_tag_activity(cursor, (info['timestamp'], info['uuid'], 'location', info['name'], \
            json.dumps({'start':info['timestamp'], 'end':'', 'count':1, 'latitude': str(info['latitude']), 'longitude': str(info['longitude']), 'accuracy':''}), file, \
            json.dumps(info)))

def parse_EasySetup(cursor, path, file):
    easysetup_result = datafromSQL(path, file, 3)
    if easysetup_result == -1 or not easysetup_result:
        return

    for easysetup in easysetup_result:
        insert_into_tag_activity(cursor,(easysetup['time'], '', 'Register from db', '', \
            str(easysetup['displayName']) +", "+ str(easysetup['mnId']) +", "+ str(easysetup['setupId'])\
            , file, json.dumps(easysetup)))

def parse_PersistentLogData(cursor, path, file):
    persistentlogdata_result = datafromSQL(path, file, 4)
    if persistentlogdata_result == -1 or not persistentlogdata_result:
        return

    uuid_pattern = r'deviceId=(?:(?:[0-9a-fA-F]{32})|(?:[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}))'
    action_added = 'added     :'
    action_removed = 'removed   :'
    result_data = []

    for item in persistentlogdata_result:
        timestamp = item['time']
        description = item['description']
        if action_added in description:
            action_type = "Add"
        elif action_removed in description:
            action_type = "Erase"
        uuid_match = re.findall(uuid_pattern, description, re.IGNORECASE)

        for uuid in uuid_match:
            uuid = uuid.replace("deviceId=", "")
            if action_type == "Add":
                info = ""
            elif action_type == "Erase":
                info = uuid

            insert_into_tag_activity(cursor, (timestamp, uuid, action_type, '', info, file, ''))

            cursor.execute('''
            INSERT INTO persistentLog (timestamp, uuid, raw)
            VALUES (?, ?, ?)
            ''', (timestamp, uuid, description))

def parse_DeviceCapability(cursor, path, file):
    devicecapability = datafromSQL(path, file, 5)
    if devicecapability == -1 or not devicecapability:
        return

    for device in devicecapability:
        insert_into_tag_activity(cursor, (device['time'], device['deviceId'], 'Property', '', \
            str(device['capabilityId']) +", "+ str(device['stringifyValue']), file, \
            json.dumps(device)))

def parse_InternalSettings(cursor, path, file):
    internal_result = datafromSQL(path, file, 6)
    if internal_result == -1 or not internal_result:
        return

    for item in internal_result:
        key = 'tag_owner_guid'
        try:
            uuid = item['settings_key'].replace(key, "")
            cursor.execute('''INSERT INTO internaluuid (uuid) VALUES (?)''', (uuid,))

        except ValueError:
            continue

def parse_appdatabase(cursor, path, file):
    appdata_result = datafromSQL(path, file, 7)
    if appdata_result == -1 or not appdata_result:
        return

    for appdata in appdata_result:
        insert_into_tag_activity(cursor, (appdata['start'], appdata['deviceId'], 'location', '', json.dumps({'start':appdata['start'], 'end':appdata['end'], 'count':appdata['count'], \
        'latitude': str(appdata['latitude']), 'longitude': str(appdata['longitude']), 'accuracy':''}),\
        file, json.dumps(appdata)))

def parse_locationhistory(cursor, path, file):
    history_result = datafromSQL(path, file, 8)
    if history_result == -1 or not history_result:
        return

    for history in history_result:
        insert_into_tag_activity(cursor, (history['date'], history['encDeviceId'], 'Enclocation', '', '', file, history['history']))

def parse_integration(integration):

    vendor = ''
    identifier = ''
    connecteduser = ''
    connecteddevice = ''
    createtime = ''
    updatetime = ''

    data = json.loads(integration)
    firstlayer_keys = data.keys()
    if 'bleD2D' in firstlayer_keys:
        sencondlayer_keys = data['bleD2D'].keys()
        if 'identifier' in sencondlayer_keys:
            identifier = data['bleD2D']['identifier']
        if 'metadata' in sencondlayer_keys:
            vendor = data['bleD2D']['metadata']['vendor']
            createtime = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(data['bleD2D']['metadata']['createTime']))
            updatetime = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(data['bleD2D']['metadata']['updateTime']))
            thirdlayer_keys = data['bleD2D']['metadata'].keys()
            if 'lastKnownConnection' in thirdlayer_keys:
                connecteduser = data['bleD2D']['metadata']['lastKnownConnection']['connectedUser']
                connecteddevice = data['bleD2D']['metadata']['lastKnownConnection']['connectedDevice']

    return {'vendor':vendor, 'identifier':identifier, 'user':connecteduser, 'device':connecteddevice,\
    'createtime':createtime, 'updatetime':updatetime}

def parse_infoList(infolist):
    data = json.loads(infolist)
    tag_items = []
    for item in data:
        firstlayer_keys = item.keys()
        if 'type' in firstlayer_keys:
            if item['type'] == 'TRACKER':
                if 'geoInfo' in firstlayer_keys:
                    timestamp = datetime.strptime(str(item['geoInfo']['timestamp']), '%Y%m%d%H%M%S')
                    tag_items.append(
                        {'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'), 'uuid': item['id'], 'name': item['name'], \
                        'latitude': item['geoInfo']['lat'], 'longitude': item['geoInfo']['long']})

    return tag_items

def parse_fme_selected_device(cursor, path, file):
    path = os.path.join(path, file)

    if not os.path.isfile(path):
        raise FileNotFoundError(f"{path} dosen\'t exist")

    tree = ET.parse(path)
    root = tree.getroot()
    tag_list = []

    for child in root:
        if child.attrib['name'] == 'SELECTED_FME_ALL_INFO':
            data_items = json.loads(child.text)
            for data in data_items:
                if data['type'] == 'TAG':
                    timestamp = datetime.strptime(str(data['firstTime']), '%Y%m%d%H%M%S')
                    insert_into_tag_activity(cursor, (timestamp.strftime('%Y-%m-%d %H:%M:%S'), data['id'], 'location',\
                    data['name'], json.dumps({'start':timestamp.strftime('%Y-%m-%d %H:%M:%S'), 'end':'', 'count':1, 'latitude':data['firstLat'],\
                     'longitude':data['firstLong'], 'accuracy':data['firstAcc']}), file, \
                    json.dumps({'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'), 'uuid': data['id'], 'name': data['name'] \
                    , 'Latitude': data['firstLat'], 'longitude': data['firstLong'],\
                     'Accuracy': data['firstAcc']})))

def find_files_with_vendor(directory, search_string):
    matching_files = []
    if 'setupdata' in search_string:
        flag = 1
        pattern = r'.*api\.smartthings\.com/catalogs/api/v3/easysetup/setupdata.*\n'
    else:
        flag = 2
        pattern = r'.*client\.smartthings\.com/chaser/trackers/lostmessage.*\n'
    time_pattern = r'date:\s*(.*?)\s*GMT'

    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text_data = f.read()

                    if search_string in text_data:
                        match = re.findall(pattern, text_data, re.IGNORECASE)[0]
                        query_params = parse_qs(urlparse(match).query)
                        query_dict = {key: value[0] for key, value in query_params.items()}

                        if flag == 1:
                            vendor_info = {'mnId': query_dict['mnId'], 'setupId': query_dict['setupId'],
                                           'serialNumber': '', 'modelName': ''}
                        elif flag == 2:
                            vendor_info = {'mnId': query_dict['mnId'], 'setupId': query_dict['setupId'], \
                                           'modelName': query_dict['modelName'],
                                           'serialNumber': query_dict['serialNumber']}

                        try:
                            time_match = re.findall(time_pattern, text_data, re.IGNORECASE)[0]
                            timestamp = datetime.strptime(time_match, '%a, %d %b %Y %H:%M:%S').strftime(
                                '%Y-%m-%d %H:%M:%S')
                        except IndexError:
                            continue

                        matching_files.append({'timestamp': timestamp, 'vendor': vendor_info, 'source': file_path})

            except (UnicodeDecodeError, FileNotFoundError):
                continue

    return matching_files

def find_files_with_uuid(directory, search_string):
    matching_files = []
    uuid_pattern = r'(?:(?:[0-9a-fA-F]{32})|(?:[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}))'
    time_pattern = r'date:\s*(.*?)\s*GMT'

    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text_data = f.read()

                    try:
                        strings_match = re.findall(search_string, text_data, re.IGNORECASE)[0]
                        if strings_match:
                            try:
                                 uuid = re.findall(uuid_pattern, text_data, re.IGNORECASE)[0]
                            except IndexError:
                                 continue

                            try:
                                time_match = re.findall(time_pattern, text_data, re.IGNORECASE)[0]
                                timestamp = datetime.strptime(time_match, '%a, %d %b %Y %H:%M:%S').strftime(
                                    '%Y-%m-%d %H:%M:%S')
                            except IndexError:
                                continue

                            matching_files.append({'timestamp': timestamp, 'string':strings_match[:-len(uuid)], 'uuid': uuid, 'source': file_path})

                    except IndexError:
                        continue

            except (UnicodeDecodeError, FileNotFoundError):
                continue

    return matching_files

def search_vendor_in_cache(cursor, path):
    oneconnect_cache_dir = ['http-Core','http-Main','http-PluginNativeFME','http-PluginWebApplication']
    cache_keyword = ['api.smartthings.com/catalogs/api/v3/easysetup/setupdata', \
                     'client.smartthings.com/chaser/trackers/lostmessage']

    return_data = []

    for sub_path in oneconnect_cache_dir:
        full_path = os.path.join(path, sub_path)
        if not os.path.isdir(full_path):
            print(f'{full_path} dosen\'t exist')
            continue

        for keyword in cache_keyword:
            match_strings = find_files_with_vendor(full_path, keyword)
            if len(match_strings) != 0:
                for match_data in match_strings:
                    insert_into_tag_activity(cursor, (match_data['timestamp'], '', 'Register from webcache', '',\
                        match_data['vendor']['mnId'] + ", " + match_data['vendor']['setupId'] + ", " + match_data['vendor']['modelName'] + ", "+ match_data['vendor']['serialNumber'], \
                        match_data['source'], json.dumps(match_data)))

def search_uuid_in_cache(cursor, path):
    oneconnect_cache_dir = ['http-Core','http-Main','http-PluginNativeFME','http-PluginWebApplication']
    patterns = [
            r'client\.smartthings\.com/presentation\?deviceId=(?:(?:[0-9a-fA-F]{32})|(?:[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}))',
            r'client\.smartthings\.com/devices/status\?includeUserDevices=true&excludeLocationDevices=false&deviceId=(?:(?:[0-9a-fA-F]{32})|(?:[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}))'
        ]

    combined_pattern = '|'.join(patterns)

    return_data = []

    for sub_path in oneconnect_cache_dir:
        full_path = os.path.join(path, sub_path)
        if not os.path.isdir(full_path):
            print(f'{full_path} dosen\'t exist')
            continue

        match_strings = find_files_with_uuid(full_path, combined_pattern)
        if len(match_strings) != 0:
            for match_data in match_strings:
                insert_into_tag_activity(cursor, (match_data['timestamp'], match_data['uuid'], 'webcache', '', match_data['string'], match_data['source'], ''))

def search_deletedTag(path, file):
    db_path = os.path.join(path,file)
    conn = sqlite.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT uuid FROM internaluuid")
    uuids_a = {row[0] for row in cursor.fetchall()}
    cursor.execute("SELECT distinct uuid FROM tagActivity where infotype = 'Registered' and (source = 'DeviceData.db' or source = 'DataLayerData.db')")
    uuids_b = {row[0] for row in cursor.fetchall()}
    deleted_uuids = uuids_a - uuids_b
    for uuid in deleted_uuids:
        cursor.execute("UPDATE internaluuid SET description = 'deleted' WHERE uuid = ?", (uuid,))

    conn.commit()

    cursor.execute("SELECT uuid, description FROM internaluuid")
    uuids = [row for row in cursor.fetchall()]

    conn.commit()
    conn.close()

    return uuids

def get_information_tag(path, dBfile, outfile, uuid, deleted):
    db_path = os.path.join(path, dBfile)
    conn = sqlite.connect(db_path)
    cursor = conn.cursor()

    tagname ='unknown'
    tagidentifier ='unknown'
    tagmodel = 'unknown'
    tagmnid = 'unknown'
    tagsetupid = 'unknown'
    registrationTime = 'unknown'

    if deleted:
        #first: try to find backupdata
        cursor.execute("SELECT * FROM tagActivity where uuid =? and infotype = 'Registered'",(uuid,))
        backup_one = cursor.fetchone()

        if backup_one is not None:
            tagname = backup_one[3]
            tagmnid = backup_one[4].split(',')[0]
            tagsetupid = backup_one[4].split(',')[1]
            tagmodel = backup_one[4].split(',')[2]
            tagidentifier = backup_one[4].split(',')[3]
            registrationTime = backup_one[0]


            outfile.write(f"\nTag uuid: {uuid}, status: recovered\n")
            outfile.write(f"Recover Method: backup data\n")
            outfile.write(f"Tag label: {tagname}\n")
            outfile.write(f"Tag model: {tagmodel}\n")
            outfile.write(f"Tag mnId: {tagmnid}, setupId: {tagsetupid}\n")
            outfile.write(f"Tag identifier: {tagidentifier}\n")
            outfile.write(f"Tag reg time: {registrationTime}\n" )

        else:
            #second: try to find logdata
            cursor.execute("SELECT * FROM tagActivity where uuid =? and infotype = 'Erase'",(uuid,))
            deleted_info = cursor.fetchone()

            if deleted_info is not None:
                #found!
                try:
                    deleted_time = deleted_info[0]
                    keywordTagname = r"label=([^,]+), manufacturerCode="
                    keywordIdentifier = r"identifier=([A-Za-z0-9]+),"
                    keywordVender = r'"vendor":\{"mnId":"(?P<mnId>[^"]+)","setupId":"(?P<setupId>[^"]+)","modelName":"(?P<modelName>[^"]+)"\}'
                    keywordData = r'"createTime":(\d+)'
                    cursor.execute("SELECT * FROM persistentLog where timestamp =? and uuid =? and raw like '%removed%'",\
                        (deleted_time,uuid))

                    result_data = cursor.fetchone()

                    if result_data:
                        matches = re.findall(keywordTagname, result_data[2])
                        if matches:
                            tagname = matches[0]

                        matches = re.findall(keywordIdentifier, result_data[2])
                        if matches:
                            tagidentifier = matches[0]

                        matches = re.findall(keywordVender, result_data[2])
                        if matches:
                            tagmnid = matches[0][0]
                            tagsetupid = matches[0][1]
                            tagmodel = matches[0][2]

                        matches = re.findall(keywordData, result_data[2])
                        if matches:
                            #버그 수정
                            registrationTime = datetime.utcfromtimestamp(int(matches[0])).strftime('%Y-%m-%d %H:%M:%S')
                except:
                    print("Error during parsing logdata")

                outfile.write(f"\nTag uuid: {uuid}, status: recovered\n")
                outfile.write(f"Recover Method: log data\n")
                outfile.write(f"Tag label: {tagname}\n")
                outfile.write(f"Tag model: {tagmodel}\n")
                outfile.write(f"Tag mnId: {tagmnid}, setupId: {tagsetupid}\n")
                outfile.write(f"Tag identifier: {tagidentifier}\n")
                outfile.write(f"Tag reg time: {registrationTime}\n")


            elif deleted_info is None:
                #Pattern
                cursor.execute("SELECT * FROM tagActivity where uuid =? and infotype ='webcache' order by timestamp asc",(uuid,))
                logone = cursor.fetchone()
                if logone is None:
                    #Fail because of no webcache
                    outfile.write(f"\nTag uuid: {uuid}, status: deleted\n")
                    outfile.write(f"Recover Method: pattern\n")
                    outfile.write(f"Tag label: {tagname}\n")
                    outfile.write(f"Tag model: {tagmodel}\n")
                    outfile.write(f"Tag mnId: {tagmnid}, setupId: {tagsetupid}\n")
                    outfile.write(f"Tag identifier: {tagidentifier}\n")
                    outfile.write(f"Tag reg time: {registrationTime}\n" )

                elif logone[4] == 'client.smartthings.com/devices/status?includeUserDevices=true&excludeLocationDevices=false&deviceId=' or \
                logone[4] == 'client.smartthings.com/presentation?deviceId=':
                    #naming is very bad
                    #deleted_time = logone[0] -> registered_time = logone[0]
                    registered_time = logone[0]
                    #try to find 'Register from webcache' in infotype
                    cursor.execute("SELECT * FROM tagActivity WHERE timestamp BETWEEN datetime(?, '-3 minutes') AND datetime(?) \
                    and uuid ='' and infotype like 'Register%' order by timestamp asc",\
                    (registered_time, registered_time,))
                    results = cursor.fetchall()

                    if results:
                    # found 'Register from webcache' in infotype    
                        for i, log in enumerate(results):
                            registrationTime = log[0]
                            if log[2] == 'Register from webcache':
                                if log[4].split(',')[2]:
                                    registrationTime = log[0]
                                    tagmnid = log[4].split(',')[0]
                                    tagsetupid = log[4].split(',')[1]
                                    tagmodel = log[4].split(',')[2]
                                    tagidentifier = log[4].split(',')[3]

                        outfile.write(f"\nTag uuid: {uuid}, status: recovered\n")
                        outfile.write(f"Recover Method: pattern\n")
                        outfile.write(f"Tag label: {tagname}\n")
                        outfile.write(f"Tag model: {tagmodel}\n")
                        outfile.write(f"Tag mnId: {tagmnid}, setupId: {tagsetupid}\n")
                        outfile.write(f"Tag identifier: {tagidentifier}\n")
                        outfile.write(f"Tag reg time: {registrationTime}\n" )
                    else:
                    # Not found 'Register from webcache' in infotype -> fail                            
                        outfile.write(f"\nTag uuid: {uuid}, status: deleted\n")
                        outfile.write(f"Recover Method: pattern\n")
                        outfile.write(f"Tag label: {tagname}\n")
                        outfile.write(f"Tag model: {tagmodel}\n")
                        outfile.write(f"Tag mnId: {tagmnid}, setupId: {tagsetupid}\n")
                        outfile.write(f"Tag identifier: {tagidentifier}\n")
                        outfile.write(f"Tag reg time: {registrationTime}\n" )

    else:
        #살아 있는 tag
        cursor.execute("SELECT * FROM tagActivity where uuid =? and infotype ='Registered'",(uuid,))
        taginfo = cursor.fetchone()
        tagname = taginfo[3]
        tagmnid = taginfo[4].split(',')[0]
        tagsetupid = taginfo[4].split(',')[1]
        tagmodel = taginfo[4].split(',')[2]
        tagidentifier = taginfo[4].split(',')[3]
        registrationTime = taginfo[0]

        outfile.write(f"\nTag uuid: {uuid}, status: live\n")
        outfile.write(f"Tag label: {tagname}\n")
        outfile.write(f"Tag model: {tagmodel}\n")
        outfile.write(f"Tag mnId: {tagmnid}, setupId: {tagsetupid}\n")
        outfile.write(f"Tag identifier: {tagidentifier}\n")
        outfile.write(f"Tag reg time: {registrationTime}\n" )

    outfile.write("\n")
    outfile.write("Tag's location history\n")
    cursor.execute("SELECT * FROM tagActivity where uuid =? and infotype = 'location' order by timestamp asc",(uuid,))
    activities = cursor.fetchall()
    index = 1
    # 변경점 241209
    for activity in activities:
        outfile.write(f"{index}, start time: {activity[0]},")
        info = json.loads(activity[4])
        outfile.write(f" end time: {info['end']}, count: {info['count']}, latitude: {info['latitude']}, longitude: {info['longitude']}, source: {activity[5]}\n")
        index += 1

    draw_map(path, dBfile, uuid)

    outfile.write("\n")
    outfile.write("Tag's Enclocation history\n")
    cursor.execute("select timestamp, uuid, COUNT(*) AS count from Tagactivity where SUBSTR(uuid, -4) = ? and infotype = 'Enclocation' GROUP BY timestamp HAVING count >= 1",(uuid[-4:],))
    activities = cursor.fetchall()
    index = 1
    for activity in activities:
        outfile.write(f"{index}, time: {activity[0]}, EncUUID: {activity[1]}, count: {activity[2]}\n")
        index += 1

    conn.commit()
    conn.close()

def draw_map(path, file, uuid):

    db_path = os.path.join(path, file)
    conn = sqlite.connect(db_path)
    cursor = conn.cursor()

    query = """
    SELECT info
    FROM tagActivity
    WHERE infotype = 'location' AND uuid = ?
    ORDER BY timestamp ASC;
    """

    cursor.execute(query,(uuid,))
    query_result = cursor.fetchall()
    if query_result:
        location_list = [json.loads(row[0]) for row in query_result]
        m = folium.Map(location=[float(location_list[0]['latitude']),float(location_list[0]['longitude'])], \
            zoom_start=6, tiles='CartoDB positron')

        coordinates = [[float(loc["latitude"]),float(loc["longitude"])] for loc in location_list]
        for i, loc in enumerate(location_list):
            folium.Marker(
                location=[float(loc["latitude"]),float(loc["longitude"])],
                popup=loc["start"]+", "+str(loc["count"]),
                icon=folium.Icon(color='blue')
            ).add_to(m)

            if i > 0:
                folium.PolyLine(
                    locations=[coordinates[i-1], [loc["latitude"], loc["longitude"]]],
                    color='red',
                    weight=2,
                    opacity=0.6
                ).add_to(m)

        m.fit_bounds(coordinates)

        output_map = file +"_"+uuid+".html"
        
        m.save(os.path.join(path, output_map))

    conn.close()

def main():
    logs = []
    parser = argparse.ArgumentParser(description='SmartTAg parSER')

    parser.add_argument('-s', '--smart', type=str, help='SmartThings Path')
    parser.add_argument('-f', '--find', type=str, help='Samsung Find Path')
    parser.add_argument('-i', '--input', type=str, help='InputDB Path with filename')
    parser.add_argument('-o', '--output', type=str, help='OutputDB Path')

    args = parser.parse_args()

    command = ' '.join(sys.argv)
    logs.append("SmartTAg parSER")
    logs.append("1. User cmd")
    logs.append(command)
    logs.append("")

    if args.smart:
        smartThings_path = args.smart
        inputmode = 0
    elif args.input:
        inputmode = 1
        input_fullpath = args.input
    else:
        print("SmartThing Path Needed, Option -s")
        sys.exit(-1)

    if args.find:
        samsungFind_path = args.find

    if args.output:
        output_path = args.output
    else:
        print("Output Path Needed, Option -o")
        sys.exit(-1)

    if inputmode == 0:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        dBfilename = input("Input Output DB name: ")

        if not dBfilename:
           dBfilename = f"output_{timestamp}.db"

        db_path = os.path.join(output_path, dBfilename)

        if os.path.exists(db_path):
            print(f"Change your file name: {dBfilename}")
            sys.exit(-1)

        conn_output = sqlite.connect(db_path)
        cursor_output = conn_output.cursor()

        cursor_output.execute('''
            CREATE TABLE IF NOT EXISTS tagActivity (
    	timestamp	TEXT,
    	uuid	TEXT,
    	infotype	TEXT,
    	name	TEXT,
    	info	TEXT,
    	source	TEXT,
    	raw	TEXT)
        ''')

        cursor_output.execute('''
            CREATE TABLE IF NOT EXISTS persistentLog (
    	timestamp	TEXT,
    	uuid TEXT,
    	raw	TEXT)
        ''')

        cursor_output.execute('''
            CREATE TABLE IF NOT EXISTS internaluuid (uuid TEXT,
            description TEXT)
        ''')

        spath = os.path.join(smartThings_path, 'databases')

        if os.path.isdir(spath):
            files = [f for f in os.listdir(spath)]
            pattern = r"com\.samsung\.android\.pluginplatform\.pluginbase\.sdk\.PluginSQLiteOpenHelper\.\S+\.location_history$"
            locationdb = [dbfile for dbfile in files if re.match(pattern, dbfile)]

            logs.append("2. Parsed following files")
            
            new_version_flag = 0
            if 'DataLayerData.db' in files:
                #new version oneconnect
                new_version_flag = 1
                logs.append('Parsing BleDeviceCapabilityStatusDomain table in DataLayerData.db')
                parse_DeviceCapability(cursor_output, spath, 'DataLayerData.db')
                logs.append('Parsing DeviceDomain table in DataLayerData.db')
                parse_DeviceData(cursor_output, spath, 'DataLayerData.db')
                if 'DataLayerData_core.db' in files:
                    logs.append('Parsing BleDeviceCapabilityStatusDomain table in DataLayerData_core.db')
                    parse_DeviceCapability(cursor_output, spath, 'DataLayerData_core.db')
                    logs.append('Parsing DeviceDomain table in DataLayerData_core.db')
                    parse_DeviceData(cursor_output, spath, 'DataLayerData_core.db')
            else:
                #for old version
                if 'DeviceCapabilityStatusData.db' in files:
                    logs.append('Parsing DeviceCapabilityStatusData.db')
                    parse_DeviceCapability(cursor_output, spath, 'DeviceCapabilityStatusData.db')
                if 'DeviceCapabilityStatusData_core.db' in files:
                    logs.append('Parsing DeviceCapabilityStatusData_core.db')
                    parse_DeviceCapability(cursor_output, spath, 'DeviceCapabilityStatusData_core.db')
                if 'DeviceData.db' in files:
                    logs.append('Parsing DeviceData.db')
                    parse_DeviceData(cursor_output, spath, 'DeviceData.db')
                if 'DeviceData_core.db' in files:
                    logs.append('Parsing DeviceData_core.db')
                    parse_DeviceData(cursor_output, spath, 'DeviceData_core.db')
            if 'PersistentLogData.db' in files:
                logs.append('Parsing PersistentLogData.db')
                parse_PersistentLogData(cursor_output, spath, 'PersistentLogData.db')
            if 'EasySetupIconNameDb.db' in files:
                logs.append('Parsing EasySetupIconNameDb.db')
                parse_EasySetup(cursor_output, spath, 'EasySetupIconNameDb.db')
            if 'InternalSettings.db' in files:
                logs.append('Parsing InternalSettings.db')
                parse_InternalSettings(cursor_output, spath, 'InternalSettings.db')
            if 'Fme.db' in files:
                logs.append('Parsing Fme.db')
                parse_Fme(cursor_output, spath, 'Fme.db')
            if 'BackgroundDeviceData.db' in files and new_version_flag ==0:
                logs.append('Parsing BackgroundDeviceData.db')
                parse_DeviceData(cursor_output, spath, 'BackgroundDeviceData.db')
            if locationdb:
                logs.append('Parsing Locationhistory')
                parse_locationhistory(cursor_output, spath, locationdb[0])
        else:
            print(f'Path {spath} doesn\'t exist')
            sys.exit(-1)

        xpath = os.path.join(smartThings_path, 'shared_prefs')

        if os.path.isdir(xpath):
            files = [f for f in os.listdir(xpath)]
            if 'FME_SELECTED_DEVICE.xml' in files:
                logs.append('Parsing FME_SELECTED_DEVICE.xml')
                parse_fme_selected_device(cursor_output, xpath, 'FME_SELECTED_DEVICE.xml')
        else:
            print(f'Path {xpath} doesn\'t exist')
            sys.exit(-1)

        cpath = os.path.join(smartThings_path, 'cache')

        if os.path.isdir(cpath):
            search_vendor_in_cache(cursor_output, cpath)
            search_uuid_in_cache(cursor_output, cpath)
        else:
            print(f'Path {cpath} doesn\'t exist')
            sys.exit(-1)

        if args.find:
            fpath = os.path.join(samsungFind_path, 'databases')
            if os.path.isdir(fpath):
                logs.append('Parsing app-database.db')
                parse_appdatabase(cursor_output, fpath, 'app-database.db')
            else:
                print(f'Path {cpath} doesn\'t exist')
                sys.exit(-1)

        conn_output.commit()
        conn_output.close()

        all_tags = search_deletedTag(output_path, dBfilename)

        outputfile = os.path.join(output_path, dBfilename+'.txt')

        with open(outputfile, 'w', encoding='utf-8') as file:
            for log in logs:
                file.write(log + "\n")

            for tag in all_tags:
                get_information_tag(output_path, dBfilename, file, tag[0], tag[1])

    else: #inputmode
        input_path, dBfilename = os.path.split(input_fullpath)

        all_tags = search_deletedTag(input_path, dBfilename)

        outputfile = os.path.join(output_path,dBfilename+'.txt')

        with open(outputfile, 'w', encoding='utf-8') as file:
            for log in logs:
                file.write(log + "\n")

            for tag in all_tags:
                get_information_tag(input_path, dBfilename, file, tag[0], tag[1])

    file.close()

if __name__ == "__main__":
    main()
