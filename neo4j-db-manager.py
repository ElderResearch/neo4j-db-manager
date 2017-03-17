"""Management utility for Neo4j databases.

Usage:
  neo4j-db-manager.py [--db-path=PATH] [--conf-file=PATH] ls
  neo4j-db-manager.py [--conf-file=PATH] sw DATABASE
  neo4j-db-manager.py [-f] [--db-path=PATH] rm DATABASE

This tool offers three verbs:

1. List (ls): List available Neo4j databases.
2. Switch (sw): Switch the active Neo4j database using sed.
3. Remove (rm): Delete a Neo4j database.

Options:
  -h --help         Show this screen.
  -f --force        Remove database without additional confirmation.
  --db-path=PATH    Location of the Neo4j database directory.
  --conf-file=PATH  Location of the Neo4j conf file.

"""

import docopt
import glob
import json
import os
import shlex
import shutil
import subprocess as sp
import sys

def confirm_delete():
    """Request Yes/No confirmation from the user."""
    while True:
        print "Confirm? (Yes/No)"

        response = sys.stdin.readline().strip().upper()
        response = response[0] if len(response) > 0 else "X"

        if response == "Y":
            return True
        elif response == "N":
            return False
        else:
            continue

if __name__ == "__main__":
    args = docopt.docopt(__doc__, version="1")
    
    # Location of the Neo4j databases and conf file
    # --------------------------------------------------------------------------
    neo_db_basedir = None
    neo_conf_file = None
    
    # 1. Look in ~/.neo4jprofile    
    profile_path = os.path.expanduser("~/.neo4jdbprofile")
    if os.path.exists(profile_path):
        with open(profile_path, "r") as fh:
            json_payload = dict(json.load(fh))
            if "NEO4J_DB_DIR" in json_payload.iterkeys():
                neo_db_basedir = str(json_payload["NEO4J_DB_DIR"])
                neo_conf_file = str(json_payload["NEO4J_CONF"])
    
    # 2a. Look in --db-path for basedir
    if args["--db-path"] is not None:
        neo_db_basedir = os.path.expanduser(str(args["--db-path"]))
        
    # 2b. Look in --conf-file for the config
    if args["--conf-file"] is not None:
        neo_conf_file = os.path.expanduser(str(args["--conf-file"]))
    
    # 3. Make sure the necessary data exists
    # Database path
    if args["ls"] or args["rm"]:
        if neo_db_basedir is None or not os.path.isdir(neo_db_basedir):
            quit("Error: Neo4j database path was not found. Use either",
                 "~/.neo4jdbprofile or --db-path to accomplish this.")

    # Config file path
    if args["ls"] or args["sw"]:
        if neo_conf_file is None or not os.path.exists(neo_conf_file):
            quit("Error: Neo4j config path was not found. Use either",
                 "~/.neo4jdbprofile or --conf-file to accomplish this.")
    
    # Carry out the program
    # --------------------------------------------------------------------------
    # MODE list
    if args["ls"]:
        cmd = shlex.split('grep dbms.active_database "%s"' % neo_conf_file)
        current_db = "=".join(sp.check_output(cmd).split("=")[1:]).strip()
        
        for db in sorted(glob.iglob(os.path.join(neo_db_basedir, "*.db"))):
            db_basename = os.path.basename(db)
            flag = "*" if db_basename == current_db else ""
            print "%1s  %s" % (flag, os.path.basename(db_basename))
    # MODE delete
    elif args["rm"]:
        rm_path = os.path.join(neo_db_basedir, args["DATABASE"])
        if not os.path.exists(rm_path):
            print "Error: The selected Neo4j database directory does not exist."
            print "Input: %s" % rm_path
            quit()
        else:
            confirmation = args["--force"] or confirm_delete()
            if confirmation:
                shutil.rmtree(rm_path)
    # MODE switch
    # Use sed to swap out the active database
    elif args["sw"]:
        cmd = ("/usr/bin/sed -i " +
               "-e 's/^\\s*#*\\s*dbms\\.active_database.*$/dbms.active_database=%s/' " +
               "\"%s\"")
        sp.check_call(args=shlex.split(cmd % (args["DATABASE"], neo_conf_file)))
