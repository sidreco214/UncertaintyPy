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
        self.value = value
        self.uncertainty = uncertainty
        self.unit = unit
        
    def __repr__(self):
        return str(self)
    
    def __str__(self):
        if self.unit == '':
            self._formstr = "{} ± {}"
            self._formPstr = "({} ± {})×10^{}"
        else:
            self._formstr = "({} ± {}) " + self.unit
            self._formPstr = "({} ± {})×10^{} " + self.unit
        
        return self.__to_str()
    
    def __to_str(self)->str:
        if _round_trad(self.uncertainty) < 1:
            n = 0
            while _round_trad(self.uncertainty, n) == 0:n+=1
            
            if n < 4:
                num = _round_trad(self.value, n)
                unum = _round_trad(self.uncertainty, n)
                decinum = len(str(num))-len(str(int(num)))-1 #num의 소숫점 자릿수
                if decinum < n: num = str(num) + '0'*(n-decinum) #불확도와 소숫점 자릿수 맞추기
                return self._formstr.format(num, unum)
            
            else:
                num = _round_trad(self.value*pow(10, n))
                unum = _round_trad(self.uncertainty*pow(10, n))
                return self._formPstr.format(num, unum, n)
        
        elif _round_trad(self.uncertainty) < 10:
            unum = int(_round_trad(self.uncertainty))
            num = int(_round_trad(self.value))
            return self._formstr.format(num, unum)
        
        else:
            n = 0
            while self.uncertainty/pow(10, n) > 1.0: n+=1
            
            if n < 4:
                num = _round_trad(self.value/pow(10,n))*pow(10, n)
                unum = _round_trad(self.uncertainty/pow(10,n))*pow(10, n)
                return self._formstr.format(num, unum)
            
            else:
                num = _round_trad(self.value/pow(10,n))
                unum = _round_trad(self.uncertainty/pow(10,n))
                return self._formPstr.format(num, unum, n)
    
    def to_latex(self)->str:
        if self.unit == '':
            self._formstr = "${} \pm {}$"
            self._formPstr = "$({} \pm {})\ \\times 10^{{{}}}$"
        else:
            self._formstr = "$({} ± {})\ \mathrm{{" + self.unit + "}}$"
            self._formPstr = "$({} \pm {})\ \\times 10^{{{}}}\ \mathrm{{" + self.unit + "}}$"
        return self.__to_str()
    
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
        if type(other) == type(self):
            temp.value = self.value + other.value
            temp.uncertainty = math.sqrt(self.uncertainty**2 + other.uncertainty**2)
        else:
            temp.value = self.value + other
            temp.uncertainty = self.uncertainty
            temp.unit = self.unit
        return temp
    
    def __add__(self, other):
        return self.add(other)
    
    def __radd__(self, other):
        return self.add(other)
    
    
    def sub(self, other):
        temp = ufloat(0, 0)
        if type(other) == type(self):
            temp.value = self.value - other.value
            temp.uncertainty = math.sqrt(self.uncertainty**2 + other.uncertainty**2)
        else:
            temp.value = self.value - other
            temp.uncertainty = self.uncertainty
            temp.unit = self.unit
        return temp
    
    def __sub__(self, other):
        return self.sub(other)
    
    def __rsub__(self, other):
        temp = ufloat(0, 0)
        if type(other) == type(self):
            temp.value =  other.value - self.value
            temp.uncertainty = math.sqrt(self.uncertainty**2 + other.uncertainty**2)
        else:
            temp.value = other - self.value
            temp.uncertainty = self.uncertainty
            temp.unit = self.unit
        return temp
    
    
    
    def mul(self, other):
        temp = ufloat(0, 0)
        if type(other) == type(self):
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
        if type(other) == type(self):
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
        if type(other) == type(self):
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
    x.unit = unit
    return x

#불확도 계산도 연쇄가 되니, sin, cos 이런거 다 만들면 sympy 안빌려도 되는거 아님?

class ufunc:
    def __init__(self, function, symbols:list):
        """ufunc

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
        value = self.function.subs(symbol_dict)
        uvalue = 0
        for i, iter in enumerate(self.partials): uvalue += (iter.subs(symbol_dict)*ufloats[i].uncertainty)**2
        uvalue = float(sympy.sqrt(uvalue))
        return ufloat(value, uvalue, unit)
    
    def f(self, ufloats:list, unit = ''):
        return self.caculate(ufloats, unit)
