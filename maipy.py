#!/usr/bin/env python

class Revisioner(): 

  conn = None

  def setup(self):
    
    args = {}
    # TODO -- add multiple users setup
    args["version"] = 0
    args["project"] = raw_input("Enter the project name:")
    if args["project"].strip() == "":
      print "Project name cant be empty"
      return
    
    args["dbhost"] = raw_input("Enter MySQL Host:")
    if args["dbhost"].strip() == "":
      print "MySQL db host cant be empty"

    args["dbsocket"] = raw_input("Enter MySQL Socket(Optional):")
    if args["dbsocket"].strip() == "":
      args["dbsocket"] = "/Applications/MAMP/tmp/mysql/mysql.sock"

    args["dbuser"] = raw_input("Enter MySQL username:")
    if args["dbuser"].strip() == "":
      print "MySQL db user cant be empty"

    args["dbpass"] = raw_input("Enter MySQL password:")
    
    args["dbname"] = raw_input("Enter MySQL Db Name:")
    if args["dbname"].strip() == "":
      print "MySQL db name cant be empty"
    
    import MySQLdb
    try:
      self.conn = MySQLdb.connect(
        host = args["dbhost"], 
        user = args["dbuser"], 
        passwd = args["dbpass"],
        unix_socket = args["dbsocket"],
      )
    except Exception as e:
      "Cannot create project, cant connect to the database"
      return
    
    f = ".revisions/project.json"
    import os
    import json
    if not os.path.exists(".revisions"):
      os.makedirs(".revisions")
    elif os.path.exists(f):
      with open(f, 'r') as content_file:
        data = content_file.read()
      data = json.loads(str(data))
      if data["project"] != args["project"]:
        print "Cannot create project, overlaps another project folder"
        return
 
    if not os.path.exists(f):
      file = open(f, 'w+')
      file.write(json.dumps(args))
      file.close()
    
    print "MySQL structure revisioner setup went successfully"
    
    print "Creating your first structure revision"
    v = ".revisions/v%d" % args['version']
    if not os.path.exists(v):
      os.makedirs(v)
   
    tables = self.structure(args)
    t = "%s/structure.json" %v
    if not os.path.exists(t):
      file = open(t, 'w+')
      file.write(json.dumps(tables))
      file.close()

    print "Done! Your MySQL structure revision zero has been created"
    return
    

  def structure(self, args):
    import MySQLdb
    if self.conn is None:
      try:
        self.conn = MySQLdb.connect(
          host = args["dbhost"], 
          user = args["dbuser"], 
          passwd = args["dbpass"],
          unix_socket = args["dbsocket"],
        )
      except Exception as e:
        "Cannot create project, cant connect to the database"
        return

    cursor = self.conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
    cursor.execute("USE "+ args["dbname"])
    
    """ current database structure """
    cursor.execute("SHOW TABLES")
    rows = cursor.fetchall()
    tables = []
    for row in rows:
      table_name = row["Tables_in_%s" % args["dbname"]]
      cursor.execute("SHOW CREATE TABLE %s" %table_name)
      table_create = cursor.fetchone()
      table_create = table_create["Create Table"]
      cursor.execute("SHOW COLUMNS FROM %s" %table_name)
      columns = []
      columns_rows = cursor.fetchall()
      for column in columns_rows:
        columns.append(column)
      
      table_columns = columns
      from datetime import datetime
      table_date = str(datetime.today().strftime("%Y-%m-%d %H:%M:%S"))
      tables.append({
        "table_name": table_name,
        "table_columns": table_columns,
        "table_create" : table_create,
        "table_date"   : table_date
      })
    return tables


  def revision(self):
    f = ".revisions/project.json"
    import os
    if not os.path.exists(f):
      print "MySQL revisioner has not been setup on this computer"
      return

    import json
    with open(f, 'r') as content_file:
      args = content_file.read()
    args = json.loads(str(args))
    print "Your current structure revision is %d" % args["version"]

  
  def dump(self, version):
    f = ".revisions/project.json"
    import os
    if not os.path.exists(f):
      print "MySQL revisioner has not been setup on this computer"
      return

    import json
    with open(f, 'r') as content_file:
      args = content_file.read()
    args = json.loads(str(args))

    r = version
    t = ".revisions/v%s/structure.json" %r
    if not os.path.exists(t):
      print "The revision number selected structure doesnt exists! Try again!"
      return
    
    with open(t, 'r') as content_file:
      structure = content_file.read()
    structure = json.loads(str(structure))

    maiesicuel = []
    # TODO -- add .sql dump project name, revision number, date
    maiesicuel.append("USE DATABASE %s" % args["dbname"])
    for table in structure:
      try: maiesicuel.append(table["table_create"])
      except: pass
      try: maiesicuel.append(table["table_drop"]) 
      except: pass
      try: maiesicuel.append(table["table_alter"])
      except: pass

    dump = ";\r\n\r\n".join(maiesicuel)
    f = "%s.v%s.dump.sql" %(args["dbname"],r)
    file = open(f, 'w')
    file.write(dump)
    file.close()
    print "Structure dump created, check the %s file" %f

  def moo(self):
    # a moo point
    return

  def watch(self):
    f = ".revisions/project.json"
    import os
    if not os.path.exists(f):
      print "MySQL revisioner has not been setup on this computer"
      return

    import json
    with open(f, 'r') as content_file:
      args = content_file.read()
    args = json.loads(str(args))

    t = ".revisions/v%s/structure.json" % args["version"]
    if not os.path.exists(t):
      # TODO -- workaround this
      print "An error occurr while getting the revision structure file"
      return

    """ current revision structure """
    with open(t, 'r') as content_file:
      rev_data = content_file.read()
    revision = json.loads(str(rev_data))
    
    """ current revision database structure """
    tables = self.structure(args) 


    niurevision = []
    for table in tables:
      compare = None
      for rev in revision:
        if rev["table_name"] == table["table_name"]:
          compare = rev
          break
        
      """ new table created """
      if compare is None:
        niurevision.append(table)
        break

      """ the table change its structure """
      if compare["table_create"] != table["table_create"]:
        rev_columns = rev["table_columns"]
        tbl_columns = table["table_columns"]
        for tbl_col in tbl_columns:
          compare_column = None
          for rev_col in rev_columns:
            if rev_col["Field"] == tbl_col["Field"]:
              compare_column = rev_col
              break
            
          """ new column created """
          if compare_column is None:
              
            table_alter = " ALTER TABLE %s ADD COLUMN %s %s" %(table["table_name"], tbl_col["Field"], tbl_col["Type"])
              
            if tbl_col["Null"] == "NO" :
              table_alter = table_alter + " NOT NULL"
              
            if tbl_col["Default"] is not None:
              table_alter = table_alter + " DEFAULT %s" %tbl_col["Default"]
              
            if tbl_col["Extra"] != "":
              table_alter = table_alter + " " + tbl_col["Extra"]
              if tbl_col["Extra"] == "auto_increment":
                tbl_col["Key"] = "PRI"
              
            if tbl_col["Key"] != "":
              if tbl_col["Key"] == "PRI": key = " PRIMARY KEY"
              elif tbl_col["Key"] == "UNI": key = " UNIQUE"
              table_alter = table_alter + key

            table_alter = table_alter + ";"

            niurevision.append({
              "table_name" : table["table_name"],
              "table_columns" : tbl_col,
              "table_alter" : table_alter
            })
            
          else:
            if rev_col == tbl_col: continue
            """ column change its structure """
              
            if rev_col["Type"] != tbl_col["Type"]:
              table_alter = "ALTER TABLE %s MODIFY COLUMN %s %s" %(table["table_name"], tbl_col["Field"], tbl_col["Type"]) 
            
              if rev_col["Null"] != tbl_col["Null"]:
                if tbl_col["Null"] == "NO":
                  table_alter = table_alter + " NOT NULL"
                else:
                  table_alter = table_alter + " NULL"

              if rev_col["Default"] != tbl_col["Default"]:
                if tbl_col["Default"] == None: 
                  table_alter = table_alter + " DROP DEFAULT"
                else: 
                  table_alter = table_alter + " SET DEFAULT %s" %tbl_col["Default"]

            if rev_col["Key"] != tbl_col["Key"]:
              print "change key value"

            niurevision.append({
              "table_name" : table["table_name"],
              "table_columns": tbl_col,
              "table_alter": table_alter
            })

        for rev_col in rev_columns:
          compare_column = None
          for tbl_col in tbl_columns:
            if rev_col["Field"] == tbl_col["Field"]:
              compare_column = rev_col
              break
          
          """ a column has been deleted """
          if compare_column is None:
            table_alter = " ALTER TABLE %s DROP COLUMN %s;" %(table["table_name"], rev_col["Field"])
