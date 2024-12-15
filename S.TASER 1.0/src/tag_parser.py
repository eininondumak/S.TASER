#! /usr/bin/env python
# # -*- coding: utf-8 -*-

# parser.py
import os
import re
import json
import time
from datetime import datetime, timezone
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, parse_qs
import pandas as pd
from typing import Tuple

import src.sqlite3db as sq
import src.query as qu

import logging
logger = logging.getLogger("app")

# -----------------------------#
# Function of Parser
def start_parsing(smartThings_path: str, samsungFind_path: str, retdb_path: str) -> Tuple[dict, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    logger.debug("Function called")

    if not sq.test(retdb_path):
        sq.execute_query(retdb_path, qu.INITIAL_DB_SCHEMA)

    smartthings_handlers = {
        'DataLayerData.db': parse_DeviceCapability,         # Parsing BleDeviceCapabilityStatusDomain table in DataLayerData.db
        'DataLayerData.db': parse_DeviceData,               # Parsing DeviceDomain table in DataLayerData.db
        'DataLayerData_core.db': parse_DeviceCapability,    # Parsing BleDeviceCapabilityStatusDomain table in DataLayerData_core.db
        'DataLayerData_core.db': parse_DeviceData,          # Parsing DeviceDomain table in DataLayerData_core.db

        'DeviceCapabilityStatusData.db': parse_DeviceCapability,        # Parsing DeviceCapabilityStatusData.db
        'DeviceCapabilityStatusData_core.db': parse_DeviceCapability,   # Parsing DeviceCapabilityStatusData_core.db
        'DeviceData.db': parse_DeviceData,                              # Parsing DeviceData.db
        'DeviceData_core.db': parse_DeviceData,                         # Parsing DeviceData_core.db
        'BackgroundDeviceData.db': parse_DeviceData,                    # Parsing BackgroundDeviceData.db

        'PersistentLogData.db': parse_PersistentLogData,    # Parsing PersistentLogData.db
        'EasySetupIconNameDb.db': parse_EasySetup,          # Parsing EasySetupIconNameDb.db
        'InternalSettings.db': parse_InternalSettings,      # Parsing InternalSettings.db
        'Fme.db': parse_Fme,                                # Parsing Fme.db
        
        '.location_history' : parse_Default,
        'FME_SELECTED_DEVICE.xml' : parse_Default,
        'app-database.db' : parse_Default
    }

    parsing_ret = dict()
    parsing_ret = {key: False for key in smartthings_handlers.keys()}

    stdb_path = os.path.join(smartThings_path, 'databases')
    if os.path.isdir(stdb_path):
        stdb_files = [f for f in os.listdir(stdb_path)]
        matching_files = list(filter(lambda x: x in smartthings_handlers, stdb_files))
        for stfile in matching_files:
            spath = os.path.join(stdb_path, stfile)
            handler_function = smartthings_handlers[stfile]
            ret = handler_function(spath, retdb_path)
            logger.info(f"Parsing \'{stfile}\' with function {handler_function.__name__}() = {ret}")
            if not parsing_ret[stfile]:
                parsing_ret[stfile] = ret

        pattern = r"com\.samsung\.android\.pluginplatform\.pluginbase\.sdk\.PluginSQLiteOpenHelper\.\S+\.location_history$"
        locationdb = [dbfile for dbfile in stdb_files if re.match(pattern, dbfile)]
        if locationdb:
            spath = os.path.join(stdb_path, locationdb[0])
            ret = parse_locationhistory(spath, retdb_path)
            logger.info(f"Parsing \'{locationdb[0]}\' with function parse_locationhistory() = {ret}")
            if not parsing_ret['.location_history']:
                parsing_ret['.location_history'] = ret
    else:
        logger.warning(f'Path {stdb_path} doesn\'t exist')
        #return
    
    xpath = os.path.join(smartThings_path, 'shared_prefs')
    if os.path.isdir(xpath):
        files = [f for f in os.listdir(xpath)]
        if 'FME_SELECTED_DEVICE.xml' in files:
            spath = os.path.join(xpath, 'FME_SELECTED_DEVICE.xml')
            ret = parse_fme_selected_device(spath, retdb_path)
            parsing_ret['FME_SELECTED_DEVICE.xml'] = ret
            logger.info(f"Parsing \'FME_SELECTED_DEVICE.xml\' with function parse_fme_selected_device() = {ret}")
    else:
        logger.warning(f'Path {xpath} doesn\'t exist')
        #return
    
    cpath = os.path.join(smartThings_path, 'cache')
    if os.path.isdir(cpath):
        search_vendor_in_cache(cpath, retdb_path)
        search_deviceId_in_cache(cpath, retdb_path)
    else:
        logger.warning(f'Path {cpath} doesn\'t exist')
        #return

    if samsungFind_path:
        fpath = os.path.join(samsungFind_path, 'databases')
        if os.path.isdir(fpath):
            files = [f for f in os.listdir(fpath)]
            if 'app-database.db' in files:
                spath = os.path.join(fpath, 'app-database.db')
                ret = parse_appdatabase(spath, retdb_path)
                parsing_ret['app-database.db'] = ret
                logger.info(f"Parsing \'app-database.db\' with function parse_appdatabase() = {ret}")
        else:
            logger.warning(f'Path {fpath} doesn\'t exist')
            #return

    all_tag_df, all_loc_df, all_enc_df = get_parsed_data(retdb_path)

    return parsing_ret, all_tag_df, all_loc_df, all_enc_df


def get_parsed_data(retdb_path: str) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    logger.debug("Function called")
    
    all_tags = search_deletedTag(retdb_path)

    columns = ["deviceId","Status","RecoveredMethod","label","Model","mnId","SetupId","logId","RegistrationTime(UTC)"]
    all_tag_df = pd.DataFrame(columns=columns)

    columns = ["deviceId","StartTime(UTC)","EndTime(UTC)","Count","Latitude","Longitude","Accuracy","Source"]
    all_loc_df = pd.DataFrame(columns=columns)

    columns = ["deviceId","Time(UTC)","EncDeviceId","Count"]
    all_enc_df = pd.DataFrame(columns=columns)

    for tag in all_tags or []:
        tag_df = get_tag_information(retdb_path, tag['deviceId'], tag['description'])
        if not tag_df.empty:
            all_tag_df = pd.concat([all_tag_df, tag_df], sort=False, ignore_index=True)

        loc_df = get_tag_location_history(retdb_path, tag['deviceId'])
        if not loc_df.empty:
            all_loc_df = pd.concat([all_loc_df, loc_df], sort=False, ignore_index=True)

        enc_df = get_tag_enclocation_history(retdb_path, tag['deviceId'])
        if not enc_df.empty:
            all_enc_df = pd.concat([all_enc_df, enc_df], sort=False, ignore_index=True)

    all_tag_df = all_tag_df.drop_duplicates()
    all_tag_df = all_tag_df.sort_values(by=['deviceId','RegistrationTime(UTC)'] ,ascending=True, ignore_index=True)

    all_loc_df = all_loc_df.drop_duplicates()
    all_loc_df = all_loc_df.sort_values(by=['deviceId','StartTime(UTC)'] ,ascending=True, ignore_index=True)
    all_loc_df['Latitude'] = pd.to_numeric(all_loc_df['Latitude'], errors="coerce")
    all_loc_df['Longitude'] = pd.to_numeric(all_loc_df['Longitude'], errors="coerce")

    all_enc_df = all_enc_df.drop_duplicates()
    all_enc_df = all_enc_df.sort_values(by=['deviceId','Time(UTC)'] ,ascending=True, ignore_index=True)

    return all_tag_df, all_loc_df, all_enc_df


def check_smartThings_path(smartThings_path: str) -> bool:
    logger.debug("Function called")
    
    path = os.path.join(smartThings_path, 'databases')
    if not os.path.isdir(path):
        return False
    
    path = os.path.join(path, 'PersistentLogData.db')
    if not os.path.isfile(path):
        return False
    
    path = os.path.join(smartThings_path, 'shared_prefs')
    if not os.path.isdir(path):
        return False
    
    path = os.path.join(smartThings_path, 'cache')
    if not os.path.isdir(path):
        return False
    
    return True


def insert_into_tag_activity(db_path, data) -> bool:
    #logger.debug("Function called")
    
    return sq.execute_query(db_path, qu.INSERT_TAG_ACTIVITY_SQL, data)


def parse_Default(spath, db_path) -> bool:
    logger.debug("Function called")
    
    return False


def parse_PersistentLogData(spath, db_path) -> bool:
    logger.debug("Function called")

    persistentlogdata_result = sq.fetch_query(spath, qu.PERSISTENTLOGDATA_SQL)
    if not persistentlogdata_result:
        return False

    deviceId_pattern = r'deviceId=(?:(?:[0-9a-fA-F]{32})|(?:[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})|(?:[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-\*{4}-\*{4}-[0-9a-fA-F]{12}))'

    '''
    deviceId_pattern = r'deviceId=(?:(?:[0-9a-fA-F]{32})|(?:[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}))'
    '''

    action_added = 'added     :'
    action_removed = 'removed   :'

    for item in persistentlogdata_result:
        timestamp = item['time']
        description = item['description']
        if action_added in description:
            action_type = "Add"
        elif action_removed in description:
            action_type = "Erase"
        deviceId_match = re.findall(deviceId_pattern, description, re.IGNORECASE)

        for deviceId in deviceId_match:
            deviceId = deviceId.replace("deviceId=", "")
            if action_type == "Add":
                info = ""
            elif action_type == "Erase":
                info = deviceId

            data = (timestamp, deviceId, action_type, '', info, os.path.basename(spath), '')
            insert_into_tag_activity(db_path, data)
            
            data = (timestamp, deviceId, description)
            sq.execute_query(db_path, qu.INSERT_PERSISTENTLOG_SQL, data)
    
    return True


def parse_DeviceCapability(spath, db_path) -> bool:
    logger.debug("Function called")

    devicecapability = sq.fetch_query(spath, qu.DEVICECAPABILITY_SQL)
    if not devicecapability:
        return False

    for device in devicecapability:
        data = (device['time'], 
                device['deviceId'], 
                'Property', 
                '',
                str(device['capabilityId']) + ", " + str(device['stringifyValue']), 
                os.path.basename(spath),
                json.dumps(device))
        
        insert_into_tag_activity(db_path, data)
    
    return True


def parse_EasySetup(spath, db_path) -> bool:
    logger.debug("Function called")

    easysetup_result = sq.fetch_query(spath, qu.EASYSETUP_SQL)
    if not easysetup_result:
        return False

    for easysetup in easysetup_result:
        data = (easysetup['time'], 
                '', 
                'Register from db', 
                '',
                str(easysetup['displayName']) + ", " 
                 + str(easysetup['mnId']) + ", " 
                 + str(easysetup['setupId']),
                os.path.basename(spath), 
                json.dumps(easysetup))
        
        insert_into_tag_activity(db_path, data)
    
    return True


def parse_InternalSettings(spath, db_path) -> bool:
    logger.debug("Function called")

    internal_result = sq.fetch_query(spath, qu.INTERNALSETTINGS_SQL)
    if not internal_result:
        return False

    for item in internal_result:
        key = 'tag_owner_guid'
        try:
            deviceId = item['settings_key'].replace(key, "")
            data = (deviceId,)
            sq.execute_query(db_path, qu.INSERT_INTERNALUUID_SQL, data)
            
        except ValueError:
            continue

    return True


def parse_Fme(spath, db_path) -> bool:
    logger.debug("Function called")

    fme_result = sq.fetch_query(spath, qu.FME_SQL)
    if not fme_result:
        return False

    infoList = parse_infoList(fme_result[0]['infoList'])
    for info in infoList:
        data = (info['timestamp'], 
                info['deviceId'], 
                'location', 
                info['label'],
                json.dumps({'start': info['timestamp'], 
                            'end': '', 
                            'count': 1, 
                            'latitude': str(info['latitude']), 
                            'longitude': str(info['longitude']), 
                            'accuracy': ''}),
                os.path.basename(spath),
                json.dumps(info))
        
        insert_into_tag_activity(db_path, data)

    return True


def parse_infoList(infolist) -> list:
    logger.debug("Function called")

    data = json.loads(infolist)
    tag_items = []

    for item in data:
        firstlayer_keys = item.keys()
        if 'type' in firstlayer_keys:
            if item['type'] == 'TRACKER':
                if 'geoInfo' in firstlayer_keys:
                    timestamp = datetime.strptime(str(item['geoInfo']['timestamp']), '%Y%m%d%H%M%S')
                    tag_items.append(
                        {'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'), 
                         'deviceId': item['id'], 
                         'label': item['name'],
                         'latitude': item['geoInfo']['lat'], 
                         'longitude': item['geoInfo']['long']})

    return tag_items


