#!/usr/bin/env python
# -*- coding: utf-8 -*-

# query.py

# Initial Database Schema
INITIAL_DB_SCHEMA = """
    CREATE TABLE IF NOT EXISTS tagActivity (
        timestamp      TEXT,
        uuid           TEXT,
        infotype       TEXT,
        name           TEXT,
        info           TEXT,
        source         TEXT,
        raw            TEXT
    );

    CREATE TABLE IF NOT EXISTS persistentLog (
        timestamp      TEXT,
        uuid           TEXT,
        raw            TEXT
    );

    CREATE TABLE IF NOT EXISTS internaluuid (
        uuid           TEXT,
        description    TEXT
    );
"""

#######################################################################

# 1. Device Data Query
DEVICEDATA_SQL = """
    SELECT 
        datetime(createdDate/1000, 'unixepoch') AS time, 
        deviceId, 
        name, 
        label, 
        integration 
    FROM 
        DeviceDomain 
    WHERE 
        integration LIKE '%bleD2D%';
"""

# 2. FME Query
FME_SQL = """
    SELECT 
        infoList, 
        pluginId 
    FROM 
        FmeAppData;
"""

# 3. Easy Setup Query
EASYSETUP_SQL = """
    SELECT 
        datetime(timestamp/1000, 'unixepoch') AS time, 
        mnId, 
        setupId, 
        displayName, 
        brandName 
    FROM 
        EasySetupIconDb;
"""

# 4. Persistent Log Data Query
PERSISTENTLOGDATA_SQL = """
    SELECT 
        datetime(timestamp/1000, 'unixepoch') AS time, 
        processName, 
        tag, 
        title, 
        description 
    FROM 
        PersistentLogDomain 
    WHERE 
        title LIKE 'getupdateddata' 
        AND (tag = 'DeviceResource' OR tag = 'DataLayerDataBaseContentProviderOnCore');
"""

# 5. Device Capability Query
DEVICECAPABILITY_SQL = """
    SELECT 
        datetime(timestamp/1000, 'unixepoch') AS time, 
        deviceId, 
        capabilityId, 
        stringifyValue 
    FROM 
        BleDeviceCapabilityStatusDomain;
"""

# 6. Internal Settings Query
INTERNALSETTINGS_SQL = """
    SELECT 
        settings_key 
    FROM 
        insettings 
    WHERE 
        settings_key LIKE 'tag_owner_guid%';
"""

# 7. App Database Query
APPDATABASE_SQL = """
    SELECT 
        deviceId, 
        datetime(start/1000, 'unixepoch') AS start, 
        datetime(end/1000, 'unixepoch') AS end, 
        count, 
        latitude, 
        longitude, 
        address 
    FROM 
        item_history;
"""

# 8. Location History Query
LOCATIONHISTORY_SQL = """
    SELECT 
        encDeviceId, 
        datetime(date/1000, 'unixepoch') AS date, 
        history 
    FROM 
        EncLocationHistory;
"""

#######################################################################

# Insert Queries

INSERT_TAG_ACTIVITY_SQL = """
    INSERT INTO 
        tagActivity (timestamp, uuid, infotype, name, info, source, raw)
    VALUES 
        (?, ?, ?, ?, ?, ?, ?);
"""

INSERT_PERSISTENTLOG_SQL = """
    INSERT INTO 
        persistentLog (timestamp, uuid, raw)
    VALUES 
        (?, ?, ?);
"""

INSERT_INTERNALUUID_SQL = """
    INSERT INTO 
        internaluuid (uuid) 
    VALUES 
        (?);
"""

#######################################################################

# Select Queries

SELECT_INTERNALUUID_SQL = """
    SELECT 
        uuid 
    FROM 
        internaluuid;
"""

SELECT_TAGACTIVITYUUID_SQL = """
    SELECT
        DISTINCT uuid
    FROM
        tagActivity
    WHERE
        infotype = 'Registered'
        AND (source = 'DeviceData.db' OR source = 'DataLayerData.db')
"""


SELECT_INTERNALUUID_DESC_SQL = """
    SELECT 
        uuid, 
        description 
    FROM 
        internaluuid;
"""

#######################################################################

# Update Query

UPDATE_DELETEDUUID_SQL = """
    UPDATE 
        internaluuid 
    SET 
        description = 'deleted' 
    WHERE 
        uuid = ?;
"""

#######################################################################
Q1_SQL = """
    SELECT *
    FROM tagActivity
    WHERE uuid = ?
        AND infotype = 'Registered';
"""

Q2_SQL = """
    SELECT *
    FROM tagActivity
    WHERE uuid = ?
        AND infotype = 'Erase';
"""

Q3_SQL = """
    SELECT *
    FROM persistentLog
    WHERE timestamp = ?
        AND uuid = ?
        AND raw LIKE '%removed%';
"""

Q4_SQL = """
    SELECT *
    FROM tagActivity
    WHERE uuid = ?
        AND infotype = 'webcache'
    ORDER BY timestamp ASC;
"""

Q5_SQL = """
    SELECT *
    FROM tagActivity
    WHERE timestamp BETWEEN datetime(?, '-3 minutes') AND datetime(?)
        AND uuid = ''
        AND infotype LIKE 'Register%'
    ORDER BY timestamp ASC;
"""

Q6_SQL = """
    SELECT *
    FROM tagActivity
    WHERE uuid = ?
        AND infotype = 'Registered';
"""

Q7_SQL = """
    SELECT *
    FROM tagActivity
    WHERE uuid = ?
        AND infotype = 'location'
    ORDER BY timestamp ASC;
"""

Q8_SQL = """
    SELECT timestamp,
        uuid,
        COUNT(*) AS count
    FROM Tagactivity
    WHERE SUBSTR(uuid, -4) = ?
        AND infotype = 'Enclocation'
    GROUP BY timestamp
    HAVING count >= 1;
"""
