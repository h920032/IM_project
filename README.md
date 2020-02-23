#  全球人壽客服排班  輸入輸出格式說明文件

*    **套件需求**  
需先使用pip安裝：numpy、pandas  
商業套件：gurobipy (開發時使用的是免費學術版。商業使用有30天免費試用)  
python3已經包含(不須另外安裝)的套件：datetime、calendar   

*   **用語解釋：「集合中擇一」**  
這表示需輸入一個指定的群組名稱，目前可選用的選項如下：  
日子集合： all, Mon, Tue, Wed, Thr, Fri  
班別集合： all, morning, noon, night, other  
(如果需要增加或修改，班別的部分請從fix_classes.csv修改；日期則是自動計算，必須修改程式才能修改日期組)

------
## 輸入格式說明
### 與主程式相同資料夾  
*    **讀檔路徑 ( path.txt )**  
以txt檔存取資料路徑（相對路徑或絕對路徑皆可）

### per_month 資料夾
> 存放必須每月更新的項目：員工資料、年份與月份、進線量預測、上個月的班表、指定班別或休假

*    **CSR員工資料表 (per_month/Employee.csv)**
 
|項目名稱|代表的意義|
|------------|--------| 
|Name_English|員工的英文名字|
|Name_Chinese|員工的中文名字|  
|ID	|員工id|
|Senior|此員工的年資 (大於0的小數) |
|Position|此員工的職位 (中文字串) |
|skill-|此員工擁有的技能 (每個技能一列，以 skill- 開頭的列皆是。需要新增技能時請一併新增員工技能列) (1表示員工有此技能，0為沒有) |
|night_perWeek|此員工一週最多能排的晚班次數  (整數，可以為0但不能為負數)|  
<img src="https://i.imgur.com/LbrxcOd.png" width = "600" align=center/>  

(上圖顯示，ID為1430的CSR是年資7年的主任，擁有phone技能，每周最多排一次晚班)


*    **預計要排班表之年與月份 (per_month/Date.csv)**  
 <img src="https://i.imgur.com/SgEYpYY.png" width = "300" align=center/>
  
*    **進線人力需求表 (per_month/Need.csv)**  
橫軸為工作日日期 (假日請勿放入此表)；  
縱軸為時段 (數字為時段開始的時間，每個時段為半小時)。  
 <img src="https://i.imgur.com/rL4R5jM.png" width = "600" align=center/>
  
*    **上個月的班表結果 (per_month/Schedule_2019_3.csv)**  
(此檔名假設上個月為2019的3月份，實際使用時會根據Date.csv的值自動算出檔名應為何)  
 <img src="https://i.imgur.com/gjNUPLo.png" width = "600" align=center/>

*    **指定班別 (per_month/Assign.csv)**   
透過獨立的表格來指定，表格中每一橫列左到右依序是：
       1. CSR_ID： 員工ID  
       2. Date：   日期（正整數，不含月份）
       3. Class：  班別英文代號（A3、CD...等等）
資料示意圖：  
<img src="https://i.imgur.com/du3Gipc.png" width = "300" align=center/>    
（上圖中，CSR 1430於1號安排O班別，CSR CSCALYSSA於2號安排O班別）


------
### parameters 資料夾
> 存放偶爾需要修改的項目：執行時間限制、目標式係數、各種排班限制式
>> 排班限制包含：特定班每人值班次數上限、值班人數下限、年資占比、技能要求、特定CSR值特定班次數上限

*    **程式執行時間 (parameters/time_limit.csv)**  
<img src="https://i.imgur.com/jGAGKMp.png" width = "120" align=center/>    timelimit   限制程式主要部份的最長執行時間  
（以秒計算，讀取、輸出資料的時間皆不列入計算）  

*    **目標式係數 (parameters/weight_p.csv)**  
<img src="https://render.githubusercontent.com/render/math?math=P_1~P_4"> 皆為≧0的數字。  0為無視此條件，100為和主要條件（缺工數）有同樣影響力

