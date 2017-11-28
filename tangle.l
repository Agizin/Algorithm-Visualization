%{
#include <stdio.h>
%}

%x RFNAME READING
			
%%

<READING>\n"#algviz enddump"	BEGIN(0);
<READING>.			putchar(*yytext);
\n"#algviz cdump"[^\n]*\n       BEGIN(READING);
\n"#algviz dumpto"[ \t]+        BEGIN(RFNAME);
<RFNAME>[^\n]+			fflush(stdout), freopen(yytext, "a", stdout),\
				fprintf(stderr, "%s\n", yytext);
<RFNAME>\n			BEGIN(READING);
.				;

%%
int yywrap(void) {return(1);}
int main(void) {
    while(yylex());
}
