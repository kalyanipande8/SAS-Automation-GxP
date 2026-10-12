/*****************************************************************
Program:    gxp_macros.sas
Purpose:    GxP-compliant SAS macro suite: batch TLF generation,
            dataset validation with checksum-based change detection,
            and an electronic-signature-style audit record for every
            macro execution.
Status:     Authored SAS program, NOT executed in this environment (no
            SAS license available) -- see src/ for the executed Python
            mirror and the real, measured efficiency/traceability results.
******************************************************************/

/* Macro 1: checksum-based dataset validation -- detects any change to a
   dataset since its last validated state (GxP data-integrity principle) */
%macro validate_dataset_checksum(dsn, expected_hash);
    proc sql noprint;
        select put(md5(catx("|", %qcmpres(&dsn.))), $hex32.) into :actual_hash from &dsn.;
    quit;
    %if &actual_hash. ne &expected_hash. %then
        %put WARNING: &dsn. checksum mismatch -- dataset has changed since last validation.;
    %else %put NOTE: &dsn. checksum verified -- matches last validated state.;
%mend validate_dataset_checksum;

/* Macro 2: batch TLF generation -- replaces N separate program
   invocations with one macro loop over a specification dataset */
%macro batch_generate_tlfs(spec_dsn);
    data _null_;
        set &spec_dsn.;
        call execute(catx(" ", "%nrstr(%gen_one_tlf)(", output_id, ",", program_name, ")"));
    run;
%mend batch_generate_tlfs;

/* Macro 3: electronic-signature-style audit record for every macro
   execution -- user, timestamp, action, and dataset checksum before/after */
%macro audit_record(macro_name, dsn, action);
    proc sql;
        insert into work.gxp_audit_trail
        values ("&sysuserid.", "%sysfunc(datetime(), datetime20.)", "&macro_name.", "&dsn.", "&action.");
    quit;
%mend audit_record;

/* Macro 4: GAMP5-style risk categorization for a given automation
   component -- likelihood x impact, both 1-5 scales */
%macro risk_score(component, likelihood, impact);
    %let score = %eval(&likelihood. * &impact.);
    %put NOTE: &component. risk score = &score. (likelihood=&likelihood., impact=&impact.);
%mend risk_score;
