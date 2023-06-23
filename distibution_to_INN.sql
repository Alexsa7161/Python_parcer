do
$$
declare
	rec record;
begin
	delete from results;
	for rec in SELECT "INN", res FROM (
-- 		SELECT "INN", '1' "res"
-- 		FROM "fin_reestr_Исключенные ФО"
-- 		Union 
		SELECT "INN",'2' "res" 
		FROM "fin_reestr_КПК"
		Union 
		SELECT "INN", '3' "res"
		FROM "fin_reestr_Кредитные организации"
		Union 
		SELECT "INN", '5' "res"
		FROM "fin_reestr_МФО"
		Union 
		SELECT "INN", '6' "res"
		FROM "fin_reestr_КПК"
		Union 
		SELECT "INN", '7' "res"
		FROM "fin_reestr_Кредитные организации"
		Union 
		SELECT INN, '8' "res"
		FROM "reestr_licenzii"
		Union 
		SELECT "INN", '9' "res"
		FROM "reestr_lombardov"
) res
		WHERE "INN" IS NOT NULL
-- 		Order By 2 asc
	loop 
		if rec.res = '1' then insert into results(INN,"Iskluch FO") values (rec.Inn,'1');
		elsif rec.res = '2' then insert into results(inn,"KPK") values (rec."INN",'1');
		elsif rec.res = '3' then insert into results(INN,"Credit Org") values (rec."INN",'1');
		elsif rec.res = '5' then insert into results(INN,"MFO") values (rec."INN",'1');
		elsif rec.res = '6' then insert into results(INN,"NPF") values (rec."INN",'1');
		elsif rec.res = '7' then insert into results(INN,"SSD") values (rec."INN",'1');
		elsif rec.res = '8' then insert into results(INN,"Reestr licenzii") values (rec."INN",'1');
		elsif rec.res = '9' then insert into results(INN,"Reestr lombardov") values (rec."INN",'1');
		end if;
	end loop;
end;
-- create table results (Inn Varchar(10) Primary key,"KPK" Varchar(1),
-- 					  "Iskluch FO" Varchar(1),
-- 					  "Credit Org" Varchar(1),
-- 					 "Reestr lombardov" Varchar(1),
-- 					 "Reestr licenzii" Varchar(1),
-- 					 "MFO" Varchar(1),
-- 					 "NPF" Varchar(1),
-- 					 "SSD" Varchar(1))
$$
-- drop table results;