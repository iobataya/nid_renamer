# nid_renamer
Rename NID (Nanosurf Image Data) file with scan parameters
## Usage
```bashpython nid_renamer.py <path_to_nid_file>
```
This will rename the NID file to include the scan parameters such as scan size, scan rate, and scan mode. The new filename will be in the format:
```NID_<scan_size>_<scan_rate>_<scan_mode>.nid
```
For example, if the original NID file is named `scan.nid` and has a scan size of 10x10 µm, a scan rate of 1 Hz, and a scan mode of "contact", the new filename will be:
```NID_10x10_1Hz_contact.nid
```
## Requirements
- Python 3.x
- Nanosurf Image Data (NID) file format
## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
