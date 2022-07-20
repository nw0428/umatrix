from array import array
import datetime

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
    #@micropython.native
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
                self.arr = array('f')
                for i in initial:
                    self.extend(i)
                return
            else:
                self.rows = 1
                self.columns = len(initial)
                self.arr = array('f', initial)
                return
        else:
            self.rows = 0
            self.columns = 0
            self.arr = array('f')
            return

    def extend(self, to_add):
        self.arr.extend(array('f', to_add))

    def add_row(self, row):
        "Adds a row to the matrix"
        self.extend(row)
        if self.columns == 0:
            self.columns = len(row)
        self.rows = self.rows + 1


    def T(self):
        '''
        Transposes the matrix turning columns into rows.
        I tried making this efficient and failed utterly. Gotta fix this
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
            out.arr.extend(self.arr)
        out.columns = self.get_columns()
        out.rows = self.get_rows()
        return out

    def add_bias_ones(self):
        out = Matrix(self.type_code)
        if self.transposed:
            return #Fix this

        for i in range(len(self.arr)):
            if i % self.columns == 0:
                out.arr.append(1)
            out.arr.append(self.arr[i])
        out.columns = self.get_columns() + 1
        out.rows = self.get_rows()
        return out

    def polynomialize(self, degree):
        "This will also add the bias ones so don't use it with add_bias_ones"
        out = Matrix(self.type_code)

        for i in range(len(self.arr)):
            if i % self.columns == 0:
                out.arr.append(1)
            for j in range(degree):
                out.arr.append(self.arr[i]**(j+1))
        out.columns = self.get_columns() * degree + 1
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


x = Matrix('f', [1,2,5]).T().clone()
y = Matrix('f', [5, 10, 25]).T()


def lin_regression(x, y):
    x = x.add_bias_ones()
    xT = x.T()
    alpha = Matrix('f')
    for i in range(x.get_columns()):
        alpha.add_row([.0000001 if i == j else 0 for j in range(x.get_columns())])
    return (alpha + xT * x).get_inverse() * xT * y.T()

def poly_regression(x, y, degree):
    x = x.polynomialize(degree)
    xT = x.T()
    alpha = Matrix('f')
    for i in range(x.get_columns()):
        alpha.add_row([.0000001 if i == j else 0 for j in range(x.get_columns())])
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

x = Matrix([67.77472353218393, 88.13098577413399, 42.52930638931034, 37.5432806277281, 1.9198458039374589, 95.64210152543843, 26.949504997381247, 4.009564303303248, 8.80509597940209, 39.79363879960982, 35.22092471535084, 39.587780219127154, 45.51274216523215, 54.12805293908667, 47.18181666996103, 93.02835319332387, 31.13950562616774, 59.7201510037116, 53.80654305953264, 28.287518357163055, 60.907829142815714, 55.76053745287567, 85.95283416834502, 90.59405475757596, 9.171543655741898, 23.025560679907777, 60.99942588993682, 37.49909274641523, 12.382262103698116, 48.1340567049508, 59.810056065284186, 55.69024159681184, 26.472862346215685, 55.64166467054768, 98.25844497890856, 67.45911742045018, 35.70496846044291, 34.53169412582007, 84.34463972723368, 61.613497631901915, 66.50117081869747, 53.66378204285315, 52.51150387842664, 75.24835517166078, 58.08863674988469, 17.82671979420205, 74.87713609834073, 32.001925460763466, 3.2125461538568656, 19.334962956074985, 49.847395753673204, 1.191178612719479, 9.880892601113356, 95.52218273763998, 27.807248036544173, 16.102315812701406, 5.777375785533733, 9.44901880427782, 6.017851911013605, 49.081003991780825, 22.471509132751898, 51.54633680998347, 7.225774728437839, 14.605177598825103, 90.07781382345678, 74.90636996433466, 1.7946030180889916, 46.15424242576249, 12.845219231094863, 11.914080644846049, 90.08027263782967, 22.493566306822455, 53.5641400860013, 97.63601172202887, 32.78747204720162, 69.6925976472022, 85.45179074365242, 11.663933878634381, 89.27638992007128, 19.801177481341924, 16.790799071367513, 44.2391504467045, 26.630908026211365, 81.30459627802874, 7.433336204865048, 70.3730079097495, 71.06472385641224, 24.657078293121803, 44.62451863254328, 46.36020966840929, 42.66378952325833, 72.85396068492615, 90.99104096999713, 36.24184082636711, 13.558126557876871, 23.49921021097202, 35.8666270288227, 54.71996671248777, 85.71856624768702, 58.90638731181609])


st = datetime.datetime.now()
out = inverse_helper(x.arr, 10)
et = datetime.datetime.now()
print(et - st)
