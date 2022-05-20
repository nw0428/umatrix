from array import array

def get_matrix_minor(arr,i,j,n):
    a = [arr[n*x:n*x + j] + arr[n*x+j+1:n*x+n] for x in range(n) if x != i]
    if len(a) < 1:
        print(arr, n, a)
    out = a[0]
    for i in range(1, len(a)):
        out = out + a[i]
    return out

def determinant_helper(arr, n):
    #base case for 2x2 matrix
    if n == 1:
        return arr[0]
    if n == 2:
        return arr[0]*arr[3]-arr[2]*arr[1]
    determinant = 0
    for c in range(n):
        a = ((-1)**c) * arr[c]
        b = a * determinant_helper(get_matrix_minor(arr,0,c,n), n-1)
        determinant += b
    return determinant

def transpose_matrix(arr, rows, columns, out):
    for c in range(columns):
        for r in range(rows):
            out.append(arr[r * columns + c])
    return out

def transposeListMatrix(m):
    return list(map(list,zip(*m)))

def inverse_helper(arr, n):
    determinant = determinant_helper(arr, n)
    #special case for 2x2 matrix:
    if n == 1:
        return [[1/arr[0]]]
    if n == 2:
        return [[arr[3]/determinant, -1*arr[1]/determinant], [-1*arr[2]/determinant, arr[0]/determinant]]
    cofactors = []
    for r in range(n):
        cofactorRow = []
        for c in range(n):
            minor = get_matrix_minor(arr,r,c,n)
            cofactorRow.append(((-1)**(r+c)) * determinant_helper(minor, n-1))
        cofactors.append(cofactorRow)
    cofactors = transposeListMatrix(cofactors)
    for r in range(len(cofactors)):
        for c in range(len(cofactors)):
            cofactors[r][c] = cofactors[r][c]/determinant
    return cofactors


class Matrix:
    '''
    Class implementing some basic matrix operations. Hopefully efficient.
    Skipping error handling and checking at the moment.
    Starting with lazy evaluation of transposition
    '''
    @micropython.native
    def __init__(self, type_code='f', initial=None):
        '''
        type_code should be one of 'i' (int), 'f'(float), or 'd'(double)
        initial should be empty, a list, or a list of lists
        '''
        self.type_code = type_code
        self.transposed = False
        if initial:
            if isinstance(initial[0], list):
                self.rows = len(initial)
                self.columns = len(initial[0])
                self.arr = array(type_code)
                for i in initial:
                    self.extend(i)
                return
            else:
                self.rows = 1
                self.columns = len(initial)
                self.arr = array(type_code, initial)
                return
        else:
            self.rows = 0
            self.columns = 0
            self.arr = array(type_code)
            return

    def extend(self, to_add):
        self.arr.extend(array(self.type_code, to_add))

    def add_row(self, row):
        "Adds a row to the matrix"
        self.extend(row)
        if self.columns == 0:
            self.columns = len(row)
        self.rows = self.rows + 1

    def T(self):
        '''
        Transposes the matrix turning columns into rows.
        I think the flag is more efficient if slightly annoying to write
        '''
        out = self.clone()
        out.transposed = not self.transposed
        return out

    def get(self, row, column):
        if self.transposed:
            return self.arr[column * self.columns + row]
        return self.arr[row * self.columns + column]

    def get_rows(self):
        if self.transposed:
            return self.columns
        return self.rows

    def get_columns(self):
        if self.transposed:
            return self.rows
        return self.columns

    # @micropython.native
    def clone(self):
        out = Matrix(self.type_code)
        if self.transposed:
            transpose_matrix(self.arr, self.rows, self.columns, out.arr)
        else:
            out.extend(self.arr)
        out.columns = self.get_columns()
        out.rows = self.get_rows()
        return out

    # @micropython.native
    def __add__(self, other):
        "Adds two matrices. This needs a sanity check for transposition"
        out = self.clone()
        for r in range(other.rows):
            rt = r * other.columns
            for c in range(other.columns):
                out.arr[rt+c] += other.get(r, c)
        return out

    # @micropython.native
    def __mul__(self, other):
        out = None
        if isinstance(other, float) or other.type_code == 'f' or other.type_code == 'd':
            out = Matrix('f')
        else:
            out = Matrix(self.type_code)
        if isinstance(other, float) or isinstance(other, int):
            out.columns = self.columns
            out.rows = self.rows
            for i in self.arr:
                out.arr.append(i * other)
            return out
        # Out will have as many rows as self and as many columns as other
        out.rows = self.get_rows()
        out.columns = other.get_columns()
        for r in range(out.get_rows()):
            for c in range(out.get_columns()):
                cross = 0
                # Would this be faster as a sum of a comprehension?
                for i in range(self.get_columns()):
                    cross += self.get(r, i) * other.get(i, c)
                out.arr.append(cross)
        return out


    # Transposition doesn't change determinant which is nice
    # @micropython.native
    def determinant(self):
        "Only meaningful with square matrices. Skipping that check atm"
        return determinant_helper(memoryview(self.arr), self.rows)

    def get_inverse(self):
        out = Matrix('f')
        out.columns = self.get_columns()
        out.rows = self.get_rows()
        for row in inverse_helper(memoryview(self.arr), self.get_columns()):
            out.extend(row)
        return out

    def __str__(self):
        if self.transposed:
            return str(self.clone())
        out = "[\n"
        for i in range(self.get_rows()):
            out += "["
            for j in range(self.get_columns()):
                out += str(self.arr[i*self.get_columns() + j]) + ","
            out += "],\n"
        out +="]"
        return out

a = Matrix('i', [[3,8],[4,6]])
b = Matrix('i', [[1,2],[3,4]])
c = Matrix('i', [[1,2,5],[3,4,2],[3,2,7]])
# print(a + b)
# print(a * b)
# a.T()
# print(a.clone())
# print(b.get_inverse())
mv = memoryview(c.arr)
# print(get_matrix_minor(mv, 1,1,3))
# print(c.determinant())
# print(c.get_inverse())


x = Matrix('f', [[1, 1],[1, 2],[1,5]])
y = Matrix('f', [5, 10, 25]).T()
# xT = x.T()
# print(xT * x)
# a = (xT * x).get_inverse() * xT * y.T()


def lin_regression(x, y):
    xT = x.T()
    alpha = Matrix('f')
    for i in range(x.get_columns()):
        alpha.add_row([.000001 if i == j else 0 for j in range(x.get_columns())])

    return (alpha + xT * x).get_inverse() * xT * y.T()

print(lin_regression(x, y))


# def getMatrixInverse(m):
#     determinant = getMatrixDeternminant(m)
#     #special case for 2x2 matrix:
#     if len(m) == 2:
#         return [[m[1][1]/determinant, -1*m[0][1]/determinant],
#                 [-1*m[1][0]/determinant, m[0][0]/determinant]]

#     #find matrix of cofactors
#     cofactors = []
#     for r in range(len(m)):
#         cofactorRow = []
#         for c in range(len(m)):
#             minor = getMatrixMinor(m,r,c)
#             cofactorRow.append(((-1)**(r+c)) * getMatrixDeternminant(minor))
#         cofactors.append(cofactorRow)
#     cofactors = transposeMatrix(cofactors)
#     for r in range(len(cofactors)):
#         for c in range(len(cofactors)):
#             cofactors[r][c] = cofactors[r][c]/determinant
#     return cofactors

