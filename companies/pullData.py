import urllib2
import ssl
import socket
import json
import csv
import os.path

def callUrl(url,code, errors):
    
    try:
        data = urllib2.urlopen(url, timeout = 3).read()
    except urllib2.URLError, e:
        with open(errors,'a') as errorfile:
            errorfile.write('code ' + code +' needs to be tried again\n')
    except socket.timeout:
        with open(errors,'a') as errorfile:
            errorfile.write('code ' + code +' needs to be tried again\n')
    except ssl.SSLError:
        with open(errors,'a') as errorfile:
            errorfile.write('code ' + code +' needs to be tried again\n')
    return data = json.loads(data)

def pullData(url, code, errors):

    data = callUrl(url, code, errors)

    if data[0][0] == 'Data did not find.':
        dictionary = {}
    else:
        dictionary = dict(zip(data[0], data[1][0]['data']))
        dictionary['Code'] = code
    return dictionary

def getData(lastCode, fname, fieldnames, lastwritten, errors):
    for num in range(lastCode, 10000):
        print num
        try:
            salesPerShareUrl = "https://www.valueresearchonline.com/stocks/salesPerShare.asp?code="+str(num)
            salesPerShareData = pullData(salesPerShareUrl, str(num), errors)
            if salesPerShareData != {}:
                with open(fname,'a') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    outcsv = csv.writer(csvfile)
                    writer.writerow(salesPerShareData)

                with open(lastwritten,'w') as txtfile:
                    txtfile.write(str(num))

        except ValueError:
            with open(errors,'a') as errorfile:
                errorfile.write('code ' + str(num) +' needs to be tried again\n')

if __name__ == '__main__':
    fname = "company-funda.csv"
    lastwritten = "lastwritten.txt"
    errors = 'errors.txt'
    lastCode = 0
    fieldnames = [u'Company',u'Code', u'Mar-92', u'Mar-93', u'Mar-94', u'Mar-95', u'Mar-96', u'Mar-97', u'Mar-98', u'Mar-99', u'Mar-00', u'Mar-01', u'Mar-02', u'Mar-03', u'Mar-04', u'Mar-05', u'Mar-06', u'Mar-07', u'Mar-08', u'Mar-09', u'Mar-10', u'Mar-11', u'Mar-12', u'Mar-13', u'Mar-14', u'Mar-15', u'Sep-15*' ]

    if os.path.isfile(lastwritten):
        with open("lastwritten.txt", 'r') as f:
            content = f.read()
            lastCode = int(content)
            print  'resuming after ', lastCode

    if(lastCode <= 0):
        with open(fname,'wb') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

    getData(lastCode +1 , fname, fieldnames, lastwritten, errors)
