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

---

1. Device: SM-A600N #3 with latest applications (kpiatest4@gmail.com)
1. Device: SM-A600N #4 with old applications (kpiatest4@gmail.com)
1. Device: SM-A600N #5 with latest applications (kpiatest4@gmail.com)

|Time|Action|Etc|
|------|---|---|
|2024 12-02 13:18 - 13:24|Install ST, SF|SM-A600N #3|
|13:24 - 13:25|Register a tracking tag and name it 'SmartTag 2 white' |SM-A600N #3, SmartTag 2 white (Y46152378105)|
|13:26 - 13:27|Install STF, Retrieve location data|SM-A600N #3|
|13:30 - 13:50|Acquire SM-A600N #3 image|s0-latest-white|
|13:40 - 13:41|Install ST, SF|SM-A600N #4|
|13:43|Register a tracking tag and name it 'SmartTag 2 black2' |SM-A600N #4, SmartTag 2 black2 (Y48081198805)|
|13:44|Install STF, Retrieve location data|SM-A600N #4|
|13:55 - 14:10|Acquire SM-A600N #4 image|s0-old-black2|
|13:56 - 14:03|Install ST, SF|SM-A600N #5|
|14:03 - 14:05|Install STF, Retrieve location data|SM-A600N #5|
|14:12 - 14:29|Acquire SM-A600N #5 image|s0-latest-mirror|
|14:32 - 14:34|Retrieve location data|SM-A600N #3|
|14:41 - 14:57|Acquire SM-A600N #3 image|s0-latest-white-2|


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
|06:04 - 06:05|Register a tracking tag and name it 'SmartTag 2 black2'|SmartTag 2 black2 (Y48081198805)|
|06:34 - 07:13|Move with tags (SST, SmartTag 2 black2)||
|07:17|Retrieve location data||
|07:18 - 07:20|Acquire smartphone image|s4-5|


#### 5. Location data deletion
1. Perform experiments following Scenario 4

|Time|Action|Etc|
|------|---|---|
|2024 12-04 07:29|Delete the 'SmartTag 2 black2's location data with STF||
|07:29|Retrieve location data||
|07:32 - 07:34|Acquire smartphone image|s5-1|
|07:36|Delete the 'SST's location data with SF||
|07:36|Retrieve location data||
|07:38 - 07:40|Acquire smartphone image|s5-2|


#### 6. Account logout
1. Perform experiments following Scenario 5

|Time|Action|Etc|
|------|---|---|
|2024 12-04 07:47|Account logout||
|07:47|Refresh application (ST,STF,SF)||
|07:49 - 07:51|Acquire smartphone image|s6-1|


#### 7. Service withdrawal
1. Perform experiments following Scenario 6
1. Device: SM-S901N with the account (kpiatest7@gmail.com)
1. Before the experiment, Delete all registered tags with the account
1. Delete applications (ST,STF,SF)


|Time|Action|Etc|
|------|---|---|
|2024 12-04 10:00 - 10:07|Install ST, SF||
|10:07 - 10:08|Register a tracking tag and name it 'SmartTag 2 black'|SmartTag 2 black (Y48081056402)|
|10:08 - 10:09|Install STF||
|10:14|Retrieve location data||
|10:15 - 10:17|Acquire smartphone image|s7-1|
|10:20|Service withdrawal||
|10:21|Refresh application (ST,STF,SF)||
|10:23 - 10:24|Acquire smartphone image|s7-2|


#### 8. Application synchronization
1. Perform experiments following Scenario 1
1. Device: SM-A600N #3 with latest applications (kpiatest4@gmail.com)
1. Device: SM-A600N #5 with latest applications (kpiatest4@gmail.com)

|Time|Action|Etc|
|------|---|---|
|2024 12-03 01:14 - 03:40|Move with tags (SmartTag 2 white, SmartTag 2 black2) |SmartTag 2 white (Y46152378105) <br> SmartTag 2 black (Y48081056402)|
|04:36 - 06:42|Move with tags (SmartTag 2 white, SmartTag 2 black2) |SmartTag 2 white (Y46152378105) <br> SmartTag 2 black (Y48081056402)|
|11:27 - 11:30|Retrieve location data|SM-A600N #3, SM-A600N #5|
|2024 12-03 23:33 - 23:49|Acquire SM-A600N #3 image|s8-device1-1|
|2024 12-03 23:53 - 12-04 00:08|Acquire SM-A600N #5 image|s8-device2-1|
|12-03 00:34|Delete location data of SM-A600N #3 with STF|SM-A600N #3, SmartTag 2 white|
|00:34 - 00:36|Refresh Smartphones|SM-A600N #3, #5|
|00:40 - 00:55|Acquire SM-A600N #3 image|s8-device1-2|
|00:59 - 01:14|Acquire SM-A600N #5 image|s8-device2-2|
|01:17|Delete location data of SM-A600N #5 with SF|SM-A600N #5, SmartTag 2 black2|
|01:18 - 01:20|Refresh Smartphones|SM-A600N #3, #5|
|01:23 - 01:38|Acquire SM-A600N #3 image|s8-device1-3|
|01:45 - 02:00|Acquire SM-A600N #5 image|s8-device2-3|
|02:03|Delete 'SmartTag 2 black 2' of SM-A600N #3|SM-A600N #3|
|01:03 - 01:04|Refresh Smartphones|SM-A600N #3, #5|
|04:26 - 04:41|Acquire SM-A600N #3 image|s8-device1-3|
|04:44 - 04:59|Acquire SM-A600N #5 image|s8-device2-3|


### Artifact details
* 





