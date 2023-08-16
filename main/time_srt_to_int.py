from datetime import datetime

def time_str_to_int_1(input_datetime):
    # 整理時間資料資料格式:'2023-02-04T19:30+00:00',
    date_time_list = input_datetime.split("T")
    date = date_time_list[0].split("-")
    time = date_time_list[1].split("+")
    time =time[0].split(':')

    # 把時間從str轉成int
    def str_to_int(input):
        for i in range(len(input)):
            try:
                input[i] = int(input[i])
            except:
                pass
    str_to_int(date)
    str_to_int(time)
    time[0] = time[0] + 8
    d = datetime(date[0],date[1],date[2],time[0],time[1],time[2])
    return [d,date,time]


def time_str_to_int_2(input_datetime):
    # 整理時間資料資料格式:'2023-02-04 09:30+00:00',
    date_time_list = input_datetime.split(" ")
    date = date_time_list[0].split("-")
    time = date_time_list[1].split(":")

    # 把時間從str轉成int
    def str_to_int(input):
        for i in range(len(input)):
            try:
                input[i] = int(input[i])
            except:
                pass
    str_to_int(date)
    str_to_int(time)
    d = datetime(date[0],date[1],date[2],time[0],time[1])
    return [d,date,time]