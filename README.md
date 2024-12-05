# Smart Tag Parser (S.TASER)

DFRWS EU 2025 - Samsung Tracking Tag Applicatino Forensics in Criminal Investigations


### Scenarios
* Timestamp is UTC

#### 1. Artifact structure
1. Device: SM-S901N

|Time|Action|Etc|
|------|---|---|
|2024 12-03 05:09 - 05:14|Install ST, SF||
|05:15|Register a tracking tag and name it 'SmartTag 2 black' |SmartTag 2 black (Y48081056402)|
|05:17|Install STF||
|05:19|Register a tracking tag and name it 'SST' |SOLUM SMART TAG (C40D6666661C) <br> * Register twice due to registration error|
|05:20|Retrieve location data||
|05:28 - 06:42|Move with tags||
|11:50 - 11:58|Acquire smartphone image|20241203-S1-default|

#### 2. Tracking tag registraion 
1. Device: SM-A600N(Rooted)

|Time|Action|Etc|
|------|---|---|
|2024 11-30 13:54 - 13:56|Register a tracking tag and name it 'SmartTag 1 black'|SmartTag 1 black (EF1FC40EB471)|
|13:56 - 13:57|Install STF||
|05:19|Register a tracking tag and name it 'SST' |SOLUM SMART TAG (C40D6666661C) <br> * Register twice due to registration error|
|05:20|Retrieve location data||
|05:28 - 06:42|Move with tags||
|11:50 - 11:58|Acquire smartphone image|20241203-S1-default|

#### 3. Location data retrieval


#### 4. Registered tracking tag deletion


#### 5. Location data deletion


#### 6. Account logout


#### 7. Service withdrawal


#### 8. Application synchronization





