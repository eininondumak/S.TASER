# Smart Tag Parser (S.TASER)

DFRWS EU 2025 - Samsung Tracking Tag Applicatino Forensics in Criminal Investigations


### Scenarios
* Timestamp is UTC

#### 1. Artifact structure
1. Device: SM-S901N with the account (kpiatest7@gmail.com)

|Time|Action|Etc|
|------|---|---|
|2024 12-03 05:09 - 05:14|Install ST, SF||
|05:15|Register a tracking tag and name it 'SmartTag 2 black' |SmartTag 2 black (Y48081056402)|
|05:17|Install STF||
|05:19|Register a tracking tag and name it 'SST' |SOLUM SMART TAG (C40D6666661C) <br> * Register twice due to registration error|
|05:20|Retrieve location data||
|05:28 - 06:42|Move with tags (SmartTag 2 black, SST)||
|11:50 - 11:58|Acquire smartphone image|20241203-S1-default|

#### 2. Tracking tag registraion 
1. Device: SM-A600N #1 (Rooted) with the account (kpiatest2@gmail.com)

|Time|Action|Etc|
|------|---|---|
|2024 11-30 13:54 - 13:56|Register a tracking tag and name it 'SmartTag 1 black'|SmartTag 1 black (EF1FC40EB471)|
|13:56 - 13:57|Install STF||
|13:54 - 13:57|Capture network data during the registration |S2-1.har|
|13:58 - 13:59|Try registering another tag that was already registered in other account|Registration fail|
|13:59|Move with tags|S2-2.har|
|2024 11-30 14:12 - <br> 2024 11-31 15:20|Move with the tag (SmartTag 1 black)||
|2024 11-31 15:45 - 15:46|Register a tracking tag and name it 'SmartTag 1 white'|SmartTag 1 white (CD50AB769464)|
|00:14|Acquire smartphone image|241201_S2_oneconncect-1|
|00:16|Hard-reset the SmartTag 1 white||
|00:16|Re-register SmartTag 1 white with 'SmartTag 1 white 2'|SmartTag 1 white 2 (CD50AB769464)|
|00:41 - 07:56|Move with tags (SmartTag 1 black, SmartTag 1 white 2)||
|09:25|Acquire smartphone image|241201_S2_oneconnect-2|

#### 3. Location data retrieval
1. Device: SM-A600N #2 (Rooted) with the account (kpiatest2@gmail.com)

|Time|Action|Etc|
|------|---|---|
|2024 11-30 13:54 - 13:56|Register a tracking tag and name it 'SmartTag 1 black'|SmartTag 1 black (EF1FC40EB471)|
|13:56 - 13:57|Install STF||
|13:54 - 13:57|Capture network data during the registration |S2-1.har|
|13:58 - 13:59|Try registering another tag that was already registered in other account|Registration fail|
|13:59|Move with tags|S2-2.har|
|2024 11-30 14:12 - <br> 2024 11-31 15:20|Move with the tag (SmartTag 1 black)||
|2024 11-31 15:45 - 15:46|Register a tracking tag and name it 'SmartTag 1 white'|SmartTag 1 white (CD50AB769464)|
|00:14|Acquire smartphone image|241201_S2_oneconncect-1|
|00:16|Hard-reset the SmartTag 1 white||
|00:16|Re-register SmartTag 1 white with 'SmartTag 1 white 2'|SmartTag 1 white 2 (CD50AB769464)|
|00:41 - 07:56|Move with tags (SmartTag 1 black, SmartTag 1 white 2)||
|09:25|Acquire smartphone image|241201_S2_oneconnect-2|

#### 4. Registered tracking tag deletion


#### 5. Location data deletion


#### 6. Account logout


#### 7. Service withdrawal


#### 8. Application synchronization





