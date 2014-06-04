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
    
    t = "%s/tables.json" %v
    if not os.path.exists(t):
      file = open(t, 'w+')
      file.write(json.dumps(tables))
    else:
      with open(t, 'r') as content_file:
        data = content_file.read()
      
      """ current revision database structure """
      revision = json.loads(data)
      changes = false
      for table in tables:
        actual_table_name = table["table_name"]
        print actual_table_name 
      
      

def main():
  r = Revisioner()
  r.install();

if __name__ == '__main__':
  main()

