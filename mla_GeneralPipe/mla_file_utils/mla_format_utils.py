suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']


def convert_to_readable_date(date):
    """
    Convert a time.localtime number into a readable number,
        i.e. 2006/05/12, 14:02:38
    :param date: time.localtime number
    :return:
    """
    new_date = '%s/%s/%s, %s:%s:%s' % ('{0:02d}'.format(date[0]),
                                       '{0:02d}'.format(date[1]),
                                       '{0:02d}'.format(date[2]),
                                       '{0:02d}'.format(date[3]),
                                       '{0:02d}'.format(date[4]),
                                       '{0:02d}'.format(date[5]))

    return new_date


def convert_to_readable_size(nbytes):
    """
    Convert a number of bytes into a readable number, i.e. 5 MB, 12 KB, etc.
    :param nbytes: size number to convert
    :type nbytes: int

    :return: converted number
    """
    if nbytes == 0:
        return '0 B'
    i = 0
    while nbytes >= 1024 and i < len(suffixes)-1:
        nbytes /= 1024.
        i += 1
    f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
    return '%s %s' % (f, suffixes[i])
