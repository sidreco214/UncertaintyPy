import math
import numpy
import sympy
import pandas

def _round_trad(value:float, n:int=0)->float:
    """traditional round

    Args:
        value (float): value
        n (int, optional): The digit of display under decimical point. Defaults to 0.

    Returns:
        float: Result
    """
    if n < 0: n = 0
    if value > 0:
        return int(value*pow(10, n) + 0.5)/pow(10, n)
    else:
        return int(value*pow(10, n) - 0.5)/pow(10, n)

def _is_numpy_int(value):
    flag = False
    for iter in [numpy.int_, numpy.int0, numpy.int8, numpy.int16, numpy.int32, numpy.int64, numpy.intc]:
        flag = flag or (type(value) is iter)
        if flag is True: break
    return flag

def _is_numpy_float(value):
    flag = False
    for iter in [numpy.float_, numpy.float16, numpy.float32, numpy.float64]:
        flag = flag or (type(value) is iter)
        if flag is True: break
    return flag

class ufloat:
    """Uncertainty float"""
    def __init__(self, value:float, uncertainty:float, unit:str = '') -> None:
        """Initialize ufloat class

        Args:
            value (float): value
            uncertainty (float): uncertainty
            unit (str, optional): displayed unit. Defaults to ''.

        Raises:
            TypeError: unit must be str
            TypeError: value must be number
            TypeError: uncertainty must be number
            ValueError: uncertainty must be unsigned number
        """
        if not type(unit) is str:
            raise TypeError("unit must be str")
        
        if not(type(value) is float or type(value) is int):
            if not (_is_numpy_int(value) or _is_numpy_float(value)):
                raise TypeError("value must be number")
        
        if not(type(uncertainty) is float or type(uncertainty) is int):
            if not (_is_numpy_int(value) or _is_numpy_float(value)):
                raise TypeError("uncertainty must be number")
        
        if uncertainty < 0:
            raise ValueError("uncertainty must be unsigned number")
        
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
        
        elif n > 0:
            if self.unit == '': return f"({num} ± {unum})x10^{n}"
            else: return f"({num} ± {unum})x10^{n} " + self.unit
        
        else:
            if self.unit == '': return f"({num} ± {unum})x10^({n})"
            else: return f"({num} ± {unum})x10^({n}) " + self.unit
    
    def __get_ustr_latex(self, num:str, unum:str, n:int)->str:
        if n == 0:
            if self.unit == '': return f"${num} \pm {unum}$"
            else: return f"$({num} \pm {unum})\ \mathrm{{{self.unit}}}$"
            
        elif n == 1:
            if self.unit == '': return f"$({num} \pm {unum})\\times 10$"
            else: return f"$({num} \pm {unum})\\times 10\ \mathrm{{{self.unit}}}$"
        
        else:
            if self.unit == '': return f"$({num} \pm {unum}) \\times 10^{{{n}}}$"
            else: return f"$({num} \pm {unum})\\times 10^{{{n}}}\ \mathrm{{{self.unit}}}$"
    
    def __parsing_to_str(self):
        n = 0
        if _round_trad(self.uncertainty) <= 1.0:
            while pow(10, -n) >= self.uncertainty: n+=1
            
            if n < 4:
                unum = _round_trad(self.uncertainty, n)
                if pow(10, -n+1) <= unum: n-=1 #반올림되어 unum 소숫점 자릿수 감소할 수 있음
                num = _round_trad(self.value, n)
                
                decinum = len(str(num))-len(str(int(num)))-1 #num의 소숫점 자릿수 = char수 - 정수부 - 소수점
                if decinum < n: num = str(num) + '0'*(n-decinum) #불확도와 소숫점 자릿수 맞추기, 반올림되면 2.1 ± 0.01이 될 수 있음
                if unum < 1.0: return str(num), str(unum), 0
                else:          return str(int(num)), str(int(unum)), 0
            
            else:
                unum = int(_round_trad(self.uncertainty*pow(10, n))) #self.uncertainty*pow(10, n) = 9.8인 경우 반올림하면 10되니
                if unum >= 10: n-=1
                
                num = int(_round_trad(self.value*pow(10, n)))
                unum = int(_round_trad(self.uncertainty*pow(10, n)))
                return str(num), str(unum), -n
        
        elif _round_trad(self.uncertainty) < 10.0:
            unum = int(_round_trad(self.uncertainty))
            num = int(_round_trad(self.value))
            return str(num), str(unum), 0
        
        else:
            while self.uncertainty/pow(10, n) >= 1.0: n+=1 #불확도가 10의 거듭제곱인 경우 1.0이 나올 수 있으니
            if n > 1: n-=1
            num = int(_round_trad(self.value/pow(10,n)))
            unum = int(_round_trad(self.uncertainty/pow(10,n)))
            return str(num), str(unum), n
    
    def __str__(self):
        if self.uncertainty == 0.0:
            if self.unit == '':
                return str(self.value)
            else: return "{} {}".format(self.value, self.unit)
        else:
            num, unum, n = self.__parsing_to_str()
            return self.__get_ustr(num, unum, n)         
    
    def to_latex(self)->str:
        if self.uncertainty == 0.0:
            if self.unit == '':
                return str(self.value)
            else: return "${}\ \mathrm{{{}}}$".format(self.value, self.unit)
        else:
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
        if type(other) is undarray:
            return other.add(self)
        
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
        if type(other) is undarray:
            return other.__rsub__(self)
        
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
        return temp
    
    
    def mul(self, other):
        if type(other) is undarray:
            return other.mul(self)
        
        temp = ufloat(0, 0)
        if type(other) is ufloat:
            temp.value = self.value * other.value
            temp.uncertainty = math.sqrt( (other.value*self.uncertainty)**2 + (self.value*other.uncertainty)**2 )
        else:
            temp.value = self.value * other
            temp.uncertainty = self.uncertainty * other
        return temp
    
    def __mul__(self, other):
        return self.mul(other)
    
    def __rmul__(self, other):
        return self.mul(other)
    
    
    def div(self, other):
        if type(other) is undarray:
            return other.rdiv(self)
        
        temp = ufloat(0, 0)
        if type(other) is ufloat:
            temp.value = self.value / other.value
            temp.uncertainty = math.sqrt( ((self.uncertainty/self.value)**2 + (other.uncertainty/other.value)**2)*temp.value**2 )
        else:
            temp.value = self.value / other
            temp.uncertainty = self.uncertainty / other
        return temp
    
    def __truediv__(self, other):
        return self.div(other)
    
    def rdiv(self, other):
        if type(other) is undarray:
            return other.div(self)
        
        temp = ufloat(0, 0)
        if type(other) is ufloat:
            temp.value = other.value / self.value
            temp.uncertainty = math.sqrt( ((self.uncertainty/self.value)**2 + (other.uncertainty/other.value)**2)*temp.value**2 )
        else:
            temp.value = other / self.value
            temp.uncertainty = abs(self.uncertainty/(self.value**2))
        return temp
    
    def __rtruediv__(self, other):
        return self.rdiv(other)
        
    def __pow__(self, n):
        if n == 1: return self
        
        temp = ufloat(0, 0)
        temp.value = self.value**n
        temp.uncertainty = abs(n*(self.value)**(n-1))*self.uncertainty
        return temp

