#Konvertere bilde/video/fil til binær data 

def convertBinary(fil):

    with open(fil, 'rb'): 
        binaryData = fil.read() 

    return binaryData


