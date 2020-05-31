import os
import process

def get_fname(x):
    return '.'.join(x.split('/')[-1].split('.')[:-1])

def listdir(dname):
    return [f for f in os.listdir(dname) if f.endswith('.tif')]

def mkdir(dname):
    try: os.makedirs(dname)
    except FileExistsError: pass

data_covid = 'data'
data_dnames = [ 'data/human', 'data/nature' ]
data_result = 'data/results'

def main():
    covids = listdir(data_covid)
    for covid in covids:
        folder = get_fname(covid)

        for dname in data_dnames:
            rname = f'{data_result}/{folder}/{dname.split("/")[-1]}'
            mkdir(rname)

            for fname in os.listdir(dname):
                data = f'{dname}/{fname}'

                oname = f'{rname}/{get_fname(fname)}.tif'
                process.process(f'{data_covid}/{covid}', f'{dname}/{fname}', oname)

main()