class undarray(numpy.ndarray):
    """undarray\n
    inherited from numpy.ndarray

    Args:
        numpy.ndarray (class): numpy's ndarray
    """
    def __new__(cls, input_array, info=None):
        if not type(input_array[0]) is ufloat:
            raise TypeError("element must be ufloat and 1D")
        
        obj = numpy.asarray(input_array).view(cls)
        obj.info = info
        return obj
    
    def __array_finalize__(self, obj):
        if obj is None: return
        self.info = getattr(obj, "info", None)
    
    def get_value(self):
        return numpy.array([x.value for x in self])
    
    def get_uncertainty(self):
        return numpy.array([x.uncertainty for x in self])
    
    def set_unit(self, unit:str):
        if not type(unit) is str:
            raise TypeError("unit must be str")
        
        return uarray([x.set_unit(unit) for x in self])
    
    def add(self, other):
        if not type(other) is ufloat: return numpy.ndarray.__add__(self, other)
        else: return undarray(numpy.array([element + other for element in self]))
    
    def __add__(self, other):
        return self.add(other)
    
    def __radd__(self, other):
        return self.add(other)
    
    
    def sub(self, other):
        if not type(other) is ufloat: return numpy.ndarray.__sub__(self, other)
        else: return undarray(numpy.array([element - other for element in self]))
    
    def __sub__(self, other):
        return self.sub(other)
    
    def __rsub__(self, other):
        return -self.sub(other)
    
    
    def mul(self, other):
        if not type(other) is ufloat: return numpy.ndarray.__mul__(self, other)
        else: return undarray(numpy.array([element*other for element in self]))
    
    def __mul__(self, other):
        return self.mul(other)
    
    def __rmul__(self, other):
        return self.mul(other)
    
    
    def div(self, other):
        if not type(other) is ufloat: return numpy.ndarray.__truediv__(self, other)
        else: return undarray(numpy.array([element/other for element in self]))
    
    def __truediv__(self, other):
        return self.div(other)
    
    def rdiv(self, other):
        if not type(other) is ufloat: return numpy.ndarray.__rtruediv__(self, other)
        else:return undarray(numpy.array([other/element for element in self]))
    
    def __rtruediv__(self, other):
        return self.rdiv(other)


