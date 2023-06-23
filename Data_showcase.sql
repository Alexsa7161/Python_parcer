-- CREATE TABLE IF NOT EXISTS BIC_audit_store (NameP VARCHAR(200), Rgn VARCHAR(10),DateIn DATE,PtType VARCHAR(10),Srvcs VARCHAR(10),XchType VARCHAR(10),UID VARCHAR(10),PrntBIC VARCHAR(10),AccountCBRBIC VARCHAR(10),
--  operation VARCHAR(64) NOT NULL,
--  modified_at   TIMESTAMP NOT NULL,
--  "Idx" Integer NOT NULL
-- );


create or replace procedure print_BIC_tree ()
language plpgsql
as $$
declare
	rec record;
	rec1 record;
	rec2 record;
BEGIN
	update "BIC_sprav_dop" set "AccountCBRBIC" = LPAD("AccountCBRBIC",9,'0');
	update "BIC_sprav" set "AccountCBRBIC" = LPAD("AccountCBRBIC",9,'0');
	update "credit_organization" set "BIC" = LPAD("BIC",9,'0');
	delete from "results_2";
	for rec1 in select * from "BIC_sprav"
	loop
		for rec2 in select * from "BIC_sprav_dop"
		loop
			if rec1."Idx" = rec2."Idx" and rec1 != rec2 then delete from "BIC_sprav" where "Idx" = rec1."Idx";
			insert into "BIC_sprav" VALUES (rec2."NameP", rec2."Rgn", rec2."DateIn", rec2."PtType", rec2."Srvcs", rec2."XchType", rec2."UID", rec2."PrntBIC", rec2."AccountCBRBIC",rec2."Idx");
			insert into BIC_audit_store VALUES (rec1."NameP", rec1."Rgn", rec1."DateIn", rec1."PtType", rec1."Srvcs", rec1."XchType", rec1."UID", rec1."PrntBIC", rec1."AccountCBRBIC", 'Delete', now(), rec1."Idx");
			insert into BIC_audit_store VALUES (rec2."NameP", rec2."Rgn", rec2."DateIn", rec2."PtType", rec2."Srvcs", rec2."XchType", rec2."UID", rec2."PrntBIC", rec2."AccountCBRBIC", 'Insert', now(),rec2."Idx");
			end if;
		end loop;
	end loop;
	for rec in SELECT "AccountCBRBIC", NULLIF("PrntBIC",' ') "Prnt", CASE WHEN "PrntBIC" = ' ' THEN 1 ELSE 0 END "Flag", "NameP", "ccode"
			   FROM "BIC_sprav" left join "credit_organization" on "BIC_sprav"."AccountCBRBIC" = "credit_organization"."BIC"
	loop
		if rec."NameP" LIKE '%УФК%' THEN rec."Prnt" = '999999999'; END IF;
		insert into results_2(BIC,PrntBIC,Flag_Col,bic_inn) values (rec."AccountCBRBIC",rec."Prnt", rec."Flag",rec."ccode");
	end loop;
	insert into results_2(BIC,PrntBIC,Flag_Col,bic_inn) values ('999999999','','1','');
end $$;


call print_BIC_tree();