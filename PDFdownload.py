import requests

'''
* Script realizzato per il download dei PDF contenenti i menu
* dalla piattaforma del Ersu di Camerino.
*
*
* @author Francesco Coppola
'''

print('Scarico i tuoi bellissimi file')

url = "https://www.docdroid.net/5zdNEGN/venerdi.pdf"  
r = requests.get(url)

with open('/mnt/c/Users/fcopp/Downloads/venerdi.pdf', 'wb') as f:  
    f.write(r.content)

# Log per i metatada dell'HTTP
print(r.status_code)  
print(r.headers['content-type'])  
print(r.encoding)  