def parse_DeviceData(spath, db_path) -> bool:
    logger.debug("Function called")

    devicedata_result = sq.fetch_query(spath, qu.DEVICEDATA_SQL)
    if not devicedata_result:
        return False

    for item in devicedata_result:
        integration = parse_integration(item['integration'])
        data = (item['time'], 
                item['deviceId'], 
                'Registered', 
                item['label'],
                integration['vendor']['mnId'] + ", " 
                + integration['vendor']['setupId'] + ", " 
                + integration['vendor']['modelName'] + ", " 
                + integration['logId'], 
                os.path.basename(spath),
                json.dumps({'timestamp': item['time'],
                            'deviceId': item['deviceId'], 
                            'label': item['label'], 
                            'integration': integration}))
        
        insert_into_tag_activity(db_path, data)
    
    return True


def parse_integration(integration):
    logger.debug("Function called")

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
            createtime = time.strftime(
                '%Y-%m-%d %H:%M:%S', time.gmtime(data['bleD2D']['metadata']['createTime']))
            updatetime = time.strftime(
                '%Y-%m-%d %H:%M:%S', time.gmtime(data['bleD2D']['metadata']['updateTime']))
            thirdlayer_keys = data['bleD2D']['metadata'].keys()
            if 'lastKnownConnection' in thirdlayer_keys:
                connecteduser = data['bleD2D']['metadata']['lastKnownConnection']['connectedUser']
                connecteddevice = data['bleD2D']['metadata']['lastKnownConnection']['connectedDevice']
    
    ret =  {'vendor': vendor, 
            'logId': identifier, 
            'user': connecteduser, 
            'device': connecteddevice,
            'createtime': createtime, 
            'updatetime': updatetime}
    
    return ret


