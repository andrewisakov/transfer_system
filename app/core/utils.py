import re


def check_datetime_format(date_time):
    # TODO: По уму бы проверить - а точно дата/время ? :)
    return re.match('\d{4}\-\d{2}\-\d{2}(\s\d{2}\:\d{2}\:\d{2})?', date_time)
