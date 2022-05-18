from array import array

def get_matrix_minor(arr,i,j,n):
    return sum([arr[n*x:n*x + j] + arr[n*x+j+1:n*x+n] for x in range(n) if x != i])

def determinant_helper(arr, n):
    #base case for 2x2 matrix
    if n == 2:
        return arr[0]*arr[3]-arr[2]*arr[1]

    determinant = 0
    for c in range(n):
        determinant += ((-1)**c)*arr[c]*determinant_helper(get_matrix_minor(arr,0,c, n))
    return determinant


class Matrix:
    '''
    Class implementing some basic matrix operations. Hopefully efficient.
    Skipping error handling and checking at the moment.
    Starting with lazy evaluation of transposition
    '''
    @micropython.native
    def __init__(self, type_code, initial):
        '''
        type_code should be one of 'i' (int), 'f'(float), or 'd'(double)
        initial should be empty, a list, or a list of lists
        '''
        self.transposed = False
        if initial:
            if isinstance(initial[0], list):
                self.rows = len(initial)
                self.columns = len(initial[0])
                self.arr = array(type_code)
                for i in initial:
                    self.arr.extend(i)
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

    def add_row(self, row):
        "Adds a row to the matrix"
        self.arr.extend(row)
        if self.columns == 0:
            self.columns = len(row)
        self.rows = self.rows + 1

    def T(self):
        '''
        Transposes the matrix turning columns into rows.
        I think the flag is more efficient if slightly annoying to write
        '''
        self.transposed = not self.transposed

    def get(self, row, column):
        if self.transposed:
            return self.array[column * self.rows + row]
        return self.array[row * self.columns + column]

    def get_rows(self):
        if self.transposed:
            return self.columns
        return self.rows

    def get_columns(self):
        if self.transposed:
            return self.rows
        return self.columns

    @micropython.native
    def __add__(self, other):
        "Adds two matrices. This needs a sanity check for transposition"
        out = Matrix(self.arr.typecode)
        if self.transposed:
            for c in range(self.columns):
                for r in range(self.rows):
                    out.arr.append(self.arr[r * self.columns + c])
        else:
            out.arr.extend(self.arr)
        out.columns = self.columns
        out.rows = self.rows
        for r in range(other.rows):
            rt = r * other.columns
            for c in range(other.columns):
                out.arr[i] += other.arr[rt + c]
        return out

    @micropython.native
    def __mul__(self, other):
        out = None
        if isinstance(other, float) or other.array.typecode == 'f' or other.array.typecode == 'd':
            out = Matrix('f')
        else:
            out = Matrix(self.arr.typecode)
        if isinstance(other, float) or isinstance(other, int):
            out.columns = self.columns
            out.rows = self.rows
            for i in self.arr:
                out.arr.append(i * other)
            return out
        # Out will have as many rows as self and as many columns as other
        out.rows = self.get_rows()
        out.columns = other.get_columns()
        for r in range(out.get_rows):
            for c in range(out.get_columns):
                cross = 0
                # Would this be faster as a sum of a comprehension?
                for i in range(self.get_columns):
                    cross += self.get(r, i) * other.get(i, c)
                out.arr.append(cross)


    # Transposition doesn't change determinant which is nice
    @micropython.native
    def determinant(self):
        "Only meaningful with square matrices. Skipping that check atm"
        return determinant_helper(memoryview(self.arr), self.rows)


Matrix('i', [1,2,3,4,5])

# Stolen from https://stackoverflow.com/questions/32114054/matrix-inversion-without-numpy
# def transposeMatrix(m):
#     return map(list,zip(*m))



# def getMatrixDeternminant(m):
#     #base case for 2x2 matrix
#     if len(m) == 2:
#         return m[0][0]*m[1][1]-m[0][1]*m[1][0]

#     determinant = 0
#     for c in range(len(m)):
#         determinant += ((-1)**c)*m[0][c]*getMatrixDeternminant(getMatrixMinor(m,0,c))
#     return determinant

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

