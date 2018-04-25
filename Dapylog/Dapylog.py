'''
This python file can load a datalog 
program and deduce facts from it. The menu
that runs with any Dapylog instance 
will let you see the facts and rules the
program knows, run the reasoner, reset
the program, add a new fact/rule to the
database, remove a fact/rule, load a 
new file, or quit the program. 

By default it will use the included 
file but you can specify your own. 
Since I didn't feel like writing a fancy 
parser, all input files must consist 
of the following single-line instructions:

<<blank line>>
nAryDatalogFact(these,are,individuals)
bodyOfAnyLength(X,ind)^anyArity(X)->head(Z)

Individuals and predicate names are words.
Variables are single capital letters.
Don't use single capital letters or blank
spaces for individual names!
Spaces other than blank lines could 
break the program.
Datalog comments don't work either. 
Maybe put them in the python file?


Author: Aaron Eberhart
'''
import os,sys

class Program:

    def __init__(self, filename=None):
    
        self.facts = []
        self.rules = []
        self.factsGiven = 0
        self.rulesGiven = 0
        
        if filename:
            self.filename = filename
            self.readFile(filename)
        else:
            self.filename = os.path.dirname(os.path.realpath(__file__))+"/datalog.dl"
            self.defaultProgram()

    def readFile(self,filename):
        f = open(filename)
        lines = f.read().splitlines()
        f.close()
        self.sortLines(lines)  
        return True  
         
    def defaultProgram(self):
        self.readFile(self.filename)

    def sortLines(self,lines):
        for line in lines:
            parts = line.split("->")
            if len(parts) == 1 and parts[0] != '':
                self.addFact(parts[0])
            elif parts[0] != '':
                self.addRule(parts[0],parts[1])
        
    def parsePredicate(self,predicate):
        ground = True
        data = predicate.split("(")
        data[1] = (data[1].split(")"))[0].split(",")
        if data[1][0] == '': data[1] = []
        for term in data[1]:
            if len(term) == 1:
                ground = False
                break
        data.append(ground)
        data.append(True)
        return data
        
    def addFact(self, fact):
        fact = self.parsePredicate(fact)
        self.facts.append(fact)
        self.factsGiven += 1
    
    def addRule(self,body,head):
        b = body.split("^")
        terms = []
        for i in range(0,len(b)):
            terms.append(self.parsePredicate(b[i]))
        self.rules.append([self.parsePredicate(head),terms,True])
        self.rulesGiven+=1

    def display(self):
        display = "\nDatabase Facts:\n"
        for i in range(0,self.factsGiven):
            if self.facts[i][3]: display += self.predToStr(self.facts[i]) + "\n"
        display += "\nDatabase Rules:\n"
        for i in range(0,self.rulesGiven):
            if self.rules[i][2]: display += self.ruleToStr(self.rules[i])
        display += "\nNew Facts:\n"
        if len(self.facts) > self.factsGiven:
            for i in range(self.factsGiven,len(self.facts)):
                display += self.predToStr(self.facts[i]) + "\n"
        else:
            display+="\nNo new facts\n\n"
        display += "\nNew Rules:\n"
        if len(self.rules) > self.rulesGiven:
            for i in range(self.rulesGiven,len(self.rules)):
                display += self.ruleToStr(self.rules[i]) + "\n"
        else:
            display+="\nNo new rules\n\n"   
        print(display)
        
    def predToStr(self,pred):
        string = str(pred[0]) + "("
        num = 0
        for var in pred[1]:
        	    string += str(pred[1][num])
        	    num+=1
        	    if num < len(pred[1]): string += ","
        return string + ")"
    
    def ruleToStr(self,rule):
        string = ""
        num = 0
        for term in rule[1]:
            string += self.predToStr(rule[1][num])
            num+=1            
            string += " ^ " if num < len(rule[1]) else " -> "
        return string + self.predToStr(rule[0]) + "\n"
    
    def copyRule(self,rule):
        active = True if rule[2] else False
        return [self.copyPred(rule[0]),self.copyBody(rule[1]),active]
        
    def copyBody(self,body):
        newBody = []
        for pred in body:
            newBody.append(self.copyPred(pred))
        return newBody
    
    def copyPred(self,pred):
        string = (pred[0]+'.')[:-1]
        terms = []
        for i in range(0,len(pred[1])):
            terms.append((pred[1][i]+'.')[:-1])
        ground = True if pred[2] else False
        active = True if pred[3] else False
        return [string,terms,ground,active]   
               
    def termIsGround(self,term):
        if len(term) > 1: return True
        return False
            
