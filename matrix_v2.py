from array import array

# @micropython.native
def get_matrix_minor(arr,i,j,n):
    a = [arr[n*x:n*x + j] + arr[n*x+j+1:n*x+n] for x in range(n) if x != i]
    if len(a) < 1:
        print(arr, n, a)
    out = a[0]
    for i in range(1, len(a)):
        out = out + a[i]
    return out

# @micropython.native
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

# @micropython.native
def transpose_matrix(arr, rows, columns, out):
    for c in range(columns):
        for r in range(rows):
            out.append(arr[r * columns + c])
    return out

# @micropython.native
def transposeListMatrix(m):
    return list(map(list,zip(*m)))

# @micropython.native
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
    # Class implementing some basic matrix operations. Hopefully efficient.
    # Skipping error handling and checking at the moment.
    # Starting with lazy evaluation of transposition
    # @micropython.native
    def __init__(self, initial=None):
        # initial should be empty, a list of numbers, or a list of lists.
        # If it is a list of numbers then you get a vertical matrix i.e. 1 column
        # If it is a list of lists, each of the interior lists is treated as a row
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
                self.rows = len(initial)
                self.columns = 1
                self.arr = array('f', initial)
                return
        else:
            self.rows = 0
            self.columns = 0
            self.arr = array('f')
            return
    # @micropython.native
    def extend(self, to_add):
        self.arr.extend(array('f', to_add))

    # @micropython.native
    def add_row(self, row):
        "Adds a row to the matrix"
        self.extend(row)
        if self.columns == 0:
            self.columns = len(row)
        self.rows = self.rows + 1

    # @micropython.native
    def T(self):
        # Transposes the matrix turning columns into rows.
        out = Matrix()
        out.arr = self.arr
        out.columns = self.get_columns()
        out.rows = self.get_rows()
        out.transposed = not self.transposed
        return out

    # @micropython.native
    def get(self, row, column):
        if self.transposed:
            return self.arr[column * self.columns + row]
        return self.arr[row * self.columns + column]

    # @micropython.native
    def get_rows(self):
        if self.transposed:
            return self.columns
        return self.rows

    # @micropython.native
    def get_columns(self):
        if self.transposed:
            return self.rows
        return self.columns

    # @micropython.native
    def clone(self):
        out = Matrix()
        if self.transposed:
            transpose_matrix(self.arr, self.rows, self.columns, out.arr)
        else:
            out.arr.extend(self.arr)
        out.columns = self.get_columns()
        out.rows = self.get_rows()
        return out

    # @micropython.native
    def add_bias_ones(self):
        out = Matrix()
        if self.transposed:
            return #Fix this

        for i in range(len(self.arr)):
            if i % self.columns == 0:
                out.arr.append(1)
            out.arr.append(self.arr[i])
        out.columns = self.get_columns() + 1
        out.rows = self.get_rows()
        return out

    # @micropython.native
    def polynomialize(self, degree):
        "This will also add the bias ones so don't use it with add_bias_ones"
        out = Matrix()

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
        out = Matrix()
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

    # @micropython.native
    def get_inverse(self):
        out = Matrix()
        out.columns = self.get_columns()
        out.rows = self.get_rows()
        for row in inverse_helper(memoryview(self.arr), self.get_columns()):
            out.extend(row)
        return out

    # @micropython.native
    def __str__(self):
        if self.transposed:
            return str(self.clone())
        out = "[\\n"
        for i in range(self.get_rows()):
            out += "["
            for j in range(self.get_columns()):
                out += str(self.arr[i*self.get_columns() + j]) + ","
            out += "],\\n"
        out +="]"
        return out

# a = Matrix([[3,8],[4,6]])
# b = Matrix([[1,2],[3,4]])
# c = Matrix([[1,2,5],[3,4,2],[3,2,7]])
# print(a + b)
# print(a * b)
# # a.T()
# # print(a.clone())
# # print(b.get_inverse())
# # mv = memoryview(c.arr)
# # print(get_matrix_minor(mv, 1,1,3))
# print(c.determinant())
# print(c.get_inverse())


