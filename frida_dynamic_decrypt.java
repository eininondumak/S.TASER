Java.perform(function() {
    // Create an instance of the C5815b class (which appears to handle encryption/decryption)
    var C5815b = Java.use("y2.b");
    var db_org, db_dec, row;
    var query_select_device, query_insert_device;
    var query_select_location, query_insert_location;
    var query_select_sync, query_insert_sync; 
    var query_select_upload, query_insert_upload; 
    var instance = C5815b.$new(); // Create a single instance of C5815b to be reused

    // Open the original and decrypted SQLite databases
    db_org = SqliteDatabase.open('/data/media/0/db/s3_location_history');
    db_dec = SqliteDatabase.open('/data/media/0/db/s3_location_history_dec',{flags:['readwrite']});

    // Prepare queries to select all rows from the four tables in the original database
    query_select_device = db_org.prepare('SELECT * FROM EncDeviceId');
    query_select_location = db_org.prepare('SELECT * FROM EncLocationHistory');
    query_select_sync = db_org.prepare('SELECT * FROM EncSyncStatus');
    query_select_upload = db_org.prepare('SELECT * FROM EncUploadStatus');

    // Iterate through each row in the EncDeviceId table
    while((row=query_select_device.step())!=null){
        const [id, encDeviceid, deviceid] = row;
        
        // Decrypt the device ID using the C5815b instance
        let decrypted_deviceid = instance.c(deviceid, 'com.samsung.android.plugin.fme.storage');
        
        // Prepare the query to insert data into the EncDeviceId table in the decrypted database
        query_insert_device = db_dec.prepare('INSERT INTO EncDeviceid values (?,?,?,?)');
        
        // Bind values to the insert query and execute it
        query_insert_device.bindInteger(1, id);
        query_insert_device.bindText(2, encDeviceid);
        query_insert_device.bindText(3, deviceid);
        query_insert_device.bindText(4, decrypted_deviceid);
        query_insert_device.step();
    }

    // Iterate through each row in the EncLocationHistory table
    while((row=query_select_location.step())!=null){
        const [id, encDeviceid, date, history] = row;
        
        // Decrypt the location history using the C5815b instance
        let decrypted_history = instance.c(history, 'com.samsung.android.plugin.fme.storage');
        
        // Prepare the query to insert data into the EncLocationHistory table in the decrypted database
        query_insert_location = db_dec.prepare('INSERT INTO EncLocationHistory values (?,?,?,?,?)');
        
        // Bind values to the insert query and execute it
        query_insert_location.bindInteger(1, id);
        query_insert_location.bindText(2, encDeviceid);
        query_insert_location.bindFloat(3, date);
        query_insert_location.bindText(4, history);
        query_insert_location.bindText(5, decrypted_history);
        query_insert_location.step();
    }

    // Iterate through each row in the EncSyncStatus table
    while((row=query_select_sync.step())!=null){
        const [id, encDeviceid, date, status] = row;
        
        // Decrypt the sync status using the C5815b instance
        let decrypted_status = instance.c(status, 'com.samsung.android.plugin.fme.storage');
        
        // Prepare the query to insert data into the EncSyncStatus table in the decrypted database
        query_insert_sync = db_dec.prepare('INSERT INTO EncSyncStatus values (?,?,?,?,?)');
        
        // Bind values to the insert query and execute it
        query_insert_sync.bindInteger(1, id);
        query_insert_sync.bindText(2, encDeviceid);
        query_insert_sync.bindFloat(3, date);
        query_insert_sync.bindText(4, status);
        query_insert_sync.bindText(5, decrypted_status);
        query_insert_sync.step();
    }

    // Iterate through each row in the EncUploadStatus table
    while((row=query_select_upload.step())!=null){
        const [id, encDeviceid, date] = row;
        
        // Prepare the query to insert data into the EncUploadStatus table in the decrypted database
        query_insert_upload = db_dec.prepare('INSERT INTO EncUploadStatus values (?,?,?)');
        
        // Bind values to the insert query and execute it
        query_insert_upload.bindInteger(1, id);
        query_insert_upload.bindText(2, encDeviceid);
        query_insert_upload.bindFloat(3, date);
        query_insert_upload.step();
    }
});
