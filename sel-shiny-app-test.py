#!/usr/bin/env python3
#
# This script verifies that certain interactive portions
# of a specific shiny server application return the expected
# output values.  The application uses dialog boxes that execute
# R source code input.
#
import os,sys,time

from selenium import webdriver
from multiprocessing.pool import ThreadPool

import logging
from logging.handlers import SysLogHandler

numTasks = 0 

logger = logging.getLogger()
logger.setLevel(logging.INFO)

syslog = SysLogHandler(address='/dev/log', facility='local7')

logger.addHandler(syslog)

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--incognito")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("headless")
chrome_options.add_argument("window-size=800x600")

fib_R_code = """
len = 12
fibvals = numeric(len)
fibvals[1] = 1
fibvals[2] = 1 
Sys.sleep(5)
for (i in 3:len) { 
   fibvals[i] = fibvals[i-1] + fibvals[i-2]
   cat(fibvals[i]," ")
} 
"""
# Looks like the shiny tutor engine defines empty text areas by div 
# class "tutor-exercise...shiny-bound-input"  with the class name 
# terminating in "shiny-bound-input" where as as pre-filled areas 
# terminate the class name with "ace-focus".  Since we don't care
# about deleting pre-filled areas yet we simpy fill the empty areas and
# run some of the pre-filled code that does generate input.
#
# We also want to tell the driver to implicitly wait for 8 seconds, this will
# cause any "find_element_" functions to "watch" the DOM for a specific element
# and end if not found after 8 seconds.  The purpose is to look for elements
# that get dynamically created as a result of an action on the page.
#def runTest(drv_instance):
def runTest(task):

  try:
    #DRIVER INIT
    drv_instance = webdriver.Chrome(chrome_options=chrome_options)
    drv_instance.implicitly_wait(15)
    #logger.info(".", sep='',end="",flush=True)
    time.sleep(1)
    try:
      #DRIVER CALL
      drv_instance.get("https://scf.berkeley.edu:3838/alucas/")
      drv_instance.find_element_by_partial_link_text('Chapter-04-collection').click()
      try:
          #TEST BLOCK
          drv_instance.find_element_by_xpath('(//a[contains(text(),"Run Code")])[1]').click()
          time.sleep(1)
          codetxt = drv_instance.find_element_by_xpath('(//div[@class="tutor-exercise-output shiny-bound-output"]/pre/code)[1]').text
          codetxtarea = drv_instance.find_element_by_xpath('(//div[@class="tutor-exercise-code-editor ace_editor ace-tm shiny-bound-input"]/textarea)').send_keys(fib_R_code)
          time.sleep(1)
          drv_instance.find_element_by_xpath('(//a[contains(text(),"Run Code")])[2]').click()
          time.sleep(1)
          solution_txt = drv_instance.find_element_by_xpath('(//div[@class="tutor-exercise-output shiny-bound-output"]/pre/code)[2]').text
          logger.info("selenium INFO: Thread: " + str(task))
          logger.info("selenium INFO: Target Node: " + drv_instance.get_cookie('SERVERID')['value'])
          logger.info("selenium INFO: Session ID: " + drv_instance.session_id)
          logger.info("selenium INFO: Fib Sequence: " + solution_txt + "\n")
      except Exception as e: 
          logger.error("selenium ERROR: target_node: " + drv_instance.get_cookie('SERVERID')['value'] + "thread id: " + str(task) + " session_id: " + drv_instance.session_id)
          logger.error("selenium TEST BLOCK ERROR: " + str(e))
          pass

    except Exception as e:
      try:
        logger.error("selenium ERROR: target_node: " + drv_instance.get_cookie('SERVERID')['value'] + "thread id: " + str(task) + " session_id: " + drv_instance.session_id)
        logger.error("selenium DRIVER CALL ERROR: " + str(e))
        drv_instance.quit()
      except Exception as e:
        logger.error("selenium DRIVER CALL ERROR: " + str(e))
        pass

  except Exception as e:
    try:
      logger.error("selenium ERROR: target_node: " + drv_instance.get_cookie('SERVERID')['value'] + "thread id: " + str(task) + " session_id: " + drv_instance.session_id)
      logger.error("selenium DRIVER INIT ERROR: " + str(e))
    except Exception as e:
      logger.error("selenium ERROR: " + str(e))
    pass
  else:
    drv_instance.quit()

def execPool(poolTasks,numTasks):
  pool = ThreadPool(processes=numTasks)
  pool.map(runTest, (n for n in poolTasks))
  pool.close()

def main():
  try:
    numTasks = int(sys.argv[1])
  except Exception as e:
    numTasks = 1

  # Causes chrome error when running if ssh is forwarding "X".
  os.environ['DISPLAY'] = ""

  logger.info("selenium INFO: Executing test threads")
  execPool(range(0,numTasks),numTasks)

if __name__ == "__main__":
  main()

