# Customer service staff scheduling automation

# Documentation of Input and Output Formats 

*    **Package Requirements**  
Please install the following libraries using pip: numpy、pandas  
Business library: gurobipy (the free academic version is used in development. A 30-day free trial for business use)  
Packages included with Python3 and do not require additional installation：datetime、calendar   

*   **Explanation of Terms: "Select One From The Set"**  
This indicates that you need to input a specific group name. Current available options are as follows:  
  - Set of Days： all, Mon, Tue, Wed, Thr, Fri  
  - Set of Shifts： all, morning, noon, night, other  
(To add or modify, please make changes to the fix_classes.csv file for shifts; for dates, they are automatically calculated and program modifications are required to change the date sets.)

------
## Description of Input Format

### In the same directory as the main program  
*    **File Reading Path ( path.txt )**  
The file path for storing data (both relative and absolute paths are valid.)

### In the "per_month" folder  
> This folder stores items that need to be updated every month: employee data, year and month, forecast of incoming call volume, last month's roster, specific shift or vacation days.

*    **CSR Staff Data (per_month/Employee.csv)**

|Item Name|Representation|
|------------|--------| 
|Name_English|The staff's English name|
|Name_Chinese|The staff's Chinese name|  
|ID	|Employee ID|
|Senior|The staff's seniority (decimal greater than 0) |
|Position|The staff's position (a string of Chinese characters) |
|skill-|The skills the staff possesses (Each skill represents a column, and any column starting with "skill-" represents a skill. ADD 1 if the employee has this skill, 0 otherwise.) |
|night_perWeek|The maximum number of night shifts this staff can be scheduled for in a week   (Must be an integer, can be 0 but cannot be negative)|  
<img src="https://i.imgur.com/LbrxcOd.png" width = "600" align=center/>  

(The image above shows that CSR with ID 1430 is a manager with a seniority of 7 years, possesses the phone skill, and can work a maximum of one night shift per week.)

*    **The Year and Month of the Expected Roster (per_month/Date.csv)**  
 <img src="https://i.imgur.com/SgEYpYY.png" width = "300" align=center/>
  
*    **Incoming Call Volume Forecast (per_month/Need.csv)**  
The horizontal axis represents the workday date (do not include holidays);  
The vertical axis represents the time period (numbers are the starting time of the period, each period is half an hour).  
 <img src="https://i.imgur.com/rL4R5jM.png" width = "600" align=center/>
  
*    **Last Month's Roster (per_month/Schedule_2019_3.csv)**  
(This filename assumes last month was March 2019, actual usage will automatically calculate the filename based on the value in Date.csv)  
 <img src="https://i.imgur.com/gjNUPLo.png" width = "600" align=center/>

*    **Assigned Shifts (per_month/Assign.csv)**   
Use an independent data table to specify, each row from left to right are:
     1. CSR_ID: Employee ID  
     2. Date: Date (positive integer, not including month)
     3. Class: Shift classification in English (A3, CD... etc.)
Data demonstrative diagram:  
<img src="https://i.imgur.com/du3Gipc.png" width = "300" align=center/>    
(The image above shows that CSR 1430 is scheduled for Shift O on the 1st, and CSR CSCALYSSA is scheduled for Shift O on the 2nd.)


------
### In the "parameters" folder  
> This folder stores items that need to be modified occasionally: execution time limit, objective function's coefficient, various roster constraints.
>> Roster constraints include: Maximum number of shifts per person, minimum number of staff on duty, seniority ratio, skill requirement, maximum number of shifts for certain CSR

*    **Execution Time of the Program (parameters/time_limit.csv)**  
<img src="https://i.imgur.com/jGAGKMp.png" width = "120" align=center/>    timelimit   restricts the maximum running time of the main part of the program  
(Measured in seconds. The time taken to read and output data are not included in the calculation.)  

