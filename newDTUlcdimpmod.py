
# coding: utf-8

# In[19]:


import os
import shutil
from timeit import default_timer as timer
from tqdm import tqdm
import time
# pip install mysql-connector
import sqlite3
import pandas as pd
from RPLCD.gpio import CharLCD
from RPi import GPIO
GPIO.setwarnings(False)
lcd = CharLCD(cols = 16,rows=2,pin_rs = 37,pin_e=35,pins_data=[33,31,29,23],numbering_mode=GPIO.BOARD)

class DTU:
    def __init__(self):
        self.position = 0
        self.levels = (0,0)
        self.source=""
        self.destination=""
        self.mediafolder="/media/pi"
        self.arr = ["Show available sources\n\r","Select Source\n\r","Destination\n\r","Transfer\n\r","Exit\n\r",' ']
        self.drives = os.listdir(self.mediafolder)
        self.framebuffer = ['']
        self.delay = 0.5
        self.num_cols = 16
        # Board pins for buttons
        self.btnUp = 11
        self.btnDown = 13
        self.btnSelect = 7
        self.treeTracker = ['menuRepeat']
        
    
    def updateTrackerIn(self,item):
        self.treeTracker.append(item)
        return
    
    def updateTrackerOut(self):
        self.treeTracker.pop()
        return
    
    def btnSetup(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(self.btnUp,GPIO.IN,pull_up_down = GPIO.PUD_UP)
        GPIO.setup(self.btnDown,GPIO.IN,pull_up_down = GPIO.PUD_UP)
        GPIO.setup(self.btnSelect,GPIO.IN, pull_up_down = GPIO.PUD_UP)
    
    def btnGetChoice(self):
        while True:
            upstate = GPIO.input(self.btnUp)
            downstate = GPIO.input(self.btnDown)
            selectstate = GPIO.input(self.btnSelect)
            """
            Hard coding button conditions
            1=UP
            2=DOWN
            3=SELECT / BACK
            """
            if upstate == False:
                return 1 
            elif downstate == False:
                
                return 2
            elif selectstate == False:
                
                return 3
           
            
    def endprogram(self):
        GPIO.cleanup()
        
    def write_to_lcd(self,lcd):
        lcd.home()
        for row in self.framebuffer:
            lcd.write_string('>')
            lcd.write_string(row.ljust(self.num_cols)[1:self.num_cols])
            
    def loop_string(self,string,lcd,row):
        # minus 2 becuause of \n \r
        for i in range(len(string)-2 - self.num_cols + 1):
            self.framebuffer[0] = string[i:i+self.num_cols]
            self.write_to_lcd(lcd)
            time.sleep(self.delay)
            
                
    def addBackItem(self,a):
        a.append("/....")
        if len(a)%2 != 0 :
            a.append(' ')
        return a
    
    def selectBackItem(self,l):
        self.treeTracker.pop()
        lastitem = self.treeTracker[-1]
        #print(locals())
        
        fntocall = locals()['self']
        getattr(fntocall,lastitem)()
    def showItem(self,value1,value2):
        lcd.clear()
        value1 = value1[:15]
        value2 = value2[:15]
        lcd.cursor_pos = (0, 0)
        lcd.write_string(">")
        lcd.write_string(str(value1))
        lcd.cursor_pos = (1, 0)
        lcd.write_string(" ")
        lcd.write_string(str(value2))
        lcd.cursor_pos = (0,0)
        self.loop_string(str(value1),lcd,0)
        btnChoice = self.btnGetChoice()
        return btnChoice
    
    def showSources(self):
        index = 0
        self.updateTrackerIn('showSources')
        self.drives = self.addBackItem(self.drives)
        self.position = 0
        while(True):
            btnChoice = self.showItem(self.drives[index],self.drives[index+1])
            if btnChoice==2:
                self.position+=1
                index += 1
            elif btnChoice==1:
                self.position-=1
                index -= 1
            elif btnChoice==3:
                #Back button
                self.selectBackItem(len(self.drives))
                
            if self.position < 0:
                self.position = len(self.drives)-2
                index = len(self.drives)-2
                
            if self.position > len(self.drives)-2:
                self.position = 0
                index = 0
     
            

            time.sleep(0.5)
            
    def menuRepeat(self):
        index = 0
        while(True):
            btnChoice = int(self.showItem(self.arr[index],self.arr[index+1]))
            print(btnChoice)
            if btnChoice == 2:
                self.position+=1
                index += 1
                time.sleep(0.5)    
            elif btnChoice==1:
                self.position-=1
                index -= 1
                time.sleep(0.5)
            elif btnChoice==3:
                time.sleep(1)
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
    
    def showLCDMessage(self,message):
        lcd.clear()
        lcd.cursor_pos = (0,3)
        message=message.split(' ')
        lcd.write_string(message[0])
        lcd.cursor_pos = (1,3)
        lcd.write_string(message[1])
        return
    
    def selectSource(self):
        index = 0
        self.updateTrackerIn('selectSource')
        self.position = 0
        while(True):
            btnChoice = self.showItem(self.drives[index],self.drives[index+1])
            if btnChoice==2:
                self.position+=1
                index += 1
            elif btnChoice==1:
                self.position-=1
                index -= 1
            elif btnChoice==3:
                #Back button
                self.source=self.drives[self.position]
                del self.drives[self.position]
                self.showLCDMessage("Source Selected")
                time.sleep(3)
                self.menuRepeat()
                
            if self.position < 0:
                self.position = len(self.drives)-2
                index = len(self.drives)-2
                
            if self.position > len(self.drives)-2:
                self.position = 0
                index = 0
     
            time.sleep(0.5)
       
        
    def selectDestination(self):
        index = 0
        self.updateTrackerIn('selectDestination')
        self.position = 0
        while(True):
            btnChoice = self.showItem(self.drives[index],self.drives[index+1])
            if btnChoice==2:
                self.position+=1
                index += 1
            elif btnChoice==1:
                self.position-=1
                index -= 1
            elif btnChoice==3:
                #Back button
                self.source=self.drives[self.position]
                del self.drives[self.position]
                self.showLCDMessage("Destination Selected")
                time.sleep(3)
                self.menuRepeat()
                
            if self.position < 0:
                self.position = len(self.drives)-2
                index = len(self.drives)-2
                
            if self.position > len(self.drives)-2:
                self.position = 0
                index = 0
     
            time.sleep(0.5)
       
    def transferContent(self):
        lcd.clear()
        contentItems=['Transfer All','Transfer Some']
        index = 0
        self.updateTrackerIn('transferContent')
        self.drives = self.addBackItem(contentItems)
        self.position = 0
        while(True):
            btnChoice = self.showItem(contentItems[index],contentItems[index+1])
            if btnChoice==2:
                self.position+=1
                index += 1
            elif btnChoice==1:
                self.position-=1
                index -= 1
            elif btnChoice==3:
                #Back button
                if self.position == 0:
                    start = timer()
                    lcd.clear()
                    lcd.cursor_pos=(0,0)
                    lcd.write
                    files = os.listdir(os.path.join(self.mediafolder,self.source))
                    destinationDir = os.path.join(self.mediafolder,self.destination)
                    sourceDir = os.path.join(self.mediafolder,self.source)
                    for f in tqdm(range(filelen),unit='KB'):
                        if os.path.isdir(os.path.join(sourceDir,files[f])):
                            shutil.copytree(os.path.join(sourceDir,files[f]),os.path.join(destinationDir,str(files[f])))
                    end = timer()
                    lcd.clear()
                    lcd.cursor_pos=(0,0)
                    lcd.write_string("Time-",end - start,"sec.")

                
            if self.position < 0:
                self.position = len(contentItems)-2
                index = len(contentItems)-2
                
            if self.position > len(contentItems)-2:
                self.position = 0
                index = 0
     
            

            time.sleep(0.5)
            
            
            
        
        
    def onSelect(self,selectedItem):
        if selectedItem == 1:
            #Display available sources and destinations
            self.showSources()
            
        if selectedItem == 2:
            
            self.selectSource()
            return

        if selectedItem == 3:
            
            self.selectDestination()
            return

        if selectedItem == 4:
            self.transferContent()
            

        
    
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
                    print(i+1,source)A

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
    dtu = DTU()
    dtu.btnSetup()
    dtu.menuRepeat()
    
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

