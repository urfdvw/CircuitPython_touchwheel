# Developer Memo
Here, I take some note about logics that are not obvious by code.

This project is not only to build a working device for password management,
it also aim to provide a framework for
"Sort of complex" devices with
similar hardware that runs
multiple mini apps,
and multiple background procedure.

# class dependency tree
- `App` (ABC): Apps with OLED UI
    - `BounceBall`: A game app
    - `Item`: App for typing password
    - `Menu` (ABC): Apps with list of text as menu
        - `Mainmenu`: App for main menu
        - `AccountList`: App for list accounts
- `Background_app` (ABC): Apps without UI
    - `FpsControl`
    - `FpsMonitor`

# File structure
All board specifications are in code.py.
Periferal drivers are in driver.py.
Time related tools are defined in timetrigger.py
Apps with UI are in Aplication.py
Background processes are in backgrounf.py

# Sound
- all sounds are just a brief beep (one frame) unless special usages
    - tictoc is used to avoid continuous sound
- sound is controlled by `self.freq`
    - it is going to control the buzzer for one frame
- press sound is only for indication (1000)
    - so in ui inpit
- release sound is when action taken (1200)
    - so in logic
- as sound is so different in every app
    - here we sacrifice the reusability
    - and let each app decide what soud they want

# Life cycle of application
The life cycle only contains 3 parts: receive, update, display.
This is designed for simple logic instead of complex procedures.
```
0 (device power on)
1 __init__
2 (wait)
3 reveive()
4 display()
5 (repeat frames)
6 | update()
7 | display()
8 update() (with exit signal)
9 (wait)
10 back to step 3 when called again
```
- reveive is viewed as the enter point of the app, usually
    - contains a enter sound
    - contains state initialization
- display is considered following a update step or receive step
    - Exception: update with exit operation does not have display step following

# Message transmission between apps
Messages are transferred by two ways:
- direct message
- broadcasting

direct message is used between two consequtive apps.
This should be used as much as possible.
It is convinent for apps helping each outher to finish a task in a relay.

broadcasting should only be used for states or inportant global message.
It can only be overwriten instead of removed.
us it wisely.

shift signal should and should only be used for app shifting signal.
usually
- 0 means no action
- -1 mean back
- 1 and above means other apps.