def parse_locationhistory(spath, db_path) -> bool:
    logger.debug("Function called")

    history_result = sq.fetch_query(spath, qu.LOCATIONHISTORY_SQL)
    if not history_result:
        return False

    for history in history_result:
        data = (history['date'], 
                history['encDeviceId'], 
                'Enclocation', 
                '', 
                '', 
                os.path.basename(spath), 
                history['history'])
        
        insert_into_tag_activity(db_path, data)
    
    return True
        

def parse_fme_selected_device(xpath, db_path) -> bool:
    logger.debug("Function called")

    cnt = 0
    tree = ET.parse(xpath)
    root = tree.getroot()

    for child in root:
        if child.attrib['name'] == 'SELECTED_FME_ALL_INFO':
            data_items = json.loads(child.text)
            for data in data_items:
                if data['type'] == 'TAG':
                    timestamp = datetime.strptime(str(data['firstTime']), '%Y%m%d%H%M%S')
                    data = (timestamp.strftime('%Y-%m-%d %H:%M:%S'), 
                            data['id'], 
                            'location',
                            data['name'], 
                            json.dumps({'start': timestamp.strftime('%Y-%m-%d %H:%M:%S'), 
                                        'end': '', 
                                        'count': 1, 
                                        'latitude': data['firstLat'],
                                        'longitude': data['firstLong'],
                                        'accuracy': data['firstAcc']}),
                            os.path.basename(xpath),
                            json.dumps({'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                                        'deviceId': data['id'], 
                                        'name': data['name'], 
                                        'Latitude': data['firstLat'], 
                                        'longitude': data['firstLong'],
                                        'Accuracy': data['firstAcc']}))
                    
                    insert_into_tag_activity(db_path, data)
                    cnt = cnt + 1
    
    if cnt > 0:
        return True
    else:
        return False


