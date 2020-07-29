import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
from numpy_financial import pmt, ipmt, ppmt, npv, irr

data_factors = np.array([[0.3, 0.5, 0.6],
                         [0.8, 0.6, 0.2],
                         [0.3, 0.3, 0.2],
                         [0.2, 0.2, 0.15],
                         [0.3, 0.3, 0.2],
                         [0.2, 0.2, 0.1],
                         [0.1, 0.1, 0.05],
                         [0.3, 0.4, 0.4],
                         [0.35, 0.25, 0.2],
                         [0.1, 0.1, 0.1]])

Capital_factors = pd.DataFrame(data_factors,
                               index=["fer", "fp", "fi", "fel", "fc", "fs", "fl", "OS", "D&E", "X"], 
                               columns=["Fluids", "Fluids-Solids", "Solids"])

"""Creo una clase Equipment de la cual van a heredar los equipos que intervengan en el proceso. La función calcC permite calcular el coste si el equipo se encuentra instalado, y si no deja el
coste del equipo sin ello"""
class Equipment:
    def __init__(self,fm=1,installed=True):
        self.fm=fm
        self.installed=installed
    def calcC(self):
        if self.installed:
            self.C *= ((1+Capital_factors.loc["fp"]["Fluids"])*self.fm+(Capital_factors.loc["fer"]["Fluids"] + Capital_factors.loc["fel"]["Fluids"]
                                                     + Capital_factors.loc["fi"]["Fluids"] + Capital_factors.loc["fc"]["Fluids"]
                                                     + Capital_factors.loc["fs"]["Fluids"] + Capital_factors.loc["fl"]["Fluids"]))
        
"""Boiler, Turbine y Pump son clases que crean dichos objetos, que por heredar de Equipment poseen su fm e installed=True. En sus constructores se encuentran los atributos que poseen, además 
del atributo C que, valdrá según los parámetros de cada equipo un valor. Posteriormente se llama a la función del padre que recalcula C dependiendo si está o no instalado el equipo"""
class Boiler(Equipment):
    def __init__(self,Q,p,fm=1,installed=True):
        Equipment.__init__(self,fm,installed)
        self.Q=Q
        self.p=p
        assert type(installed) == bool

        if self.Q < 5000 or self.Q > 800000:
            print(f"    - WARNING: boiler vapor production out of method bounds, 5000 < Q < 800000. Results may not be accurate.")

        if self.p < 10 or self.p > 70:
            print(f"    - WARNING: boiler pressure out of method bounds, 10 < p < 70. Results may not be accurate.")

        if self.Q < 20000:
            self.C = 106000 + 8.7*self.Q
        elif self.Q < 200000:
            if self.p < 15:
                self.C = 110000 + 4.5*self.Q**0.9
            elif self.p < 40:
                self.C = 106000 + 8.7*self.Q
            else:
                self.C = 110000 + 4.5*self.Q**0.9
        else:
            self.C = 110000 + 4.5*self.Q**0.9
        self.calcC()

class Turbine(Equipment):
    def __init__(self,kW,fm=1,installed=True):
        Equipment.__init__(self,fm,installed)
        self.kW=kW
        assert type(installed) == bool
        if self.kW < 100 or self.kW > 20000:
            print(f"    - WARNING: steam turbine power out of method bounds, 100 < kW < 20000. Results may not be accurate.")
        self.C = -12000 + 1630*self.kW**0.75
        self.calcC()

class Pump(Equipment):
    def __init__(self,Q,fm=1,installed=True):
        Equipment.__init__(self,fm,installed)
        self.Q=Q
        assert type(installed) == bool
        if self.Q < 0.2 or self.Q > 126:
            print(f"    - WARNING: pump caudal out of method bounds, 0.2 < Q (L/s) < 126. Results may not be accurate.")
        self.C = 6900 + 206*self.Q**0.9
        self.calcC()

#Para el condensador, según el enunciado, el coste ya se conoce de otro proyecto
class Condenser:
    def __init__(self):
        self.C=400000 * (10000 / 15000)**0.8
        


