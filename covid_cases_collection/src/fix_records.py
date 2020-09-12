import optparse
from collections import OrderedDict
import os


def parse_parameters(opts):
    param = OrderedDict()
    param['file'] = opts.file
    param['operation'] = opts.operation
    param['number_of_records'] = int(opts.number_of_records)
    return param


def delete_last_record(series_file):
    with open(series_file, "r+", encoding="utf-8") as f:

        # Move the pointer to the end of the file
        f.seek(0, os.SEEK_END)

        # This code means the following code skips the very last character in the file -
        # i.e. in the case the last line is null we delete the last line
        # and the penultimate one
        pos = f.tell() - 1

        # Read each character in the file one at a time from the penultimate
        # character going backwards, searching for a newline character
        # If we find a new line, exit the search
        while pos > 0 and f.read(1) != "\n":
            pos -= 1
            f.seek(pos, os.SEEK_SET)

        # So long as we're not at the start of the file, delete all the characters ahead
        # of this position
        if pos > 0:
            f.seek(pos, os.SEEK_SET)
            f.truncate()
            print("Last record removed !")
        f.close()

def main(opts):
    params= parse_parameters(opts)
    if params['operation'] == "dl":
        for i in range(params['number_of_records']):
            delete_last_record(params['file'])
    
if __name__ == '__main__':

    optparser = optparse.OptionParser()

    optparser.add_option(
        "-f", "--file", default = "../data/out/jhu_c.csv", help="The path of the file to be fixed")
    optparser.add_option(
        "-o", "--operation", default='dl', help="use dl: deletes the last line")
    optparser.add_option(
        "-n", "--number_of_records", default=1, help="applies operation specified in parameter -o over the last n records")
    opts = optparser.parse_args()[0]

    main(opts)