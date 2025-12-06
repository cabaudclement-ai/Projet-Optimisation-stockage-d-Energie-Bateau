# -*- coding: utf-8 -*-
"""
Created on Mon Sep 29 11:13:25 2025

@author: cabaud
"""

#Importation des modules

import numpy as np
import turtle
import matplotlib.pyplot as plt

#Le type de bateau est toujours le même

#Variables

mer = 1
pas = 1                     #réel positif (min)
rho_air = 1.204                 #réel positif (kg/m^3) à 20 °C
rho_eau_mer = 1025             #réel positif (kg/m^3) à la surface

#Caractéristiques bateau

A_air = 5       #réel positif (m²) Surface de résistance au vent
A_S = 3.5       #réel positif (m²) Surface tirant d'eau
C_T = 0.1       #eau de mer
C_A = 1         #0.8 à 1.2

eta = 0.8       #elec/meca

#Choix de la trajectoire
choix = 'choix_trapeze'
#### Attention ! trapeze étais à la fois le nom d'une fonction et  d'une variable !




#Entrées

nb_stop_batterie = 1            #entier
nb_stopH2 = 1                   #entier
pourcentage_H2 = 0.4            #entre 0 et 1      part de puissance consommée par la batterie et la pile
V_bateau = 10                   #réel positif (m/s)
Distance_trajet = 20000          #réel positif (m)
Duree_tot_jour = 28800          #réel positf (s)
Durée_stop = 1800               #réel positif (s)
Pcharge_batterie = 800          #réel positif (W)
Pcharge_H2 = 800                #réel positif (W)
Tpscharge_batterie = 300        #réel positif (s)
Tpscharge_H2 = 360              #réel positif (s)



Puissance_Uniquement_batterie = 300000 #réel positif (W) Puissance au delà de laquelle le moteur fonctionne uniquement avec la batterie

acceleration_mot = 1            #réel positif (m/s²)

stock_H2 = 2000000000             #réel positif (J)
stock_Batterie = 300000000       #réel positif (J)


#Sortie

#H2_stock              #réel positif (L ?)
#batt_capa             #réel positif (C)
#P_pile_H              #réel positif (W)
#P_batt                #réel positif (W)

#############################################################################################################################
#Fonctions utilisées
#############################################################################################################################




#besoin pour le parcours   #trapèze, x est la distance d'accélération jusqu'à arriver à V_bateau désirée
#La vitesse (la trajectoire) est ici un besoin dimensionnant pour le reste de l'étude


def trapeze (t, acceleration_mot, vitesse_mot, distance_trajet):
    
    if t <= vitesse_mot/acceleration_mot:
        return "acceleration = ", acceleration_mot,"vitesse = ", t*acceleration_mot,"position = ", 0.5*acceleration_mot*(t**2)
    
    
    elif t > vitesse_mot/acceleration_mot and t <= vitesse_mot/acceleration_mot + (distance_trajet/vitesse_mot - (vitesse_mot)/acceleration_mot):
        return "acceleration = ", 0,"vitesse = ", vitesse_mot,"position", trapeze (vitesse_mot/acceleration_mot, acceleration_mot, vitesse_mot, distance_trajet)[-1] + vitesse_mot*(t-vitesse_mot/acceleration_mot)
    
    
    elif t > vitesse_mot/acceleration_mot + (distance_trajet/vitesse_mot - (vitesse_mot)/acceleration_mot) and t <= (distance_trajet/V_bateau)+(V_bateau/acceleration_mot) :
        return "acceleration = ", -acceleration_mot,"vitesse = ", vitesse_mot - acceleration_mot*(t-(vitesse_mot/acceleration_mot + (distance_trajet/vitesse_mot - (vitesse_mot)/acceleration_mot))), "position = ", trapeze (distance_trajet/vitesse_mot, acceleration_mot, vitesse_mot, distance_trajet)[-1] + vitesse_mot*(t-distance_trajet/vitesse_mot) - 0.5*acceleration_mot*((t-distance_trajet/vitesse_mot)**2)


def trajectoire (t, choix, acceleration_mot, vitesse_mot, distance_trajet):
    if choix == 'choix_trapeze':
        return trapeze (t, acceleration_mot, vitesse_mot, distance_trajet)

