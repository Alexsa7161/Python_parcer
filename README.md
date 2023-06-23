# Python_parcer
site parsing https://cbr.ru , data processing (working with files) and exporting dataframes to the postgres database and to email.  
parcer_1 - parcer.  
downloaded_dates.json - date of last launch.  
PAGES.json - sites for parcing.  
2023-06-23 - data saved on this date.  
distibution_to_INN.sql - sql-script for generating data in the form of:  
<pre>
  INN          KPK  ... NPF   SSD  
7604370744      0        1     0
3906098008      1        0     0  
9729348321      0        0     1
...            ...      ...   ...  
<pre>
Data_showcase.sql - sql-script for generating data in the form of:  
<pre>
  BIC          PrntBIC   Flag_Col   Bank_INN  
215000042     044525985     1       450000464
205000024       null        0       450000938  
044525677     043469751     1       630000009
   ...           ...       ...         ... 
<pre>  
AND: auditing for changes in the "BIC_sprav" table - recording the date-time, type of change and data (current or forgotten)
