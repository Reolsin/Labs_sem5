#declarations
'''
UINT int
PRINT int
UINT int = 5
PRINT int
CUINT cint = 5
PRINT cint
1DARRAYOFUINT arrint1 = [1, 2, 3]
PRINT arrint1
2DARRAYOFUINT arrint2 = [1, arrint1(2), int; ; cint, cint, 1]
PRINT arrint2
BOOLEAN b
PRINT b
BOOLEAN b = FALSE
PRINT b
CBOOLEAN cb = FALSE
PRINT cb
1DARRAYOFBOOL arrbool1 = [TRUE, cb]
PRINT arrbool1
2DARRAYOFBOOL arrbool2 = [cb, b; ; ;TRUE, arrbool1(1)]
PRINT arrbool2
'''
#arrays
'''
UINT a
1DARRAYOFUINT a1 = [4, 5, 6]
PRINT a1
2DARRAYOFUINT a2 = [1, 2, 3; 3, 2, 1; ]
PRINT a2
1DARRAYOFBOOL b1 = [TRUE, FALSE]
PRINT b1
2DARRAYOFBOOL b2 = [TRUE, FALSE; ; ;TRUE, FALSE]
PRINT b2

EXTEND1 a1 4
PRINT a1
a1(3) = 5
PRINT a1
UINT a = a1(3)
PRINT a
a = INC a1(0)
PRINT a
PRINT a1
a = SIZE1 a1
PRINT a

EXTEND1 a2 4
PRINT a2
EXTEND2 a2 2 4
PRINT a2
a2(2,3) = 5
PRINT a2
a = a2(0,0)
PRINT a
a = INC a2(0,0)
PRINT a
PRINT a2
a = SIZE1 a2
PRINT a
a = SIZE2 a2 2
PRINT a
a2(1) = a1
PRINT a2
a1 = a2(0)
PRINT a1
'''

#assign-exprs
text = '''
BOOLEAN a
a = 4 GT 5
PRINT a
a = 4 LT 5
PRINT a
a = FALSE OR TRUE
PRINT a
a = NOT FALSE
PRINT a
UINT b = 5
b = INC b
PRINT b
b = DEC b
PRINT b
'''
#func arrays
'''
r = 0 FUNCTION f(a = 0) {
    1DARRAYOFUINT a1 = [4, 5, 6]
    PRINT a1
    2DARRAYOFUINT a2 = [1, 2, 3; 3, 2, 1; ]
    PRINT a2
    1DARRAYOFBOOL b1 = [TRUE, FALSE]
    PRINT b1
    2DARRAYOFBOOL b2 = [TRUE, FALSE; ; ;TRUE, FALSE]
    PRINT b2

    EXTEND1 a1 4
    PRINT a1
    a1(3) = 5
    PRINT a1
    UINT a = a1(3)
    PRINT a
    a = INC a1(0)
    PRINT a
    PRINT a1
    a = SIZE1 a1
    PRINT a

    EXTEND1 a2 4
    PRINT a2
    EXTEND2 a2 2 4
    PRINT a2
    a2(2,3) = 5
    PRINT a2
    a = a2(0,0)
    PRINT a
    a = INC a2(0,0)
    PRINT a
    PRINT a2
    a = SIZE1 a2
    PRINT a
    a = SIZE2 a2 2
    PRINT a
    a2(1) = a1
    PRINT a2
    a1 = a2(0)
    PRINT a1
}
UINT a
[a] = f()
'''
#func assign-exprs
'''
r = 0 FUNCTION f(a = FALSE) {
    a = 4 GT 5
    PRINT a
    a = 4 LT 5
    PRINT a
    a = FALSE OR TRUE
    PRINT a
    a = NOT FALSE
    PRINT a
    UINT b = 5
    b = INC b
    PRINT b
    b = DEC b
    PRINT b
}
UINT a
[a] = f()
'''
#func call
'''
[r1 = 0, r2 = 5] FUNCTION f(a1 = 0, a2 = 5) {
    PRINT r1
    PRINT r2
    INC a1
    PRINT a1
    PRINT a2
}
UINT a
UINT b
[a, b] = f(1, 1)
PRINT a
PRINT b
[,] = f(, )

[a, ] = f(b, )
PRINT a
PRINT b

'''



#factorial
'''
UINT a
res = 0 FUNCTION sum(first = 0, second = 0) {
    WHILE second GT 0 DO {
        INC first
        DEC second
        }
    res = first
}

res = 0 FUNCTION mul(f = 0, s = 0) {
    INC s
    WHILE (DEC s) GT 0 DO {
        [res] = sum(res, f)
    }
}

res = 0 FUNCTION factorial(int = 1) {
    UINT tmp = int
    IF int GT 1 {
        [tmp] = factorial(DEC tmp)
        [res] = mul(int, tmp)
    } ELSE {
        res = 1
    }
}

res = 1 FUNCTION while_factorial(int = 1) {
    UINT i = 1
    WHILE i LT int DO {
        INC i
        [res] = mul(res, i)
    }
}

[a] = sum(5, 5)
PRINT a
[a] = mul(5, 5)
PRINT a
[a] = factorial(8)
PRINT a
[a] = while_factorial(4)
PRINT a
'''

#robot prog
'''
WHILE LEFT DO BACK

WHILE TRUE DO {
    IF RIGHT {
        WHILE LEFT DO {}
    }
}
'''

#fibonachi
'''
res = 0 FUNCTION sum(first = 0, second = 0) {
    WHILE second GT 0 DO {
        INC first
        DEC second}
    res = first
}
res = 0 FUNCTION fib(int = 1) {
    UINT b = 1
    UINT t
    WHILE b LT int DO {
        PRINT b
        t = b
        [b] = sum(res,b)
        res = t
        }
    }

UINT a
[a] = fib(9)

'''
