%{
#include <stdio.h>
%}

%x RFNAME READING
			
%%

<READING>"```"		BEGIN(0);
<READING>.		putchar(*yytext);
"```{CDUMP}"[^\n]*\n	BEGIN(READING);
"```{DUMPTO "		BEGIN(RFNAME);
<RFNAME>[^}]+		fflush(stdout), freopen(yytext, "a", stdout);
<RFNAME>\}[^\n]*\n	BEGIN(READING);
.			;

%%
int yywrap(void) {return(1);}
int main(void) {
    while(yylex());
}