def uarray(lis:list)->undarray:
    """Return undarray

    Args:
        lis (list): list contained ufloat

    Raises:
        TypeError: lis must be list
        TypeError: lis must contain ufloat

    Returns:
        undarray: undarray
    """
    if not type(lis) is list: raise TypeError("lis must be list")
    if not type(lis[0]) is ufloat: raise TypeError("lis must contain ufloat") 
    return undarray(numpy.array(lis))

def set_unit(x:ufloat | list | undarray, unit:str)->(ufloat | list | undarray | None):
    """Set Unit

    Args:
        x (ufloat | list | undarray): target to set unit
        unit (str): displayed unit

    Raises:
        TypeError: type error

    Returns:
        (ufloat | list | undarray | None): Result 
    """
    if type(x) is ufloat:
        x.unit = unit
        return x
    
    elif type(x) is list:
        if type(x[0]) is ufloat:
            return [set_unit(iter, unit) for iter in x]
    
    elif type(x) is undarray:
        return uarray([set_unit(i, unit) for i in x])
    else: raise TypeError("Error Type") 

#undarray caculation
def sum(x:undarray):
    if not type(x) is undarray:
        raise TypeError("x must be undarray")
    
    temp = ufloat(0, 0)
    for iter in x:
        temp += iter
    
    return temp

def mean(x:undarray):
    if not type(x) is undarray:
        raise TypeError("x must be undarray")
    
    return sum(x)/len(x)

def average(x:undarray):
    return mean(x)

def std_p(x:undarray)->float:
    """Caculate Population Standard Distribution

    Args:
        x (undarray): undarray

    Raises:
        TypeError: x must be undarray
        ValueError: undarray must be contained 2 or more elements

    Returns:
        float: Population Standard Distribution
    """
    if not type(x) is undarray:
        raise TypeError("x must be undarray")
    m = mean(x)
    n = len(x)
    if n < 2: raise ValueError("undarray must be contained 2 or more elements")
    return sqrt(sum((x - m)**2)/n)

def std_s(x:undarray)->float:
    """Caculate Sample Standard Distribution

    Args:
        x (undarray): undarray

    Raises:
        TypeError: x must be undarray
        ValueError: undarray must be contained 2 or more elements

    Returns:
        float: Sample Standard Distribution
    """
    if not type(x) is undarray:
        raise TypeError("x must be undarray")
    m = mean(x)
    n = len(x)
    if n < 2: raise ValueError("undarray must be contained 2 or more elements")
    return sqrt(sum((x - m)**2)/(n-1))

#expotential and logarithm
def exp(x:ufloat | undarray | float):
    if type(x) is ufloat:
        temp = ufloat(0, 0)
        temp.value = math.exp(x.value)
        temp.uncertainty = temp.value * x.uncertainty
        return temp
    
    elif type(x) is list:
        if type(x[0]) is ufloat:
            return uarray([exp(iter) for iter in x])
    
    elif type(x) is undarray:
        return uarray([exp(iter) for iter in x])
    
    else:
        return math.exp(x)

