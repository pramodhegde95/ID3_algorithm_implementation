import sys, csv
import math, random, copy


#entropy calculation
def calculateentropy(no_rows):
    initialent = 0.0
    #count number of 1's and 0's
    totalvalues = {}
    for row in no_rows:
        r = row[len(row) - 1]
        if r not in totalvalues:
            totalvalues[r] = 0
        totalvalues[r] =  totalvalues[r]+1
    for i in totalvalues.keys():
        initialent = initialent - float(totalvalues[i]) / len(no_rows) * math.log(float(totalvalues[i]) / len(no_rows),2) 
    return initialent

#gain calculation function
def calculategain(row,list1,list2,ent=calculateentropy):
    gainvalue = ent(row) - float(len(list1)) / len(row) * ent(list1) - (1 - float(len(list1)) / len(row)) * ent(list2)
    return gainvalue


#function to calculate the variance impurity of data set
def calculatevarience(no_rows):
     totaldata = len(no_rows)
     #count number of 1's and 0's
     totalvalues = {}
     for row in no_rows:
        r = row[len(row) - 1]
        if r not in totalvalues:
            totalvalues[r] = 0
        totalvalues[r] =  totalvalues[r]+1
     varience = (totalvalues['0'] * totalvalues['1']) / (totaldata * totaldata)#K0 * K1 / K^2
     return varience


#making list based on attribute value
def attributedevide(no_rows, column, value):
    val = None
    list1 = []
    list2 = []
    val = lambda r: r[column] == value
    for r in no_rows:
        if val(r):
          list1.append(r)
    for r in no_rows:
        if not val(r):
           list2.append(r)
    return (list1, list2)


#class to create the nodes of tree.
class decisionnode:
    def __init__(self, rightchild=None, leftchild=None, value=None, dicnry=None, col=-1):
        self.col = col
        self.rightchild = rightchild
        self.leftchild = leftchild
        self.value = value
        self.dicnry = dicnry

#build tree with entropy gain or varience
def buildtree(no_rows, var=calculateentropy):
    column = len(no_rows[0]) - 1 #last column
    bestgain = 0.0
    batt = None #attribute that is going to be next children
    bcolumn= None #to select best attribute for the node and not use it in subsequent iteration
    
    for c in range(0, column):

        valueatcol = {}#dictionary to store the count of true-true match with the target attribute
        for r in no_rows:
            valueatcol[r[c]] = 1 #check positive values
        for value in valueatcol.keys():
            (attlist1, attlist2) = attributedevide(no_rows, c, value)
            gain =calculategain(no_rows,attlist1,attlist2,var)
            if gain > bestgain: 
                bestgain = gain
                bcolumn = (c, value)
                batt = (attlist1, attlist2)

    # recursive calls
    if bestgain > 0:
        positiveatt = buildtree(batt[0])
        negativeatt = buildtree(batt[1])
        return decisionnode(rightchild=positiveatt, leftchild=negativeatt, value=bcolumn[1], col=bcolumn[0])
    else:
        return decisionnode(dicnry=keeptrackunique(no_rows))
    
#every attribute no. of 1's and 0's are stored
def keeptrackunique(no_rows):
    totalvalues = {}
    for row in no_rows:
        r = row[len(row) - 1]
        if r not in totalvalues:
            totalvalues[r] = 0
        totalvalues[r] =  totalvalues[r]+1#increment the value for the key
    return totalvalues

#print tree in required format
def printtree(tree, header_data, indent):
    if tree.dicnry != None:
        for key in tree.dicnry:
            print(str(key))
    else:
        print("")
        print(indent + str(header_data[tree.col]) + ' = ' + str(tree.value) + ' : ', end="")
        printtree(tree.rightchild, header_data, indent + '  |')

        print(indent + str(header_data[tree.col]) + ' = ' + str(int(tree.value) ^ 1) + ' : ', end="")#stop getting to newline
        printtree(tree.leftchild, header_data, indent + '  |')


#function to calculate the accuracy
def calculateaccuracy(rows, tree):
    correct_predictions = 0
    for row in rows:
        pred_val = groupvalues(row, tree)
        if row[-1] == pred_val:
            correct_predictions += 1
    accuracy = 100 * correct_predictions / len(rows)
    return accuracy


#group the data's of the tree formed from the given data
def groupvalues(value, tree):
    if tree.dicnry != None:#check the initial condition
        for key in tree.dicnry:
            pvalue = key
        return pvalue
    else:
        v = value[tree.col]
        if type(v)==int:
            if v >= tree.value:
                child = tree.rightchild
            else:
                child = tree.leftchild
        else:
            if v == tree.value:
                child = tree.rightchild
            else:
                child = tree.leftchild
        pvalue = groupvalues(value, child)
    return pvalue

#count whether the class belongs to 0's or 1's and
#calculate the sume of particular class
def classcount(tree, occu):
    if tree.dicnry != None:
        for key in tree.dicnry:
          occu[key] = occu[key] + tree.dicnry[key]
        return occu

    leftside = classcount(tree.rightchild, occu)
    rightside = classcount(tree.leftchild, leftside)
    return rightside

#replace subtree according to the pruning algorithm
def replaceNodes(copyt, rsubtree, subtreetr):
    if (copyt.dicnry != None):#intial condtiton check to see if tree contains any node
        return copyt
    if (copyt == rsubtree):
        copyt = subtreetr
        return copyt

    copyt.leftchild = replaceNodes(copyt.leftchild, rsubtree, subtreetr)
    copyt.rightchild = replaceNodes(copyt.rightchild, rsubtree, subtreetr)
    return copyt

