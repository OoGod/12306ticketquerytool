# tickets.py
# coding: utf-8

# docopt 将文档字符串docstring中定义的格式自动解析
# 出参数并返回一个字典

"""命令行火车票查看器
Usage:
    tickets [-gdtkz] <from> <to> <date>
"""

from docopt import docopt
from stations import stations
import requests
from prettytable import PrettyTable
from colorama import init, Fore

init()


class TrainsCollection:
    header = '车次 车站 时间 历时 一等 二等 高级软卧 软卧 硬卧 硬座 无座'.split()

    def __init__(self, available_trains, available_place, options):
        """查询火车班次集合
        """
        self.available_trains = available_trains
        self.available_place = available_place
        self.options = options

    @property
    def trains(self):
        # @propety 属性获取器装饰器,对属性的访问进行控制
        for raw_train in self.available_trains:
            raw_train_list = raw_train.split('|')
            train_no = raw_train_list[3]
            initial = train_no[0].lower()
            duration = raw_train_list[10]
            if not self.options or initial in self.options:
                # 对始/达 着色 绿/红
                train = [
                    train_no,
                    '\n'.join([Fore.LIGHTGREEN_EX + self.available_place[raw_train_list[6]] + Fore.RESET,
                               Fore.LIGHTRED_EX + self.available_place[raw_train_list[7]] + Fore.RESET]),
                    '\n'.join([Fore.LIGHTGREEN_EX + raw_train_list[8] + Fore.RESET,
                               Fore.LIGHTRED_EX + raw_train_list[9] + Fore.RESET]),
                    duration,
                    raw_train_list[-6] if raw_train_list[-6] else '--',
                    raw_train_list[-7] if raw_train_list[-7] else '--',
                    raw_train_list[-15] if raw_train_list[-15] else '--',
                    raw_train_list[-8] if raw_train_list[-8] else '--',
                    raw_train_list[-14] if raw_train_list[-14] else '--',
                    raw_train_list[-11] if raw_train_list[-11] else '--',
                    raw_train_list[-9] if raw_train_list[-9] else '--',
                ]
                yield train

    def pretty_print(self):
        pt = PrettyTable()
        pt._set_field_names(self.header)
        for train in self.trains:
            pt.add_row(train)
        print(pt)


def cli():
    """ 命令行接口 """
    # 获取文档字符串模板组成的命令行参数字典对象
    arguments = docopt(__doc__)
    from_station = stations.get(arguments['<from>'])
    to_station = stations.get(arguments['<to>'])
    date = arguments['<date>']

    # url = ('https://kyfw.12306.cn/otn/leftTicket/queryZ?'
    #        'leftTicketDTO.train_date={}&'
    #        'leftTicketDTO.from_station={}&leftTicketDTO.to_station={}&purpose_codes=ADULT').format(
    #     date, from_station, to_station
    # )
    # url = ('https://kyfw.12306.cn/otn/leftTicket/queryX?'
    #     'leftTicketDTO.train_date={}&'
    #     'leftTicketDTO.from_station={}&leftTicketDTO.to_station={}&purpose_codes=ADULT').format(
    #     date,from_station, to_station
    #     )
    url = ('https://kyfw.12306.cn/otn/leftTicket/query?'
        'leftTicketDTO.train_date={}&'
        'leftTicketDTO.from_station={}&leftTicketDTO.to_station={}&purpose_codes=ADULT').format(
        date, from_station, to_station
    )
    print(url)
    # 不验证证书
    r = requests.get(url, verify=False)
    available_trains = r.json()['data']['result']
    available_place = r.json()['data']['map']
    options = ''.join([
        key for key, value in arguments.items() if value is True
    ])
    TrainsCollection(available_trains, available_place, options).pretty_print()


if __name__ == '__main__':
    cli()