#            if rev_col["Key"] != "": table_alter = table_alter + " ALTER TABLE %s DROP KEY %s;"%(table["table_name"], rev_col["Field"])
            niurevision.append({
              "table_name": table["table_name"],
              "table_columns" : rev_col,
              "table_alter" : table_alter
            })

    for rev in revision:
      compare = None
      for table in tables:
        if rev["table_name"] == table["table_name"]:
          compare = rev
          break
        
      """ a table has been deleted """
      if compare is None:
        niurevision.append({
          "table_name" : rev["table_name"],
          "table_drop" : " DROP TABLE %s" % rev["table_name"]
        })

    if len(niurevision) == 0:
      print "No structure changes found,\r\n the current revision still: v%s" %args["version"]

    else:
      args["version"] = args["version"] + 1
      f = ".revisions/project.json"
      file = open(f, "w")
      file.write(json.dumps(args))
      file.close()
      v = ".revisions/v%d" % args['version']
      os.makedirs(v)
      t = "%s/structure.json" %v
      file = open(t, 'w')
      file.write(json.dumps(niurevision))
      file.close()
      print "A new structure revision has been created \r\n"
      print "the current revision now is: v%s" %args["version"]


def main():
  
  r = Revisioner()
  
  import argparse
  parser = argparse.ArgumentParser(description='Revisioner params.')
  parser.add_argument('-s', '--setup', action="store_true", help='Creates a new revisioner project')
  parser.add_argument('-d', '--dump', action="store_true", help='Creates a dump of a revision, use -v to set the revision number')
  parser.add_argument('-w', '--watch', action="store_true", help='Watch for changes in the structure and create a new revision')
  parser.add_argument('-r', '--revision', action="store_true", help='Get current revision number')
  parser.add_argument('-v', '--version', default=0, help='Revision version number')
  args = parser.parse_args()
  
  if args.setup is True: r.setup()
  elif args.watch is True: r.watch()
  elif args.dump is True: r.dump(args.version)
  else: r.revision()

if __name__ == '__main__':
  main()