def log(x:ufloat | undarray | float, base = math.e):
    if type(x) is ufloat:
        if x.value <= 0.0: raise ValueError("math domain error")
        temp = ufloat(0, 0)
        temp.value = math.log(x.value, base)
        temp.uncertainty = abs(x.uncertainty/(x.value*math.log(base)))
        return temp
    
    elif type(x) is list:
        if type(x[0]) is ufloat:
            return uarray([log(iter) for iter in x])
    
    elif type(x) is undarray:
        return uarray([log(iter) for iter in x])
    
    else:
        if x <= 0.0: raise ValueError("math domain error")
        return math.log(x, base)

def log10(x:ufloat | undarray | float):
    return log(x, 10)

def log2(x:ufloat | undarray | float):
    return log(x, 2)

#sqrt
def sqrt(x:ufloat | undarray | float):
    if type(x) is ufloat:
        if x.value < 0: raise ValueError("math domain error")
        temp = ufloat(0, 0)
        temp.value = math.sqrt(x.value)
        temp.uncertainty = x.uncertainty/(2*temp.value)
        return temp
    
    elif type(x) is list:
        if type(x[0]) is ufloat:
            return uarray([sqrt(iter) for iter in x])
    
    elif type(x) is undarray:
        return uarray([sqrt(iter) for iter in x])
    
    else:
        if x < 0: raise ValueError("math domain error")
        return math.sqrt(x)

#trigonometry function
def sin(x:ufloat | undarray | float):
    """sin

    Args:
        x (Any): ufloat or float measured in radian
    """
    if type(x) is ufloat:
        temp = ufloat(0, 0)
        temp.value = math.sin(x.value)
        temp.uncertainty = abs(x.uncertainty * math.cos(x.value))
        return temp
    
    elif type(x) is list:
        if type(x[0]) is ufloat:
            return uarray([sin(iter) for iter in x])
    
    elif type(x) is undarray:
        return uarray([sin(iter) for iter in x])
    
    else:
        return math.sin(x)

def cos(x:ufloat | undarray | float):
    """cos

    Args:
        x (Any): ufloat or float measured in radian
    """
    if type(x) is ufloat:
        temp = ufloat(0, 0)
        temp.value = math.cos(x.value)
        temp.uncertainty = abs(math.sin(x.value) * x.uncertainty)
        return temp
    
    elif type(x) is list:
        if type(x[0]) is ufloat:
            return uarray([cos(iter) for iter in x])
    
    elif type(x) is undarray:
        return uarray([cos(iter) for iter in x])
    
    else:
        return math.cos(x)

def tan(x:ufloat | undarray | float):
    """tan

    Args:
        x (Any): ufloat or float measured in radian
    """
    if type(x) is ufloat:
        temp = ufloat(0, 0)
        temp.value = math.tan(x.value)
        temp.uncertainty = abs(x.uncertainty/math.cos(x.value)**2)
        return temp
    
    elif type(x) is list:
        if type(x[0]) is ufloat:
            return uarray([tan(iter) for iter in x])
    
    elif type(x) is undarray:
        return uarray([tan(iter) for iter in x])
    
    else:
        return math.tan(x)

def csc(x:ufloat | undarray | float):
    """csc
    
    Args:
        x (Any): ufloat or float measured in radian
    """
    if type(x) is ufloat:
        temp = ufloat(0, 0)
        temp.value = 1/math.sin(x.value)
        temp.uncertainty = abs(x.uncertainty*math.cos(x.value)/(math.sin(x.value))**2)
        return temp
    
    elif type(x) is list:
        if type(x[0]) is ufloat:
            return uarray([csc(iter) for iter in x])
    
    elif type(x) is undarray:
        return uarray([csc(iter) for iter in x])
    
    else:
        return 1/math.sin(x)


def sec(x:ufloat | undarray | float):
    """sec
    
    Args:
        x (Any): ufloat or float measured in radian
    """
    if type(x) is ufloat:
        temp = ufloat(0, 0)
        temp.value = 1/math.cos(x.value)
        temp.uncertainty = abs(x.uncertainty*math.sin(x.value)/(math.cos(x.value))**2)
        return temp
    
    elif type(x) is list:
        if type(x[0]) is ufloat:
            return uarray([sec(iter) for iter in x])
    
    elif type(x) is undarray:
        return uarray([sec(iter) for iter in x])
    
    else:
        return 1/math.cos(x)

