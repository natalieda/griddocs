# ===================================================================== #
# authors: DDP group SURFsara & SKSP Lofar group			#
# support: contact <helpdesk@surfsara.nl> 				#
#                                                            	        #
# usage: python state.py files						#
# description:                                                       	#
#	Display the status of each file listed in "files" and the	#
#	percentage of staged files.
# output:								#
#	ONLINE: means that the file is only on disk.			#
#	NEARLINE: means that the file in only on tape.			#
#	ONLINE_AND_NEARLINE: means that the file is on disk and tape.	#
# ===================================================================== #

#!/usr/bin/env python

import pythonpath
import sys
import time
from collections import Counter

try:
   import gfal2
except ImportError:
   print("GFAL2 LIBRARY CANNOT BE IMPORTED")
   pass


def check_status_list(surls, verbose=True):
   """ Check the status of a list of SURLs.
   Args:
      surls (list): list to read SURLS from.
      verbose (bool): print the status to the terminal.
   Return:
      results (list): list of tuples containing the SURL and the State.
   """
   results=[]
   nf=100
   mx=len(surls)
   i=0
   while i<mx:
      mxi=min(i+nf,mx)
      s=surls[i:mxi]
      for sc in s:
         results.append(check_status(sc, verbose=verbose))
      i=i+nf
      time.sleep(1)
   return results

def check_status(surl, verbose=True):
   """ Obtain the status of a file from the given SURL.
   Args:
      surl (str): the SURL pointing to the file.
      verbose (bool): print the status to the terminal.
   Returns:
      surl, status (tuple): the SURL of a file and its status as stored in the 'user.status' attribute.
   Usage:
   >>> from state import check_status
   >>> filename="srm://srm.grid.sara.nl:8443/pnfs/path-to-your-file"
   >>> check_status(filename)
   """
   context = gfal2.creat_context()
   status = context.getxattr(surl, 'user.status')
   if verbose:
      if status=='ONLINE_AND_NEARLINE' or status=='ONLINE':
         color="\033[32m"
      else:
         color="\033[31m"
   print('{:s} {:s}{:s}\033[0m'.format(surl, color, status))
   return (surl, status)


def convert_to_surl(files):
   """Convert the files from any URL format ('/pnfs' or 'gsiftp://' or 'srm://') to proper SURLs supported by SURFsara dCache. The SURL format is required for gfal to return the file status.
   Args:
      files (str): the file that contains the URLs.
   Returns:
      surls (list): the list of converted SURLs.
   Usage:
   >>> from state import convert_to_surl
   >>> files="file-with-urls"
   >>> convert_to_surl(files)
   """
   f=open(files,'r')
   urls=f.read().split()
   f.close()
   surls=[]
   for url in urls:
      temp=url.split("/pnfs")[0]
      surls.append(url.replace(temp, "srm://srm.grid.sara.nl:8443", 1))
   return surls

def percent_staged(results):
   """Count the percentage of files that are staged.
   Args:
      results (list): list of tuples of (srm, status) 
   Returns:
      percent (float): the percentage of staged vs. unstaged files
   """
   total_files=len(results)
   counts = Counter(x[1] for x in results)
   staged=counts['ONLINE_AND_NEARLINE']+counts['ONLINE']
   unstaged=counts['NEARLINE ']
   percent=str(((float(staged))/total_files)*100)
   print('{:s} percent of files staged'.format(percent))
   return percent


 
if __name__ == '__main__':
   files = sys.argv[1]
   surls = convert_to_surl(files)
   results = check_status_list(surls)   
   percent = percent_staged(results)

