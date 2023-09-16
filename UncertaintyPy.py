import math
import numpy
import sympy

def _round_trad(value:float, n:int=0):
    if n < 0: n = 0
    if value > 0:
        return int(value*pow(10, n) + 0.5)/pow(10, n)
    else:
        return int(value*pow(10, n) - 0.5)/pow(10, n)

class ufloat:    
    def __init__(self, value:numpy.float64, uncertainty:numpy.float64, unit:str = '') -> None:
        if not type(unit) is str:
            raise TypeError("unit must be str")
        
        self.value = value
        self.uncertainty = uncertainty
        self.unit = unit
        
    def __repr__(self):
        return str(self)
    
    def __get_ustr(self, num:str, unum:str, n:int)->str:
        if n == 0:
            if self.unit == '': return f"{num} ± {unum}"
            else: return f"({num} ± {unum}) " + self.unit
            
        elif n == 1:
            if self.unit == '': return f"({num} ± {unum})x10"
            else: return f"({num} ± {unum})x10 " + self.unit
        
        else:
            if self.unit == '': return f"({num} ± {unum})x10^{n}"
            else: return f"({num} ± {unum})x10^{n} " + self.unit
    
    def __get_ustr_latex(self, num:str, unum:str, n:int)->str:
        if n == 0:
            if self.unit == '': return f"${num} \pm {unum}$"
            else: return f"$({num} \pm {unum})\ \mathrm{{{self.unit}}}$"
            
        elif n == 1:
            if self.unit == '': return f"$({num} \pm {unum})\\times 10$"
            else: return f"$({num} \pm {unum})\\times 10\ \mathrm{{{self.unit}}}$"
        
        else:
            if self.unit == '': return f"$({num} \pm {unum})\ \\times 10^{{{n}}}$"
            else: return f"$({num} \pm {unum})\ \\times 10^{{{n}}}\ \mathrm{{{self.unit}}}$"
    
    def __parsing_to_str(self):
        n = 0
        if _round_trad(self.uncertainty) < 1.0:
            while _round_trad(self.uncertainty, n) == 0:n+=1
            
            if n < 4:
                num = _round_trad(self.value, n)
                unum = _round_trad(self.uncertainty, n)
                decinum = len(str(num))-len(str(int(num)))-1 #num의 소숫점 자릿수 = char수 - 정수부 - 소수점
                if decinum < n: num = str(num) + '0'*(n-decinum) #불확도와 소숫점 자릿수 맞추기, 반올림되면 2.1 ± 0.01이 될 수 있음
                return num, unum, 0
            
            else:
                num = int(_round_trad(self.value*pow(10, n)))
                unum = int(_round_trad(self.uncertainty*pow(10, n)))
                return num, unum, n
        
        elif _round_trad(self.uncertainty) < 10.0:
            unum = int(_round_trad(self.uncertainty))
            num = int(_round_trad(self.value))
            return num, unum, 0
        
        else:
            while self.uncertainty/pow(10, n) >= 1.0: n+=1 #불확도가 10의 거듭제곱인 경우 1.0이 나올 수 있으니
            if n > 1: n-=1
            num = int(_round_trad(self.value/pow(10,n)))
            unum = int(_round_trad(self.uncertainty/pow(10,n)))
            return num, unum, n
    
    def __str__(self):
        if self.uncertainty == 0.0:
            if self.unit == '':
                return str(self.value)
            else: return "{} {}".format(self.value, self.unit)
        else:
            num, unum, n = self.__parsing_to_str()
            return self.__get_ustr(num, unum, n)         
    
    def to_latex(self)->str:
        num, unum, n = self.__parsing_to_str()
        return self.__get_ustr_latex(num, unum, n)
    
    def set_unit(self, unit:str):
        self.unit = unit
        return self
    
    def __pos__(self):
        return self
    
    def __neg__(self):
        temp = ufloat(0, 0)
        temp.value = 0 - self.value
        temp.uncertainty = self.uncertainty
        temp.unit = self.unit
        return temp
    
    def add(self, other):
        temp = ufloat(0, 0)
        if type(other) is ufloat:
            temp.value = self.value + other.value
            temp.uncertainty = math.sqrt(self.uncertainty**2 + other.uncertainty**2)
        else:
            temp.value = self.value + other
            temp.uncertainty = self.uncertainty
        return temp
    
    def __add__(self, other):
        return self.add(other)
    
    def __radd__(self, other):
        return self.add(other)
    
    
    def sub(self, other):
        temp = ufloat(0, 0)
        if type(other) is ufloat:
            temp.value = self.value - other.value
            temp.uncertainty = math.sqrt(self.uncertainty**2 + other.uncertainty**2)
        else:
            temp.value = self.value - other
            temp.uncertainty = self.uncertainty
        return temp
    
    def __sub__(self, other):
        return self.sub(other)
    
    def __rsub__(self, other):
        temp = ufloat(0, 0)
        if type(other) is ufloat:
            temp.value =  other.value - self.value
            temp.uncertainty = math.sqrt(self.uncertainty**2 + other.uncertainty**2)
        else:
            temp.value = other - self.value
            temp.uncertainty = self.uncertainty
            temp.unit = self.unit
        return temp
    
    
    
    def mul(self, other):
        temp = ufloat(0, 0)
        if type(other) is ufloat:
            temp.value = self.value * other.value
            temp.uncertainty = math.sqrt( (other.value*self.uncertainty)**2 + (self.value*other.uncertainty)**2 )
        else:
            temp.value = self.value * other
            temp.uncertainty = self.uncertainty * other
            temp.unit = self.unit
        return temp
    
    def __mul__(self, other):
        return self.mul(other)
    
    def __rmul__(self, other):
        return self.mul(other)
    
    
    def div(self, other):
        temp = ufloat(0, 0)
        if type(other) is ufloat:
            temp.value = self.value / other.value
            temp.uncertainty = math.sqrt( ((self.uncertainty/self.value)**2 + (other.uncertainty/other.value)**2)*temp.value**2 )
        else:
            temp.value = self.value / other
            temp.uncertainty = self.uncertainty / other
            temp.unit = self.unit
        return temp
    
    def __truediv__(self, other):
        return self.div(other)
    
    def rdiv(self, other):
        temp = ufloat(0, 0)
        if type(other) is ufloat:
            temp.value = other.value / self.value
            temp.uncertainty = math.sqrt( ((self.uncertainty/self.value)**2 + (other.uncertainty/other.value)**2)*temp.value**2 )
        else:
            temp.value = other / self.value
            temp.uncertainty = abs(self.uncertainty/(self.value**2))
            temp.unit = self.unit
        return temp
    
    def __rtruediv__(self, other):
        return self.rdiv(other)
        
    def __pow__(self, n):
        if n == 1: return self
        
        temp = ufloat(0, 0)
        temp.value = self.value**n
        temp.uncertainty = abs(n*(self.value)**(n-1))*self.uncertainty
        return temp

