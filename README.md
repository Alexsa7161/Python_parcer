# Python_parcer
site parsing https://cbr.ru , data processing (working with files) and exporting dataframes to the postgres database and to email.  
parcer_1 - parcer.  
downloaded_dates.json - date of last launch.  
PAGES.json - sites for parcing.  
2023-06-23 - data saved on this date.  
distibution_to_INN.sql - sql-script for generating data in the form of:  
<pre>
  INN          KPK ...  NPF   SSD  
7604370744      0        1     0
3906098008      1        0     0  
9729348321      0        0     1
...            ...      ...   ... 
<pre>