print (choix)


def R_T(t, choix, vitesse_mot, distance_trajet, rho_air, rho_eau_mer, A_S, A_air, C_T, C_A):
    cte_eau_de_mer = 0.5*rho_eau_mer*A_S*C_T #calucle de F = 1/2 rho S V^2
    cte_air = 0.5*rho_air*A_air*C_A
    v = trajectoire (t, choix, acceleration_mot, vitesse_mot, distance_trajet)[3]
    return "trainee eau de mer = ", cte_eau_de_mer*v**2,"trainee air = ",  cte_air*v**2, "Resultante de trainee = ", (cte_air+cte_eau_de_mer)*((trajectoire (t, choix, acceleration_mot, vitesse_mot, distance_trajet))[3])**2


def Puissance_bateau(t, choix, vitesse_mot, distance_trajet, A_S, A_air, C_T, C_A, eta, pourcentage_H2, Puissance_uniquement_batterie):
    puissance_mecanique = R_T(t, choix, vitesse_mot, distance_trajet, rho_air, rho_eau_mer, A_S, A_air, C_T, C_A)[-1]*trajectoire(t, choix, acceleration_mot, vitesse_mot, distance_trajet)[3]
    puissance_electrique = (1/eta)*(R_T(t, choix, vitesse_mot, distance_trajet, rho_air, rho_eau_mer, A_S, A_air, C_T, C_A)[-1]*trajectoire(t, choix, acceleration_mot, vitesse_mot, distance_trajet)[3])
    
    if puissance_electrique <= Puissance_uniquement_batterie :

        puissance_H2, puissance_batterie = pourcentage_H2*puissance_electrique, (1-pourcentage_H2)*puissance_electrique
    else :
        puissance_H2, puissance_batterie = 0, puissance_electrique
        

    #Prendre en compte que si on a besoin de beaucoup d'énergie, on tire uniquement sur la batterie
    
    
    return "Puissance mecanique", puissance_mecanique, "Puissance electrique", puissance_electrique, "Puissance_H2", puissance_H2, "Puissance batterie", puissance_batterie



###########################################################################################################################
#Création et remplissage des listes
###########################################################################################################################

Trapeze = []

Resistance_T = []

Puissance_mec_Bateau, Puissance_elec_Bateau , Puissance_H2, Puissance_Batterie= [0], [0], [0], [0]

Consomation_H2 , Consomation_Batterie = [0], [0]            #à chaque instant

Accumulateur, Pile_H2 = [0], [0]

T, X, V, A= [0], [0], [0], [0]

R, P = [0],[0]



for i in range(int((Distance_trajet/V_bateau)+(V_bateau/acceleration_mot))):
    
    Trapeze.append(trapeze(T[-1], acceleration_mot, V_bateau, Distance_trajet))
    Resistance_T.append(R_T(T[-1], choix, V_bateau, Distance_trajet, rho_air, rho_eau_mer, A_S, A_air, C_T, C_A))
    
    Puissance_mec_Bateau.append(Puissance_bateau(T[-1], choix, V_bateau, Distance_trajet, A_S, A_air, C_T, C_A, eta, pourcentage_H2, Puissance_Uniquement_batterie)[1])
    Puissance_elec_Bateau.append(Puissance_bateau(T[-1], choix, V_bateau, Distance_trajet, A_S, A_air, C_T, C_A, eta, pourcentage_H2, Puissance_Uniquement_batterie)[3])
    Puissance_H2.append(Puissance_bateau(T[-1], choix, V_bateau, Distance_trajet, A_S, A_air, C_T, C_A, eta, pourcentage_H2, Puissance_Uniquement_batterie)[5])
    Puissance_Batterie.append(Puissance_bateau(T[-1], choix, V_bateau, Distance_trajet, A_S, A_air, C_T, C_A, eta, pourcentage_H2, Puissance_Uniquement_batterie)[-1])

    
    

    
    T.append(T[-1]+1)
    X.append(Trapeze[i][-1])
    V.append(Trapeze[i][3])
    A.append(Trapeze[i][1])
    R.append(Resistance_T[i][-1])
    
