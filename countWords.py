import os
from threading import Thread,Lock
import time
import sys
import mimetypes
import re
words=0
last=False
static_threads=4
mutex=Lock()
def count_words(thread_data):
    mutex.acquire()
    global words
    global last
    try:
        position=int(thread_data['position'])#Position pointer
        size=int(thread_data['block_size'])#size of characters/bytes to read
        fd=thread_data['file']#file to read
        fd.seek(position)#go to the position
        text=fd.read(size)#read from file the next characters ==size
        if thread_data['id']==0 or thread_data['id']==3:#if is the first or last thread strip text
            text.strip()
        time.sleep(1)#sleep
        state=False
        if last==True and text[0]!=" ":#if the last thread's last char wasnt space and this thread's buffer's first char isnt space  too, words are one less
            words-=1
        if text[len(text)-1]!=" " :#if last char of buffer isnt space last is true
            last=True
        else:
            last=False
        for character in text:#count words
            if character == " " or character == "\n" or character == "\t":
                state = False
            # If next character is not a word separator and
            # state is false, then set the state as true and
            # increment word count
            elif state == False:
                state = True
                words+=1
    finally:
        mutex.release()

def thread_create(block_size,file):
    threads = list()
    for index in range(0,static_threads):#create threads
        print("Main    : create and start thread :.", index)
        thread_data={"file":file,"block_size":block_size,"position":index*block_size,"id":index}#pass thread's data to directory
        try:
            x = Thread(target=count_words, args=(thread_data,))#new thread
        except:
            print ("Error: unable to start thread")#catch error
        threads.append(x)
        x.start()
    for index, thread in enumerate(threads):#join
        print("Main    : before joining thread :.", index)
        thread.join()
        print("Main    : thread %d done" % (index))
def parent_child(file):
    global words
    try:
        n = os.fork()
        # n greater than 0  means parent process
        if n > 0:
            print("Parent process and id is : ", os.getpid())
            pid, status = os.waitpid(n, 0)
            print ("wait returned, pid = %d, status = %d" % (pid, status))
        # n equals to 0 means child process
        else:
            print("Child process and id is : ", os.getpid())
            file_size = os.path.getsize(file)#Get file size
            block_size=file_size/static_threads#Get thread's size
            fd=open(file,"r")#open file for read
            thread_create(block_size,fd)#funtion to create threaad
            fd.close()#close file
            fd2=open("output.txt","a")#open file to append the results
            fd2.write("pid : " +str(os.getpid())+" file : "+file+" words : "+str(words)+"\n")#write results
            fd2.close()
            print("pid : %d file : %s words : %d" % (os.getpid(),file,words)) #print words fileName and pid
            words=0#we go to new proccess so words are 0 again
            sys.exit(0)#exit proccess
    except KeyboardInterrupt:
        print("\n Exitting Program !!!!")
        sys.exit()

if __name__ == "__main__":#main
    directory=input("Give the directory wou want to search the files :")#get directory input from user
    for path in os.listdir(directory):#list files
        full_path = os.path.join(directory, path)#get file's fullpath
        mime = mimetypes.guess_type(full_path)#get type of file
        if re.search('text', str(mime)) != None:#if it contains text
            print("-" * 50)
            parent_child(full_path)#fork function



