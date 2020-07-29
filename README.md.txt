He incluído en el economic_assessment.py anotaciones que explican las clases (sus atributos y métodos) además de anotaciones en el main. En este README se hace un resumen de las clases empleadas

CLASES EMPREADAS EN EL EJERCICIO

---Clases que permiten crear los equipos necesarios para la planta---

-La clase Equipment posee 
	. constructor con dos atributos (fm e installed)
	. una función que recalcula los costes (calcC()) en caso de que el equipo se encuentre instalado

De esta clase van a heredar Boiler, Turbine y Pump

-La clase Boiler posee
	. constructor con los atibutos heredados de Equipment (fm e installed), además de Q y p (que se han de pasar 	al crear el objeto de tipo Boiler. Además se calcula en este constructor los costes(C) y se llama a la función heredada calcC que recalcula la variable C si se encuentra instalada.

-La clase Turbine y Pump poseen una estructura de clase muy similar a Boiler

-La clase Condenser
	. No hereda de una clase superior. Al conocerse el coste de este equipo de otro proyecto, el constructor únicamente asigna el valor de C en función a una expresión.

---Clase que genera el proceso de la planta---

- La clase ProcessPlant contiene
	. Un constructor que por defecto le da a capacity_factor un valor de 0.9, pero que al crear el objeto se le puede pasar otro valor. Además de una serie de atributos que posee la clase
	. Funciones:
		* addEquipment recibe los equipos (objetos que nos hemos creado con las clases anteriores) con los que va a contar la planta y los almacena en un atributo llamado equipment (array)
		* calcCAPEX() permite calcular y guardar en una variable dicho valor. Es la suma de C de todos los equipos que posea nuestra planta. Por ello, en esta función se recorre equipment y se van sumando los costes (objeto.C)
		* calcOPEX() calcula y almacena en una variable el OPEX. Para ello es necesario conocer el consumo de agua y salarios. Ambas variables también las almacenamos en la clase porque deben ser accesibles posteriormente por calcFinancialModel()
		* calcLoan() recibe por parámetros loan, interest y years (los cuales en el ejercicio han sido inicializados a los valores pedidos). Calcula y almacena como atributos loan_payment, loan_interest y loan_principal
		*calcDepreciation recibe como parámetros el porcentaje anual y el valor residual, que han sido inicializados a los valores pedidos. Almacena en un array los valores de depreciación.
		* calcSales() calcula y almacena las ventas
		* calcFinancialModel() recibe por argumento la tasa de descuento, la cual ha sido inicializada al valor pedido de 5.3%. Lleva a cabo el cálculo de EBT, los impuestos, el beneficio neto (EAT), el flujo de caja y el flujo de caja acumulado. Con todo ello, también calcula el NTV (Net Present Value) y el IRR(Internal Rate Return). 
Printea todos los resultados que piden en el enunciado.
		--Métodos extras para resolver los ejercicios voluntarios--
		* calcPayback() función que únicamente printea el año en el cual el flujo neto acumulado es mayot o igual a 0, que será cuando las pérdidas iniciales se hayan recuperado, pero no tengamos aún un beneficio real.
		* print_plot() permite dibujar en una gráfica € vs years el flujo de caja acumulado (linea), el EBT(barras), el flujo de caja (barras) y el EAT (barras)
		* exportExcel. Guarda los resultados obtenidos en un archivo externo que se encuentra al mismo nivel que economic_assessment.py


En cuanto al método main, contiene las instancias y las llamadas a los métodos de las clases necesarias.
He decidido dejar el main en el mismo archivo que las clases ya que no se especificaba nada en el ejercicio. De querer separarse, el main se lleva a un archivo a parte (por ejemplo main.py) y se haría 'from economic_assessment.py import *' para importar las clases.