def cot(x:ufloat | undarray | float):
    """cot
    
    Args:
        x (Any): ufloat or float measured in radian
    """
    if type(x) is ufloat:
        temp = ufloat(0, 0)
        temp.value = 1/math.tan(x.value)
        temp.uncertainty = abs(x.uncertainty/math.sin(x.value)**2)
        return temp
    
    elif type(x) is list:
        if type(x[0]) is ufloat:
            return uarray([cot(iter) for iter in x])
    
    elif type(x) is undarray:
        return uarray([cot(iter) for iter in x])
    
    else:
        return 1/math.tan(x)

#inverse trigonometry function
def asin(x:ufloat | undarray | float):
    """Return the arc sine\nThe result is between -pi/2 and pi/2
    
    Args:
        x (Any): ufloat or float measured in radian
    """
    if type(x) is ufloat:
        temp = ufloat(0, 0)
        temp.value = math.asin(x.value)
        temp.uncertainty = x.uncertainty/math.sqrt(1-x.value**2)
        return temp
    
    elif type(x) is list:
        if type(x[0]) is ufloat:
            return uarray([asin(iter) for iter in x])
    
    elif type(x) is undarray:
        return uarray([asin(iter) for iter in x])
    
    else:
        return math.asin(x)

def acos(x:ufloat | undarray | float):
    """Return the arc cosine.\nThe result is between 0 and pi.
    
    Args:
        x (Any): ufloat or float measured in radian
    """
    if type(x) is ufloat:
        temp = ufloat(0, 0)
        temp.value = math.acos(x.value)
        temp.uncertainty = x.uncertainty/math.sqrt(1-x.value**2)
        return temp
    
    elif type(x) is list:
        if type(x[0]) is ufloat:
            return uarray([acos(iter) for iter in x])
    
    elif type(x) is undarray:
        return uarray([acos(iter) for iter in x])
    
    else:
        return math.acos(x)

def atan(x:ufloat | undarray | float):
    """Return the arc tangent.\nThe result is between -pi/2 and pi/2.
    
    Args:
        x (Any): ufloat or float measured in radian
    """
    if type(x) is ufloat:
        temp = ufloat(0, 0)
        temp.value = math.atan(x.value)
        temp.uncertainty = x.uncertainty/(x.value**2 + 1)
        return temp
    
    elif type(x) is list:
        if type(x[0]) is ufloat:
            return uarray([atan(iter) for iter in x])
    
    elif type(x) is undarray:
        return uarray([atan(iter) for iter in x])
    
    else:
        return math.atan(x)

#hyperbolic function
def sinh(x:ufloat | undarray | float):
    """sinh
    
    Args:
        x (Any): ufloat or float measured in radian
    """
    if type(x) is ufloat:
        temp = ufloat(0, 0)
        temp.value = math.sinh(x.value)
        temp.uncertainty = x.uncertainty*math.cosh(x.value)
        return temp
    
    elif type(x) is list:
        if type(x[0]) is ufloat:
            return uarray([sinh(iter) for iter in x])
    
    elif type(x) is undarray:
        return uarray([sinh(iter) for iter in x])
    
    else:
        return math.sinh(x)

def cosh(x:ufloat | undarray | float):
    """cosh
    
    Args:
        x (Any): ufloat or float measured in radian
    """
    if type(x) is ufloat:
        temp = ufloat(0, 0)
        temp.value = math.cosh(x.value)
        temp.uncertainty = abs(x.uncertainty*math.sinh(x.value))
        return temp
    
    elif type(x) is list:
        if type(x[0]) is ufloat:
            return uarray([cosh(iter) for iter in x])
    
    elif type(x) is undarray:
        return uarray([cosh(iter) for iter in x])
    
    else:
        return math.cosh(x)

def tanh(x:ufloat  | undarray | float):
    """tanh
    
    Args:
        x (Any): ufloat or float measured in radian
    """
    if type(x) is ufloat:
        temp = ufloat(0, 0)
        temp.value = math.tanh(x.value)
        temp.uncertainty = x.uncertainty/math.cosh(x.value)**2
        return temp
    
    elif type(x) is list:
        if type(x[0]) is ufloat:
            return uarray([tanh(iter) for iter in x])
    
    elif type(x) is undarray:
        return uarray([tanh(iter) for iter in x])
    
    else:
        return math.tanh(x)