# x = Matrix([67.77472353218393, 88.13098577413399, 42.52930638931034, 37.5432806277281, 1.9198458039374589, 95.64210152543843, 26.949504997381247, 4.009564303303248, 8.80509597940209, 39.79363879960982, 35.22092471535084, 39.587780219127154, 45.51274216523215, 54.12805293908667, 47.18181666996103, 93.02835319332387, 31.13950562616774, 59.7201510037116, 53.80654305953264, 28.287518357163055, 60.907829142815714, 55.76053745287567, 85.95283416834502, 90.59405475757596, 9.171543655741898, 23.025560679907777, 60.99942588993682, 37.49909274641523, 12.382262103698116, 48.1340567049508, 59.810056065284186, 55.69024159681184, 26.472862346215685, 55.64166467054768, 98.25844497890856, 67.45911742045018, 35.70496846044291, 34.53169412582007, 84.34463972723368, 61.613497631901915, 66.50117081869747, 53.66378204285315, 52.51150387842664, 75.24835517166078, 58.08863674988469, 17.82671979420205, 74.87713609834073, 32.001925460763466, 3.2125461538568656, 19.334962956074985, 49.847395753673204, 1.191178612719479, 9.880892601113356, 95.52218273763998, 27.807248036544173, 16.102315812701406, 5.777375785533733, 9.44901880427782, 6.017851911013605, 49.081003991780825, 22.471509132751898, 51.54633680998347, 7.225774728437839, 14.605177598825103, 90.07781382345678, 74.90636996433466, 1.7946030180889916, 46.15424242576249, 12.845219231094863, 11.914080644846049, 90.08027263782967, 22.493566306822455, 53.5641400860013, 97.63601172202887, 32.78747204720162, 69.6925976472022, 85.45179074365242, 11.663933878634381, 89.27638992007128, 19.801177481341924, 16.790799071367513, 44.2391504467045, 26.630908026211365, 81.30459627802874, 7.433336204865048, 70.3730079097495, 71.06472385641224, 24.657078293121803, 44.62451863254328, 46.36020966840929, 42.66378952325833, 72.85396068492615, 90.99104096999713, 36.24184082636711, 13.558126557876871, 23.49921021097202, 35.8666270288227, 54.71996671248777, 85.71856624768702, 58.90638731181609])
# y = Matrix([474.4230647252875, 616.916900418938, 297.7051447251724, 262.8029643940967, 13.438920627562212, 669.494710678069, 188.64653498166874, 28.066950123122737, 61.63567185581463, 278.55547159726876, 246.5464730074559, 277.1144615338901, 318.589195156625, 378.8963705736067, 330.2727166897272, 651.1984723532671, 217.97653938317418, 418.0410570259812, 376.6458014167285, 198.01262850014137, 426.35480399971, 390.32376217012967, 601.6698391784151, 634.1583833030318, 64.20080559019328, 161.17892475935443, 426.99598122955774, 262.4936492249066, 86.67583472588682, 336.9383969346556, 418.6703924569893, 389.83169117768284, 185.31003642350979, 389.4916526938337, 687.8091148523599, 472.2138219431513, 249.9347792231004, 241.72185888074046, 590.4124780906358, 431.2944834233134, 465.50819573088233, 375.64647429997206, 367.58052714898645, 526.7384862016254, 406.62045724919284, 124.78703855941434, 524.139952688385, 224.01347822534427, 22.48782307699806, 135.3447406925249, 348.93177027571244, 8.338250289036353, 69.16624820779349, 668.6552791634799, 194.65073625580922, 112.71621068890984, 40.44163049873613, 66.14313162994475, 42.124963377095234, 343.56702794246576, 157.3005639292633, 360.8243576698843, 50.58042309906487, 102.23624319177571, 630.5446967641974, 524.3445897503426, 12.56222112662294, 323.0796969803374, 89.91653461766404, 83.39856451392234, 630.5619084648076, 157.45496414775718, 374.9489806020091, 683.452082054202, 229.51230433041133, 487.84818353041544, 598.162535205567, 81.64753715044067, 624.9347294404989, 138.60824236939345, 117.53559349957258, 309.6740531269315, 186.41635618347956, 569.1321739462012, 52.033353434055336, 492.6110553682465, 497.4530669948857, 172.59954805185262, 312.3716304278029, 324.521467678865, 298.6465266628083, 509.97772479448304, 636.9372867899799, 253.69288578456977, 94.9068859051381, 164.49447147680414, 251.06638920175888, 383.0397669874144, 600.0299637338092, 412.3447111827126])

# @micropython.native
def get_alpha(n):
    alpha = Matrix()
    for i in range(n):
        alpha.add_row([.0000001 if i == j else 0 for j in range(n)])
    return alpha

# @micropython.native
def lin_regression(x, y):
    x = x.add_bias_ones()
    xT = x.T()
    alpha = get_alpha(x.get_columns())
    return (alpha + xT * x).get_inverse() * xT * y

# @micropython.native
def poly_regression(x, y, degree):
    x = x.polynomialize(degree)
    xT = x.T()
    alpha = get_alpha(x.get_columns())
    return (alpha + xT * x).get_inverse() * xT * y


# print(lin_regression(x, y))
