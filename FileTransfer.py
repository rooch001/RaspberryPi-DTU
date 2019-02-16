
# coding: utf-8

# In[13]:


# source = "D:\\sourceDir\\temp"
# for f in files:
#     ss = zipfile.ZipFile(sourceDir,'w',zipfile.ZIP_DEFLATED)
#     ss.write(source+ "\\"+ f, os.path.basename(sourceDir))
# print(ss)
# ss.close()
import os
import shutil 
from timeit import default_timer as timer
def testDataTranferUtility():
    start = timer()
    files = os.listdir("D:\\sourceDir")
    destinationDir = "D:\\destinationDir"
    sourceDir = "D:\\sourceDir"
    # paste commented code here
    try:
        for f in files:
            shutil.copytree(sourceDir + "\\"+ f,destinationDir + "\\"+ str(f))
    except Exception as e:
        print(e)
    end = timer()
    print("Time-Elapsed : " ,end - start,"sec.")

testDataTranferUtility()

