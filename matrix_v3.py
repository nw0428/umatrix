from array import array
from cmath import e , log
from math import sqrt

# @micropython.native


# Purpose: this function is used as a helper function in order to attain the
# smaller matrices used in finding the determinant of the main matrix
# Parameters: this takes in an array that represents a matrix, the i'th and
# j'th parameter are the matrix indeces in which the matrix minor will be
# centered
# returns: this returns the smaller matrix that will be used in the calculation
# of the determinant
#
# edge case not addressed if it is a 1 by 1 matrix it will be less than length
# 1 but continue and not print a[0]
def get_matrix_minor(arr,i,j,n):
    a = [arr[n*x:n*x + j] + arr[n*x+j+1:n*x+n] for x in range(n) if x != i]
    if len(a) < 1:
        print(arr, n, a)
    out = a[0]
    for i in range(1, len(a)):
        out = out + a[i]
    return out


#@micropython.native
# Purpose: to find the determinant of a matrix
# Parameters: the array which a determinant is being calculated for and the
# n by n dimensions since it must be the same in order for a determinant
# to exist
# returns: the determinant of the matrix
def determinant_helper(arr, n):
    if n == 1:
        return arr[0]
    determinant = 0
    for c in range(n):
        a = ((-1)**c) * arr[c]
        b = a * determinant_helper(get_matrix_minor(arr,0,c,n), n-1)
        determinant += b
    return determinant


# @micropython.native
# Purpose: to tranpose any given matrix
# Parameters: the array containing the matrix, the ammount of rows and columns
# in the matrix as well as an empty array that will be populated by the
# transposed matrix
# returns: the transposed matrix
def transpose_matrix(arr, rows, columns, out):
    for c in range(columns):
        for r in range(rows):
            out.append(arr[r * columns + c])
    return out


# @micropython.native
# Purpose: to inverse of a given matrix
# Parameters: the array which a determinant is being calculated for and the
# n by n dimensions since it must be the same in order for a determinant
# to exist
# returns: the inverse of the matrix
def inverse_helper(arr, n):
    # determinant = determinant_helper(arr, n)
    # if n == 1:
    #     return [[1/determinant]]
    # cofactors = array('f')
    # cofactorRow = array('f')
    # for r in range(n):
    #     for c in range(n):
    #         minor = get_matrix_minor(arr,r,c,n)
    #         cofactorRow.append(((-1)**(r+c)) * determinant_helper(minor, n-1))
    #     cofactors.extend(cofactorRow[-n:])
    # cofactors = transpose_matrix(cofactors,n,n,array('f'))
    # for c in range(len(cofactors)):
    #        cofactors[c] = cofactors[c]/determinant
    # return cofactors
    copyarr = arr
    Inv = identity(n)
    for fd in range(n):
        fdScaler = 1.0 / copyarr[fd*n+fd]
        for j in range(n):
            copyarr[fd*n+j] *= fdScaler
            Inv[fd*n+j] *= fdScaler
        for i in range(n):
            if i == fd:
                continue
            crScaler = copyarr[i*n+fd]
            for j in range(n):
                copyarr[i*n+j] = copyarr[i*n+j] - crScaler * copyarr[fd*n+j]
                Inv[i*n+j] = Inv[i*n+j] - crScaler * Inv[fd*n+j]
    return Inv

