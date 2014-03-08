class Revisioner(): 

    def init(self): 
        from ConfigParser import ConfigParser
        self.cp = ConfigParser()
        self.nivel = "production"
        self.cp.read("application.ini")
        
        print self.cp.get(self.nivel, "dbhost")

        from Database import Database
        self.db = Database()


def main():
    r = Revisioner()
    r.init()


if __name__ == '__main__':
    main()