#Incrémentation sur l'énergie
#Air sous la courbe = énergie
#Utilisation de la méthode des trapèzes avec un pas de temps de 1 seconde

E_H2, E_batterie = 0, 0
Liste_E_H2, Liste_E_Batterie = [], []

Liste_stock_H2, Liste_stock_Batterie = [stock_H2], [stock_Batterie]

for k in range(len(Puissance_H2)-1) :
    E_H2 += 0.5*(Puissance_H2[k]+Puissance_H2[k+1])
    E_batterie += 0.5*(Puissance_Batterie[k]+Puissance_Batterie[k+1])
    
    Liste_E_H2.append(E_H2)
    Liste_E_Batterie.append(E_batterie)
    
    Liste_stock_H2.append(Liste_stock_H2[-1] - 0.5*(Puissance_H2[k]+Puissance_H2[k+1]))
    Liste_stock_Batterie.append(Liste_stock_Batterie[-1] - 0.5*(Puissance_Batterie[k]+Puissance_Batterie[k+1]))



E_H2 = Liste_E_H2[-1]                       #Energie nécessaire pour faire un trajet
E_batterie = Liste_E_Batterie[-1]
    
Energie = ['Energie H2 (J) =', E_H2,
           'Energie H2 (kWh) =', E_H2/3600000,
           'Energie Batterie (J) = ', E_batterie,
           'Energie Batterie (kWh) = ', E_batterie/3600000]



            


#Tracés d'un seul trajet

plt.figure()
plt.plot(T,X)
plt.title("Position")
plt.xlabel("t (s)")
plt.ylabel("X (m)")
plt.grid(True)
plt.legend()

plt.figure()
plt.plot(T,V)
plt.title("Vitesse")
plt.xlabel("t (s)")
plt.ylabel("V (m/s)")
plt.grid(True)
plt.legend()

plt.figure()
plt.plot(T,A)
plt.title("Accélération")
plt.xlabel("t (s)")
plt.ylabel("A (m/s²)")
plt.grid(True)
plt.legend()

plt.figure()
plt.plot(T,Puissance_mec_Bateau)
plt.title("Puissance mécanique")
plt.xlabel("t (s)")
plt.ylabel("P (W)")
plt.grid(True)
plt.legend()

plt.figure()
plt.plot(T,Puissance_elec_Bateau)
plt.title("Puissance électrique")
plt.xlabel("t (s)")
plt.ylabel("P (W)")
plt.grid(True)
plt.legend()

plt.figure()
plt.plot(T,Puissance_H2)
plt.title("Puissance H2")
plt.xlabel("t (s)")
plt.ylabel("P (W)")
plt.grid(True)
plt.legend()

plt.figure()
plt.plot(T,Puissance_Batterie)
plt.title("Puissance Batterie")
plt.xlabel("t (s)")
plt.ylabel("P (W)")
plt.grid(True)
plt.legend()


plt.figure()
plt.plot(T,Liste_stock_H2)
plt.plot(T,Liste_stock_Batterie)
plt.title("Réserve pile H2 et batterie")
plt.xlabel("t (s)")
plt.ylabel("E (J)")
plt.grid(True)
plt.legend()


T.pop()
plt.figure()
plt.plot(T,Liste_E_H2)
plt.plot(T,Liste_E_Batterie)
plt.title("Consomation pile H2 et batterie")
plt.xlabel("t (s)")
plt.ylabel("E (J)")
plt.grid(True)
plt.legend()

plt.show()




##############################################################################################################################
#Création d'une timeline sur une journée
##############################################################################################################################

#Initialisation pour toute la timeline (t_####)

t_Temps_traversee= len(T)

t_Trapeze = []

t_Resistance_T = []

t_Puissance_mec_Bateau, t_Puissance_elec_Bateau , t_Puissance_H2, t_Puissance_Batterie= [0], [0], [0], [0]

t_Consomation_H2 , t_Consomation_Batterie = [0], [0]

t_Accumulateur, Pile_H2 = [0], [0]

t_T, t_X, t_V, t_A= [0], [0], [0], [0]

t_R, t_P = [0],[0]

