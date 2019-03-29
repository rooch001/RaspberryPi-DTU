
# coding: utf-8

# In[19]:


import os
import shutil
from timeit import default_timer as timer
from tqdm import tqdm
import time
from subprocess import call
# pip install mysql-connector
import mysql.connector
from mysql.connector import errorcode

import pandas as pd
from RPLCD.gpio import CharLCD
from RPi import GPIO
GPIO.setwarnings(False)
lcd = CharLCD(cols = 16,rows=2,pin_rs = 37,pin_e=35,pins_data=[33,31,29,23],numbering_mode=GPIO.BOARD)

class DTU:
    def __init__(self,db):
        self.position = 0
        self.levels = (0,0)
        self.source=""
        self.destination=""
        self.mediafolder="/media/pi"
        self.arr = ["Show available sources\n\r","Select Source\n\r","Destination\n\r","Transfer\n\r","Reset\n\r","Shut Down\n\r",' ']
        self.arr2 = ["Select folder\n\r","Show Selected\n\r","Start transfer\n\r"]
        self.drives = os.listdir(self.mediafolder)
        self.framebuffer = ['']
        self.delay = 0.5
        self.num_cols = 16
        # Board pins for buttons
        self.btnUp = 11
        self.btnDown = 13
        self.btnSelect = 7
        self.treeTracker = ['menuRepeat']
        self.selectedFiles = []
        self.dbInstance = db
        #self.log = file()
        
    
    def updateTrackerIn(self,item):
        if not self.treeTracker[-1] == item:
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
        return int(input())
        #while True:
        """upstate = GPIO.input(self.btnUp)
            downstate = GPIO.input(self.btnDown)
            selectstate = GPIO.input(self.btnSelect)
        
            Hard coding button conditions
            1=UP
            2=DOWN
            3=SELECT / BACK
            
            if upstate == False:
                return 1 
            elif downstate == False:
                
                return 2
            elif selectstate == False:
                
                return 3
           """
            
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
        if not a[-1]=="/...." and not a[-1]==" ":
            a.append("/....")
            a.append(' ')
        return a
    
    def selectBackItem(self):
        self.treeTracker.pop()
        lastitem = self.treeTracker[-1]
        #print(locals())
        fntocall = locals()['self']
        time.sleep(0.5)
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
        print(self.drives)
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
                self.selectBackItem()
            if self.position < 0:
                self.position = len(self.drives)-2
                index = len(self.drives)-2
                
            if self.position > len(self.drives)-2:
                self.position = 0
                index = 0
     
            

            time.sleep(0.5)
            
    def menuRepeat(self):
        index = 0
        self.position=0
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
                self.position = 5
                index = 5
            elif self.position == 6:
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
        self.drives=self.addBackItem(self.drives)
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
                if self.position==len(self.drives)-2:
                    self.menuRepeat()
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
       
    def selectSpecificFolder(self):
        index = 0
        self.updateTrackerIn('selectSpecificFolder')
        self.position = 0
        folders = os.listdir(self.mediafolder +"/"+ self.source)
        folders = self.addBackItem(folders)
        time.sleep(0.5)
        print(folders)
        while(True):
            btnChoice = self.showItem(folders[index],folders[index+1])
            if btnChoice==2:
                self.position+=1
                index += 1
            elif btnChoice==1:
                self.position-=1
                index -= 1
            elif btnChoice==3:
                if self.position == len(folders) - 2:
                    self.selectBackItem()
                if folders[self.position] not in self.selectedFiles:
                    self.selectedFiles.append(folders[self.position])
                    self.showLCDMessage("File Selected")
                else:
                    self.showLCDMessage("Already selected!")
                
            if self.position < 0:
                self.position = len(folders)-2
                index = len(folders)-2
                
            if self.position > len(folders)-2:
                self.position = 0
                index = 0
     
            time.sleep(0.5)
        
        
    def selectDestination(self):
        index = 0
        self.updateTrackerIn('selectDestination')
        self.drives=self.addBackItem(self.drives)
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
                if self.position==len(self.drives)-2:
                    self.menuRepeat()
                self.destination=self.drives[self.position]
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
            
    def startSpecificTransfer(self):
        try:
            
            self.updateTrackerIn('transferSome')
            start = timer()
            lcd.clear()
            lcd.cursor_pos=(0,0)
            lcd.write_string("Tranferring Specific")
            
            destinationDir = os.path.join(self.mediafolder,self.destination)
            sourceDir = os.path.join(self.mediafolder,self.source)
            print(sourceDir,destinationDir)
            filelen = len(self.selectedFiles)

            dirsize = 0
            insertQuery = """INSERT INTO datadtu (nooffolders,amountofdata,processtime) VALUES (%s,%s,%s)"""
            
            
            
            for f in tqdm(range(len(self.selectedFiles)),unit='KB'):
                dirsize+=self.folderSize(os.path.join(sourceDir,self.selectedFiles[f]))
                if os.path.isdir(os.path.join(sourceDir,self.selectedFiles[f])):
                    print("Kyun ghusa be??")
                    shutil.copytree(os.path.join(sourceDir,self.selectedFiles[f]),os.path.join(destinationDir,str(self.selectedFiles[f])))
                elif os.path.isfile(os.path.join(sourceDir,self.selectedFiles[f])):
                    shutil.copyfile(os.path.join(sourceDir,self.selectedFiles[f]),os.path.join(destinationDir,str(self.selectedFiles[f])))
                    
            end = timer()
            lcd.clear()
            lcd.cursor_pos=(0,0)
            self.dbInstance.execute(insertQuery,(filelen,dirsize,round(end-start)))
            lcd.write_string("Time-"+str(round(end - start))+" sec.")
            time.sleep(0.5)
        except Exception as error:
            print(error)
            self.showLCDMessage("Cannot Transfer!")
            time.sleep(0.5)
            self.menuRepeat()
            
    def transferSome(self):
        index = 0
        self.updateTrackerIn('transferSome')
        self.arr2 = self.addBackItem(self.arr2)
        self.position = 0
        if len(self.arr2) % 2 == 0:        
            self.arr2.append(' ')
        print("Idher bhi hu")
        time.sleep(0.5)
        while(True):
            btnChoice = self.showItem(self.arr2[index],self.arr2[index+1])
            if btnChoice==2:
                self.position+=1
                index += 1
            elif btnChoice==1:
                self.position-=1
                index -= 1
            elif btnChoice==3:
                
                if self.position == len(self.arr2) - 2:
                    self.selectBackItem()
                    
                if self.position == 0:
                    self.selectSpecificFolder()
                elif self.position == 1:
                    self.showSelectedItems()
                elif self.position == 2:
                    self.startSpecificTransfer()
                    
                    
                else:
                    pass
                    
            if self.position < 0:
                self.position = len(self.arr2)-2
                index = len(self.arr2)-2
                
            if self.position > len(self.arr2)-2:
                self.position = 0
                index = 0
            time.sleep(0.5)
            
            
    def showSelectedItems(self):
        index = 0
        self.updateTrackerIn('showSelectedItems')
        self.selectedFiles = self.addBackItem(self.selectedFiles)
        
        self.position = 0
        print("aaraha hu")
        print(self.selectedFiles)
        time.sleep(0.5)



        while(True):
            btnChoice = self.showItem(self.selectedFiles[index],self.selectedFiles[index+1])
            if btnChoice==2:
                self.position+=1
                index += 1
            elif btnChoice==1:
                self.position-=1
                index -= 1
            elif btnChoice==3:
                print("Selected:",self.position)
                if self.position == len(self.selectedFiles) - 2:
                    # array initialize to empty array
                    if len(self.selectedFiles) == 2:
                        self.selectedFiles = []
                    self.selectBackItem()
                
                del self.selectedFiles[self.position]
                self.showLCDMessage("File Deselected!")
                self.showSelectedItems()
            
            if self.position < 0:
                self.position = len(self.selectedFiles)-2
                index = len(self.selectedFiles)-2
                
            if self.position > len(self.selectedFiles)-2:
                self.position = 0
                index = 0
            #print("Time called ")
    def transferContent(self):
        try:
            lcd.clear()
            contentItems=['Transfer All','Transfer Some']
            index = 0
            self.updateTrackerIn('transferContent')
            contentItems = self.addBackItem(contentItems)
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
                    #Select button
                    print("Selected back item:",self.position)
                    if self.position == len(contentItems) - 2:
                        self.selectBackItem()
                    
                    if self.position == 0:
                        start = timer()
                        lcd.clear()
                        lcd.cursor_pos=(0,0)
                        lcd.write_string("Tranferring        PKMKB")
                        files = os.listdir(os.path.join(self.mediafolder,self.source))
                        destinationDir = os.path.join(self.mediafolder,self.destination)
                        sourceDir = os.path.join(self.mediafolder,self.source)
                        print(sourceDir,destinationDir)
                        filelen = len(files)
                    
                        dirsize = self.folderSize(sourceDir)
                        insertQuery = """INSERT INTO datadtu (nooffolders,amountofdata,processtime) VALUES (%s,%s,%s)"""
                        for f in tqdm(range(len(files)),unit='KB'):
                            if os.path.isdir(os.path.join(sourceDir,files[f])):
                                shutil.copytree(os.path.join(sourceDir,files[f]),os.path.join(destinationDir,str(files[f])))
                        end = timer()
                        self.dbInstance.execute(insertQuery,(filelen,dirsize,round(end-start)))

                        lcd.clear()
                        lcd.cursor_pos=(0,0)
                        lcd.write_string("Time-"+str(round(end - start))+" sec.")
                    else:
                        print("M here")
                        self.transferSome()
                        
                        
                if self.position < 0:
                    self.position = len(contentItems)-2
                    index = len(contentItems)-2
                    
                if self.position > len(contentItems)-2:
                    self.position = 0
                    index = 0
                time.sleep(0.5)
                
        except Exception as error:
            print(error)
            self.showLCDMessage("Cannot Transfer!")
            time.sleep(0.5)
            self.menuRepeat()
           
    
    def folderSize(self,path):
        total = 0
        if not os.path.isfile(path):
            for i in os.scandir(path):
                if i.is_file():
                    total += i.stat().st_size
                elif i.is_dir():
                    total += self.folderSize(i.path)
        else:
            return os.stat(path).st_size
        return (total)
           
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
            if self.source != "" and self.destination != "":
                self.transferContent()
            else:
                self.showLCDMessage("Select-Source Destination")
                time.sleep(4)
                self.menuRepeat()
            
        if selectedItem == 5:
            self.source=""
            self.destination=""
            self.drives = os.listdir(self.mediafolder)
            self.framebuffer = ['']
            self.selectedFiles=[]
            self.showLCDMessage("Resetting... ")
            time.sleep(3)
            self.menuRepeat()
        if selectedItem==6:
            time.sleep(1)
            lcd.clear()
            time.sleep(1)
            
            call("sudo poweroff", shell=True)
            
        
    
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
class Database:
    def __init__(self):
        try:
            self.cursor = mysql.connector.connect(host = "192.168.129.244", user='test',password="1234",database="dtu").cursor()

        except mysql.connector.Error as err:
        
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)
    
    def createTables(self):

        sql = """CREATE TABLE if not exists datadtu (
            ID INTEGER PRIMARY KEY AUTO_INCREMENT  ,
            nooffolders INTEGER(5),
            amountofdata FLOAT(11,11),
            processtime FLOAT(11,11)
        );"""
    
        self.cursor.execute(sql)
        
    # get instance of cursor (or get cursor object)
    def getDatabaseInstance(self):
        return self.cursor
    # make any Query
    def makeQuery(self):
        return self.cursor.execute(query)
  
   
    def printTable(self):
        self.cursor.execute("SELECT * FROM datadtu;")
        result = self.cursor.fetchall()
        for row in result:
            print(row)
    




if __name__ == "__main__":
    
    print("Welcome to DTU")
    #dtu.connectDatabase()
    # un-comment this to make table in the database
    #dtu.createTables()
   
    db = Database()
    dtu = DTU(db.getDatabaseInstance())
    dtu.btnSetup()
    dtu.menuRepeat()
    db.printTable()
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

