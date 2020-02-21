#  全球人壽客服排班  輸入輸出格式說明文件(CSR版)
*   (指定選項擇一)表示需輸入一個指定的群組名稱，目前可選用的選項如下：
日子集合： all, Mon, Tue, Wed, Thr, Fri
班別集合： all, morning, noon, night, other, 
(如果需要增加或修改，班別的部分請從fix_classes.csv修改；日期則是自動計算，必須修改程式才能修改日期組)

*    套件需求
需先使用pip安裝：numpy、pandas
商業套件： gurobipy (開發時使用的是免費學術版。商業使用有30天免費試用)
python3已經包含(不須另外安裝)的套件：datetime、calendar

---

## 輸入資料格式說明
*    CSR員工資料表 (data/per_month/Employee.csv)
欄位: 英文名字、中文名字、員工id、員工年資、員工職位、員工技能(1為有，0為沒有)、員工一週能排的晚班次數、員工上月斷頭周晚班次數、員工上月末日週五是否晚班(1為有，0為沒有)
![](https://i.imgur.com/O1NvcKc.png)

*    預計要排班表之年與月份 (data/per_month/Date.csv)
![](https://i.imgur.com/SgEYpYY.png)

*    進線人力需求表 (data/per_month/Need.csv)
![](https://i.imgur.com/rL4R5jM.png)

*    上個月的班表結果 (data/per_month/Schedule_2019_3.csv)
(假設上個月的班表為2019的3月份班表)
![](https://i.imgur.com/gjNUPLo.png)

*    班別時間表 (data/parameters/fixed/fix_class_time.csv)
列: 班別代號 / 行: 涵蓋時段
![](https://i.imgur.com/TSi6eVt.png)

*    班別集合表 (data/parameters/fixed/fix_classes.csv)
第一項是班別集合名稱，隨後的項目是所涵蓋的班別代號
![](https://i.imgur.com/YF0Tzwj.png)

*    班別的午休時間 (data/parameters/fixed/fix_resttime.csv)
第一欄為午休時段，隨後的項目為在該時段午休的班別
![](https://i.imgur.com/9C8MLOf.png)

*    CSR的職位高低排名 (data/parameters/fixed/position.csv)
由左至右為職位的低到高
![](https://i.imgur.com/MY3vbCu.png)

## 可調整參數說明
*    程式執行時間 (data/parameters/time_limit.csv)
![](https://i.imgur.com/jGAGKMp.png =150x100) timelimit   限制程式最長執行時間（以秒計算）

*    目標式係數 (data/parameters/weight_p.csv)
$P_{1\sim4}$ 皆為≧0的數字。 0為無視此條件，100為和主要條件（缺工數）有同樣影響一
（這裡程式需要多加個常數，讓每個可變動項的影響力相同）



|數學變數名稱|變數意涵|輸入格式|
| -------- | -------- | -------- |
|$P_1$|冗員多寡的重要程度|數字|
|$P_2$|每位CSR排晚班次數公平性的重要程度|數字|
|$P_3$|每位CSR每週內每天午休時間一致性的重要程度|數字|
|$P_4$|每位CSR排午班次數公平性的重要程度|數字|
