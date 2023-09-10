
import sympy
import numpy as np
r = 0 #real
u = 1 #uncertaintity

def symbols(para):
    """sympy symbols
    """
    return sympy.symbols(para)

class setfunc:
    def __init__(self, function, *symbols):
        """Set Function, 계산할 함수를 설정합니다.

        Args:
            function (function): 계산할 함수식(sympy)
            
            *symbols (sympy symbols): 함수식의 변수
        """
        self.func = function
        self.item = len(symbols)
        self.symbols = symbols
        
        self.partials = []
        for x in self.symbols: self.partials.append(self.func.diff(x).simplify()) 
    
    def caculate(self, dict, *uncertainties):
        """함수값과 불확도를 계산해서 리스트로 리턴합니다.
        
            Args:
                dict (dictionary): sympy subs에 전달할 인수
                
                *uncertainties (float): 불확도
        """
        if(self.item != len(uncertainties)): return 0
        value = float(self.func.subs(dict))
        uvalue=0
        for i in range(0,self.item): uvalue += (self.partials[i].subs(dict)*uncertainties[i])**2
        uvalue = float(sympy.sqrt(uvalue))
        return [value, uvalue]
    
def _roundt(num:float):
    """소숫점 첫번째 자리에서 반올림

    Args:
        num (float): 반올림할 값

    Returns:
        int: 소숫점 첫번째 자리에서 반올림하여 리턴합니다.
    """
    if num >= 0: return int(num+0.5)
    else: return int(num-0.5)


def express(lis:list, unit:str = '', style:str = ''):
    """[값1, 불확도1]를 "(값1 ± 불확도1) unit"로 리턴합니다. 만약 2차원 리스트라면 [[값1, 불확도1], [값2, 불확도2], ...]를 ["(값1 ± 불확도1) unit", "(값2 ± 불확도2) unit", ...]으로 리턴합니다.
    
        Args:
            lis (list): 2차원 리스트 [[값1, 불확도1], [값2, 불확도2], ...]
            
            unit (str): 기본값 '', 기본값인 경우 (값1 ± 불확도1) 형식으로 리턴
            
            style (str): 기본값 '', "latex", "noParenthesis"로 지정 가능
        
        Todo:
            11e-6 같은 식으로 데이터가 숫자가 들어오는 경우 제대로 작동하지 않음, str로 바꿔서 e가 있는 지 확인한 후, 값과 불확도를 모두 e가 없도록 10의 거듭제곱을 한 뒤, 마지막에 x10^(-15) 같은 형태로 돌려주는 작업필요
    """
    if style == "latex":
        if unit == '':
            formstr = "$({} \pm {})$"
            formPstr = "$({} \pm {})\\times 10^{}$"
        else:
            formstr = "$({} \pm {})\ \mathrm{{" + unit + "}}$"
            formPstr = "$({} \pm {})\\times 10^{}\ \mathrm{{" + unit + "}}$"
            
    elif style == "noParenthesis":
        if unit == '':
            formstr = "{} ± {}"
            formPstr = "({} ± {})×10^{}"
        else:
            formstr = "({} ± {}) " + unit
            formPstr = "({} ± {})×10^{} " + unit
            
    else:
        if unit == '':
            formstr = "({} ± {})"
            formPstr = "({} ± {})×10^{}"
        else:
            formstr = "({} ± {}) " + unit
            formPstr = "({} ± {})×10^{} " + unit
    
    strlist = []
    
    if type(lis[0]) == float or type(lis[0]) == np.float64: tlis = [lis] #[값, 불확도]와 numpy 호환성
    else: tlis = lis
    
    for element in tlis:
        n=0
        if int(element[u]) < 1:
            #0이 안될때까지 10의 거듭제곱을 곱하다보면 첫 불확도의 소숫점 자릿수를 구할 수 있음
            while int(element[u]*pow(10,n)) == 0: n+=1
            unum = _roundt(element[u]*pow(10,n))/pow(10,n)
            n = len(str(unum))-len(str(int(unum)))-1 #unum의 소숫점 자릿수, 반올림하고나면 달라질 수 있음 ex 0.981
            unum = str(unum)
            
            num = _roundt(element[r]*pow(10,n))/pow(10,n)
            decinum = len(str(num))-len(str(int(num)))-1 #num의 소숫점 자릿수
            if decinum < n: num = str(num) + '0'*(n-decinum)
            else: num = str(num)

            
            strlist.append(formstr.format(num, unum))
        elif int(element[u]) >= 10:
            #0이 되는 순간까지 10의 거듭제곱을 나누다보면, 자릿수+1을 구할 수 있음
            while int(element[u]*pow(10,-n)) != 0: n+=1
            strlist.append(formPstr.format(_roundt(element[r]*pow(10,-n+1))/10, _roundt(element[u]*pow(10,-n+1))/10, n) )
        else: #n=0 인 경우 그대로 소숫점 첫번째 자리에서 반올림하여 표현
            strlist.append(formstr.format(_roundt(element[r]), _roundt(element[u])) )
    
    if type(lis[0]) == float or type(lis[0]) == np.float64: return strlist[0]
    else: return strlist
