# Folder Synchronization

The **Folder Synchronization Tool** is a Python script for synchronizing the contents of two folders using MD5 checksums. This tool compares the files and subfolders in an original folder with those in a replica folder and ensures they are consistent.

## Features

- **Synchronization:** Automatically copy missing or changed files from the original folder to the replica folder.
- **Subfolder Handling:** Create subfolders in the replica if they exist in the original.
- **Deletion:** Remove files and subfolders from the replica if they no longer exist in the original.
- **Scheduled Sync:** Use the scheduler to perform synchronization at regular intervals.
- **Logging:** Log synchronization events for tracking and debugging.

### Prerequisites

- Python 3.11.5
- Additional libraries can be installed using `pip`: logging; hashlib, apscheduler

### Usage

1. Clone the repository to your local machine.
2. Run the script using the following command:

python main.py original_folder_path replica_folder_path synchronization_interval log_file

- `original_folder_path`: The path to the original folder to be synchronized.
- `replica_folder_path`: The path to the replica folder where changes will be applied.
- `synchronization_interval`: Interval in *minutes* for scheduled synchronization.
- `log_file`: The name of the log file to store synchronization events.

### Example

python main.py '/path/to/original_folder' '/path/to/replica_folder' 30 'log_file.log'

This example will synchronize the contents of the original_folder with the replica_folder every 30 minutes, and the synchronization events will be logged in the log_file.log file.