def search_vendor_in_cache(cpath, db_path):
    logger.debug("Function called")

    oneconnect_cache_dir = ['http-Core', 'http-Main',
                            'http-PluginNativeFME', 'http-PluginWebApplication']
    cache_keyword = ['api.smartthings.com/catalogs/api/v3/easysetup/setupdata',
                     'client.smartthings.com/chaser/trackers/lostmessage']

    for sub_path in oneconnect_cache_dir:
        full_path = os.path.join(cpath, sub_path)
        if not os.path.isdir(full_path):
            logger.info(f'{full_path} dosen\'t exist')
            continue

        for keyword in cache_keyword:
            match_strings = find_files_with_vendor(full_path, keyword)
            if len(match_strings) != 0:
                for match_data in match_strings:
                    data = (match_data['timestamp'], 
                            '', 
                            'Register from webcache', 
                            '',
                            match_data['vendor']['mnId'] + ", " 
                             + match_data['vendor']['setupId'] + ", " 
                             + match_data['vendor']['modelName'] + ", " 
                             + match_data['vendor']['logId'],
                            match_data['source'], 
                            json.dumps(match_data))

                    insert_into_tag_activity(db_path, data)


def find_files_with_vendor(directory, search_string):
    logger.debug("Function called")

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
                        match = re.findall(
                            pattern, text_data, re.IGNORECASE)[0]
                        query_params = parse_qs(urlparse(match).query)
                        query_dict = {key: value[0]
                                      for key, value in query_params.items()}

                        if flag == 1:
                            vendor_info = {'mnId': query_dict['mnId'], 
                                           'setupId': query_dict['setupId'],
                                           'logId': '', 
                                           'modelName': ''}
                        elif flag == 2:
                            vendor_info = {'mnId': query_dict['mnId'], 
                                           'setupId': query_dict['setupId'],
                                           'modelName': query_dict['modelName'],
                                           'logId': query_dict['serialNumber']}

                        try:
                            time_match = re.findall(time_pattern, text_data, re.IGNORECASE)[0]
                            timestamp = datetime.strptime(time_match, '%a, %d %b %Y %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
                        except IndexError:
                            continue

                        matching_files.append({'timestamp': timestamp, 'vendor': vendor_info, 'source': file_path})

            except (UnicodeDecodeError, FileNotFoundError):
                continue

    return matching_files


def search_deviceId_in_cache(cpath, db_path):
    logger.debug("Function called")

    oneconnect_cache_dir = ['http-Core', 'http-Main',
                            'http-PluginNativeFME', 'http-PluginWebApplication']
    '''                        
    patterns = [
        r'client\.smartthings\.com/presentation\?deviceId=(?:(?:[0-9a-fA-F]{32})|(?:[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}))',
        r'client\.smartthings\.com/devices/status\?includeUserDevices=true&excludeLocationDevices=false&deviceId=(?:(?:[0-9a-fA-F]{32})|(?:[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}))'
    ]
    '''

    patterns = [
    r'client\.smartthings\.com/presentation\?deviceId=(?:(?:[0-9a-fA-F]{32})|(?:[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})|(?:[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-\*{4}-\*{4}-[0-9a-fA-F]{12}))',
    r'client\.smartthings\.com/devices/status\?includeUserDevices=true&excludeLocationDevices=false&deviceId=(?:(?:[0-9a-fA-F]{32})|(?:[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})|(?:[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-\*{4}-\*{4}-[0-9a-fA-F]{12}))'
    ]   

    combined_pattern = '|'.join(patterns)

    for sub_path in oneconnect_cache_dir:
        full_path = os.path.join(cpath, sub_path)
        if not os.path.isdir(full_path):
            logger.info(f'{full_path} dosen\'t exist')
            continue

        match_strings = find_files_with_deviceId(full_path, combined_pattern)
        if len(match_strings) != 0:
            for match_data in match_strings:
                data = (match_data['timestamp'], 
                        match_data['deviceId'], 
                        'webcache', 
                        '', 
                        match_data['string'], 
                        match_data['source'], 
                        '')

                insert_into_tag_activity(db_path, data)


def find_files_with_deviceId(directory, search_string):
    logger.debug("Function called")

    matching_files = []

    deviceId_pattern = r'(?:(?:[0-9a-fA-F]{32})|(?:[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})|(?:[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-\*{4}-\*{4}-[0-9a-fA-F]{12}))'

    '''
    deviceId_pattern = r'(?:(?:[0-9a-fA-F]{32})|(?:[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}))'
    '''

    time_pattern = r'date:\s*(.*?)\s*GMT'

    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text_data = f.read()

                    try:
                        strings_match = re.findall(
                            search_string, text_data, re.IGNORECASE)[0]
                        if strings_match:
                            try:
                                deviceId = re.findall(
                                    deviceId_pattern, text_data, re.IGNORECASE)[0]
                            except IndexError:
                                continue

                            try:
                                time_match = re.findall(
                                    time_pattern, text_data, re.IGNORECASE)[0]
                                timestamp = datetime.strptime(time_match, '%a, %d %b %Y %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
                            except IndexError:
                                continue

                            matching_files.append(
                                {'timestamp': timestamp, 
                                 'string': strings_match[:-len(deviceId)], 
                                 'deviceId': deviceId, 
                                 'source': file_path}
                                 )

                    except IndexError:
                        continue

            except (UnicodeDecodeError, FileNotFoundError):
                continue

    return matching_files


def parse_appdatabase(cpath, db_path) -> bool:
    logger.debug("Function called")

    appdata_result = sq.fetch_query(cpath, qu.APPDATABASE_SQL)
    if not appdata_result:
        return False

    for appdata in appdata_result:
        data = (appdata['start'], 
                appdata['deviceId'], 
                'location', 
                '', 
                json.dumps({'start': appdata['start'], 
                            'end': appdata['end'], 
                            'count': appdata['count'],
                            'latitude': str(appdata['latitude']), 
                            'longitude': str(appdata['longitude']), 
                            'accuracy': ''}),
                os.path.basename(cpath),
                json.dumps(appdata))
        
        insert_into_tag_activity(db_path, data)

    return True


def search_deletedTag(db_path):
    logger.debug("Function called")

    all_deviceId = sq.fetch_query(db_path, qu.SELECT_INTERNALUUID_SQL)
    if all_deviceId:
        all_deviceId = {item['deviceId'] for item in all_deviceId}
    else:
        all_deviceId = set()

    live_deviceId = sq.fetch_query(db_path, qu.SELECT_TAGACTIVITYUUID_SQL)
    if live_deviceId:
        live_deviceId = {item['deviceId'] for item in live_deviceId}
    else:
        live_deviceId = set()

    deleted_deviceId = all_deviceId - live_deviceId

    for deviceId in deleted_deviceId:
        sq.execute_query(db_path, qu.UPDATE_DELETEDUUID_SQL, (deviceId,))

    deviceIds = sq.fetch_query(db_path, qu.SELECT_INTERNALUUID_DESC_SQL)

    return deviceIds


def get_tag_information(db_path, deviceId, deleted):
    logger.debug("Function called")

    taglabel = 'unknown'
    taglogId = 'unknown'
    tagmodel = 'unknown'
    tagmnid = 'unknown'
    tagsetupid = 'unknown'
    registrationTime = 'unknown'

    columns = ["deviceId","Status","RecoveredMethod","label","Model","mnId","SetupId","logId","RegistrationTime(UTC)"]
    df = pd.DataFrame(columns=columns)

    if deleted:
        # first: try to find backupdata
        #Q1
        backup_one = sq.fetch_query(db_path, qu.Q1_SQL, (deviceId,))
        if backup_one is not None:
            for taginfo in backup_one:
                taglabel = taginfo['name']
                tagmnid = taginfo['info'].split(',')[0]
                tagsetupid = taginfo['info'].split(',')[1]
                tagmodel = taginfo['info'].split(',')[2]
                taglogId = taginfo['info'].split(',')[3]
                registrationTime = taginfo['timestamp']

                new_data = [deviceId, "Recovered", "backup data", taglabel, tagmodel, tagmnid, tagsetupid, taglogId, registrationTime]
                df.loc[len(df)] = new_data

                print_tag_information(deviceId, "Recovered", "backup data", taglabel, tagmodel, tagmnid, tagsetupid, taglogId, registrationTime)

        else:
            # second: try to find logdata
            #Q2
            deleted_info = sq.fetch_query(db_path, qu.Q2_SQL, (deviceId,))

            if deleted_info is not None:
                # found!
                for taginfo in deleted_info:
                    try:
                        deleted_time = taginfo['timestamp']
                        keywordlabel = r"label=([^,]+), manufacturerCode="
                        keywordlogId = r"identifier=([A-Za-z0-9]*[A-Za-z0-9]{1}\*{4}[A-Za-z0-9]*),"

                        '''
                        keywordlogId = r"identifier=([A-Za-z0-9]+),"
                        '''

                        keywordVender = r'"vendor":\{"mnId":"(?P<mnId>[^"]+)","setupId":"(?P<setupId>[^"]+)","modelName":"(?P<modelName>[^"]+)"\}'
                        keywordData = r'"createTime":(\d+)'

                        #Q3
                        result_data = sq.fetch_query(db_path, qu.Q3_SQL, (deleted_time, deviceId))

                        if result_data is not None:
                            for rdata in result_data:
                                matches = re.findall(keywordlabel, rdata['raw'])
                                if matches:
                                    taglabel = matches[0]

                                matches = re.findall(keywordlogId, rdata['raw'])
                                if matches:
                                    taglogId = matches[0]

                                matches = re.findall(keywordVender, rdata['raw'])
                                if matches:
                                    tagmnid = matches[0][0]
                                    tagsetupid = matches[0][1]
                                    tagmodel = matches[0][2]

                                matches = re.findall(keywordData, rdata['raw'])
                                if matches:
                                    registrationTime = datetime.fromtimestamp(int(matches[0]), timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
                                    
                    except Exception as e:
                        logger.error(f"{e}: Error during parsing logdata")

                    new_data = [deviceId, "Recovered", "log data", taglabel, tagmodel, tagmnid, tagsetupid, taglogId, registrationTime]
                    df.loc[len(df)] = new_data

                    print_tag_information(deviceId, "Recovered", "log data", taglabel, tagmodel, tagmnid, tagsetupid, taglogId, registrationTime)

            else:
                # Pattern recovery
                #Q4
                logone = sq.fetch_query(db_path, qu.Q4_SQL, (deviceId,))
                # flags = 0 (fail), 1 (succuess)
                recovery_flags = 0

                if logone is not None:
                    for taginfo in logone:
                        info_patten = ['client.smartthings.com/devices/status?includeUserDevices=true&excludeLocationDevices=false&deviceId=',
                                       'client.smartthings.com/presentation?deviceId=']
                        if taginfo['info'] in info_patten:
                            registered_time = taginfo['timestamp']
                            #Q5
                            results = sq.fetch_query(db_path, qu.Q5_SQL, (registered_time, registered_time,))
                            if results is not None:
                                # found 'Register from webcache or Register from db' in infotype
                                for i, log in enumerate(results):
                                    registrationTime = log['timestamp']
                                    if log['infotype'] == 'Register from webcache':
                                        if log['info'].split(',')[2]:
                                            registrationTime = log['timestamp']
                                            tagmnid = log['info'].split(',')[0]
                                            tagsetupid = log['info'].split(',')[1]
                                            tagmodel = log['info'].split(',')[2]
                                            taglogId = log['info'].split(',')[3]

                                            new_data = [deviceId, "Recovered", "pattern", taglabel, tagmodel, tagmnid, tagsetupid, taglogId, registrationTime]
                                            df.loc[len(df)] = new_data

                                            print_tag_information(deviceId, "recovered", "pattern", taglabel, tagmodel, tagmnid, tagsetupid, taglogId, registrationTime)
                                            recovery_flags = 1


                        if recovery_flags != 1:
                            # every fail case with webcache
                            registrationTime = registered_time
            
                if recovery_flags != 1:
                    # put failcase data in dataframe    
                    new_data = [deviceId, "deleted", "pattern", taglabel, tagmodel, tagmnid, tagsetupid, taglogId, registrationTime]
                    df.loc[len(df)] = new_data

                    print_tag_information(deviceId, "deleted", "pattern", taglabel, tagmodel, tagmnid, tagsetupid, taglogId, registrationTime)

    else:
        # live tag
        #Q6
        taginfos = sq.fetch_query(db_path, qu.Q6_SQL, (deviceId,))
        for taginfo in taginfos:
            taglabel = taginfo['name']
            tagmnid = taginfo['info'].split(',')[0]
            tagsetupid = taginfo['info'].split(',')[1]
            tagmodel = taginfo['info'].split(',')[2]
            taglogId = taginfo['info'].split(',')[3]
            registrationTime = taginfo['timestamp']

            new_data = [deviceId, "live", "-", taglabel, tagmodel, tagmnid, tagsetupid, taglogId, registrationTime]
            df.loc[len(df)] = new_data

            print_tag_information(deviceId, "live", "-", taglabel, tagmodel, tagmnid, tagsetupid, taglogId, registrationTime)

    return df


def print_tag_information(deviceId, status, method, taglabel, tagmodel, tagmnid, tagsetupid, taglogId, registrationTime):
    logger.debug("Function called")

    logger.info(f"Tag deviceId: {deviceId}, status: {status}")
    logger.info(f"Recovered Method: {method}")
    logger.info(f"Tag label: {taglabel}")
    logger.info(f"Tag model: {tagmodel}")
    logger.info(f"Tag mnId: {tagmnid}, setupId: {tagsetupid}")
    logger.info(f"Tag logId: {taglogId}")
    logger.info(f"Tag reg time: {registrationTime}")


def get_tag_location_history(db_path, deviceId):
    logger.debug("Function called")
    logger.info("Tag's location history")

    #Q7
    activities = sq.fetch_query(db_path, qu.Q7_SQL, (deviceId,))

    columns = ["deviceId","StartTime(UTC)","EndTime(UTC)","Count","Latitude","Longitude","Accuracy","Source"]
    df = pd.DataFrame(columns=columns)

    index = 1
    for activity in activities or []:
        info = json.loads(activity['info'])
        new_data = [deviceId, activity['timestamp'], info['end'], info['count'], info['latitude'], info['longitude'], info['accuracy'], activity['source']]
        df.loc[len(df)] = new_data

        logger.info(f"{index}, "
                    f"start time: {activity['timestamp']}, "
                    f"end time: {info['end']}, "
                    f"count: {info['count']}, "
                    f"latitude: {info['latitude']}, "
                    f"longitude: {info['longitude']}, "
                    f"source: {activity['source']}")
        index += 1
    
    return df


def get_tag_enclocation_history(db_path, deviceId):
    logger.debug("Function called")
    logger.info("Tag's Enclocation history")

    #Q8
    activities = sq.fetch_query(db_path, qu.Q8_SQL, (deviceId[-4:],))

    columns = ["deviceId","Time(UTC)","EncDeviceId","Count"]
    df = pd.DataFrame(columns=columns)

    index = 1
    for activity in activities or []:
        new_data = [deviceId, activity['timestamp'], activity['deviceId'], activity['count']]
        df.loc[len(df)] = new_data

        logger.info(f"{index}, "
                    f"date: {activity['timestamp']}, "
                    f"EncDeviceId: {activity['deviceId']}, "
                    f"Count: {activity['count']}")
        index += 1
    
    return df