class ProcessPlant():
    #Atributos
    def __init__(self,capacity_factor=0.9):
        self.equipment=[]
        self.CAPEX=0
        self.OPEX=0
        self.water=0
        self.salaries=0
        self.capacity_factor=capacity_factor
        self.loan_payment=0
        self.loan_interest=0
        self.loan_principal=0
        self.depreciation_array=[]
        self.sales=0
        self.df=""

    #Añade los equipos creados en un array de objetos
    def addEquipment(self,equip):
        self.equipment.append(equip)
    #Calcula el CAPEX, teniendo en cuenta todos los equipos del proceso industrial y se lo asigna a la variable self.CAPEX
    def calcCAPEX(self):
        for eq in self.equipment:
            self.CAPEX=self.CAPEX+eq.C
    #Calcula el OPEX, asignándole el valor a la variable de la clase correspondiente
    def calcOPEX(self):
        self.water= 1.29 * 10 * 8760 * self.capacity_factor
        self.salaries= 4 * 3 * 30000
        self.OPEX=self.water+self.salaries
    #Permite llevar a cabo el cálculo de los tres parámetros de Loan, necesarios para calcular el FinancialModel (aunque el loan.payment no se ha usado en ningún caso)
    def calcLoan(self,loan=0.6,interest=0.04,years=10):
        quantity=loan*self.CAPEX
        assert quantity > 0
        assert interest >= 0 and interest <= 1
        assert years > 1

        self.loan_payment   = pmt(interest, years, quantity)
        self.loan_interest  = ipmt(interest, np.arange(years) + 1, years, quantity)
        self.loan_principal = ppmt(interest, np.arange(years) + 1, years, quantity)

    #Calcula la depreciación. Guarda los resultados en un lista  
    def calcDepreciation(self,annual_percent=0.07, residual_value=0):
        assert annual_percent >= 0 and annual_percent <= 1
        annual_depreciation = []
        prev = 1
        while True:
            if prev < annual_percent:
                annual_depreciation.append(prev)
                break
            annual_depreciation.append(annual_percent)
            prev = prev - annual_percent
        self.depreciation_array = -1 * np.array(annual_depreciation) * (self.CAPEX - residual_value)
    #Permite calcular las ventas y las almacena en una variable de la clase
    def calcSales(self):
        self.sales = 1500 * 0.05 * 8760 * self.capacity_factor

    def calcFinancialModel(self,discount_rate=0.053):
        years = 20

        investment    = np.array([-self.CAPEX*0.4] + [0 for i in range(years-1)])
        depreciation  = np.hstack(([0], self.depreciation_array, [0 for i in range(years-1-len(self.depreciation_array))]))
        loan_prin     = np.hstack(([0], self.loan_principal, [0 for i in range(years-1-len(self.loan_principal))]))
        loan_int      = np.hstack(([0], self.loan_interest, [0 for i in range(years-1-len(self.loan_interest))]))

        sales_array    = np.zeros(years)
        water_array    = np.zeros(years)
        salaries_array = np.zeros(years)   

        for i in range(years):
            if i == 0:
                sales_array[i]    = 0
                water_array[i]    = 0
                salaries_array[i] = 0
            elif i == 1:
                sales_array[i]    = self.sales
                water_array[i]    = -1*self.water
                salaries_array[i] = -1*self.salaries
            else:
                sales_array[i]    = sales_array[i-1]*1.03
                water_array[i]    = water_array[i-1]*1.03
                salaries_array[i] = salaries_array[i-1]*1.02

        self.ebt   = np.vstack((investment, depreciation, loan_int, sales_array, water_array, salaries_array)).sum(axis=0)
        taxes = self.ebt * -0.3
        for i in range(len(taxes)):
            if taxes[i] > 0:
                taxes[i] = 0
        self.eat = self.ebt - taxes
        self.cash_flow = self.eat - depreciation + loan_prin
        self.cumulative_cash_flow = np.cumsum(self.cash_flow)

        data = np.vstack((investment, sales_array, depreciation, loan_prin, loan_int, salaries_array, water_array, self.ebt, 
                          taxes, self.eat, self.cash_flow, self.cumulative_cash_flow))
        self.df   = pd.DataFrame(data,
                            index=['Investment', 'Sales', 'Depreciation', 'Loan principal', 'Loan interest', 'Salaries',
                                   'Water', 'EBT', 'Taxes', 'EAT', 'Cash Flow', 'Cumulative Cash Flow'],
                            columns=[i for i in range(years)])  
        
        net_present_value = npv(discount_rate, self.cash_flow)
        internal_rate_return = irr(self.cash_flow)
        print(self.df)
        print(f"The project has a net present value of {'{:,.2f}'.format(net_present_value)}€ and an internal rate of return of {round(internal_rate_return*100, 2)}%")
    #Permite conocer en qué momento el proceso comienza a generar beneficios. Se estudia en función de los flujos de caja acumulados
    def calcPayback(self):
        for i in range (len(self.cumulative_cash_flow)):
            if self.cumulative_cash_flow[i]>=0:
                print("El año en el cual empezarás a ganar dinero será ",i)
                break
    def print_plot(self):
        x = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19]
        plt.figure(figsize=(10,6))
        # set width of bar
        barWidth = 0.25
         
        # set height of bar
        bars1 = self.eat
        bars2 = self.cash_flow
        bars3 = self.ebt
         
        # Set position of bar on X axis
        r1 = np.arange(len(bars1))
        r2 = [x + barWidth for x in r1]
        r3 = [x + barWidth for x in r2]
         
        # Make the plot
        plt.bar(r1, bars1, color='blue', width=barWidth, edgecolor='white', label='EAT')
        plt.bar(r2, bars2, color='red', width=barWidth, edgecolor='white', label='cash flow')
        plt.bar(r3, bars3, color='black', width=barWidth, edgecolor='white', label='EBT')
        plt.plot(x, self.cumulative_cash_flow, label ="cumulative cash flow")
         
        # Add xticks on the middle of the group bars
        plt.xlabel('years', fontweight='bold')
        plt.ylabel('€', fontweight='bold')
        plt.xticks([r + barWidth for r in range(len(bars1))], x)
         
        # Create legend & Show graphic
        plt.legend()
        plt.show()
    #Función que permite exportar los resultados a un archivo externo
    def exportExcel(self):
        #Dentro del paréntesis se situa la ruta donde se quiere exportar los resultados
        self.df.to_csv("./datos.csv")
        

