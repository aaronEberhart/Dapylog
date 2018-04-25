# Dapylog

--From .py file comment:

This python file can load a datalog 
program and deduce facts from it. The menu
that runs with any Dapylog instance 
will let you see the facts and rules the
program knows, run the reasoner, reset
the program, add a new fact/rule to the
database, remove a fact/rule, load a 
new file, save the program in a new file,
or quit the program. 

By default it will use the included 
file but you can specify your own. 
Since I didn't feel like writing a fancy 
parser, all input files must consist 
of the following types of 
single-line instructions:

--blank lines--</br>
nAryDatalogFact(these,are,individuals)</br>
bodyOfAnyLength(X,ind)^anyArity(X)->head(Z)</br>

Individuals and predicate names are words.
Variables are single capital letters.
Don't use single capital letters or blank
spaces for individual names!
Spaces other than blank lines could 
break the program.
Datalog comments don't work either. 
Maybe put them in the python file?
