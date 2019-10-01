import pandas as pd


def formsim(C1, C2):
    X1 = set(list(C1.keys())[0].split(','))
    X2 = set(list(C2.keys())[0].split(','))
    Y1 = set(list(C1.values())[0])
    Y2 = set(list(C2.values())[0])

    LX1 = list(X1 - X1.intersection(X2))
    # print(LX1)
    LX2 = list(X2 - X1.intersection(X2))
    # print(LX2)
    LY1 = list(Y1 - Y1.intersection(Y2))
    # print(LY1)
    LY2 = list(Y2 - Y1.intersection(Y2))
    # print(LY2)

    total = len(X1.union(X2)) * len(Y1.union(Y2))
    # print(total)
    zeros = len(LX1) * len(LY2) + len(LX2) * len(LY1)
    # print(zeros)

    return (total - zeros) / total


def formsimMatrix(concept_list):
    # concept_list = concept_list1.copy()
    row_names = []
    for i in range(len(concept_list)):
        row_names.append('C' + str(i))

    sim_matrix = []
    for j in range(len(concept_list)):
        k = 0
        inner_matrix = []
        while (k <= j):
            #            if j == k:
            #                inner_matrix.append(1.0)
            #            else:
            inner_matrix.append(formsim(concept_list[j], concept_list[k]))
            k += 1
        sim_matrix.append(inner_matrix)

    data_dict = dict(zip(row_names, sim_matrix))
    sim_matrix_df = pd.DataFrame.from_dict(data_dict, orient='index', columns=row_names)

    return sim_matrix_df


skipset = set()


def lexicOrder(str1, str2):
    r_str = ""
    new_str = sorted([str1, str2])
    r_str += new_str[0] + ',' + new_str[1]
    return r_str


def replaceInItems(curr, target, mapp):
    templ = []
    for k in mapp.keys():
        if curr in k:
            templ.append(k)
    for ki in templ:
        val = mapp.get(ki)
        mapp.pop(ki)
        new_ki = ki.replace(curr, target)
        new_ki = new_ki + ''
        mapp[new_ki] = val


def charmProperty(xi, xj, prop_y, minSup, nodes, newN):
    if len(prop_y) >= minSup:
        if (set(nodes.get(xi)) == set(nodes.get(xj))):
            skipset.add(xj)
            tempo = lexicOrder(xi, xj)
            replaceInItems(xi, tempo, newN)
            replaceInItems(xi, tempo, nodes)
            return tempo
        elif (set(nodes.get(xi, {})).issubset(set(nodes.get(xj, {})))):
            tempo = lexicOrder(xi, xj)
            replaceInItems(xi, tempo, newN)
            replaceInItems(xi, tempo, nodes)
            return tempo
        elif (set(nodes.get(xj, {})).issubset(set(nodes.get(xi, {})))):
            skipset.add(xj)
            newN[lexicOrder(xi, xj)] = prop_y
        else:
            if (set(nodes.get(xi, {})) != set(nodes.get(xj, {}))):
                newN[lexicOrder(xi, xj)] = prop_y
    return xi


def isSubsumed(c, y):
    for val in c.values():
        if val == y:
            return True
    return False


def charmExtended(nodes, c, minSup):
    items = list(nodes.keys())
    for idx1 in range(len(items)):
        xi = items[idx1]
        if xi in skipset:
            continue
        x_prev = xi
        x = ''
        newN = {}
        for idx2 in range(idx1 + 1, len(items)):
            xj = items[idx2]
            if xj in skipset:
                continue
            x = lexicOrder(xi, xj)
            y = nodes.get(xi, {})
            temp = set()
            temp = temp.union(y)
            temp = temp.intersection(nodes.get(xj, {}))
            xi = charmProperty(xi, xj, temp, minSup, nodes, newN)
        if newN:
            charmExtended(newN, c, minSup)
        if (x_prev and nodes.get(x_prev) and not isSubsumed(c, nodes.get(x_prev))):
            c[x_prev] = list(nodes.get(x_prev))
        if (x and nodes.get(x) and not isSubsumed(c, nodes.get(x))):
            c[x] = list(nodes.get(x))


def charm(ip, minSup):
    # print(ip)
    new_ip = ip.copy()
    for i in ip.keys():
        if len(ip.get(i)) < minSup:
            new_ip.pop(i)
    c = {}
    charmExtended(new_ip, c, minSup)

    return c


def itemset(df):
    df = df.drop(['Unnamed: 0'], axis=1)

    itemdict = {}
    for i in df.columns:
        l = df[i]
        trans = ['T' + str(j) for j in range(len(l)) if l[j] == 1]
        itemdict[i] = trans

    return itemdict


def minSupport(df, perc):
    doc_names = list(df['Unnamed: 0'])
    tids = []
    for i in range(len(doc_names)):
        tids.append('T' + str(i))

    tid_to_names = dict(zip(tids, doc_names))

    return int((len(tid_to_names) * perc) / 100)


def dict_to_list(concept_dict):
    conc_list = []
    for i in concept_dict:
        d = {i: concept_dict[i]}
        conc_list.append(d)

    return conc_list


sample_data = pd.read_csv('sample_bin.csv')
ip = itemset(sample_data)
minSup = minSupport(sample_data, 70)
concepts = charm(ip, minSup)
concept_list = dict_to_list(concepts)
similarity_matrix = formsimMatrix(concept_list)

similarity_matrix.to_csv('similarity_matrix.csv')