t_E_H2,t_E_batterie = 0, 0
t_Liste_E_H2, t_Liste_E_Batterie = [stock_H2], [stock_Batterie]

t_Liste_stock_H2, t_Liste_stock_Batterie = [stock_H2], [stock_Batterie]

t_Limite_H2, t_Limite_Batterie = [E_H2], [E_batterie]


while len(t_T) + t_Temps_traversee <= Duree_tot_jour and len(t_T) + min(Durée_stop, Tpscharge_batterie, Tpscharge_H2) <= Duree_tot_jour:
    print(t_Liste_stock_H2[-1])
    print(t_T[-1])
    #Initialisation pour une séquence, nous concaténetions ensuite (s_###)
    
        #Lancement d'un trajet dans le cas où il rest du temps et après recharge
    s_Trapeze = []

    s_Resistance_T = []

    s_Puissance_mec_Bateau, s_Puissance_elec_Bateau , s_Puissance_H2, s_Puissance_Batterie= [0], [0], [0], [0]

    s_Consomation_H2, s_Consomation_Batterie = [0], [0]            

    s_Accumulateur, s_Pile_H2 = [0], [0]

    s_T, s_X, s_V, s_A= [0], [0], [0], [0]

    s_R, s_P = [0],[0]

    s_E_H2, s_E_batterie = 0, 0
    s_Liste_E_H2, s_Liste_E_Batterie = [], []


    

#Itération d'un trajet    
    for i in range(int((Distance_trajet/V_bateau)+(V_bateau/acceleration_mot))):
        
        t_Trapeze.append(trapeze(s_T[-1], acceleration_mot, V_bateau, Distance_trajet))
        t_Resistance_T.append(R_T(s_T[-1], choix, V_bateau, Distance_trajet, rho_air, rho_eau_mer, A_S, A_air, C_T, C_A))
        
        t_Puissance_mec_Bateau.append(Puissance_bateau(s_T[-1], choix, V_bateau, Distance_trajet, A_S, A_air, C_T, C_A, eta, pourcentage_H2, Puissance_Uniquement_batterie)[1])
        t_Puissance_elec_Bateau.append(Puissance_bateau(s_T[-1], choix, V_bateau, Distance_trajet, A_S, A_air, C_T, C_A, eta, pourcentage_H2, Puissance_Uniquement_batterie)[3])
        t_Puissance_H2.append(Puissance_bateau(s_T[-1], choix, V_bateau, Distance_trajet, A_S, A_air, C_T, C_A, eta, pourcentage_H2, Puissance_Uniquement_batterie)[5])
        t_Puissance_Batterie.append(Puissance_bateau(s_T[-1], choix, V_bateau, Distance_trajet, A_S, A_air, C_T, C_A, eta, pourcentage_H2, Puissance_Uniquement_batterie)[-1])
    
    
    
    
    
        s_T.append(s_T[-1]+1)
        t_X.append(t_Trapeze[i][-1])
        t_V.append(t_Trapeze[i][3])
        t_A.append(t_Trapeze[i][1])
        t_R.append(t_Resistance_T[i][-1])
        t_T.append(t_T[-1]+1)
    
    
    
    
        print('test len',len(t_T), len(t_Liste_stock_Batterie))
        print('un trajet effectué')
    
 



#calcul des Energies et Stocks pour 

    # for k in range(len(t_T)-1) :
    
    #     t_E_H2 += 0.5*(t_Puissance_H2[k]+t_Puissance_H2[k+1])
    #     t_E_batterie += 0.5*(t_Puissance_Batterie[k]+t_Puissance_Batterie[k+1])
    
    #     t_Liste_E_H2.append(t_E_H2)
    #     t_Liste_E_Batterie.append(t_E_batterie)
    
    #     t_Liste_stock_H2.append(t_Liste_stock_H2[-1] - 0.5*(t_Puissance_H2[k]+t_Puissance_H2[k+1]))
    #     t_Liste_stock_Batterie.append(t_Liste_stock_Batterie[-1] - 0.5*(t_Puissance_Batterie[k]+t_Puissance_Batterie[k+1]))
        
    #     t_Limite_H2.append(E_H2)
    #     t_Limite_Batterie.append(E_batterie)
