import sys, threading
import time
import numpy as np 
from scipy.optimize import linprog 
from PyQt5.QtWidgets import QApplication,QFormLayout,QWidget,QVBoxLayout,QHBoxLayout,QFrame,QLineEdit,QRadioButton,QLabel,QTableWidget,QPushButton
from PyQt5.QtGui import QIcon,QIntValidator
sys.setrecursionlimit(10**7) ,threading.stack_size(2**27)
Zopt = np.inf 
iterations = 0
noeuds = 1
upper_bound = None
class Resulta(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle('RESULTAT'),self.setWindowIcon(QIcon("Icon.ico"))
        self.solution,self.valeur_solution,self.temp,self.iterations,self.noeuds=Vecteur(self),QLineEdit(self),QLineEdit(self),QLineEdit(self),QLineEdit(self)
        self.etat,layout=QLabel('Solution Optimale :',self),QFormLayout()
        self.etat.setMinimumWidth(300)
        layout.addRow(self.etat,self.solution),self.solution.setReadOnly()
        for i in [['Valeur de la solution optimale :',self.valeur_solution],['Temps d''exécution : ',self.temp],['Itérations :',self.iterations],['Noeuds branch-and-bound :',self.noeuds]]:
            layout.addRow(QLabel(i[0]),i[1]),i[1].setReadOnly(True)
        self.setLayout(layout)
    
class Vecteur(QFrame):
    def __init__(self,parent=None):
        super().__init__(parent=parent)
        self.hlayout,self.vect=QHBoxLayout(),[]
        self.hlayout.setSpacing(0)
        self.setLayout(self.hlayout)
    def setReadOnly(self):
        [i.setReadOnly(True) for i in self.vect]
    def set_Taille(self,n):
        [self.hlayout.removeWidget(i) for i in self.vect]
        try:
            self.vect=[QLineEdit() for _ in range(int(n))]
            [self.hlayout.addWidget(i) for i in self.vect]
        except:
            self.vect=[]
class Choix(QFrame):
    def __init__(self,parent=None):
        super().__init__(parent=parent)
        self.choix1,self.choix2,layout=QRadioButton('PLNE',self),QRadioButton('PLNE 0/1',self),QHBoxLayout()
        layout.addWidget(self.choix1),layout.addWidget(self.choix2)
        self.setLayout(layout)
class TypePrblm(QFrame):
    def __init__(self,parent=None):
        super().__init__(parent=parent)
        self.min,self.max,layout=QRadioButton('Min',self),QRadioButton('Max',self),QHBoxLayout()
        layout.addWidget(self.min),layout.addWidget(self.max)
        self.setLayout(layout)
class MainWindo(QWidget):
    def __init__(self):
        super().__init__()
        def nbrvariable_changed():   
            try:
                self.coeff.set_Taille(self.nbr_variable.text())
                self.matric.setRowCount(int(self.nbr_variable.text()))
            except:
                self.matric.setRowCount(0)
        def nbrcontarint_changed():
            try:
                self.rhs.set_Taille(int(self.nbr_constraint.text()))
                self.matric.setColumnCount(int(self.nbr_constraint.text()))
            except:
                self.matric.setColumnCount(0)
        self.setWindowIcon(QIcon("Icon.ico")),self.setObjectName('MainWindo'),self.setGeometry(100,50,800,600)
        self.nbr_variable,self.nbr_constraint,self.rhs,self.coeff,self.choix,self.type,self.matric,self.calculer=QLineEdit(self),QLineEdit(self),Vecteur(self),Vecteur(self),Choix(self),TypePrblm(self),QTableWidget(self),QPushButton('Calculer',self)
        self.nbr_variable.setPlaceholderText("Nombre de variables "),self.nbr_constraint.setPlaceholderText("Nombre de constraint "),self.nbr_variable.setValidator(QIntValidator(1,9)),self.nbr_constraint.setValidator(QIntValidator(1,9))
        self.nbr_variable.textChanged.connect(nbrvariable_changed ),self.nbr_constraint.textChanged.connect(nbrcontarint_changed)
        self.calculer.clicked.connect(self.calcule)
        self.setLayout(),self.show()
    def calcule(self):
        def BranchAndBound(A,b,objectif):
            global Xopt
            global Zopt
            global iterations
            global noeuds
            global upper_bound
            n = len(A[0]) 
            solution_relaxe = linprog(objectif, A_ub = A, b_ub = b, bounds = [(0,upper_bound) for i in range(n)], method = 'simplex')
            if solution_relaxe.success == True:
                X = solution_relaxe.x # X : solution
                ZX = solution_relaxe.fun # ZX : Valeur de la solution X
                iterations += solution_relaxe.nit 
                no_int_vector = np.array([X[j] for j in range(len(X)) if X[j] != int(X[j])]) # vecteur contient valeurs non entières si elle existent
                if len(no_int_vector) != 0:
                    m = max(no_int_vector)
                    i = X.tolist().index(m) # i : index du maximum des valeurs non entières
                    if Zopt > ZX:
                        e = np.array([0 for k in range(n)])
                        e[i] = -1
                        # Noeud droit : sous problème 1 SP1
                        SP1 = np.vstack([A, e])
                        b1 = np.append(b, -(int(X[i])+1))
                        e[i] = 1
                        # Noeud gauche : sous problème 2 SP2
                        SP2 = np.vstack([A, e])
                        b2 = np.append(b, int(X[i]))
                        BranchAndBound(SP2, b2, objectif) # resoudre le sous problème SP2
                        BranchAndBound(SP1, b1, objectif) # resoudre le sous problème SP1
                        noeuds += 2
                else: # si no_int_vector est vide donc X est une solution entière
                    if ZX <= Zopt:
                        Xopt = X # mise à jour de la solution entière
                        Zopt = ZX
        global Xopt
        global Zopt
        global iterations
        global noeuds
        global upper_bound
        Zopt,iterations,noeuds = np.inf,0,1
        upper_bound = None if self.choix.choix1.isChecked() else 1
        type_problem = 'Min' if self.type.min.isChecked() else 'Max'
        C = np.array([int(i.text()) for i in self.coeff.vect])
        C1 = list(C)
        n =int(self.nbr_variable.text())
        C=list(map(lambda x: -x,C)) if  type_problem == 'Max' else C
        R =int(self.nbr_constraint.text())
        A = [[     self.matric.item(i,j).text()   for j in range(R) ] for i in range(R)]
        B =[int(i.text()) for i in self.rhs.vect]
        start = time.time() 
        BranchAndBound(A,B,C)
        end = time.time()
        self.result=Resulta()
        try:
            if Zopt != np.inf:
                self.result.solution.set_Taille(n)
                [self.result.solution.vect[j].setText(str(int(Xopt[j])) ) for j in range(n)]
                self.result.valeur_solution.setText(str(-Zopt)) if type_problem == 'Max' else self.result.valeur_solution.setText(str(Zopt)) 
            else:
                self.result.etat.setText('Le problème est irréalisable')
        except NameError: # le block except s'exécute si le problème est irréalisable
            self.result.etat.setText('Le problème est irréalisable')
        
        self.result.temp.setText(str(end-start ))
        self.result.iterations.setText(str(iterations ))
        self.result.noeuds.setText(str(noeuds))
        self.result.show()
    def setLayout(self):
        a0,h,h1,h2,h3,h4,h5=QVBoxLayout(),QHBoxLayout(),QHBoxLayout(),QHBoxLayout(),QHBoxLayout(),QHBoxLayout(),QHBoxLayout()
        [h.addWidget(i) for i in [self.nbr_variable,self.nbr_constraint]]
        [h1.addWidget(i) for i in [QLabel('Choix :'),self.choix]]
        [h2.addWidget(i) for i in [QLabel('Type de problème : '),self.type]]
        [h3.addWidget(i) for i in [QLabel('RHS : '),self.rhs]]
        [h4.addWidget(i) for i in [QLabel('Entrer les coefficients de la fonction objectif :'),self.coeff]]
        [a0.addLayout(i) for i in [h,h1,h2,h3,h4]]
        a0.addWidget(self.matric),h5.addStretch(1),h5.addWidget(self.calculer)
        a0.addLayout(h5)
        return super().setLayout(a0)
                # Zopt = +infini # ecrire Max pour maximisation , Min pour minimisation
if __name__=="__main__":
    app=QApplication(sys.argv)
    app.setApplicationName('Branch And Bound')
    app.setStyleSheet(open('style.qss','r').read())
    app.setApplicationVersion('1.0.0')
    windo=MainWindo()
    sys.exit(app.exec_())
