from database import *
from Manager import Manager


def main():
    ResultItemModel.create_table(safe=True)
    Checked.create_table(safe=True)
    man = Manager()
    man.run()
    data = [[i.url,i.word] for i in ResultItemModel.select()]
    from pandas import DataFrame
    df = DataFrame(data,columns=['url','word'])
    df.to_excel('result.xlsx',sheet_name='results')


if __name__ == '__main__':
    main()
