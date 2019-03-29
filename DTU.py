
# coding: utf-8

# In[19]:


import os
import shutil
from timeit import default_timer as timer
from tqdm import tqdm
import datetime
# pip install mysql-connector
import sqlite3
import pandas as pd
from RPLCD.gpio import CharLCD
from RPi import GPIO
GPIO.setwarnings(False)
lcd = CharLCD(cols = 16,rows=2,pin_rs = 37,pin_e=35,pins_data=[33,31,29,23],numbering_mode=GPIO.BOARD)

class Lcdinterface:
    def __init__(self):
        self.position = 0
        self.levels = (0,0)
        self.source=""
        self.destination=""
        self.mediafolder="/media/pi"
        self.arr = ["Show sources\n\r","Source\n\r","Destination\n\r","Transfer\n\r","Exit\n\r",' ']
        self.drives = os.listdir(self.mediafolder)
    def showItem(self,value1,value2):
        lcd.clear()
        lcd.cursor_pos = (0, 0)
        lcd.write_string(">")
        lcd.write_string(str(value1))
        lcd.cursor_pos = (1, 0)
        lcd.write_string(" ")
        lcd.write_string(str(value2))
        temp = int(input("1-down,2-up,3-select"))
        return temp
    
    def showSources(self):
        index = 0
        while(True):
            temp = self.showItem(self.drives[index],self.drives[index+1])
            if temp==1:
                self.position+=1
                index += 1
            elif temp==2:
                self.position-=1
                index -= 1
            elif temp==3:
                self.menuRepeat()
                
            if self.position < 0:
                self.position = 4
                index = 4
            elif self.position == 5:
                self.position=0
                index = 0
                
    def onBack(self):
        self.menuRepeat()
    def menuRepeat(self):
        index = 0
        while(True):
            temp = self.showItem(self.arr[index],self.arr[index+1])
            if temp==1:
                self.position+=1
                index += 1
            elif temp==2:
                self.position-=1
                index -= 1
            elif temp==3:
                self.onSelect(index+1)
                
            if self.position < 0:
                self.position = 4
                index = 4
            elif self.position == 5:
                self.position=0
                index = 0
                
    def onDown(self):
        self.clearpointer(position,1)
        self.position += 1
    def onUp(self):
        self.position -= 1
    
    def onSelect(self,selectedItem):
        if selectedItem == 1:
            self.showSources()
            
        if selectedItem == 2:
            pass
        if selectedItem == 4:
            lcd.clear()
            start = timer()
            files = os.listdir(os.path.join(self.mediafolder,self.source))
            destinationDir = os.path.join(self.mediafolder,self.destination)
            sourceDir = os.path.join(self.mediafolder,self.source)
            for f in tqdm(range(filelen),unit='KB'):
                if os.path.isdir(os.path.join(sourceDir,files[f])):
                    shutil.copytree(os.path.join(sourceDir,files[f]),os.path.join(destinationDir,str(files[f])))
            end = timer()  
            lcd.write_string("Time-",end - start,"sec.")
    

        
    
        """try:
            #Show all sources
            if choice == 1:
                print("Availabe sources:\n")
                for i,source in enumerate(self.drives):
                    print(i+1,source)
                return

            #Select source
            elif choice == 2:
                print("Availabe sources:\n")
                for i,source in enumerate(self.drives):
                    print(i+1,source)

                select = self.askChoice("Select a source: ")
                self.source=self.drives[select-1]
                print("\nSource selected!\n")
                return

            #Select dest
            elif choice == 3:
                print("Availabe destinations:\n")
                for i,source in enumerate(self.drives):
                    if source==self.source:
                        continue
                    print(i+1,source)

                select = self.askChoice("Select a destination: ")
                self.destination=self.drives[select-1]
                print("\nDestination selected!\n")
                return

            #Transfer content
            elif choice == 4:
                print("[1] Transfer all content\n","\n[2] Select content to transfer")
                ch=self.askChoice("\nChoose an option: ")
                if ch == 1:
                    start = timer()
                    files = os.listdir(os.path.join(self.mediafolder,self.source))
                    filelen = len(files)
                    destinationDir = os.path.join(self.mediafolder,self.destination)
                    sourceDir = os.path.join(self.mediafolder,self.source)
                    # paste commented code here
                    for f in tqdm(range(filelen),unit='KB'):
                        if os.path.isdir(os.path.join(sourceDir,files[f])):
                            shutil.copytree(os.path.join(sourceDir,files[f]),os.path.join(destinationDir,str(files[f])))
                    end = timer()  
                    dirsize = self.folderSize('D:\sourceDir\SOURCE')
                    i = 1
                    insertQuery = INSERT INTO datadtu (nooffolders,amountofdata,processtime) VALUES (?,?,?);
                    self.cursor.execute(insertQuery,(filelen,dirsize,end))
                    self.connection.commit()
                    print("Time-Elapsed : " ,end - start,"sec.")

                elif ch == 2:
                    pass
                
                return
            
            elif choice == 5:
                self.printTable()
                
            elif choice == 6:
                pass 

        except Exception as e:
            print("ERROR: ",e)"""
"""class DTU:
    def __init__(self):
        
        #self.destFolder="USB Transfer"
    # use once to create tables
    def createTables(self):
        # id , time taken to process,amount of data,no of folders,
        sql = CREATE TABLE datadtu (
            ID INTEGER PRIMARY KEY AUTOINCREMENT  ,
            nooffolders INTEGER(5),
            amountofdata FLOAT(11,11),
            processtime FLOAT(11,11)
        );
        self.getDatabaseInstance().execute(sql)
    # connect to database dtu.db and set cursor
    def connectDatabase(self):
        self.connection = sqlite3.connect("dtu.db")
        self.cursor = self.connection.cursor()
        
    # get instance of cursor (or get cursor object)
    def getDatabaseInstance(self):
        return self.cursor
    # make any Query
    def makeQuery(self,query):
        return self.cursor.execute(query)
    
            
    # Returns folder size (Recursive algorithm)
    def folderSize(self,path):
        total = 0
        for i in os.scandir(path):
            if i.is_file():
                total += i.stat().st_size
            elif i.is_dir():
                total += self.folderSize(i.path)
        return (total)
    def askChoice(self,string):
        return int(input(string))
    # prints database table
    def printTable(self):
        self.cursor.execute(SELECT * FROM datadtu;)
        result = self.cursor.fetchall()
        for row in result:
            print(row)
    # Convert Database into csv             
    def csvdb(self):
        df = pd.read_sql_query("SELECT * FROM datadtu;",self.connection)
        return df"""
if __name__ == "__main__":
    print("Welcome to DTU")
    #dtu.connectDatabase()
    # un-comment this to make table in the database
    #dtu.createTables()
    lcdint = Lcdinterface()
    lcdint.menuRepeat()
    """while(True):
        ch = dtu.showMenu()

        #Exit condition
        if ch not in [1,2,3,4,5]:
            print("Bye for now!")
            break

        #On choice selected
        dtu.choiceSelected(ch)
        
        
        input("press [ENTER] to continue")
"""

