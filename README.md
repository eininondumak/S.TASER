# Smart Tag Parser (S.TASER)

### DFRWS EU 2025 - Samsung Tracking Tag Application Forensics in Criminal Investigations

<br>



## 1. Samsung tracking tags







## 2. Applications


|Name|Paper-proposal Ver.|Camera-ready Ver.|etc.|
|---|---|---|---|
|SmartThings (ST)|1.8.18.21|1.8.21.28|Rooting detection adpoted|
|SmartThings Find (STF)|1.8.21.28|1.8.27-10||
|Samsubg Find (SF)|1.3.12|1.4.00.10||


### * Applications' functions in the experiments

* Tag registration in [SmartThings](picture/Tag%20registration.jpg)

* Location data retrieval in [SmartThings Find/Samsung Find](picture/SmartThings%20Find.jpg)

* Tag deletion in [SmartThings](picture/Tag%20deletion.jpg)

* Location deletion in [SmartThings Find/Samsung Find](picture/Location%20deletion%20SF.jpg)

* Account logout in [SmartThings](picture/Sign%20out.jpg)

* Service withdrawal in [SmartThings](picture/Leave%20service.jpg)


## 3. Experimental scenarios and results


|No|Experiment type|Experiment summary|
|---|---|---|
|1|[Basic artifact structure](https://github.com/eininondumak/S.TASER/blob/main/Scenarios/1.md#1-artifact-structure)|Tag registration, location data retrieval|
|2|[Tracking tag registration](https://github.com/eininondumak/S.TASER/blob/main/Scenarios/2.md#2-tracking-tag-registraion)|Tag registration, deletion, re-registration and network packet collection|
|3|[Location data retrieval](https://github.com/eininondumak/S.TASER/blob/main/Scenarios/3.md#3-location-data-retrieval)|Location data retrieval through STF and SF, network packet collection|
|4|[Registered tracking tag deletion](https://github.com/eininondumak/S.TASER/blob/main/Scenarios/4.md#4-registered-tracking-tag-deletion)|Registered tag deletion through ST|
|5|[Location data deletion](https://github.com/eininondumak/S.TASER/blob/main/Scenarios/5.md#5-location-data-deletion)|Location data deletion through STF and SF|
|6|[Account logout](https://github.com/eininondumak/S.TASER/blob/main/Scenarios/6.md#6-account-logout)|Account logout through ST|
|7|[Service withdrawal](https://github.com/eininondumak/S.TASER/blob/main/Scenarios/7.md#7-service-withdrawal)|Withdrawing from the SmartThings service through ST|
|8|[Application synchronization](https://github.com/eininondumak/S.TASER/blob/main/Scenarios/8.md#8-application-synchronization)|Comparison of results after location data deletion and STF and SF synchronization in multi-device environment|

<br>

## 4. Artifacts structure of paper-proposal version


|Database (Table)|deviceId|mnId|setupId|modelName|logId(identifier)|timestamp|GeoInfo|
|---|---|---|---|---|---|---|---|
|DeviceData.db (DeviceDomain)|○|○|○|○|○|○|
|BackgroundDeviceData.db <br> (DeviceDomain)|○|○|○|○|○|○|
|DeviceData_core.db (DeviceDomain)|○|○|○|○|○|○|
|PersistentLogData.db (PersistentLogDomain)|○|○|○|○|○|○|
|Fme.db (FmeAppData)|○|○|||||○|
|DeviceCapabilityStatusData.db <br> (BleDeviceCapabilityStatusDomain)|○|||||||
|DeviceCapabilityStatus-<br>Data_core.db <br> (BleDeviceCapabilityStatusDomain)|○|||||||
|InternalSettings.db (insettings)|○|||||||
|EasySetupIconNameDb.db (EasySetupIconDb)|||○|○||○|
|FME_SELECTED_DEVICE.xml|○|○|||||○|
|cache Files|○||○|○||○||
|com.samsung.android.plugin-<br>platform.pluginbase-<br>.sdk.PluginSQLiteQpenHelper.-<br>[AppId].location_history  * Encrypted|○||||||○|
|app-database.db (DeviceDomain)|○||||||○|
|find-sdk (FmeAppData) <br> * Encrypted|○||||||○|
* app-database.db and find-sdk are artifacts of SF, The others are artifacts of ST/STF

<br>

### 5. Location data

The structure of the location information database for STF and SF is almost identical.
In the STF table structure, the location information is stored in the history column of the EncLocationHistory table in an encrypted form.
The history column stores location information in JSON format, and the important fields (timestamp, geolocation) are as shown in the table below.

<img src = "/picture/locations.png" width='60%' height='60%'>




#### * Key elements in history column 

|No|Key|Descripton|etc.|
|---|---|---|---|
|1|start|earlest time from clustered location data||
|2|end|latest time from clustered location data||
|3|count|the number of clustered location data||
|4|sumLatitude|Sum of latitude data||
|5|sumLongitude|Sum of longitude data||
|6|Latitude|Avg of latitude data||
|7|Longitude|Avg of longitude data||
|8|locations|Individual data of clustered location information|JSON format|

<br>

The location information in SF is stored in the item_history table, containing the same data as STF. However, the 'locations' key-value present in STF is not found in SF.

#### * Compare the location data from the apps with real-world GPS data

To verify the accuracy of the artifacts related to the tag's location information, GPS data was collected separately while the tags were in motion. The comparison of the location information analyzed in Scenarios 3 and 8 with GPS data from the same time periods is shown below. The analysis results accurately reflect the actual movement of the tags.

* GPS data was collected every 2 seconds. The GPS data collected within a 5-second window before and after the timestamp of the analyzed location information was displayed on the map.

#### 1. Scenario 3

* Blue: Clustered (Avg) tag location data, Green: GPS
<img src = "/picture/tag_gps1.png" width='60%' height='60%'>

* Blue: Unclustered tag location data, Green: GPS
<img src = "/picture/tag_gps2.png" width='60%' height='60%'>

* Blue: Clustered tag location data, Green: Unclustered tag location data
<img src = "/picture/tag_tag.png" width='60%' height='60%'>

#### 2. Scenario 8

* Blue: Clustered tag location data, Green: GPS
<img src = "/picture/tag_gps3.png" width='60%' height='60%'>


### 6. Network data

* In scenarios 2 and 3, network data between the smartphone and the server was collected. The APIs requested by the application to the server during the tag registration and location information retrieval processes were identified as follows.

<img src = "/picture/locations.png" width='60%' height='60%'>