def comparecount(fcount):#count and compare whether 0's are more or 1's
    if fcount['0'] > fcount['1']:
       fcount['0'] = fcount['0'] + fcount['1']
       del fcount['1']
       return fcount
    else:
       fcount['1'] = fcount['0'] + fcount['1']
       del fcount['0']
       return fcount
    

def treepruning(tree, l, k, data):
    storetree = None
    intialbest = tree#make the tree as best initially
    intialbestacc = calculateaccuracy(data, tree)
    for j in range(1, l):
        storetree = copy.deepcopy(tree)#to place the copy
        m = random.randint(1, k)
        for q in range(1, m):
            (nodes, icount) = nodesno({}, storetree, 0)
            if (icount > 0):
                p = random.randint(1, icount)
                subtree = nodes[p]
                valoccurence = {}#count the number of 0's and 1's...intialize it to zero
                valoccurence["0"] = 0
                valoccurence["1"] = 0
                fcount = classcount(subtree, valoccurence)
                comparecount(fcount)
                subtree = decisionnode(dicnry=fcount)
                storetree = replaceNodes(storetree, nodes[p], subtree)
        
        newaccuracy = calculateaccuracy(data, storetree)#accuracy calculation
        if (newaccuracy > intialbestacc):
            intialbestacc = newaccuracy
            intialbest = storetree
    return intialbest, intialbestacc


#count number of nodes
def nodesno(nodes, tree, count):
    if tree.dicnry != None:
        return nodes, count
    count = count + 1
    nodes[count] = tree
    (nodes, count) = nodesno(nodes, tree.rightchild, count)
    (nodes, count) = nodesno(nodes, tree.leftchild, count)
    return nodes, count

def main():
        #reading from the terminal
        arguments = sys.argv

        #Input must have 6 arguments l k files and "yes/no" to print
        if (len(arguments) < 6):
            print ("Error.. wrong input...Follow ReadMe file for instructions")
        else:
            l = int(arguments[1])
            k = int(arguments[2])
            training_set= str(arguments[3])
            validation_set = str(arguments[4])
            testing_set = str(arguments[5])
            printing = str(arguments[6]).lower()

            with open(training_set, "r") as csvfile:
                filereader = csv.reader(csvfile, delimiter=',')
                attributes = next(filereader)#read first line
                training_dataset = list(filereader)#remaining data

            # tree with gain heuristics
            treegain = buildtree(training_dataset, var=calculateentropy)
            if(printing == "yes"):
                print("")
                print("Decison Tree based on gain: ")
                printtree(treegain, attributes, '')


            with open(testing_set, "r") as csvfile:
                filereader = csv.reader(csvfile, delimiter=',')
                test_dataset = list(filereader)

            with open(validation_set, "r") as csvfile:
                filereader = csv.reader(csvfile, delimiter=',')
                validation_dataset = list(filereader)

            print("Accuracy of trining data Gain: ", calculateaccuracy(training_dataset, treegain))

            print("Accuracy of validation data Gain: ", calculateaccuracy(validation_dataset, treegain))

            print("Accuracy of test data Gain: ", calculateaccuracy(test_dataset, treegain))


            (prunedvalidationtree, acprunedvalidation) = treepruning(treegain, l, k,validation_dataset)
            print("     Pruned validation data accuracy GAIN HEURISTICS: ", acprunedvalidation)
            print(" ")
            (prunedtesttree, acprunedtest) = treepruning(treegain, l, k, test_dataset)
            
            if (printing == "yes"):
                print("     Pruned tree of test data for GAIN HEURISTICS : ")
                printtree(prunedtesttree, attributes, '')
                
            print(" ")
            print("     Pruned test data accuracy GAIN HEURISTICS: ", acprunedtest)


            valuesforl = [5, 8, 13, 15, 17, 19, 25, 29, 30, 45]
            valuesfork = [9, 15, 17, 20, 24, 26, 28, 29, 34, 40]
            
            print(" ")
            print("     Pruned test data accuracy with l and k GAIN HEURISTICS")

            for lvg, kvg in  zip(valuesforl, valuesfork):
                (prunedtesttree, acprunedtest) = treepruning(treegain, lvg, kvg,test_dataset)
                print("l = ", lvg)
                print("k = ", kvg)
                print("Accuracy=", acprunedtest)


            # tree on variance 
            treevarience = buildtree(training_dataset, var=calculatevarience)
            if (printing == "yes"):
                print(" ")
                print("Decision tree based on varience : ")
                printtree(treevarience, attributes, '')

            print("Accuracy of trining data Varience: ", calculateaccuracy(training_dataset, treevarience))

            print("Accuracy of validiation data Varience: ", calculateaccuracy(validation_dataset, treevarience))

            print("Accuracy of test data Varience:  ", calculateaccuracy(test_dataset, treevarience))


            (prunedvalidationvarience, acVprunedvalidation) = treepruning(treevarience, l, k, validation_dataset)
            print("     Pruned validation data accuracy VARIENCE IMPURIRY : ", acVprunedvalidation)
            print(" ")
            (prunedtreevarience, acVprunedtest) = treepruning(treevarience, l, k, test_dataset)
            
            if (printing == "yes"):
                print("     Pruned tree of test data VARIENCE IMPURIRY ")
                printtree(prunedtreevarience, attributes, '')


            print(" ")
            print("     Pruned test data accuracy VARIENCE IMPURIRY : ", acVprunedtest)
            print(" ")
            print("     Pruned test data accuracy with l and k VARIENCE IMPURIRY")

            for lvv, kvv in zip(valuesforl, valuesfork):
                (prunedtreevarience, acVprunedtest) = treepruning(treevarience, lvv, kvv,test_dataset)
                print("l = ", lvv)
                print("k = ", kvv)
                print("Accuracy=",acVprunedtest)

if __name__ == "__main__":
    main()