class Reasoner:

    def __init__(self,program=None):
        self.program = program if program else Program()
        
    def newProgram(self,program):
        self.program = program
        
    def reason(self,show=False):
        self.show = show
        beginning = 0
        end = 1
        print("\nStarting Reasoner\n")
        while beginning != end:
            beginning = len(self.program.facts)
            self.testRules()
            end = len(self.program.facts)
        if self.show: print("Checked All Rules\nNothing New To Add") 
        print("Reasoner Done\n\n")

    def testRules(self):
        for rule in self.program.rules:
            if rule[2]:
                newRule = self.program.copyRule(rule)
                if self.show: print("Testing Rule:\n",self.program.ruleToStr(rule))
                self.testRule(newRule)
    
    def testRule(self,rule):
        for fact in self.program.facts: 
            if fact[3] and fact[0] == rule[1][0][0]:
                dic = {}
                newRule = self.substitute(rule,fact,dic,0) if not rule[1][0][2] else self.program.copyRule(rule)
                self.solveRule(newRule,dic)
                
    def substitute(self,rule,fact,dic,k):
         newBody = self.program.copyBody(rule[1]) 
         for i in range(0,len(newBody[k][1])):
             if newBody[k][1][i] in dic.keys() and dic[newBody[k][1][i]] == fact[1][i]:
                 continue
             elif newBody[k][1][i] not in dic.keys() and len(newBody[k][1][i]) == 1:
                 dic[newBody[k][1][i]] = fact[1][i]
             newBody[k][2] = True
         active = True if rule[2] else False
         newRule = [self.program.copyPred(rule[0]),newBody,active]
         return newRule
         
    def solveRule(self,rule,dic):
        if self.isSatisfied(rule[1],dic):
            self.addHead(rule[0],dic)
        else:
            self.tryNewSubstitutions(rule,dic)
     
    def nextSubstitutionIndex(self,body,var):
        for i in range(0,len(body)):
            newAtom = self.switchTerms(body[i],var)
            if not newAtom[2]:
                return body.index(body[i])
            elif newAtom[2] and self.isGround(newAtom[1]) and not self.isFact(newAtom):
                return -1*body.index(body[i])
        return False
      
    def isGround(self,terms):
        for item in terms:
            if len(item) == 1: 
                return False
        return True
    
    def isSatisfied(self,body,var):
        for atom in body:
            newAtom = self.switchTerms(atom,var)
            if not newAtom[2] or not self.isFact(newAtom):
                return False
        return True
              
    def tryNewSubstitutions(self,rule,var):
        i = self.nextSubstitutionIndex(rule[1],var)
        if i < 0: return False
        trial = rule[1][i]
        for fact in self.program.facts:
            if fact[3] and self.partialMatch(self.switchTerms(trial,var),fact):
                dic = dict(var)
                newRule = self.substitute(rule,fact,var,i)
                self.solveRule(newRule,var)
                var = dict(dic)

    def partialMatch(self,atom,fact):
        if not fact[3] or atom[0]!=fact[0]: return False
        for i in range(0,min(len(atom[1]),len(fact[1]))):
            if len(atom[1][i]) != 1 and atom[1][i] != fact[1][i]:
                return False
        return True
    
    def isFact(self,atom):
        return atom in [fact for fact in self.program.facts if fact[3]]

    def switchTerms(self,atom,var):
        newAtom = [(atom[0]+'.')[:-1]]
        terms = []
        for i in range(0,len(atom[1])):
            terms.append((var[atom[1][i]]+'.')[:-1] if atom[1][i] in var.keys() else (atom[1][i]+'.')[:-1])
        newAtom.append(terms)
        newAtom.append(True)
        newAtom.append(True if atom[3] else False)
        if not self.isFact(newAtom): newAtom[2] = False
        return newAtom
        
    def groundHead(self,atom,var):
        head = [(atom[0]+'.')[:-1]]
        terms = []
        for i in range(0,len(atom[1])):
            terms.append((var[atom[1][i]]+'.')[:-1])
        head.append(terms)
        head.append(True)
        head.append(True)
        return head

    def addHead(self,head,var):
        newFact = self.groundHead(head,var)
        if self.isFact(newFact): return True
        if self.show: print("Added:\t",self.program.predToStr(newFact),"\n")
        self.program.facts.append(newFact)
        return True
    
    def display(self):
        self.program.display()