def identity(n):
    I = array('f')
    for r in range(n):
        for c in range(n):
            if r == c:
                I.append(1)
            else:
                I.append(0)
    return I



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
    # Purpose: to append an array to the matrix
    # Parameters: self which is the matrix class and to_add which is a list
    # that will be added onto the array
    # returns: none
    def extend(self, to_add):
        self.arr.extend(array('f', to_add))

    # @micropython.native
    # Purpose: to add a row to the matrix
    # Parameters: self which is the matrix class and row which is a list of
    # integers or floats wishing to be added
    # returns: none
    def add_row(self, row):
        "Adds a row to the matrix"
        self.extend(row)
        if self.columns == 0:
            self.columns = len(row)
        self.rows = self.rows + 1

    # @micropython.native
    # Purpose: Transposes the matrix turning columns into rows.
    # Parameters: self which is the matrix class
    # returns: a new instance of matrix which contains the transposed matrix
    def T(self):
        out = Matrix()
        out.arr = self.arr
        out.transposed = not self.transposed
        out.columns = self.get_columns()
        out.rows = self.get_rows()
        return out

    # @micropython.native
    # Purpose: to attain a specific index of a the matrix
    # Parameters: self which is the matrix class, row and column are the indeces
    # in which the desired value resides
    # returns: the value that the indeces point to in the array
    def get(self, row, column):
        if self.transposed:
            return self.arr[column * self.columns + row]
        return self.arr[row * self.columns + column]

    # @micropython.native
    # Purpose: to attain the number of rows in the matrix
    # Parameters: self which is the matrix class
    # returns: the number of rows depending on whether it is tranposed or not
    def get_rows(self):
        if self.transposed:
            return self.columns
        return self.rows

    # @micropython.native
    # Purpose: to attain the number of columns in the matrix
    # Parameters: self which is the matrix class
    # returns: the number of columns depending on whether it is tranposed or not
    def get_columns(self):
        if self.transposed:
            return self.rows
        return self.columns

    # @micropython.native
    # Purpose: to clone the existing matrix
    # Parameters: self which is the matrix class
    # returns: a clone that depending on transposition rows and columns
    # copied as needed
    def clone(self):
        out = Matrix()
        if self.transposed:
            out.arr = transpose_matrix(self.arr, self.rows, self.columns, out.arr)
        else:
            out.arr.extend(self.arr)
        out.columns = self.get_columns()
        out.rows = self.get_rows()
        return out

    # @micropython.native
    # Purpose: to add the biased ones needed in order to formulate a clean
    # linear regression
    # Parameters: self which is the matrix class
    # returns: a matrix instance which accounts for the biased ones
    def add_bias_ones(self):
        out = Matrix()
        if self.transposed:
            return add_bias_ones(T(self))
        for i in range(len(self.arr)):
            if i % self.columns == 0:
                out.arr.append(1)
            out.arr.append(self.arr[i])
        out.columns = self.get_columns() + 1
        out.rows = self.get_rows()
        return out

    # @micropython.native
    # Purpose: helper function to use in order to attain a polynomial regression
    # Parameters: self which is the matrix class, and the degree in which the
    # polynomial regression will take place
    # returns: a matrix instance which accounts for the biased ones
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


    def weights(self):
        out = Matrix()
        for i in range(len(self)):
            out.arr.append(0)
        out.columns = self.get_columns()
        out.rows = self.get_rows()
        return  out




    # @micropython.native
    # Purpose: to add two matrices given
    # Parameters: self which is the matrix class and an other matrix which will
    # be added to the first
    # returns: the added matrices
    def __add__(self, other):
        "Adds two matrices. This needs a sanity check for transposition"
        out = self.clone()
        for r in range(other.rows):
            rt = r * other.columns
            for c in range(other.columns):
                out.arr[rt+c] += other.get(r, c)
        return out

    # @micropython.native
    # Purpose: to cross multiply two matrices given
    # Parameters: self which is the matrix class and an other matrix which will
    # be added to the first
    # returns: the multiplied matrix
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

    # @micropython.native
    # Purpose: to find the determinant of a matrix
    # Parameters: the array which a determinant is being calculated for
    # returns: the determinant of the matrix
    def determinant(self):
        if self.rows == self.columns :
            return determinant_helper(self.arr, self.rows)
        else:
            return 0

    # @micropython.native
    # Purpose: to find the inverse of a matrix
    # Parameters: the array which a determinant is being calculated for
    # returns: the inverse of the matrix
    def get_inverse(self):
        out = Matrix()
        out.arr = inverse_helper(self.arr, self.get_columns())
        out.columns = self.get_columns()
        out.rows = self.get_rows()
        return out

    def check_invmatrix(arr,inv,n):
        I = identity(n)
        if arr*inv == I:
            return inv
        return inv

    # @micropython.native
    # Purpose: to attain the matrix in string format
    # Parameters: the array which a determinant is being calculated for
    # returns: a string which contains the matrix and all of its values in the
    # correct order
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
# print(a)
# print(a.T())
# print(a.clone())
# print(b.get_inverse())
# mv = memoryview(c.arr)
# print(get_matrix_minor(mv, 1,1,3))
# print(c.determinant())
# print(c.get_inverse())
#
#
# # x = Matrix([67.77472353218393, 88.13098577413399, 42.52930638931034, 37.5432806277281, 1.9198458039374589, 95.64210152543843, 26.949504997381247, 4.009564303303248, 8.80509597940209, 39.79363879960982, 35.22092471535084, 39.587780219127154, 45.51274216523215, 54.12805293908667, 47.18181666996103, 93.02835319332387, 31.13950562616774, 59.7201510037116, 53.80654305953264, 28.287518357163055, 60.907829142815714, 55.76053745287567, 85.95283416834502, 90.59405475757596, 9.171543655741898, 23.025560679907777, 60.99942588993682, 37.49909274641523, 12.382262103698116, 48.1340567049508, 59.810056065284186, 55.69024159681184, 26.472862346215685, 55.64166467054768, 98.25844497890856, 67.45911742045018, 35.70496846044291, 34.53169412582007, 84.34463972723368, 61.613497631901915, 66.50117081869747, 53.66378204285315, 52.51150387842664, 75.24835517166078, 58.08863674988469, 17.82671979420205, 74.87713609834073, 32.001925460763466, 3.2125461538568656, 19.334962956074985, 49.847395753673204, 1.191178612719479, 9.880892601113356, 95.52218273763998, 27.807248036544173, 16.102315812701406, 5.777375785533733, 9.44901880427782, 6.017851911013605, 49.081003991780825, 22.471509132751898, 51.54633680998347, 7.225774728437839, 14.605177598825103, 90.07781382345678, 74.90636996433466, 1.7946030180889916, 46.15424242576249, 12.845219231094863, 11.914080644846049, 90.08027263782967, 22.493566306822455, 53.5641400860013, 97.63601172202887, 32.78747204720162, 69.6925976472022, 85.45179074365242, 11.663933878634381, 89.27638992007128, 19.801177481341924, 16.790799071367513, 44.2391504467045, 26.630908026211365, 81.30459627802874, 7.433336204865048, 70.3730079097495, 71.06472385641224, 24.657078293121803, 44.62451863254328, 46.36020966840929, 42.66378952325833, 72.85396068492615, 90.99104096999713, 36.24184082636711, 13.558126557876871, 23.49921021097202, 35.8666270288227, 54.71996671248777, 85.71856624768702, 58.90638731181609])
# # y = Matrix([474.4230647252875, 616.916900418938, 297.7051447251724, 262.8029643940967, 13.438920627562212, 669.494710678069, 188.64653498166874, 28.066950123122737, 61.63567185581463, 278.55547159726876, 246.5464730074559, 277.1144615338901, 318.589195156625, 378.8963705736067, 330.2727166897272, 651.1984723532671, 217.97653938317418, 418.0410570259812, 376.6458014167285, 198.01262850014137, 426.35480399971, 390.32376217012967, 601.6698391784151, 634.1583833030318, 64.20080559019328, 161.17892475935443, 426.99598122955774, 262.4936492249066, 86.67583472588682, 336.9383969346556, 418.6703924569893, 389.83169117768284, 185.31003642350979, 389.4916526938337, 687.8091148523599, 472.2138219431513, 249.9347792231004, 241.72185888074046, 590.4124780906358, 431.2944834233134, 465.50819573088233, 375.64647429997206, 367.58052714898645, 526.7384862016254, 406.62045724919284, 124.78703855941434, 524.139952688385, 224.01347822534427, 22.48782307699806, 135.3447406925249, 348.93177027571244, 8.338250289036353, 69.16624820779349, 668.6552791634799, 194.65073625580922, 112.71621068890984, 40.44163049873613, 66.14313162994475, 42.124963377095234, 343.56702794246576, 157.3005639292633, 360.8243576698843, 50.58042309906487, 102.23624319177571, 630.5446967641974, 524.3445897503426, 12.56222112662294, 323.0796969803374, 89.91653461766404, 83.39856451392234, 630.5619084648076, 157.45496414775718, 374.9489806020091, 683.452082054202, 229.51230433041133, 487.84818353041544, 598.162535205567, 81.64753715044067, 624.9347294404989, 138.60824236939345, 117.53559349957258, 309.6740531269315, 186.41635618347956, 569.1321739462012, 52.033353434055336, 492.6110553682465, 497.4530669948857, 172.59954805185262, 312.3716304278029, 324.521467678865, 298.6465266628083, 509.97772479448304, 636.9372867899799, 253.69288578456977, 94.9068859051381, 164.49447147680414, 251.06638920175888, 383.0397669874144, 600.0299637338092, 412.3447111827126])
#

