HORIZON-JPL 0.1.8
==================
This Python API, is an effort towards opening NASA's PDS data sets to the public with a focus on
ease of access. Thus creating, NASA's JPL Horizons On-Line Ephemeris System API

Download the package from: https://pypi.python.org/pypi/HorizonJPL or from pip:
      ```
      pip install horizonjpl
      ```

Please note, this API is currently in development and things are subject to change in future versions.

Demo
------------------------------

To run the demo you just have to do the following steps in a terminal:
1. ```cd``` into demo directory
2. ```pip install -r requirements.txt``` to install dependancies
3. ```python demo.py``` to start the server
4. Now you can navigate to http://127.0.0.1:5000 to see the demo

Future Plans
------------------------------

Things yet to be implemented from HORIZON system:
 - Ephemeris and Trajectory calculations
 - Small Body advanced search
 - Convenience API calls

Creating a robust fault tolerant API is the number one goal. Included in this goal is various subgoals:
 - Easy to access/read documentation
 - Ultra fast response parsing
 - Utilize cache wherever makes the most sense without affecting the integridy of the data
 - Simple RESTful API

Background
------------------------------
From http://en.wikipedia.org/wiki/Ephemeris:
```
For scientific uses, a modern planetary ephemeris comprises software that generates positions of planets and often of
their satellites, asteroids, or comets, at virtually any time desired by the user.
```

External Documentation & Resources
------------------------------

- Explorer Demo - http://nasa.apphb.com
- Planetary Data System: http://pds.nasa.gov/
- Jet Propulsion Labs: http://www.jpl.nasa.gov/
- HORIZON User Manual: http://ssd.jpl.nasa.gov/?horizons_doc

Contributors
------------------------------
```
Matthew Mihok (@mattmattmatt)
Dexter Jagula (@djagula)
Siddarth Kalra (@SiddarthKalra)
Tiago Moreira (@Kamots)
```