def csch(x:ufloat | undarray | float):
    """csch
    
    Args:
        x (Any): ufloat or float measured in radian
    """
    if type(x) is ufloat:
        temp = ufloat(0, 0)
        temp.value = 1/math.sinh(x.value)
        temp.uncertainty = abs(x.uncertainty*math.cosh(x.value)/math.sinh(x.value)**2)
        return temp
    
    elif type(x) is list:
        if type(x[0]) is ufloat:
            return uarray([csch(iter) for iter in x])
    
    elif type(x) is undarray:
        return uarray([csch(iter) for iter in x])
    
    else:
        return 1/math.sinh(x)
    
def sech(x:ufloat | undarray | float):
    """sech
    
    Args:
        x (Any): ufloat or float measured in radian
    """
    if type(x) is ufloat:
        temp = ufloat(0, 0)
        temp.value = 1/math.cosh(x.value)
        temp.uncertainty = abs(x.uncertainty*math.sinh(x.value)/math.cosh(x.value)**2)
        return temp
    
    elif type(x) is list:
        if type(x[0]) is ufloat:
            return uarray([sech(iter) for iter in x])
    
    elif type(x) is undarray:
        return uarray([sech(iter) for iter in x])
    
    else:
        return 1/math.cosh(x)

def coth(x:ufloat | undarray | float):
    """coth
    
    Args:
        x (Any): ufloat or float measured in radian
    """
    if type(x) is ufloat:
        temp = ufloat(0, 0)
        temp.value = 1/math.tanh(x.value)
        temp.uncertainty = abs(x.uncertainty/math.sinh(x.value)**2)
        return temp
    
    elif type(x) is list:
        if type(x[0]) is ufloat:
            return uarray([cot(iter) for iter in x])
    
    elif type(x) is undarray:
        return uarray([coth(iter) for iter in x])
    
    else:
        return 1/math.tanh(x)
    
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

class utable:
    def __init__(self, *cols:ufloat):
        self.cols = cols
    
    def to_pandas(self):
        return pandas.DataFrame({key:value for key, value in enumerate(self.cols)})
    
    def to_latex(self, Data_only = True):
        if Data_only is False:
            return self.to_pandas().to_latex()
        
        else:
            data = numpy.array(self.cols)
            temp = str('')
            for iter in data.T:
                string = iter[0].to_latex()
                for i in range(1, len(iter)):
                    string += " & " + iter[i].to_latex()
                temp += string + " \cr\n"
            return temp

class uMLS:
    def __init__(self, x:undarray, y:undarray):
        
        if type(x) is undarray: X = x.get_value()
        else: raise TypeError("x must be undarray")
        
        if type(y) is undarray: Y = y.get_value()
        else: raise TypeError("y must be undarray")
        
        _a = (numpy.mean(X*Y)-numpy.mean(X)*numpy.mean(Y))/(numpy.mean(X**2)-(numpy.mean(X))**2)
        _b = numpy.mean(Y)-_a*numpy.mean(X)
        
        n = len(X)
        if n < 3:
            raise ValueError("The number of data must be more than 2")
        self.s = numpy.sqrt(numpy.sum((Y-(_a*X+_b))**2)/(n-2)) #standard distrubution
        
        _ua = float(self.s*numpy.sqrt(n/(n*numpy.sum(X**2)-(numpy.sum(X))**2)))
        _ub = float(self.s*numpy.sqrt(numpy.sum(X**2)/(n*numpy.sum(X**2)-(numpy.sum(X))**2)))
        
        self.mse = numpy.mean((Y-(_a*X+_b))**2)
        self.rmse = numpy.sqrt(self.mse)
        
        self.a = ufloat(_a, _ua)
        self.b = ufloat(_b, _ub)
        
    def fit(self):
        return (self.a, self.b)
    
    def Std(self):
        return self.s
    
    def Mse(self):
        return self.mse
    
    def Rmse(self):
        return self.rmse
    
    def __str__(self):
        return "y = ax + b, a={}, b={}, RMSE={}".format(self.a, self.b, self.rmse)
    
    def __repr__(self):
        return self.__str__()