class Revisioner(): 

  def install(self):

    import argparse
    parser = argparse.ArgumentParser(description='Process Revisioner params.')
    parser.add_argument('--project', help='Project name')

    parser.add_argument('--dbhost', help='MySQL Db host', default="localhost")
    parser.add_argument('--dbuser', help='MySQL Db user')
    parser.add_argument('--dbpass', help='MySQL Db pass')
    parser.add_argument('--dbname', help='MySQL Db name to revision')

    args = parser.parse_args()

    if args.project is None:
      print "Project name cant be empty"
      return

    if args.dbhost is None:
      print "MySQL db host cant be empty"
      return

    if args.dbuser is None:
      print "MySQL db user cant be empty"
      return

    if args.dbpass is None:
      print "MySQL db pass cant be empty"
      return

    if args.dbname is None:
      print "MySQL db name cant be empty"
      return

    import MySQLdb
    try:
      self.conn = MySQLdb.connect(
        host = args.dbhost, 
        user = args.dbuser, 
        passwd = args.dbpass, 
        unix_socket = '/Applications/MAMP/tmp/mysql/mysql.sock',
      )
    except Exception as e:
      print e
      return

    import os
    if not os.path.exists(".revisions"):
      os.makedirs(".revisions")

    import json
    f = ".revisions/%s.json" % args.project
    if not os.path.exists(f):
      file = open(f, 'w+')
      data = { 
          "dbname" : args.dbname, 
          "version": 0, 
          "dbuser" : args.dbuser,
          "dbhost" : args.dbhost,
          "project": args.project
      }
      file.write(json.dumps(data))
    else:
      with open(f, 'r') as content_file:
        data = content_file.read()
      
      data = json.loads(str(data))
   
    v = ".revisions/v%d" % data['version']
    if not os.path.exists(v):
      os.makedirs(v)

    cursor = self.conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
    cursor.execute("USE "+ args.dbname)

    """ current database structure """
    cursor.execute("SHOW TABLES")
    rows = cursor.fetchall()
    tables = []
    for row in rows:
      table_name = row["Tables_in_%s" % args.dbname]
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
    
    niurevision = []
    t = "%s/tables.json" %v
    if not os.path.exists(t):
      file = open(t, 'w+')
      file.write(json.dumps(tables))
    
    else:
      with open(t, 'r') as content_file:
        data = content_file.read()
      
      """ current revision database structure """
      revision = json.loads(data)
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
                table_alter = table_alter + tbl_col["extra"]

              if tbl_col["Key"] != "":
                if tbl_col["Key"] == "PRI": key = "PRIMARY"
                elif tbl_col["Key"] == "UNI": key = "UNIQUE"
                table_alter = table_alter + " ADD %s(%s)" %(key, tbl_col["Field"]) 

              table_alter = table_alter + ";"

              niurevision.append({
                "table_name" : table["table_name"],
                "table_columns" : tbl_col,
                "table_alter" : table_alter
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
#              if rev_col["Key"] != "": table_alter = table_alter + " ALTER TABLE %s DROP KEY %s;"%(table["table_name"], rev_col["Field"])

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

      print niurevision

def main():
  r = Revisioner()
  r.install();

if __name__ == '__main__':
  main()

