# Smart Tag Parser (S.TASER)

DFRWS EU 2025 - Samsung Tracking Tag Applicatino Forensics in Criminal Investigations


### Experimental scenarios
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
|00:13|Retrieve location data||
|00:14|Acquire smartphone image|241201_S2_oneconncect-1|
|00:16|Hard-reset the SmartTag 1 white||
|00:16|Re-register SmartTag 1 white with 'SmartTag 1 white 2'|SmartTag 1 white 2 (CD50AB769464)|
|00:41 - 07:56|Move with tags (SmartTag 1 black, SmartTag 1 white 2)||
|09:24|Retrieve location data||
|09:25|Acquire smartphone image|241201_S2_oneconnect-2|

#### 3. Location data retrieval
1. Device: SM-A600N #2 (Rooted) with the account (kpiatest2@gmail.com)

|Time|Action|Etc|
|------|---|---|
|2024 12-01 01:00|Install applications and log-in the account||
|01:06 - 01:14|Install ST, STF and Retrieve location data||
|01:06 - 01:14|Install SF and Retrieve location data||
|01:06 - 01:14|Capture network data during the location data retrieval|S3-oneconnect.har <br> S3-find.har|
|01:16|Acquire smartphone image|241201_S3_oneconncect|
|01:16|Acquire smartphone image|241201_S3_find|
|01:30|Decrypt STF's encrypted location data|s3_location_history <br> s3_location_history_dec|

#### 4. Registered tracking tag deletion
1. Perform experiments following Scenario 1

|Time|Action|Etc|
|------|---|---|
|2024 12-04 05:14 - 05:15|Retrieve location data||
|05:20 - 05:29|Acquire smartphone image|s4-1|
|05:35|Delete the tag (SmartTag 2 black)|SmartTag 2 black (Y48081056402)|
|05:37 - 05:38|Acquire smartphone image|s4-2|
|05:44 - 05:45|Re-register SmartTag 2 black with 'SmartTag 2 black re'|SmartTag 2 black re (CD50AB769464)|
|05:47 - 09:50|Acquire smartphone image|s4-3|
|05:52|Delete the tag (SmartTag 2 black re)||
|05:55 - 05:57|Acquire smartphone image|s4-4|
|06:04 - 06:05|Register a tracking tag and name it 'SmartTag 2 black2'|SmartTag 2 black2(Y48081198805)|
|----------|Move with tags (SST, SmartTag 2 black2)||
|07:17|Retrieve location data||
|07:18 - 07:20|Acquire smartphone image|s4-5|

#### 5. Location data deletion
1. Perform experiments following Scenario 4

|Time|Action|Etc|
|------|---|---|
|2024 12-04 07:29|Delete the 'SmartTag 2 black's location data with STF||
|07:29|Retrieve location data||
|07:32 - 07:34|Acquire smartphone image|s5-1|
|07:36|Delete the 'SST's location data with SF||
|07:36|Retrieve location data||
|07:38 - 07:40|Acquire smartphone image|s5-2|

#### 6. Account logout


#### 7. Service withdrawal


#### 8. Application synchronization