|數學變數名稱|變數意涵|輸入格式|
| -------- | -------- | -------- |
|<img src="https://render.githubusercontent.com/render/math?math=P_1">|冗員多寡的重要程度|數字|
|<img src="https://render.githubusercontent.com/render/math?math=P_2">|每位CSR排晚班次數公平性的重要程度|數字|
|<img src="https://render.githubusercontent.com/render/math?math=P_3">|每位CSR每週內每天午休時間一致性的重要程度|數字|
|<img src="https://render.githubusercontent.com/render/math?math=P_4">|每位CSR排午班次數公平性的重要程度|數字|

資料示意圖:  
<img src="https://i.imgur.com/Ld0C7Gr.png" width = "150" align=center/>
  
部分月份的計算權重示意圖 :  
( 下圖由左至右分別為月份、缺工人數、冗員人數、每位CSR的晚班次數、午休、每位CSR的午班次數 )  
<img src="https://i.imgur.com/cf9vInO.png" width = "600" align=center/>  
由第10列可得知五個數值的平均值，並且以缺工人數當成參考點來換算其餘欄位的相對數值，以此來得知該如何調P1到P4的權重數值。  
例如 : 若想要讓權重為61的冗員人數變得與權重1的缺工人數一樣重要，則將有關冗員人數權重的P1調大 61/1 = 61倍。

*    **CSR每人每月最多排多少次某特定班別 (parameters/class_upperlimit.csv)**  
透過獨立的表格來指定，表格中每一橫列左到右依序是：  
     1. Class： 班別代號（例如：M1, A2 …等）
     2. Limit： 每月值班次數上限（每位CSR一個月內最多排這麼多次此班別)
資料示意圖：
<img src=" https://i.imgur.com/LYDfEaJ.png" width = "250" align=center/>  
(上圖表示：每月每個CSR最多排M1班2次)

*    **於指定的日子與班別，指定職位以上之CSR須達人數下限 (parameters/lower_limit.csv)**  
透過獨立的表格來指定，表格中每一橫列左到右依序是：  
     1. Date： 日期（正整數：1至該月最後一天的日期。需為工作日）
     2. Classes： 班別集合（於班別集合中擇一，例如all,night)
     3. Position： 職位中文名稱（沒有限制時可填「任意」）
     4. Need： 最少需要多少人（正整數）   
 
資料示意圖：    
<img src="https://i.imgur.com/OsMVuTQ.png" width = "350" align=center/>    
（上圖第一行表示在1號的晚班，職位在主任以上的CSR至少要有1人值班）  


*    **於指定的日子與班別，達指定年資之CSR需占指定比例以上 (parameters/senior.csv)**  
透過獨立的表格來指定，表格中每一橫列左到右依序是：  
     1. Dates：日子（於日期集合中擇一，例如all,Mon)
     2. Classes：班別（於班別集合中擇一，例如all,night)
     3. Ratio：最少占多少比例（0~1之間的數字，包含0和1）
     4. Senior：指定的年資（數字，可以接受小數)  

資料示意圖：  
<img src="https://i.imgur.com/RFGD6lw.png" width = "400" align=center/>  
( 上圖顯示，星期一的晚班，1.5年年資以上者需達45%；星期三的早班，1年年資以上者需達55% )

*    **特定班別每天需幾人值班，且值班者需擁有對應的一項技能 (parameters/skill_class_limit.csv)**
透過獨立的表格來指定，表格中每一橫列左到右依序是：
     1. Class：班別英文代號 ( A3、CD...等)
     2. Need：每天需要幾人值此班別 (人數會正好符合，不會超過此數值)
     3. Skill：對應的技能的英文名稱 (和員工資料中的技能大小寫需相同，例如：chat, CD)
     4. Special：假期後的開工日是否需要特殊處理 (1為是，0為否)
     5. Special_need：假期後的開工日需要幾人值此班別（若Special填0，則本欄之數值不會被使用）  
資料示意圖：  
<img src="https://i.imgur.com/OUm94oY.png" width = "450" align=center/>   
(上圖顯示，M1班每天需1人，值班者必須有phone技能)  
(上圖顯示，OB班每天需1人，值班者必須有outbound技能；逢假日後的開工日，OB班須2人)  


