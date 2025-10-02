import numpy as np
import matplotlib.pyplot as plt
import time
import random

def ndecim (x) :
    if x == int(x) :
        return 0
    else :
        n = int(x)
        return (len(str(x))-len(str(n))-1)

def suite(y,a,b,n) :                                                             ## calcule le n ieme terme de la suite où y est le premier terme, et a et b sont des réels
            k = 0                                                                ## /!\ : 0 < a < 4 ; 0 < b ; 0 < y < 1
            while k < n :
                y = a*y*(1-b*y)
                k += 1
            return y

def dessin (y,a,b,n) :                                                           ## fait le graphe de la suite, conditions entrées
    if a <= 0 or a >= 4 or y <= 0 or y >= 1/b or b <= 0 or n < 0 :
        return False
    else :
        x = np.linspace(0,n,n+1)
        u = [suite(y,a,b,k) for k in range (0,n+1)]
        plt.ylim(0,1/b)
        plt.xlabel("n")
        plt.ylabel("u(n)")
        plt.scatter(x,u,s=5)
        plt.plot(x,u,label="u")
        plt.legend()
        plt.show()

##def fract_essai_1 (b,p) :                                                      ## essai 1 du programme de fractale : considérer que la limite est proche de la 100 ieme
##    def suite(y,a,b,n) :                                                       ## itération et que la variation de a va modifier la  valeur ~ valeur d'adhérence : faux
##            k = 0
##            while k < n :
##                y = a*y*(1-b*y)
##                k += 1
##            return y
##    y = 1/(2*b)
##    t0 = time.time()
##    l = []
##    a = 2.4
##    while a < 4 :
##        l.append(suite(y, a, b, 100))
##        a += ((4-2.4)/10000)/p
##        print("a =", a)
##    print("le nombre de valeurs est :", len(l))
##    x = np.linspace(2.4, 4.0, len(l))
##    plt.ylim(0,1/b)
##    plt.xlabel("a")
##    plt.ylabel("limite")
##    plt.scatter(x,l,s=0.1)
##    print("Fait en {}s".format(time.time()-t0))
##    plt.show()

##def fract_essai_2 (b,p) :                                                      ## essai 2 : éclatement dû à l'augmentation de +1 à chaque valeur de a : complexité élevée
##    y = 1/(2*b)
##    t0 = time.time()
##    l = []
##    a = 2.4
##    i = 0
##    while a < 4 :
##        l.append(suite(y, a, b, 100 + i))                                      ## idée : on varie l'itération élevée pour "faire varier la limite"
##        i += 1
##        a += (4-2.4)/(p*10000)
##        if i % 1000 == 0 :
##            print("a =", a)
##        if int(time.time()-t0) != 0 and int(time.time()-t0) % 1500 == 0 :
##            print("ça fait ", time.time()-t0)
##            time.sleep(300)
##    print("le nombre de valeurs est :", len(l))
##    x = np.linspace(2.4, 4.0, len(l))
##    plt.ylim(0,1/b)
##    plt.xlabel("a")
##    plt.ylabel("limite")
##    plt.scatter(x,l,s=0.002)
##    print("Fait en {}s".format(time.time()-t0))
##    plt.show()

def fract (b,p) :                                                                ## Dessine l'évolution des valeurs d'adhérence de la suite en fonction de a : b un réel > 0,
    y = 1/(2*b)                                                                  ## et p coeff tel que si p augmente alors le pas diminue, y0 doit appartenir à ]0,1/b[
    t0 = time.time()                                                             ## t0 : la date de lancement du programme
    l = []
    a = 3.49
    i = 0
    while a < 4 :
        l.append(suite(y, a, b, 1000 + 200 * random.random()))                   ## idée : on génère une itération aléatoire élevée pour "faire varier la limite", complexité moindre car croissance constante, non linéaire
        a += (4-3.49)/(p*10000)                                                  ## le coefficient correspond au pas : on veut 10 000*p valeurs de a dans l'intervalle [2.4,4[
        i += 1
        if i % 500 == 0 :                                                        ## pour éviter d'avoir aucun contrôle sur la console / être spammé
            print("a =", a)
        if int(time.time()-t0) != 0 and int(time.time()-t0) % 1200 == 0 :        ## permet de faire 10(+10) min de calculs pour 10 min de pause (le temps de pause étant compté)
            print("ça fait ", time.time()-t0)
            time.sleep(600)
    print("le nombre de valeurs est :", len(l))
    x = np.linspace(3.49, 4, len(l))
    plt.ylim(0,1/b)                                                              ## l'intervalle ]0,1/b[ est stable par la fonction associée à la suite
    plt.xlabel("a")
    plt.ylabel("limite")
    plt.scatter(x,l,s=0.001)
    print("Fait en {}s".format(time.time()-t0))
    plt.show()

def fract_b (p,i,f,pas) :                                                        ## dessine plusieurs fractales en fonction de b variant de i > 0 à f avec un pas de pas
    def fract_fract_b (y,b,p) :
        l = []
        a = 2.4
        i = 0
        while a < 4 :
            l.append(suite(y, a, b, 1000 + 200 * random.random()))
            a += (4-2.4)/(p*10000)
            i += 1
            if i % 500 == 0 :
                print("a =", a)
            if int(time.time()-t0) != 0 and int(time.time()-t0) % 1200 == 0 :
                print("ça fait ", time.time()-t0)
                time.sleep(600)
        print("fait ça en {}s".format(time.time()-t0))
        x = np.linspace(2.4, 4.0, len(l))
        plt.scatter(x,l,s=0.1, label = "b = {}".format(round(b, ndecim(b))))     ## arrondit les valeurs de la légende correctement
    t0 = time.time()
    y = 1/(2*f)
    for k in np.arange (i,f, pas) :
        fract_fract_b (y,k,p)
    plt.ylim(0,1/i)
    plt.xlabel("a")
    plt.ylabel("limite")
    plt.legend()
    print("Fait en {}s".format(time.time()-t0))
    plt.show()

def fract_y(p,b,i,f,pas) :                                                       ## dessine les fractales en fonction de y0 : ça ne change rien
    if f >= 1/b :                                                                ## pour garantir l'existence de y dans ]0,1[
        return False
    else :
        def fract_fract_y (y,b,p) :
            l = []
            a = 2.4
            i = 0
            while a < 4 :
                l.append(suite(y, a, b, 1000 + 200 * random.random()))
                a += (4-2.4)/(p*10000)
                i += 1
                if i % 500 == 0 :
                    print("a =", a)
                if int(time.time()-t0) != 0 and int(time.time()-t0) % 1200 == 0 :
                    print("ça fait ", time.time()-t0)
                    time.sleep(600)
            print("fait ça en {}s".format(time.time()-t0))
            x = np.linspace(2.4, 4.0, len(l))
            plt.scatter(x,l,s=0.1, label = "y0 = {}".format(round(y, ndecim(y))))
        t0 = time.time()
        for k in np.arange (i,f,pas) :
            fract_fract_y (k,b,p)
        plt.ylim(0,1/b)
        plt.xlabel("a")
        plt.ylabel("limite")
        plt.legend()
        print("Fait en {}s".format(time.time()-t0))
        plt.show()

print(fract(1,200))