def set_unit(x:ufloat, unit:str):
    if type(x) is ufloat:
        x.unit = unit
        return x
    elif type(x) is list or type(x) is numpy.ndarray:
        return [set_unit(i, unit) for i in x]
    else: raise TypeError("Error Type")    

#expotential and logarithm
def exp(x):
    if type(x) is ufloat:
        temp = ufloat(0, 0)
        temp.value = math.exp(x.value)
        temp.uncertainty = temp.value * x.uncertainty
        return temp
    
    else:
        return math.exp(x)

def log(x, base = math.e):
    if type(x) is ufloat:
        if x.value <= 0.0: raise ValueError("math domain error")
        temp = ufloat(0, 0)
        temp.value = math.log(x.value, base)
        temp.uncertainty = abs(x.uncertainty/(x.value*math.log(base)))
        return temp
    else:
        if x <= 0.0: raise ValueError("math domain error")
        return math.log(x, base)

def log10(x):
    return log(x, 10)

def log2(x):
    return log(x, 2)

#sqrt
def sqrt(x):
    if type(x) is ufloat:
        if x.value < 0: raise ValueError("math domain error")
        temp = ufloat(0, 0)
        temp.value = math.sqrt(x.value)
        temp.uncertainty = x.uncertainty/(2*temp.value)
        return temp
    else:
        if x < 0: raise ValueError("math domain error")
        return math.sqrt(x)

#trigonometry function
def sin(x):
    """sin

    Args:
        x (Any): ufloat or float measured in radian
    """
    if type(x) is ufloat:
        temp = ufloat(0, 0)
        temp.value = math.sin(x.value)
        temp.uncertainty = abs(x.uncertainty * math.cos(x.value))
        return temp
    else:
        return math.sin(x)

#inverse trigonometry function
def csc(x):
    """csc
    
    Args:
        x (Any): ufloat or float measured in radian
    """
    if type(x) is ufloat:
        temp = ufloat(0, 0)
        temp.value = 1/math.sin(x.value)
        temp.uncertainty = abs(x.uncertainty*math.cos(x.value)/(math.sin(x.value))**2)
        return temp
    else:
        return 1/math.sin(x)

class ufunc:
    def __init__(self, function, symbols:list):
        """sympy based ufloat function

        Args:
            function (Sympy.symbol): Sympy symbol function
            symbols (list): Sympy symbol list
        """
        self.function = function
        self.symbols = symbols
        
        self.partials = []
        for x in self.symbols: self.partials.append(self.function.diff(x).simplify())
        
    def __repr__(self):
        return str(self.function)
    
    def _repr_latex_(self):
        return self.function._repr_latex_()
    
    def caculate(self, ufloats:list, unit = ''):
        if(len(self.partials) != len(ufloats)): raise ValueError("Missing Variables")
        
        symbol_dict = {symbol:ufloats[i].value for i, symbol in enumerate(self.symbols) }
        value = float(self.function.subs(symbol_dict))
        uvalue = 0
        for i, iter in enumerate(self.partials): uvalue += (iter.subs(symbol_dict)*ufloats[i].uncertainty)**2
        uvalue = float(sympy.sqrt(uvalue))
        return ufloat(value, uvalue, unit)
    
    def f(self, ufloats:list, unit = ''):
        return self.caculate(ufloats, unit)
