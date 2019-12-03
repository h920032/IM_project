全球人壽客服排班  
輸入輸出格式說明文件(CSR版)
=======================================

* （指定選項擇一）表示需輸入一個指定的群組名稱，目前可選用的選項如下：
	日子集合： all, Mon, Tue, Wed, Thr, Fri
	班別集合： all, morning, noon, night, other, 
（如果需要增加或修改，班別的部分請從Classes.csv修改；
　日期則是自動計算，必須修改程式才能修改日期組）
* 套件需求 
需先使用pip安裝：numpy、pandas
 商業套件： gurobipy （開發時使用的是免費學術版。商業使用有30天免費試用）
 python3已經包含（不須另外安裝）的套件：datetime、calendar

---
