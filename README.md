maipy
==================
MySQL Revision is a python command-line tool to keep revisions of the MySQL data structure. The idea is to combine this tool with git(or svn) repositories, this way you can share the database structure changes between users, stages, servers(development. production)

Install
=======
Using Git

git submodule add clone https://github.com/vrunoa/MySQLRevisions.py

./maipy.py --setup

git add .revisions

Usage
=====
Revisioner arguments:

* -h, --help            show this help message and exit
  
* -s, --setup           Creates a new revisioner project
  
* -d, --dump            Creates a dump of a revision, use -v to set the
                        revision number
                        
* -w, --watch           Watch for changes in the structure and create a new
                        revision
                        
* -r, --revision        Get current revision number
  
* -v VERSION, --version VERSION Revision version number
   
command
``` bash
./maipy.py -r
```
output
``` bash
"Your current structure revision is 1"
```

Example
=======
Lets say we have a project with this table structure

| Id            | Name          | LastName |
| ------------- |:-------------:| --------:|
| 1             | Bruno         | Alassia  |

We setup a revisioner project for this structure,
``` bash
./maipy.py --setup
```
Once done, we have our revision zero. 

A dump for this revision will be
``` bash
USE DATABASE test;

CREATE TABLE `users` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `Name` varchar(100) NOT NULL,
  `LastName` varchar(100) NOT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1
```

Now we realize we forgot to set the <b>Email</b> column

| Id            | Name          | LastName | Email            |
| ------------- |:-------------:| --------:| ---------------: |
| 1             | Bruno         | Alassia  | hello@urucas.com |

Add it to our table structure and crate a new revision with the --watch argument
``` bash
./maipy.py --watch

"A new structure revision has been created
the current revision now is: v1"
```

A new dump for this revision will be
``` bash
./maipy.py --dump

USE DATABASE test;
ALTER TABLE users ADD COLUMN Email varchar(100) NOT NULL;
```

TODO
====
* <b>Test</b> A lot! This is really <b>beta</b>!
* Add multiple users account each one with his own database params(host,socket,username,password)
* Add date, project data to the .sql created on ./maipy --dump
* Obligate the user to always mantain their structure updated before creating a watch
* Add documentation on SVN install

