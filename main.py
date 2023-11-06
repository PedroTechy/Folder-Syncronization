#Imports

import sys       #for args management 
import os        #for paths/files/folder acessement
import time      #for time 
import logging   #for logging purposes
import hashlib   #for md5 hashing (to compare the files)
import shutil    #to handle file/folder create/delete/... operations
from apscheduler.schedulers.background import BackgroundScheduler # to handle scheduling 
from apscheduler.triggers.interval import IntervalTrigger



def compute_md5(file_name):
    """ 
    Calculates the md5 hash of a given file path
    """
    hash_md5 = hashlib.md5()
    with open(file_name, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)

    return hash_md5.hexdigest()


def file_to_hashvalue(folder):
    
    """List files and their MD5 checksums in a folder using the relative path as the dict key and the checksum as the value; 
    Creat list of subfolders within the main root folder"""
    
    file_hashes = {}
    subfolders = set()

    for root, dirs, files in os.walk(folder):
        
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, folder)
            file_hashes[relative_path] = compute_md5(file_path)

        for directory in dirs:
            dir_path = os.path.join(root, directory)
            relative_path = os.path.relpath(dir_path, folder)
            subfolders.add(relative_path)

    return file_hashes, subfolders


def synchronize_folders(original_folder, replica_folder):

    """
    Performs de folder synchronization. Takes both folders and compares their content using the md5 values. If a given is new or has a different value in the 2 folders, it is copied. 
    Then, if a file (and folder) is not present in the Original folder, its deleted in the replica.
    """

    try:

        logger = logging.getLogger('')        
        logger.info("Syncronization started!")
        print(f"Syncronization started: {time.ctime()}")

        original_hashvalues, original_subfolders = file_to_hashvalue(original_folder)
        replica_hashvalues, replica_subfolders  = file_to_hashvalue(replica_folder)

        # Copy missing files and update changed files in the replica folder
        for relative_path, original_md5 in original_hashvalues.items():
            replica_md5 = replica_hashvalues.get(relative_path)

            #Get full path to check its existence
            replica_file_path = os.path.join(replica_folder, relative_path)
            if not os.path.exists(replica_file_path):  

                # File doesn't exist -> creat it from original
                os.makedirs(os.path.dirname(replica_file_path), exist_ok=True)
                shutil.copy2(os.path.join(original_folder, relative_path), replica_file_path)
                log_events(relative_path, 'created')

            #If path exists, check if md5 is the same or not
            elif original_md5 != replica_md5:

                # File exists but different md5 value (assume file has changed)-> update it
                shutil.copy2(os.path.join(original_folder, relative_path), replica_file_path)
                log_events(relative_path, 'updated')

        # Add folders (and subfolders) in the replica folder that are empty
        for relative_path in original_subfolders - replica_subfolders:
            replica_dir_path = os.path.join(replica_folder, relative_path)
            if not os.path.exists(replica_dir_path):
                os.makedirs(replica_dir_path)
                log_events(relative_path, 'created')


        # Delete files in the replica folder (and subfolders) that do not exist in the original folder
        for relative_path in set(replica_hashvalues.keys()) - set(original_hashvalues.keys()):
            replica_file_path = os.path.join(replica_folder, relative_path)
            os.remove(replica_file_path)
            log_events(relative_path, 'removed')

        
        # Delete folders (and subfolders) in the replica folder that do not exist in the original folder
        for relative_path in replica_subfolders - original_subfolders:
            replica_dir_path = os.path.join(replica_folder, relative_path)
            os.rmdir(replica_dir_path)
            log_events(relative_path, 'removed')

        
        logger.info("Syncronization ended!")
        print(f"Syncronization ended: {time.ctime()} \n")

    except Exception as e:
        print("An error occurred during synchronization:", e)


def main():
    
    if len(sys.argv) != 5:
        print("Wrong number of arguments passed")
        print("Usage: python main.py original_folder_path replica_folder_path synchronization_interval log_file")
        return

    #Associate the args passed to variables
    original_folder = sys.argv[1]
    replica_folder = sys.argv[2]
    sync_interval = int(sys.argv[3])
    log_file = sys.argv[4]
    
    #Set up the logger 
    logging.basicConfig(
    filename=log_file, 
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Schedule the synchronization to run every 'sync_interval' minutes 
    
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        synchronize_folders,
        'interval',
        minutes=sync_interval,
        args=(original_folder, replica_folder)
    )

    # Perform the initial synchronization immediately 
    synchronize_folders(original_folder, replica_folder)

    scheduler.start()

    try:
        while True:
            pass
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()


def log_events(altered_file_path, event_type):

    """
    This function adds the new log events to the log file and prints them in the console.
    """

    event_types = ['removed', 'created', 'updated']
    if event_type == event_types[0]:
        logger = logging.getLogger('Syncronization System: [Remove]')  
        msg = f"File/Folder {altered_file_path} {event_types[0]}."      
        logger.info(msg)
        print(msg)
        
    elif event_type == event_types[1]:
        logger = logging.getLogger('Syncronization System: [Create]')     
        msg = f"File/Folder {altered_file_path} {event_types[1]}."      
        logger.info(msg)
        print(msg)
        
    else:
        logger = logging.getLogger('Syncronization System: [Update]')
        msg = f"File/Folder {altered_file_path} {event_types[2]}."      
        logger.info(msg)
        print(msg)
        
    

if __name__ == "__main__":
    main()

