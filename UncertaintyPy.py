import numpy
import sympy
def _round_trad(value:float, n:int=0):
    if n < 0: n = 0
    if value > 0:
        return int(value*pow(10, n) + 0.5)/pow(10, n)
    else:
        return int(value*pow(10, n) - 0.5)/pow(10, n)    

#나중에 단순 사칙 연산은 ufunc을 사용하지 않고 계산할 수 있게 매서드 추가
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

def symbols(symbol:str):
    """sympy symbols

    Args:
        symbol (str): symbol string

    Returns:
        Sympy.symbol: Sympy symbols
    """
    return sympy.symbols(symbol)

class ufunc:
    def __init__(self, function, symbols:list):
        self.function = function
        self.symbols = symbols
        
        self.partials = []
        for x in self.symbols: self.partials.append(self.function.diff(x).simplify())
    
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