*    **Objective Function's Coefficient (parameters/weight_p.csv)**  
<img src="https://render.githubusercontent.com/render/math?math=P_1~P_4"> are numbers ≧ 0. 0 means to disregarding this condition, 100 means this condition has the same impact as the main condition (insufficient staff).

|Mathematical Variable Name |Variable Meaning|Input Format|
| -------- | -------- | -------- |
|<img src="https://render.githubusercontent.com/render/math?math=P_1">|Importance of surplus staffing|Number|
|<img src="https://render.githubusercontent.com/render/math?math=P_2">|Importance of equality in the number of night shifts per CSR|Number|
|<img src="https://render.githubusercontent.com/render/math?math=P_3">|Importance of lunch break consistency per day in a week per CSR|Number|
|<img src="https://render.githubusercontent.com/render/math?math=P_4">|Importance of equality in the number of afternoon shifts per CSR|Number|

Demonstrative Dataset:  
<img src="https://i.imgur.com/Ld0C7Gr.png" width = "150" align=center/>
  
A brief statistic of the average weighting of some months:
(The image below from left to right respectively represents: month, number of shortage staff, number of surplus staff, number of night shifts per CSR, lunch breaks, number of afternoon shifts per CSR)  
<img src="https://i.imgur.com/cf9vInO.png" width = "600" align=center/>  
The 10th row of the image shows the average value of the five numbers, and uses the number of shortage staff as a reference point to calculate the relative values of the remaining columns. This can indicate how to adjust the weighting values P1 to P4.
For example: if you want the weighting of surplus staff (61) to be as important as the number of shortage staff (1), then the weighting of P1 related to the surplus staff number should be increased by 61/1 = 61 times.

*    **The Maximum Times a Specific Shift can be Scheduled for Each CSR in a Month (parameters/class_upperlimit.csv)**  
Use an independent data table to specify, each row from left to right are:  
    1. Class： Shift classification (For instance: M1, A2 …etc.)
    2. Limit： The maximum times this shift can be scheduled in a month (The maximum times a CSR can be scheduled for this shift in a month.)
Demonstrative Diagram of Data：
<img src="https://i.imgur.com/LYDfEaJ.png" width = "250" align=center/>  
(The image above shows that each CSR can be scheduled for Shift M1 at the most 2 times in a month.)

*    **Minimum Number of CSR Above a Certain Position on Specified Days and Shifts (parameters/lower_limit.csv)**  
Use an independent data table to specify, each row from left to right are:  
    1. Date： Date (Positive integer: from the 1st to the last day of the month. Must be a workday.)
    2. Classes： Shift Group (Select one from the set of shifts, for example all, night.)
    3. Position： Position in Chinese characters (When there's no constraint, "任意" can be filled.)
    4. Need： Minimum required number of staff（Positive integer）
  
Demonstrative Diagram of Data：    
<img src="https://i.imgur.com/OsMVuTQ.png" width = "350" align=center/>    
(The first row in the image shows that on the 1st, during the night shift, there must at least be 1 manager or higher level manager on duty.)

*    **During Specified Days and Shifts, the Staff Above Specified Seniority Levels Must Account for More Than a Specific Ratio (parameters/senior.csv)**  
Use an independent data table to specify, each row from left to right are:  
    1. Dates：Date (Select one from the set of Dates, for example all,Mon)
    2. Classes：shift (Select one from the set of Shifts, for example all,night.)
    3. Ratio：Minimum Ratio (a number between 0 and 1, 0 and 1 are both acceptable.)
    4. Senior：Required Seniority (Number, decimal numbers accepted.)  

Demonstrative Diagram of Data：
<img src="https://i.imgur.com/RFGD6lw.png" width = "400" align=center/>  
(The image shows that on Monday night shift, those with over 1.5 years seniority must account for 45%; on Wednesday morning shift, those with over 1 year seniority must account for 55%.)

*    **The Number of Staff Required for a Specific Shift Each Day, and the Staff Must Possess the Corresponding Skill  (parameters/skill_class_limit.csv)**
Use an independent data table to specify, each row from left
