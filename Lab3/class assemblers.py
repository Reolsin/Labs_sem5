def _OR(first, second) -> Expression:
    if type(first) == VAL and type(second) == VAL:
        if first.type == bool and second.type == bool:
            return VAL(bool, first.ident or second.ident)
        elif first.type == int or second.type == int:
            raise Exception('Incorrect types.')
        else:
            return OR(first, second)
    else:
        return OR(first, second)

def _GT(first, second) -> Expression:
    if type(first) == VAL and type(second) == VAL:
        if first.type == int and second.type == int:
            return VAL(bool, first.ident > second.ident)
        elif first.type == bool or second.type == bool:
            raise Exception('Incorrect types.')
        else:
            return GT(first, second)
    else:
        return GT(first, second)

def _LT(first, second) -> Expression:
    if type(first) == VAL and type(second) == VAL:
        if first.type == int and second.type == int:
            return VAL(bool, first.ident < second.ident)
        elif first.type == bool or second.type == bool:
            raise Exception('Incorrect types.')
        else:
            return LT(first, second)
    else:
        return LT(first, second)

def _NOT(first) -> Expression:
    if type(first) == VAL:
        if first.type == bool:
            return VAL(bool, not first.ident)
        elif first.type == int:
            raise Exception('Incorrect types.')
        else:
            return NOT(first)
    else:
        return NOT(first)

def _INC(first) -> Expression:
    if (type(first) == VAL and first.type == Var) or type(first) == Brackets:
        return INC(first)
    else:
        raise Exception('Incorrect types.')

def _DEC(first) -> Expression:
    if type(first) == VAL and first.type == Var:
        return DEC(first)
    else:
        raise Exception('Incorrect types.')