xs = [[298, 88, 113], [501, 147, 186], [387, 109, 142], [276, 86, 111], [445, 133, 172], [584, 173, 223], [571, 190, 237], [579, 240, 282], [411, 118, 155], [96, 172, 142], [67, 174, 129], [59, 149, 111], [73, 140, 111], [100, 259, 187], [111, 230, 178], [146, 265, 216], [241, 347, 301], [54, 146, 104], [99, 216, 166], [187, 282, 241], [34, 66, 54]]
ys = [178, 178, 178, 178, 178, 178, 178, 178, 178, 353, 353, 353, 353, 353, 353, 353, 353, 353, 353, 353, 353]
Xs =  Matrix(xs)
Ys = Matrix(ys)
# # @micropython.native
def get_alpha(n):
    alpha = Matrix()
    for i in range(n):
        alpha.add_row([.0000001 if i == j else 0 for j in range(n)])
    return alpha
#
# # @micropython.native
def lin_regression(x, y):
    x = x.add_bias_ones()
    xT = x.T()
    alpha = get_alpha(x.get_columns())
    return (alpha + (xT * x)).get_inverse() * xT * y

# # @micropython.native
def poly_regression(x, y, degree):
    x = x.polynomialize(degree)
    xT = x.T()
    alpha = get_alpha(x.get_columns())
    return (alpha + xT * x).get_inverse() * xT * y
