import click
import time
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


@click.command()
@click.option('--step','-s',type=(int,int),help='Define a mashing step as <TIME TEMPERATURE> (units: minutes and Celsius)',multiple=True)
def mash(step):
    print "An overview of the defined mashing profile:"
    # loop over given mashing steps
    for itr in range(len(step)):
        mins,temp=step[itr]
        print " Step %d: %d minutes in %d C" % (itr+1,mins,temp)
    print "NOTE! Please take into account the heating latency when defining the profile."
    if click.confirm('Do you wish to continue with the given mashing profile?'):
        print ">> Mashing begins"
    else:
        print "MASHING ABORTED!"

def valve(status):
    # set valve status

    # check that new and current state differ
    if status==valve_status:
        warn("0001: Tried to re-set current valve status. Doing nothing.")
        return

    if status==OPEN:
        # open valve TODO
        print ">> Opening valve ..."
        # wait 5 seconds for the valve to open
        time.sleep(5)
        # set new valve status flag
        valve_status=OPEN
    elif status==CLOSED:
        # close valve TODO
        print ">> Closing valve ..."
        # wait 5 seconds
        time.sleep(5)
        # set new status
        valve_status=CLOSED
    else:
        warn("0002: Tried to call 'valve' with wrong status code. Doing nothing.")
        return

def pump(status):
    # set pump status

    # check that new and current state differ
    if status==pump_status:
        warn("0003: Tried to re-set current pump status. Doing nothing.")
        return

    if status==ON:
        if valve_status==CLOSED:
            warn("0004: Tried to start pump with valve closed. Doing nothing.")
            return

        # start pump TODO
        print ">> Starting pump ..."
        # wait 1 second
        time.sleep(1)
        # set new pump status flag
        pump_status=ON
    elif status==OFF:
        # stop pump TODO
        print ">> Stopping pump ..."
        # wait 1 second
        time.sleep(1)
        # set new status
        pump_status=OFF
    else:
        warn("0005: Tried to call 'pump' with wrong status code. Doing nothing.")
        return

def heater(status):
    # set heater element status

    # check that new and current state differ
    if status==heater_status:
        warn("0006: Tried to re-set current heater status. Doing nothing.")
        return

    if status==ON:
        # fire heater relay TODO
        print ">> Turning on heater element ..."
        # set new status
        heater_status=ON
    elif status==OFF:
        print ">> Turning off heater element ..."
        heater_status=OFF
    else:
        warn("0007: Tried to call 'heater' with wrong status code. Doing nothing.")
        return

if __name__=='__main__':
    mash()
