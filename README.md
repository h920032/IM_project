#  全球人壽客服排班  輸入輸出格式說明文件(CSR版)
*   **(指定選項擇一)表示需輸入一個指定的群組名稱，目前可選用的選項如下：**
日子集合： all, Mon, Tue, Wed, Thr, Fri
班別集合： all, morning, noon, night, other, 
(如果需要增加或修改，班別的部分請從fix_classes.csv修改；日期則是自動計算，必須修改程式才能修改日期組)

*    **套件需求**
需先使用pip安裝：numpy、pandas
商業套件： gurobipy (開發時使用的是免費學術版。商業使用有30天免費試用)
python3已經包含(不須另外安裝)的套件：datetime、calendar

## 輸入資料格式說明
*    **CSR員工資料表 (data/per_month/Employee.csv)**
欄位: 英文名字、中文名字、員工id、員工年資、員工職位、員工技能(1為有，0為沒有)、員工一週能排的晚班次數、員工上月斷頭周晚班次數、員工上月末日週五是否晚班(1為有，0為沒有)

<img src="https://i.imgur.com/O1NvcKc.png" width = "600" align=center/>

*    **預計要排班表之年與月份 (data/per_month/Date.csv)**

<img src="https://i.imgur.com/SgEYpYY.png" width = "300" align=center/>

*    **進線人力需求表 (data/per_month/Need.csv)**

<img src="https://i.imgur.com/rL4R5jM.png" width = "600" align=center/>

*    **上個月的班表結果 (data/per_month/Schedule_2019_3.csv)**
(假設上個月的班表為2019的3月份班表)

<img src="https://i.imgur.com/gjNUPLo.png" width = "600" align=center/>

*    **班別時間表 (data/parameters/fixed/fix_class_time.csv)**
列: 班別代號 / 行: 涵蓋時段
![](https://i.imgur.com/TSi6eVt.png)

*    **班別集合表 (data/parameters/fixed/fix_classes.csv)**
第一項是班別集合名稱，隨後的項目是所涵蓋的班別代號
![](https://i.imgur.com/YF0Tzwj.png)

*    **班別的午休時間 (data/parameters/fixed/fix_resttime.csv)**
第一欄為午休時段，隨後的項目為在該時段午休的班別

<img src="https://i.imgur.com/9C8MLOf.png" width = "500" align=center/>

*    **CSR的職位高低排名 (data/parameters/fixed/position.csv)**
由左至右為職位的低到高

<img src="https://i.imgur.com/MY3vbCu.png" width = "500" align=center/>

## 可調整參數說明
*    **程式執行時間 (data/parameters/time_limit.csv)**

<img src="https://i.imgur.com/jGAGKMp.png" width = "120" align=center/> timelimit   限制程式最長執行時間（以秒計算）

*    **目標式係數 (data/parameters/weight_p.csv)**
$P_{1\sim4}$ 皆為≧0的數字。 0為無視此條件，100為和主要條件（缺工數）有同樣影響一
（這裡程式需要多加個常數，讓每個可變動項的影響力相同）

|數學變數名稱|變數意涵|輸入格式|
| -------- | -------- | -------- |
|$P_1$|冗員多寡的重要程度|數字|
|$P_2$|每位CSR排晚班次數公平性的重要程度|數字|
|$P_3$|每位CSR每週內每天午休時間一致性的重要程度|數字|
|$P_4$|每位CSR排午班次數公平性的重要程度|數字|

資料示意圖:

<img src="https://i.imgur.com/Ld0C7Gr.png" width = "150" align=center/>

部分月份的計算權重示意圖 :
( 下圖由左至右分別為月份、缺工人數、冗員人數、每位CSR的晚班次數、午休、每位CSR的午班次數 )

<img src="https://i.imgur.com/cf9vInO.png" width = "600" align=center/>

由第10列可得知五個數值的平均值，並且以缺工人數當成參考點來換算其餘欄位的相對數值，以此來得知該如何調P1到P4的權重數值。
例如 : 若想要讓權重為61的冗員人數變得與權重1的缺工人數一樣重要，則將有關冗員人數權重的P1調大 61/1 = 61倍。

*    **指定班別 (data/per_month/Assign.csv)**
透過獨立的表格來指定，表格中每一橫列左到右依序是：
    1. 員工編號（英文名稱）
    2. 日期（正整數，不含月份）
    3. 班別英文代號（A3、CD...之類的）

資料示意圖：

<img src="https://i.imgur.com/du3Gipc.png" width = "300" align=center/>
( CSR 1430於1號安排O班別 )</br>
( CSR CSCALYSSA於2號安排O班別 )

*    **指定日子與班別之一般CSR員工或指定職位人數下限 (data/parameters/lower_limit.csv)**
透過獨立的表格來指定，表格中每一橫列左到右依序是：
    1. 日子（正整數: 1至該月最後一天的日期）
    2. 班別（指定選項擇一，例如all,night)
    3. 職位中文名稱（不限請填「任意」）
    4. 最少需要多少人（正整數）

資料示意圖：

<img src="https://i.imgur.com/0K2PYPa.png" width = "300" align=center/>
( 2543這位CSR最多只能排兩次星期一的晚班 )</br>
( 2511這位CSR最多只能排兩次星期五的晚班 )

*    **特定班別只需某項技能之排班限制 (data/parameters/skill_class_limit.csv)**
透過獨立的表格來指定，表格中每一橫列左到右依序是：
    1. 日子（指定選項擇一，例如all,Mon)
    2. 班別（指定選項擇一，例如all,night)
    3. 最少占多少比例（0~1之間的數字，包含0和1）
    4. 指定的年資（數字 )

資料示意圖：

<img src="https://i.imgur.com/RFGD6lw.png" width = "300" align=center/>
( 星期一的晚班，1.5年年資以上者需達45% )</br>
( 星期三的早班，1年年資以上者需達55% )

*    **CSR員工排某班別的次數上限 (data/parameters/class_upperlimit.csv)**
透過獨立的表格來指定，表格中每一橫列左到右依序是：
    1. 班別英文代號 ( A3、CD...之類的 )
    2. 次數上限 ( 正整數 )
    
資料示意圖：

<img src="https://i.imgur.com/9aGrpIa.png" width = "400" align=center/>
( 每位CSR最多只能排2次M1這個班別 )

*    **讀檔路徑 ( path.txt )**
以txt檔存取資料路徑

## 輸出格式說明
*    **排班結果**
(週末顯示為"X")

<img src="https://i.imgur.com/8U4rwKt.png" width = "600" align=center/>

*    **冗員與缺工人數**

<img src="https://i.imgur.com/gGc5onH.png" width = "600" align=center/>

*    **其他資訊**


| 員工排班表           |<img src="https://i.imgur.com/JMQIgtg.png" width = "400" align=center/>|
| -------------------- | ------------------------------------------ |
| 員工本月晚班次       | <img src="https://i.imgur.com/xrXRlL0.png" width = "150" align=center/> |
| 每個時段缺工百分比表 | <img src="https://i.imgur.com/3HqyVJG.png" width = "150" align=center/> |
| 每天缺工百分比表     | <img src="https://i.imgur.com/2rLJS2l.png" width = "150" align=center/> |
| 缺工人數表           |<img src="https://i.imgur.com/76ivr6g.png" width = "400" align=center/>|
|員工每週有哪幾種休息時間|<img src="https://i.imgur.com/MDHOuPG.png" width = "400" align=center/>|