#
# # @micropython.native
def LDF(x, y):
    alpha = get_alpha(x.get_columns())
    aT = alpha.T()
    return aT*x

#--------------------------------Big O TESTING----------------------------------

# arr = Matrix([[3,8],[4,6]])
# arr1 = Matrix([[8,90,888,202],[55,677,899,544],[3,4,5,6],[77,876,900,11.2]])
# arr2 = Matrix([[8,90,888,202,55,677],[899,544,3,4,5,6],[77,876,900,11.2,85,76],[22,32,12,11,44,52],[70,38,9,111,2,65],[32,12,999,87,65,45]])
# arr3 = Matrix([[8,90,888,202,55,677,899,544],[3,4,5,6,77,876,900,11.2],[85,76,22,32,12,11,44,52],[70,38,9,111,2,65,32,12],[999,87,65,45,69.6925976472022, 85.45179074365242, 11.663933878634381, 89.27638992007128], [19.801177481341924, 16.790799071367513, 44.2391504467045, 26.630908026211365, 81.30459627802874, 7.433336204865048, 70.3730079097495, 71.06472385641224], [24.657078293121803, 44.62451863254328, 46.36020966840929, 42.66378952325833, 72.85396068492615, 90.99104096999713, 36.24184082636711, 13.558126557876871], [23.49921021097202, 35.8666270288227, 54.71996671248777, 85.71856624768702, 58.90638731181609, 22,566,777]])
# arr4 = Matrix([[67.77472353218393, 88.13098577413399, 42.52930638931034, 37.5432806277281, 1.9198458039374589, 95.64210152543843, 26.949504997381247, 4.009564303303248, 8.80509597940209, 39.79363879960982], [35.22092471535084, 39.587780219127154, 45.51274216523215, 54.12805293908667, 47.18181666996103, 93.02835319332387, 31.13950562616774, 59.7201510037116, 53.80654305953264, 28.287518357163055], [60.907829142815714, 55.76053745287567, 85.95283416834502, 90.59405475757596, 9.171543655741898, 23.025560679907777, 60.99942588993682, 37.49909274641523, 12.382262103698116, 48.1340567049508], [59.810056065284186, 55.69024159681184, 26.472862346215685, 55.64166467054768, 98.25844497890856, 67.45911742045018, 35.70496846044291, 34.53169412582007, 84.34463972723368, 61.613497631901915], [66.50117081869747, 53.66378204285315, 52.51150387842664, 75.24835517166078, 58.08863674988469, 17.82671979420205, 74.87713609834073, 32.001925460763466, 3.2125461538568656, 19.334962956074985], [49.847395753673204, 1.191178612719479, 9.880892601113356, 95.52218273763998, 27.807248036544173, 16.102315812701406, 5.777375785533733, 9.44901880427782, 6.017851911013605, 49.081003991780825], [22.471509132751898, 51.54633680998347, 7.225774728437839, 14.605177598825103, 90.07781382345678, 74.90636996433466, 1.7946030180889916, 46.15424242576249, 12.845219231094863, 11.914080644846049], [90.08027263782967, 22.493566306822455, 53.5641400860013, 97.63601172202887, 32.78747204720162, 69.6925976472022, 85.45179074365242, 11.663933878634381, 89.27638992007128, 19.801177481341924], [16.790799071367513, 44.2391504467045, 26.630908026211365, 81.30459627802874, 7.433336204865048, 70.3730079097495, 71.06472385641224, 24.657078293121803, 44.62451863254328, 46.36020966840929], [42.66378952325833, 72.85396068492615, 90.99104096999713, 36.24184082636711, 13.558126557876871, 23.49921021097202, 35.8666270288227, 54.71996671248777, 85.71856624768702, 58.90638731181609]])
# tot = [arr,arr1,arr2,arr3,arr4]
# totlen = [2,4,6,8,10]