*    **CSR員工排某班別的次數上限 (parameters/class_upperlimit.csv)**  
透過獨立的表格來指定，表格中每一橫列左到右依序是：
     1. Class：班別英文代號 ( A3、CD...等)  
     2. Limit：次數上限 ( 正整數 )    
資料示意圖：  
<img src="https://i.imgur.com/0K2PYPa.png" width = "350" align=center/>  
( 上圖顯示，2543這位CSR最多只能排兩次星期一的晚班，而2511這位CSR最多只能排兩次星期五的晚班 )  

------
### parameters/fixed 資料夾  
> 存放很少需要修改的項目：班別時間表、班別集合、午休時間表、技能班別對應表、職位表

*    **班別時間表 (parameters/fixed/fix_class_time.csv)**  
最左一欄是班別代號，上方的橫列表示時段(半小時為一個時段，數字表示時段幾點開始)  
中間為1表示此班別涵蓋此時段、0表示不涵蓋此時段  
![](https://i.imgur.com/TSi6eVt.png)  
(上圖中可看出O班為休假，因為O班不涵蓋任何時段)  
(上圖顯示，A2班從9:00上到5:30，中間在12:00 ~ 1:00午休)

*    **班別集合表 (parameters/fixed/fix_classes.csv)**  
第一欄是班別集合的名稱，隨後的項目是此集合所涵蓋的班別  
![](https://i.imgur.com/YF0Tzwj.png)  
(上圖中morning集合為早班，包含A2,A3,A4,A5,MS,AS六個班別)  
(not_assigned集合指沒有在Assign.csv指定就不能排的班別，包含O,MA,AS三種休假班)  

*    **班別的午休時間 (parameters/fixed/fix_resttime.csv)**  
第一欄為午休時段(午休皆一小時，數字為午休幾點開始)，隨後的項目為在該時段午休的班別  
<img src="https://i.imgur.com/9C8MLOf.png" width = "600" />  
(上圖顯示，第一個午休時段為11:30 ~ 12:30，N1與M1班別為此種午休方式)

*    **技能與班別的對應 (parameters/fixed/fix_skill_classes.csv)**
第一欄是技能的名稱，隨後的項目是必須有此技能才能值班的班別  
<img src="https://i.imgur.com/vycr4Wh.png" width = "600" />  
(上圖顯示，必須有chat技能，才能值C2,C3,C4這三個班別)  

*    **CSR的職位高低排名 (parameters/fixed/position.csv)**  
由左至右為職位的低到高  
<img src="https://i.imgur.com/MY3vbCu.png" width = "500" />  
(上圖中，職位低到高：約聘、專員、主任、襄理、副理)  




------
## 輸出格式說明
*    **排班結果**  
(週末顯示為"X")

<img src="https://i.imgur.com/i9uB9q4.png" width = "600" />  

*    **冗員與缺工人數**  

<img src="https://i.imgur.com/WXkMagX.png" width = "600" />  

*    **綜合資訊**  
包含班表、各員工的晚班次數與每周午休種類數、缺工統計表(包含人數統計、各時段與各日期百分比)  

|試算表名稱			|示意圖|
|------------------ | ---- |
|班表				|<img src="https://i.imgur.com/i9uB9q4.png " width="500"/>|
|缺工冗員表			|<img src="https://i.imgur.com/WXkMagX.png " width="500"/>|
|缺工人數			|<img src=" https://i.imgur.com/5v5ciC8.png " width="500"/>|
|每天缺工百分比		|<img src="https://i.imgur.com/shlrxEi.png " width="350"/>|
|各時段缺工百分比	|<img src="https://i.imgur.com/3HqyVJG.png " width="300"/>|
|午班、晚班次數		|<img src="https://i.imgur.com/sOXukIB.png " width="400"/>|
|每週休息時間		|<img src="https://i.imgur.com/Kza9KOZ.png " width="500"/>|