#Método main en el cual se instancian las clases para crear los objetos que necesitemos y llamamos a las funciones que necesitemos		
if __name__ == '__main__':
    #Creamos los equipos que piden en el enunciado
    boiler1=Boiler(10000,70)
    turbine1=Turbine(1500)
    pump1=Pump(2.84)
    condenser1=Condenser()
    #Creamos el proceso que se quiere analizar
    process1=ProcessPlant() #Por defecto capacity factor vale 0.9.Introduce otro valor si desea cambiar este atributo
    #Añadimos los equipos (objetos) al proceso que deseamos
    process1.addEquipment(boiler1)
    process1.addEquipment(turbine1)
    process1.addEquipment(pump1)
    process1.addEquipment(condenser1)
    #LLamamos a las funciones de la clase ProcessPlant para el proceso correspondiente necesarias para llevar a cabo toda
    process1.calcCAPEX()
    process1.calcOPEX()
    process1.calcLoan() #Por defecto está loan a 0.6, interest a 0.04 y year a 10. Introduce ambos valores si se desea cambiar ambos atributos
    process1.calcDepreciation() #Por defecto el porcentaje anual el del 7% y el valor residual de 0
    process1.calcSales()
    process1.calcFinancialModel()
    process1.calcPayback()
    #Exporta los resultados
    process1.exportExcel()
    #Realiza la gráfica correspondiente
    process1.print_plot()

