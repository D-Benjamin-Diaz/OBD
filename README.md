# OBD SCAN - By Benjamin D

## Description
A Python based OBD scanner that runs on the Terminal featuring DTC code reading, Freeze Frame inspection,
Live Data Displan and Data Collection and CSV export of said collection for data analytics.

Initially, it pings all the sensors and data that can be collected to filter out what data does your car
make available to you. Then, it queries those commands only repeatedly for you to have access to your car's
computer (PCM) data live.

## Future Objectives
Make this project a standalone application that runs on desktop as a .exe instead of the terminal only. Featuring
graphs and data analytics for car diagnosis. Potentially, an LLM/AI trained to diagnose a car based on 
the collected data.

## Requirements
- OBD Library 
- Rich Package for Python

## Run Demo
You can run a demo using the following command: 
```cmd
python -m obdscan --demo
```

