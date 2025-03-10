#!/usr/bin/env python3
"""
# Purpose: For a Google Drive User(s), get all drive file ACLs for files shared with selected domains.
# Note: This script can use Basic or Advanced GAM:
#	https://github.com/jay0lee/GAM
#	https://github.com/taers232c/GAMADV-XTD3
# Customize: Set DOMAIN_LIST and DESIRED_ALLOWFILEDISCOVERY.
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# 1: Get ACLs for all files, if you don't want all users, replace all users with your user selection in the command below
#    You can minimize the number of files listed by using a query with the visibility keyword.
#      query "visibility='domainCanFind'" - Set DESIRED_ALLOWFILEDISCOVERY = True
#      query "visibility='domainWithLink'" - Set DESIRED_ALLOWFILEDISCOVERY = False
#      query "visibility='domainCanFind' or visibility='domainWithLink'" - Set DESIRED_ALLOWFILEDISCOVERY = Any
#    Change the query as desired.
#    If you are looking for ACLs referencing specific domains, list them in DOMAIN_LIST.
#    For Advanced GAM, add the following clause to the command for each domain: pm type domain domain xyz.com em
#  $ Basic GAM: gam all users print filelist id title permissions owners query "visibility='domainCanFind'" > filelistperms.csv
#  $ Advanced GAM: gam config auto_batch_min 1 redirect csv ./filelistperms.csv multiprocess all users print filelist fields id,title,permissions,owners.emailaddress query "visibility='domainCanFind'" pm type domain em
# 2: From that list of ACLs, output a CSV file with headers "Owner,driveFileId,driveFileTitle,permissionId,role,domain,allowFileDiscovery"
#    that lists the driveFileIds and permissionIds for all ACLs shared with the selected domains.
#    (n.b., driveFileTitle, role, domain and allowFileDiscovery are not used in the next step, they are included for documentation purposes)
#  $ python3 GetSharedWithDomainDriveACLs.py filelistperms.csv deleteperms.csv
# 3: Inspect deleteperms.csv, verify that it makes sense and then proceed
# 4: If desired, delete the ACLs
#  $ gam csv deleteperms.csv gam user "~Owner" delete drivefileacl "~driveFileId" "~permissionId"
"""

import csv
import re
import sys

FILE_NAME = 'name'
ALT_FILE_NAME = 'title'

# If you want to limit finding ACLS for a specific list of domains, use the list below, e.g., DOMAIN_LIST = ['domain.com',] DOMAIN_LIST = ['domain1.com', 'domain2.com',]
DOMAIN_LIST = []
# Specify desired value of allowFileDiscovery field: True, False, Any (matches True and False)
DESIRED_ALLOWFILEDISCOVERY = 'Any'

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

PERMISSIONS_N_TYPE = re.compile(r"permissions.(\d+).type")

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, ['Owner', 'driveFileId', 'driveFileTitle', 'permissionId', 'role', 'domain', 'allowFileDiscovery'], lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin

for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  for k, v in iter(row.items()):
    mg = PERMISSIONS_N_TYPE.match(k)
    if mg and v == 'domain':
      permissions_N = mg.group(1)
      domain = row[f'permissions.{permissions_N}.domain']
      allowFileDiscovery = row.get(f'permissions.{permissions_N}.allowFileDiscovery', str(row.get(f'permissions.{permissions_N}.withLink') == 'False'))
      if (not DOMAIN_LIST or domain in DOMAIN_LIST) and (DESIRED_ALLOWFILEDISCOVERY in ('Any', allowFileDiscovery)):
        outputCSV.writerow({'Owner': row['owners.0.emailAddress'],
                            'driveFileId': row['id'],
                            'driveFileTitle': row.get(FILE_NAME, row.get(ALT_FILE_NAME, 'Unknown')),
                            'permissionId': f'id:{row[f"permissions.{permissions_N}.id"]}',
                            'role': row[f'permissions.{permissions_N}.role'],
                            'domain': domain,
                            'allowFileDiscovery': allowFileDiscovery})

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
