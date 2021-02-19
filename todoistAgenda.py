from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import datetime
import os
from shutil import copyfile
import json

with open("credentials.json","r") as creds:
    credentials = json.load(creds)

def openWebPage(email=credentials['email'],password=credentials['pw']):
	
    url = 'https://todoist.com/Users/showlogin'
    
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    
    driver = webdriver.Chrome(options=options) # 
    driver.get(url)

    inputElement = driver.find_element_by_id("email")
    inputElement.send_keys(email)

    time.sleep(2)

    inputElement2 = driver.find_element_by_id("password")
    inputElement2.send_keys(password)

    time.sleep(2)

    inputElement.submit()

    return(driver)

def getTasks(driver):

	soup = BeautifulSoup(driver.page_source, "html.parser")

	span = soup.find_all("div","task_content")
	span2 = soup.find_all("span","task_list_item__project")

	tasks = [sp.text for sp in span]
	projects = [sp2.text for sp2 in span2]

	return(dict(zip(tasks,projects)))



### Create the LaTeX file for my agenda
def create_File(task_dict,home=credentials['home_dir']):
    os.chdir(home) # go to location where the template file is located
    today = datetime.date.today().strftime('%m-%d-%y')
    today2 = datetime.date.today().strftime('%m/%d/%y')
    today_wkday = datetime.date.today().strftime('%A')
    new_loc = home + '/' + today
    os.mkdir(new_loc) # Create the directory to put the file in
    copyfile('template.txt',new_loc+'/'+today+'.tex') # Move the template to new file

    os.chdir(new_loc) # move to the new location
    f = open(today+'.tex','a')
    # write the header
    f.write(today_wkday + ", "+today2+"\n")
    f.write("\\end{center}")

    for i in range(6):
        f.write('\n')

    f.write('\\begin{enumerate}\n\n')

    # Write the task items and their projects
    skip = ['Check: Calendar','Text','Set agenda','Add any leftover running stats','Weigh in','Message','Schedule','Update Goodreads']
    for task, project in task_dict.items():
    	if task in skip:
    		print('Skipping',task)
    	else:
    		f.write('\\item \\textbf{')
    		f.write(task)
    		f.write('} (Project: ' + project + ')')
    		f.write('\n\n\n\n\n')


    f.write('\\end{enumerate}\n')
    f.write('\\end{document}')
    f.close()


### Function to stop the script if the day's directory already exists
def stopProgram(home=credentials['home_dir']):
    os.chdir(home)
    today = datetime.date.today().strftime('%m-%d-%y')
    new_loc = home + '/' + today
    if os.path.exists(new_loc):
        return(True)
    else:
        return(False)




if __name__=="__main__":

	# '/Users/stephensmith/Dropbox/Daily Agendas' if using Mac
    
    if stopProgram():
        exit()

    print("Opening Todoist page.\n")    
    driver = openWebPage()

    time.sleep(3)

    print("Refreshing the page to allow today's tasks to update.\n")
    driver.refresh()

    time.sleep(3)

    print("Obtaining Tasks.\n")
    task_dict = getTasks(driver)
    print(task_dict)

    if bool(task_dict):
    	flag = False
    else:
    	flag = True # dictionary is empty and we have to run again

    i = 1
    driver.quit()
    driver = openWebPage()	

    while flag and i < 5:
    	print(i)
    	time.sleep(i)
    	task_dict = getTasks(driver)
    	i += 1
    	flag = not (bool(task_dict))


    if flag:
    	print("Unable to obtain tasks.\n")
    else:
    	print("Found Tasks!\n")

    driver.quit()

    create_File(task_dict=task_dict)

