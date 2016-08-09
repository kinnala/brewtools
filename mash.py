import click
import time
import sys
import os
from warnings import warn

# constants for states
OPEN=0
CLOSED=1
ON=2
OFF=3

# default state
valve_status=CLOSED
pump_status=OFF
heater_status=OFF

def printlogo():
    print """
                                     ``````          
                             `..........--`         
           `--....```````   ....````.....-`         
           `-............`  `..........-:++         
           ---.....```...`  -+//::/:://+hmd/`````   
          :hhs/:::------:.  `hyos+/:://+shyh.   `.  
    `.` `.ydmh+/////+oosy`   yyhs+/:://+ooo/      ` 
   `.     oooo+:/::/ooyyh    /dyss+///+++oss      ` 
   `      +o++++///+syhho    .yh+////:///ydd`     ` 
  ``      hds+/+/://ooyh:     ss++/::::/+syh-   ``  
   ``    .hyy+/:::::/+yy`     +yys+/::+/++sss.```   
    ``` `/yyo+//:::++oys      :dhyso///+oooyh:      
       `-hso+o+/:/+oyhh+      .ddo++///////+y/      
        -hy++++//++oshd:       so+/+o+////:/+`      
        -y+/+:-:://:+yy.       .:::.`````           
          ...--:::/++o/                             
    ______                 _____           _     
    | ___ \               |_   _|         | |    
    | |_/ /_ __ _____      _| | ___   ___ | |___ 
    | ___ \ '__/ _ \ \ /\ / / |/ _ \ / _ \| / __|
    | |_/ / | |  __/\ V  V /| | (_) | (_) | \__ \\
    \____/|_|  \___| \_/\_/ \_/\___/ \___/|_|___/
                                             
           PC-ASSISTED BREWING SINCE 2016  
        """

@click.command()
@click.option('--step','-s',type=(int,int),help='Define a mashing step as <TIME TEMPERATURE> (units: minutes and Celsius)',multiple=True)
def mash(step):
    print "An overview of the defined mashing profile:"
    # loop over given mashing steps
    for itr in range(len(step)):
        mins,temp=step[itr]
        if temp>0:
            print " Step %d: %d minutes in %d C" % (itr+1,mins,temp)
        else:
            if mins>0:
                print " Step %d: pause of %d minutes" % (itr+1,mins)
            else:
                print " Step %d: pause until user confirmation" % (itr+1)

    print "NOTE! Please take into account the heating latency when defining the profile."
    if click.confirm('Do you wish to continue with the given mashing profile?'):
        print "Starting the mash."
        valve(OPEN)
        pump(ON)
        for itr in range(len(step)):
            mins,temp=step[itr]
            if temp>0:
                print "Beginning step no %d: %d minutes in %d C" % (itr+1,mins,temp)
                runstep_keep(mins,temp)
            else:
                if mins>0:
                    print "Beginning step no %d: pause for %d minutes" % (itr+1,mins)
                    runstep_pause(mins)
                else:
                    print "Beginning step no %d: pause until user confirmation" % (itr+1)
                    runstep_pause_user()
                    
        pump(OFF)
        valve(CLOSED)
    else:
        print "MASHING ABORTED!"

# <hardware specific routines>

def hardware_open_valve():
    print ">> Opening valve"
    time.sleep(5)

def hardware_close_valve():
    print ">> Closing valve"
    time.sleep(5)

def hardware_start_pump():
    print ">> Starting pump"
    time.sleep(1)

def hardware_stop_pump():
    print ">> Stopping pump"
    time.sleep(1)

def hardware_start_heater():
    print ">> Starting heater element"

def hardware_stop_heater():
    print ">> Stopping heater element"

# </hardware specific routines>

def draw_bar(p,remaining,width=40):
    bar="["+"#"*int(p*width)+"-"*(width-int(p*width))+"] "+str(int(remaining/60.))+"m "+str(int(remaining%60))+"s"+" "*10
    sys.stdout.write(bar+"\b"*len(bar))
    sys.stdout.flush()

def runstep_keep(mins,temp):
    seconds=mins*60
    inittime=time.time()
    endtime=inittime+seconds
    while True:
        if endtime-time.time()<0:
            # quit step
            break
        # TODO heating cycle
        draw_bar((time.time()-float(inittime))/float(seconds),float(endtime)-time.time())
        time.sleep(1)
    sys.stdout.write(" "*50)
    sys.stdout.write("\b"*50)
    sys.stdout.flush()

def runstep_pause(mins):
    # shut down circulation
    pump(OFF)
    valve(CLOSED)
    # perform pause
    seconds=mins*60
    inittime=time.time()
    endtime=inittime+seconds
    while True:
        if endtime-time.time()<0:
            # quit step
            break
        draw_bar((time.time()-float(inittime))/float(seconds),float(endtime)-time.time())
        time.sleep(1)
    sys.stdout.write(" "*50)
    sys.stdout.write("\b"*50)
    sys.stdout.flush()
    # start circulation
    valve(OPEN)
    pump(ON)

def runstep_pause_user():
    # shut down circulation
    pump(OFF)
    valve(CLOSED)
    # pause
    while True:
        if click.confirm('Waiting for user interference. Do you want to continue mashing?'):
            break
        # TODO beep
    # start circulation
    valve(OPEN)
    pump(ON)

def valve(status):
    # set valve status
    global valve_status

    # check that new and current state differ
    if status==valve_status:
        warn("0001: Tried to re-set current valve status. Doing nothing.")
        return

    if status==OPEN:
        # open the valve using low-level routine
        hardware_open_valve()
        # set new valve status flag
        valve_status=OPEN
    elif status==CLOSED:
        # close valve
        hardware_close_valve()
        # set new status
        valve_status=CLOSED
    else:
        warn("0002: Tried to call 'valve' with wrong status code. Doing nothing.")
        return

def pump(status):
    # set pump status
    global pump_status
    global valve_status

    # check that new and current state differ
    if status==pump_status:
        warn("0003: Tried to re-set current pump status. Doing nothing.")
        return

    if status==ON:
        if valve_status==CLOSED:
            warn("0004: Tried to start pump with valve closed. Doing nothing.")
            return

        # start pump
        hardware_start_pump()
        # set new pump status flag
        pump_status=ON
    elif status==OFF:
        # stop pump
        hardware_stop_pump()
        # set new status
        pump_status=OFF
    else:
        warn("0005: Tried to call 'pump' with wrong status code. Doing nothing.")
        return

def heater(status):
    # set heater element status
    global heater_status
    global pump_status
    global valve_status

    # check that new and current state differ
    if status==heater_status:
        warn("0006: Tried to re-set current heater status. Doing nothing.")
        return

    if status==ON:
        if valve_status==CLOSED:
            warn("0008: Tried to turn on heating element with valve closed. Doing nothing.")
            return
        if pump_status==OFF:
            warn("0009: Tried to turn on heating element with pump off. Doing nothing.")
            return
        # fire heater relay
        hardware_start_heater()
        # set new status
        heater_status=ON
    elif status==OFF:
        hardware_stop_heater()
        heater_status=OFF
    else:
        warn("0007: Tried to call 'heater' with wrong status code. Doing nothing.")
        return

if __name__=='__main__':
    os.system('setterm -cursor off')
    printlogo()
    mash()
    os.system('setterm -cursor on')