#####ERREUR ICI DANS CETTE BOUCLE        
    
#Entrée dans le procédé de décision
    

    t_T.append(t_T[-1]+1)
    
    t_Trapeze.append([0, 0, 0, 0])
    t_Resistance_T.append([0, 0, 0, 0, 0, 0])
    t_Puissance_mec_Bateau.append(0)
    t_Puissance_elec_Bateau.append(0)
    t_Puissance_H2.append(0)
    t_Puissance_Batterie.append(0)
    t_X.append(0)
    t_V.append(0)
    t_A.append(0)
    t_R.append(0)
        
    

            
        
    print('test len',len(t_T), len(t_Liste_stock_Batterie))
    print("pause sans recharge")




           

###### En test   
t_Limite_H2, t_Limite_Batterie = [E_H2], [E_batterie] 

for k in range(len(t_Puissance_H2)-1) :
    
    t_E_H2 += 0.5*(t_Puissance_H2[k]+t_Puissance_H2[k+1])
    t_E_batterie += 0.5*(t_Puissance_Batterie[k]+t_Puissance_Batterie[k+1])

    t_Liste_E_H2.append(t_E_H2)
    t_Liste_E_Batterie.append(t_E_batterie)

    t_Liste_stock_H2.append(t_Liste_stock_H2[-1] - 0.5*(t_Puissance_H2[k]+t_Puissance_H2[k+1]))
    t_Liste_stock_Batterie.append(t_Liste_stock_Batterie[-1] - 0.5*(t_Puissance_Batterie[k]+t_Puissance_Batterie[k+1]))
    
    t_Limite_H2.append(E_H2)
    t_Limite_Batterie.append(E_batterie)


###### En test        



print('fin de journée')

plt.figure()
plt.plot(t_T,t_X)
plt.title("Position")
plt.xlabel("t (s)")
plt.ylabel("X (m)")
plt.grid(True)
plt.legend()

plt.figure()
plt.plot(t_T,t_V)
plt.title("Vitesse")
plt.xlabel("t (s)")
plt.ylabel("V (m/s)")
plt.grid(True)
plt.legend()

plt.figure()
plt.plot(t_T,t_A)
plt.title("Accélération")
plt.xlabel("t (s)")
plt.ylabel("A (m/s²)")
plt.grid(True)
plt.legend()

plt.figure()
plt.plot(t_T,t_Puissance_mec_Bateau)
plt.title("Puissance mécanique")
plt.xlabel("t (s)")
plt.ylabel("P (W)")
plt.grid(True)
plt.legend()

plt.figure()
plt.plot(t_T,t_Puissance_elec_Bateau)
plt.title("Puissance électrique")
plt.xlabel("t (s)")
plt.ylabel("P (W)")
plt.grid(True)
plt.legend()

plt.figure()
plt.plot(t_T,t_Puissance_H2)
plt.title("Puissance H2")
plt.xlabel("t (s)")
plt.ylabel("P (W)")
plt.grid(True)
plt.legend()

plt.figure()
plt.plot(t_T,t_Puissance_Batterie)
plt.title("Puissance Batterie")
plt.xlabel("t (s)")
plt.ylabel("P (W)")
plt.grid(True)
plt.legend()


plt.figure()
plt.plot(t_T,t_Liste_stock_H2)
plt.plot(t_T,t_Liste_stock_Batterie)
plt.plot(t_T,t_Limite_H2)
plt.plot(t_T,t_Limite_Batterie)
plt.title("Réserve pile H2 et batterie t_Liste_stock_H2 et t_Liste_stock_Batterie")
plt.xlabel("t (s)")
plt.ylabel("E (J)")
plt.grid(True)
plt.legend()


plt.figure()
plt.plot(t_T,t_Liste_E_H2)
plt.plot(t_T,t_Liste_E_Batterie)
plt.title("Consomation pile H2 et batterie t_Liste_E_H2 et t_Liste_E_Batterie")
plt.xlabel("t (s)")
plt.ylabel("E (J)")
plt.grid(True)
plt.legend()

plt.show()


####################################################################################################################################
#Sorties
####################################################################################################################################


#Sortie
#H2_stock
#batt_capa
#P_pile_H
#P_batt

