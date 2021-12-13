import pickle

def save(nodes, filename):
    f = open(filename, 'wb')
    pickle.dump(nodes, f)
    f.close()

def load_file(filename):
    f = open(filename, 'rb')
    nodes = pickle.load(f)
    f.close()
    return nodes