class Dapylog:

    def __init__(self,reasoner=None):
        self.reasoner = reasoner if reasoner else Reasoner()
        self.factsAdded = 0
        self.analyzed = False
        self.showMenu()
        
    def showMenu(self):
        self.menuSwitch(self.intSafe(input("Choose one:\n\n1\tDisplay Current Database\n2\tRun Reasoner on Database\n3\tAdd Fact To Database\n4\tAdd Rule To Database\n5\tDelete Fact From Database\n6\tDelete Rule From Database\n7\tReset Database\n8\tLoad New File\n9\tSave Program to File\n10\tExit Program\n:")))

    def menuSwitch(self,option):
        if option == 1: self.display()
        elif option == 2: self.analyze()
        elif option == 3: self.addFact()
        elif option == 4: self.addRule()
        elif option == 5: self.delFact()
        elif option == 6: self.delRule()
        elif option == 7: self.resetDatabase()
        elif option == 8: self.loadNewFile()
        elif option == 9: self.saveFile()
        elif option == 10: quit()
        else: print("\nInvalid Input\nTry Again\n\n"); self.showMenu()
        
    def display(self):
        self.reasoner.display()
        self.showMenu()
        
    def analyze(self):
        if not self.analyzed: 
            steps = True if self.intSafe(input("\nShow Steps?\n1\tyes\nother\tno\n:")) == 1 else False
            self.reasoner.reason(steps)
            self.analyzed = True
        else: print("\nCurrent database has already been analyzed.\n")
        self.showMenu()
    
    def resetDatabase(self):
        facts = self.reasoner.program.facts
        original = self.reasoner.program.factsGiven
        while len(facts) > original: del facts[len(facts)-1]
        self.analyzed = False
        for fact in self.reasoner.program.facts: fact[3] = True
        for rule in self.reasoner.program.rules: rule[2] = True
        print("\nDatabase Reset To Initial State\n")
        self.showMenu()
    
    
    def addFact(self):
        newFact = True if self.intSafe(input("\nAdd new fact or re-add deleted fact?\n1\tnew\nother\told\n:")) == 1 else False
        if newFact: self.addNewFact()
        else: self.addOldFact()
        
    def addOldFact(self):
        facts = [fact for fact in self.reasoner.program.facts if not fact[3]]
        options = "\nAdd Which Fact?\n"
        for i in range(0,len(facts)):
            options+="{0}\t{1}\n".format(i+1,self.reasoner.program.predToStr(facts[i]))
        options+="other\tGo Back\n".format(len(facts)+1)
        print(options)
        choice = input("Choice\n:")
        if len(facts) > 0 and choice.isdigit() and self.intSafe(choice) < len(facts)+1: self.reasoner.program.facts[self.reasoner.program.facts.index(facts[self.intSafe(choice)-1])][3] = True
        self.showMenu()
    
    def addNewFact(self):
        fact = ""
        while len(fact) < 1: fact = input("\nFact Name:\t")
        ground = True
        arity = ""
        while not arity.isdigit(): arity = input("Fact arity:\t")
        i = 1
        terms = []
        while len(terms) < int(arity): 
            term = input("Term "+str(i)+":\t")
            if len(term) > 1: terms.append(term); i += 1
            else: print("Not an allowed individual")
        self.reasoner.program.facts.append([fact,terms,ground,True])
        self.analyzed = False
        print()
        self.showMenu()
    
    def addRule(self):
        newRule = True if self.intSafe(input("\nAdd new rule or re-add deleted rule?\n1\tnew\nother\told\n:")) == 1 else False
        if newRule: self.addNewRule()
        else: self.addOldRule()
        
    def addOldRule(self):
        rules = [rule for rule in self.reasoner.program.rules if not rule[2]]
        options = "\nAdd Which Rule?\n"
        for i in range(0,len(rules)):
            options+="{0}\t{1}\n".format(i+1,self.reasoner.program.ruleToStr(rules[i]))
        options+="other\tGo Back\n".format(len(rules)+1)
        print(options)
        choice = input("Choice\n:")
        if len(rules)>0 and choice.isdigit() and self.intSafe(choice)<len(rules)+1: self.reasoner.program.rules[self.reasoner.program.rules.index(rules[self.intSafe(choice)-1])][2] = True
        self.showMenu()
        
    def addNewRule(self):
        print("\nFirst add predicates in body")
        body = [self.makeRuleAtom()]
        while self.intSafe(input("\nAdd another predicate to body?\n1\tyes\nother\tno\n:")) == 1: body.append(self.makeRuleAtom());
        print("\nNow input predicate for head.")
        head = self.makeRuleAtom()
        self.reasoner.program.rules.append([head,body,True])
        print()
        self.showMenu()
    
    def makeRuleAtom(self):
        fact = ""
        while len(fact) < 1: fact = input("\nPredicate Name:\t\t")
        ground = True
        arity = ""
        while not arity.isdigit(): arity = input("Predicate arity:\t")
        i = 1
        terms = []
        while len(terms) < int(arity): 
            term = input("Term "+str(i)+":\t")
            if len(term) > 0: terms.append(term); i += 1
            else: print("Not an allowed individual")
        return [fact,terms,ground,True]
  
    def loadNewFile(self):
        try:
            fn = os.path.dirname(os.path.realpath(__file__))+'/'+input("\nEnter Filename\n:")
            self.reasoner.program = Program(fn)
            self.analyzed = False
            print("\nSuccess!\n")
        except:
            print("\nFile Error\n")
        finally:
            self.showMenu()
    
    def delFact(self):
        facts = [fact for fact in self.reasoner.program.facts if fact[3]]
        options = "\nDelete Which Fact?\n"
        for i in range(0,len(facts)):
            options+="{0}\t{1}\n".format(i+1,self.reasoner.program.predToStr(facts[i]))
        options+="other\tGo Back\n".format(len(facts)+1)
        print(options)
        choice = input("Choice\n:")
        if len(facts) > 0 and choice.isdigit() and self.intSafe(choice) < len(facts)+1: self.reasoner.program.facts[self.reasoner.program.facts.index(facts[self.intSafe(choice)-1])][3] = False
        self.showMenu()
    
    def delRule(self):
        rules = [rule for rule in self.reasoner.program.rules if rule[2]]
        options = "\nDelete Which Rule?\n"
        for i in range(0,len(rules)):
            options+="{0}\t{1}\n".format(i+1,self.reasoner.program.ruleToStr(rules[i]))
        options+="other\tGo Back\n".format(len(rules)+1)
        print(options)
        choice = input("Choice\n:")
        if len(rules)>0 and choice.isdigit() and self.intSafe(choice)<len(rules)+1: self.reasoner.program.rules[self.reasoner.program.rules.index(rules[self.intSafe(choice)-1])][2] = False
        self.showMenu()
        
    def saveFile(self):
        thisDirectory = os.path.dirname(os.path.realpath(__file__))+"/"
        result = ""
        if self.reasoner.program.filename == thisDirectory+"datalog.dl":
            if self.intSafe(input("\nSave new file?\n1\tnew file\nother\tgo back\n:")) == 1: result = self.saveNewFile(thisDirectory)
        else:
            option = self.intSafe(input("\nSave new file or overwrite current file?\n1\tnew file\n2\toverwrite file\nother\tgo back\n:"))
            if option == 1: result = self.saveNewFile(thisDirectory)
            elif option == 2: result = self.writeFile(self.reasoner.program.filename)
        print(result)
        self.showMenu()
    
    def saveNewFile(self,here):
        filename = here+input("\nInput new file name\n:")
        while filename == here+"datalog.dl" or filename == here+"Dapylog.py":
            filename = here+input("\nCannot overwrite program file\nInput new file name\n:")
        if os.path.isfile(filename) and self.intSafe(input("\nThat file already exists.\nSure you want to overwrite?\n1\tyes\nother\tno\n:")) != 1: print();self.showMenu()
        return self.writeFile(filename)
            
    def writeFile(self,filename):
        try:
            f = open(filename, 'w+')
            for fact in self.reasoner.program.facts:
                f.write(self.reasoner.program.predToStr(fact)+"\n")
            f.write("\n")
            for rule in self.reasoner.program.rules:
                for i in range(0,len(rule[1])):
                    f.write(self.reasoner.program.predToStr(rule[1][i])+("^" if i < len(rule[1])-1 else "->"))
                f.write(self.reasoner.program.predToStr(rule[0])+"\n")
            f.close()
            return "\nSuccess!\n"
        except:
            return "\nFile error\n"
         
    def intSafe(self,input):
        try:
            num = int(input)
            return num
        except:
            return input
        

dpl = Dapylog()

