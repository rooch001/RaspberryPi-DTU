#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import threading
import time
import shutil


# In[ ]:


def copyfunc(src,dst):
    shutil.copytree(src,dst)


# In[ ]:


start = time.time()
src="E:\\"
dst="F:\\"
threads = []
for file in os.listdir(src):
    t = threading.Thread(target=copyfunc,args=(src+file,dst+"abcd\\"+file))
    t.start()
    threads.append(t)
    
for thread in threads:
    thread.join()
    
end=time.time()

print(end-start)


# In[ ]:


start = time.time()
copyfunc("E:\\","F:\\abcde")
end=time.time()
print(end-start)


# In[ ]:


import os


# In[ ]:


os.listdir('F:\\')


# In[ ]:


import subprocess


# In[ ]:


subprocess.run([])