print(lin_regression(Xs, Ys))
print("linear regression complete")
print(poly_regression(Xs, Ys, 2))
print("polynomial(2) regression complete")
print(poly_regression(Xs, Ys, 3))
print("polynomial(3) regression complete")
print(poly_regression(Xs, Ys, 4))
print("polynomial(4) regression complete")
# for i in range(5):
#     st = datetime.datetime.now()
#     out = get_matrix_minor(tot[i].arr,0,0,totlen[i])
#     et = datetime.datetime.now()
#     print(et - st)
#
# for i in range(5):
#     st = datetime.datetime.now()
#     out = determinant_helper(tot[i].arr, totlen[i])
#     et = datetime.datetime.now()
#     print(et - st)
#
# out = array('f')
# for i in range(5):
#     st = datetime.datetime.now()
#     out = transpose_matrix(tot[i].arr, totlen[i], totlen[i], out)
#     et = datetime.datetime.now()
#     print(et - st)
#
# for i in range(5):
#     st = datetime.datetime.now()
#     out = inverse_helper(tot[i].arr, totlen[i])
#     et = datetime.datetime.now()
#     print(et - st)
#
# for i in range(5):
#     st = datetime.datetime.now()
#     out = Matrix(tot[i].arr)
#     et = datetime.datetime.now()
#     print(et - st)
#
# for i in range(5):
#     st = datetime.datetime.now()
#     out = tot[i].T()
#     et = datetime.datetime.now()
#     print(et - st)
#
# row = [1,2]
# row1 = [1,2,3,4]
# row2 = [1,2,3,4,5,6]
# row3 = [1,2,3,4,5,6,7,8]
# row4 = [1,2,3,4,5,6,7,8,9,10]
# totrow = [row,row1,row2,row3,row4]
# for i in range(5):
#     st = datetime.datetime.now()
#     out = tot[i].add_row(totrow[i])
#     et = datetime.datetime.now()
#     print(et - st)
#
# for i in range(5):
#     st = datetime.datetime.now()
#     out = tot[i].extend(tot[i].arr)
#     et = datetime.datetime.now()
#     print(et - st)
#
# for i in range(5):
#     st = datetime.datetime.now()
#     out = tot[i].get(i, i)
#     et = datetime.datetime.now()
#     print(et - st)
#
# for i in range(5):
#     st = datetime.datetime.now()
#     out = tot[i].get_rows()
#     et = datetime.datetime.now()
#     print(et - st)
#
# for i in range(5):
#     st = datetime.datetime.now()
#     out = tot[i].get_columns()
#     et = datetime.datetime.now()
#     print(et - st)
#
# for i in range(5):
#     st = datetime.datetime.now()
#     out = tot[i].clone()
#     et = datetime.datetime.now()
#     print(et - st)
#
# for i in range(5):
#     st = datetime.datetime.now()
#     out = tot[i]+tot[i]
#     et = datetime.datetime.now()
#     print(et - st)
#
# for i in range(5):
#     st = datetime.datetime.now()
#     out = tot[i]*tot[i]
#     et = datetime.datetime.now()
#     print(et - st)
# for i in range(5):
#     st = datetime.datetime.now()
#     out = tot[i].determinant()
#     et = datetime.datetime.now()
#     print(et - st)
#
# for i in range(5):
#     st = datetime.datetime.now()
#     out = tot[i].get_inverse()
#     et = datetime.datetime.now()
#     print(et - st)
#
# for i in range(5):
#     st = datetime.datetime.now()
#     print(tot[i])
#     et = datetime.datetime.now()
#     print(et - st)
