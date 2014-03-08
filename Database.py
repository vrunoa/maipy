# database connection ---
from MySQLdb1 import MySQLdb
class Database():

        def __init__(self):
                return
#                self.config = Config()
#                host         = self.config.getConfig('resources.db.params.host')
#                user         = self.config.getConfig('resources.db.params.username')
#                passwd = self.config.getConfig('resources.db.params.password')
#                db                 = self.config.getConfig('resources.db.params.dbname')
                self.conn = MySQLdb.connect (host = "localhost", user = "root", passwd = "perrito", db = "cinemarosario")

        def __del__(self):
                self.conn.close()

        def seleccionar(self, query):
                self.cursor = self.conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
                self.cursor.execute (query)
                return self.cursor.fetchall()

        def insertar(self, tabla, query_param):
                self.cursor = self.conn.cursor()
                self.items  = query_param.items()
                self.keys   = [item[0] for item in self.items]
                self.values = [item[1] for item in self.items]
                self.sql = "INSERT INTO %s (%s) values (%s)" % (tabla, ", ".join(self.keys), ", ".join(self.values))
#                print self.sql
                self.cursor.execute(self.sql)
                return self.conn.insert_id()

        def insertarVarios(self, tabla, objects):
            for obj in objects:
                self.insertar(tabla, obj)

        def query(self,query):
                self.cursor = self.conn.cursor()
                self.cursor.execute(query)

        def escapeHTML(self, fuente):
                from BeautifulSoup import BeautifulStoneSoup
                fuente = unicode( BeautifulStoneSoup( fuente, convertEntities= BeautifulStoneSoup.HTML_ENTITIES) )
                return fuente

        def escapeUnicode(self, cadena):
                vec = {
                        '0421' : '&#1057;',
                        '00a0' : '&nbsp;',
                        '00A1' : '&iexcl;',
                        '00A2' : '&cent;', '00A3' : '&pound;',        '00A4' : '&curren;',        '00A5' : '&yen;',
                        '00A7' : '&sect;',
                        '00A8' : '&uml;',
                        '00A9' : '&copy;',
                        '00AA' : '&ordf;',
                        '00AB' : '&laquo;',
                        '00AC' : '&not;',
                        '00AE' : '&reg;',
                        '00AF' : '&macr;',
                        '00B0' : '&deg;',
                        '00B1' : '&plusmn;',
                        '00B4' : '&acute;',
                        '00B5' : '&micro;',
                        '00B6' : '&para;',
                        '00B7' : '&middot;',
                        '00B8' : '&bedil;',
                        '00BA' : '&ordm;',
                        '00BB' : '&raquo;',
                        '00BF' : '&iquest;',
                        '00C0' : '&Agrave;',        '00C1' : '&Aacute;',        '00C2' : '&Acirc;','00C3' : '&Atilde;', '00C4' : '&Auml;','00C5' : '&Aring;','00C6' : '&AElig;',
                        '00C7' : '&Ccedil;',
                        '00C8' : '&Egrave;',        '00C9' : '&Eacute;',        '00CA' : '&Ecirc;','00CB' : '&Euml;',
                        '00CC' : '&Igrave;',        '00CD' : '&Iacute;',        '00CE' : '&Icirc;','00CF' : '&Iuml;',
                        '00D1' : '&Ntilde;',
                        '00D2' : '&Ograve;',        '00D3' : '&Oacute;', '00D4' : '&Ocirc;', '00D5' : '&Otilde;', '00D6' : '&Ouml;', '00D8' : '&Oslash;',
                        '00D9' : '&Ugrave;',        '00DA' : '&Uacute;',        '00DB' : '&Ucirc;','00DC' : '&Uuml;',
                        '00DF' : '&szlig;',
                        '00E0' : '&agrave;',        '00E1' : '&aacute;',        '00E2' : '&acirc;','00E3' : '&atilde;', '00E4' : '&auml;','00E5' : '&aring;','00E6' : '&aElig;',
                        '00E7' : '&ccedil;',
                        '00E8' : '&egrave;',        '00E9' : '&eacute;',        '00EA' : '&ecirc;','00EB' : '&euml;',
                        '00EC' : '&igrave;',        '00ED' : '&iacute;',        '00EE' : '&icirc;','00EF' : '&iuml;',
                        '00F1' : '&ntilde;',
                        '00F2' : '&ograve;',        '00F3' : '&oacute;', '00F4' : '&ocirc;', '00F5' : '&otilde;', '00F6' : '&ouml;', '00F8' : '&oslash;',
                        '00F7' : '&divide;',
                        '00F9' : '&ugrave;',        '00FA' : '&uacute;',        '00FB' : '&ucirc;','00FC' : '&uuml;',
                        '00FF' : '&yuml;',
                        '20AB' : '&dong;'
                }
                import re
                regex  = re.compile(r"\\r\\n", re.IGNORECASE)
                fuente = re.sub(regex, '&nbsp;', cadena)
                for code in vec:
                        regex  = re.compile(r"\\\u%s" % code, re.IGNORECASE)
                        fuente = re.sub(regex, vec[code], fuente)
                return fuente


        def escapeUnicodeX(self, cadena):
                fuente = cadena
                vec = {
                        '\xbb' : '&raquo;'
                }
                import re
                for code in vec:
                        regex  = re.compile(r"%s" % code, re.IGNORECASE)
                        fuente = re.sub(regex, vec[code], fuente)

                return fuente

        def escapeString(self, data, noescape = [] ):
                import re

                if isinstance(data, dict):
                        for key in data:
                                val = str(data[key])
                                val = re.sub("'+",'',val)
                                val = re.sub('"+','',val)
                                if key not in noescape: val = MySQLdb.escape_string(val)
                                data[key] = "'%s'" % val
                        return data

                try:
                        data = str(data)
                        data = re.sub("'+",'',data)
                        data = re.sub('"+','',data)
                        return MySQLdb.escape_string(data)
                except Exception ,e:
                        print e
                        return ''

        def setEncoding(self, type = None):
               if type is None: type = 'utf8'
               import sys
               if sys.getdefaultencoding == type: return
               reload(sys)
               sys.setdefaultencoding
               sys.setdefaultencoding(type)

# --- database connection
