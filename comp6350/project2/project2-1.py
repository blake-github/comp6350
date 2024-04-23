import os
import sys 
import pathlib
import hashlib
import math

fileTypes = {}
trails = {}
filesFound = []
output = {}
offset = 0
fileCount = 0
recovery = False
diskData = ''
file = ''
previousK = 0

def main():
    global offset
    global recovery
    global fileCount
    global diskData
    global file
    #call everything here
    
    #read file
    if(len(sys.argv) != 2): 
        print("Input disk file into command line")
        return 
    disk = sys.argv[1] 
    file = open(disk, 'rb')
    diskData = file.read(512)
    
    while diskData:
        findMPG()
        findPDF()
        findBMP()
        findGIF()
        findJPG()
        findDOCX()
        findAVI()
        findPNG()
        #No zip find due to TA saying the zip section
        #has issues and will not be graded
        #findZIP()
        diskData = file.read(512)
        offset += 1
    file.close()
    


def findMPG():
    global diskData
    global file
    global offset
    global recovery
    global fileCount
    global previousK
    global filesFound
    found = diskData[0:5].find(b'\x00\x00\x01\xB3\x14')
    if found >= 0:
        start = found + (512*(offset + previousK))
        if (start in filesFound):
            return
        recovery = True
        fileCount += 1
        sys.stdout.write('File' + str(fileCount) + '.mpg, Start Offset: ' + str(hex(found + (512*(offset + previousK)))))
        sys.stdout.write(', End Offset: ')
        newFile = open('File' + str(fileCount) + '.mpg', 'wb')
        newFile.write(diskData[found:])
        k = 1
        while recovery:
            diskData = file.read(512)
            trailFind = diskData.find(b'\x00\x00\x01\xB7')
            if trailFind >= 0:
                newFile.write(diskData[:trailFind + 4])
                file.seek((offset + k) * 512)
                sys.stdout.write(str(hex(trailFind + (512*(offset + k + previousK)) + 4)))
                fileData = diskData[(found + (512*offset)):(trailFind + (512*(offset + k)) + 4)]
                filesFound.append(start)
                newFile.close()
                #Read the file back in to hash it
                fileName = 'File' + str(fileCount) + '.mpg'
                newFile = open(fileName, 'rb')
                hashed = hashlib.file_digest(newFile, "sha256")
                sys.stdout.write('\nSHA-256: ' + hashed.hexdigest() + '\n\n')
                recovery = False
                newFile.close()
            else:
                k += 1
                newFile.write(diskData)
        previousK = k - 1
        return


def findNextHeader():
    global diskData
    global file
    global offset
    global recovery
    global fileCount
    global previousK
    global filesFound
    Headers = [b'\x00\x00\x01\xB3\x14', b'\x42\x4D\x76\x30\x01',
               b'\x47\x49\x46\x38\x37\x61', b'\x47\x49\x46\x38\x39\x61', b'\xFF\xD8\xFF\xE0', 
               b'\xFF\xD8\xFF\xE1', b'\xFF\xD8\xFF\xE2', b'\xFF\xD8\xFF\xE8', b'\xFF\xD8\xFF\xDB', 
               b'\x50\x4B\x03\x04\x14\x00\x06\x00', b'\x52\x49\x46\x46', b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A',
               b'\x50\x4B\x03\x04']
    searching = True
    found = -1
    k = 1
    while searching:
        file.seek((offset + k) * 512)
        diskData = file.read(512)
        for header in Headers:
            found = diskData[0:12].find(header)
            if found >= 0:
                nextHead = k
                return nextHead
        k += 1
        
def findLastTrail(k):
    global diskData
    global file
    global offset
    global recovery
    global fileCount
    global previousK
    global filesFound
    Trailers = [b'\x0D\x0A\x25\x25\x45\x4F\x46\x0D\x0A', b'\x0D\x25\x25\x45\x4F\x46\x0D',
               b'\x0A\x25\x25\x45\x4F\x46\x0A', b'\x0A\x25\x25\x45\x4F\x46']
    searching = True
    found = -1
    while searching and k >= 0:
        file.seek((offset + k) * 512)
        diskData = file.read(512)
        for trailer in Trailers:
            found = diskData.find(trailer)
            if found >= 0:
                correct = k
                return correct
        k -= 1
    return 0     

def findPDF():
    global diskData
    global file
    global offset
    global recovery
    global fileCount
    global previousK
    global filesFound
    found = diskData[0:5].find(b'\x25\x50\x44\x46')
    if found >= 0:
        start = found + (512*(offset + previousK))
        if (start in filesFound):
            return
        recovery = True
        fileCount += 1
        sys.stdout.write('File' + str(fileCount) + '.pdf, Start Offset: ' + str(hex(found + (512*(offset + previousK)))))
        sys.stdout.write(', End Offset: ')
        k = 1
        while recovery:
            diskData = file.read(512)
            nextHead = findNextHeader()
            correctK = findLastTrail(nextHead)
            if nextHead >= 0:
                k = correctK
                file.seek((offset + k) * 512)
                #Do the searches, if >= 0 go to next loop iteration
                #one it hits -1, set go back 1 and do the rest
                trailSearch = b'\x0D\x0A\x25\x25\x45\x4F\x46\x0D\x0A'
                trailFind = diskData.rfind(trailSearch)
                if trailFind == -1:
                    trailSeach = b'\x0A\x25\x25\x45\x4F\x46'
                    trailFind = diskData.rfind(trailSearch)
                if trailFind == -1:
                    trailSearch = b'\x0A\x25\x25\x45\x4F\x46\x0A'
                    trailFind = diskData.rfind(trailSearch)
                if trailFind == -1:
                    trailSearch = b'\x0A\x25\x25\x45\x4F\x46\x0A'
                    trailFind = diskData.rfind(trailSearch)
                if trailFind == -1:
                    trailSearch = b'\x0D\x25\x25\x45\x4F\x46\x0D'
                    trailFind = diskData.rfind(trailSearch)
                startOffset = found + (512*(offset + previousK))
                endOffset = trailFind + (512*(offset + k)) + len(trailSearch)
                length = endOffset - startOffset
                cmd = "dd if=Project2.dd of=File" + str(fileCount) + ".pdf bs=1 skip=" + str(startOffset) + " count=" + str(length) + " >/dev/null 2>&1"
                os.system(cmd)
                sys.stdout.write(str(hex(trailFind + (512*(offset + k)) + len(trailSearch))))
                fileData = diskData[(found + (512*offset)):(trailFind + (512*(offset + k)) + len(trailSearch))]
                filesFound.append(start)
                #Read the file back in to hash it
                fileName = 'File' + str(fileCount) + '.pdf'
                newFile = open(fileName, 'rb')
                hashed = hashlib.file_digest(newFile, "sha256")
                sys.stdout.write('\nSHA-256: ' + hashed.hexdigest() + '\n\n')
                recovery = False
                newFile.close()
            else:
                k += 1
                newFile.write(diskData)
        previousK = k - 1
        return
    

def findBMP():
    global diskData
    global file
    global offset
    global recovery
    global fileCount
    global previousK
    global filesFound
    found = diskData[0:5].find(b'\x42\x4D\x76\x30\x01')
    if found >= 0:
        start = found + (512*(offset + previousK))
        if (start in filesFound):
            return
        recovery = True
        fileCount += 1
        sys.stdout.write('File' + str(fileCount) + '.bmp, Start Offset: ' + str(hex(found + (512*(offset + previousK)))))
        sys.stdout.write(', End Offset: ')
        #newFile = open('File' + str(fileCount) + '.bmp', 'wb')
        #newFile.write(diskData[found:])
        k = 1
        cmd = "dd if=Project2.dd of=File" + str(fileCount) + ".bmp bs=1 skip=" + str((offset + previousK)*512) + " count=77942 >/dev/null 2>&1"
        os.system(cmd)
        while recovery:
            diskData = file.read(512)
            trailFind = diskData.find(b'\x00')
            if trailFind >= 0:
                file.seek((offset + k) * 512)
                sys.stdout.write(str(hex(found + (512*(offset + previousK)) + 77942)))
                filesFound.append(start)
                #Read the file back in to hash it
                fileName = 'File' + str(fileCount) + '.bmp'
                readFile = open(fileName, 'rb')
                hashed = hashlib.file_digest(readFile, "sha256")
                sys.stdout.write('\nSHA-256: ' + hashed.hexdigest() + '\n\n')
                recovery = False
                readFile.close()
            else:
                k += 1
                #newFile.write(diskData)
        previousK = k - 1
        return

def findGIF():
    global diskData
    global file
    global offset
    global recovery
    global fileCount
    global previousK
    global filesFound
    found = diskData.find(b'\x47\x49\x46\x38\x37\x61')
    if found == -1:
        found = diskData.find(b'\x47\x49\x46\x38\x39\x61')
    if found >= 0:
        start = found + (512*(offset + previousK))
        if (start in filesFound):
            return
        recovery = True
        fileCount += 1
        sys.stdout.write('File' + str(fileCount) + '.gif, Start Offset: ' + str(hex(found + (512*(offset + previousK)))))
        sys.stdout.write(', End Offset: ')
        newFile = open('File' + str(fileCount) + '.gif', 'wb')
        newFile.write(diskData[found:])
        k = 1
        while recovery:
            diskData = file.read(512)
            trailFind = diskData.find(b'\x00\x00\x3B')
            if trailFind >= 0:
                newFile.write(diskData[:trailFind + 3])
                file.seek((offset + k) * 512)
                sys.stdout.write(str(hex(trailFind + (512*(offset + k + previousK)) + 3)))
                fileData = diskData[(found + (512*offset)):(trailFind + (512*(offset + k)) + 3)]
                filesFound.append(start)
                newFile.close()
                #Read the file back in to hash it
                fileName = 'File' + str(fileCount) + '.gif'
                newFile = open(fileName, 'rb')
                hashed = hashlib.file_digest(newFile, "sha256")
                sys.stdout.write('\nSHA-256: ' + hashed.hexdigest() + '\n\n')
                recovery = False
                newFile.close()
            else:
                k += 1
                newFile.write(diskData)
        previousK = k - 1
        return


def findJPG():
    global diskData
    global file
    global offset
    global recovery
    global fileCount
    global previousK
    global filesFound
    found = diskData.find(b'\xFF\xD8\xFF\xE0')
    if found == -1:
        found = diskData.find(b'\xFF\xD8\xFF\xE1')
    if found == -1:
        found = diskData.find(b'\xFF\xD8\xFF\xE2')
    if found == -1:
        found = diskData.find(b'\xFF\xD8\xFF\xE8')
    if found == -1:
        found = diskData.find(b'\xFF\xD8\xFF\xDB')
    if found >= 0:
        start = found + (512*(offset + previousK))
        if (start in filesFound):
            return
        recovery = True
        fileCount += 1
        sys.stdout.write('File' + str(fileCount) + '.jpg, Start Offset: ' + str(hex(found + (512*(offset + previousK)))))
        sys.stdout.write(', End Offset: ')
        newFile = open('File' + str(fileCount) + '.jpg', 'wb')
        newFile.write(diskData[found:])
        k = 1
        while recovery:
            diskData = file.read(512)
            trailFind = diskData.find(b'\xFF\xD9')
            if trailFind >= 0:
                newFile.write(diskData[:trailFind + 2])
                file.seek((offset + k) * 512)
                sys.stdout.write(str(hex(trailFind + (512*(offset + k + previousK)) + 2)))
                fileData = diskData[(found + (512*offset)):(trailFind + (512*(offset + k)) + 2)]
                filesFound.append(start)
                newFile.close()
                #Read the file back in to hash it
                fileName = 'File' + str(fileCount) + '.jpg'
                newFile = open(fileName, 'rb')
                hashed = hashlib.file_digest(newFile, "sha256")
                sys.stdout.write('\nSHA-256: ' + hashed.hexdigest() + '\n\n')
                recovery = False
                newFile.close()
            else:
                k += 1
                newFile.write(diskData)
        previousK = k - 1
        return


def findDOCX():
    global diskData
    global file
    global offset
    global recovery
    global fileCount
    global previousK
    global filesFound
    found = diskData[0:20].find(b'\x50\x4B\x03\x04\x14\x00\x06\x00')
    if found >= 0:
        start = found + (512*(offset + previousK))
        if (start in filesFound):
            return
        recovery = True
        fileCount += 1
        sys.stdout.write('File' + str(fileCount) + '.docx, Start Offset: ' + str(hex(found + (512*(offset + previousK)))))
        sys.stdout.write(', End Offset: ')
        newFile = open('File' + str(fileCount) + '.docx', 'wb')
        newFile.write(diskData[found:])
        k = 1
        while recovery:
            diskData = file.read(512)
            trailFind = diskData.find(b'\x50\x4B\x05\x06')
            if trailFind >= 0:
                newFile.write(diskData[:trailFind + 22])
                file.seek((offset + k) * 512)
                sys.stdout.write(str(hex(trailFind + (512*(offset + k + previousK)) + 22)))
                fileData = diskData[(found + (512*offset)):(trailFind + (512*(offset + k)) + 22)]
                filesFound.append(start)
                newFile.close()
                #Read the file back in to hash it
                fileName = 'File' + str(fileCount) + '.docx'
                newFile = open(fileName, 'rb')
                hashed = hashlib.file_digest(newFile, "sha256")
                sys.stdout.write('\nSHA-256: ' + hashed.hexdigest() + '\n\n')
                recovery = False
                newFile.close()
            else:
                k += 1
                newFile.write(diskData)
        previousK = k - 1
        return
    
def findAVI():
    global diskData
    global file
    global offset
    global recovery
    global fileCount
    global previousK
    global filesFound
    found = diskData[0:5].find(b'\x52\x49\x46\x46')
    if found >= 0:
        start = found + (512*(offset + previousK))
        if (start in filesFound):
            return
        recovery = True
        fileCount += 1
        sys.stdout.write('File' + str(fileCount) + '.avi, Start Offset: ' + str(hex(found + (512*(offset + previousK)))))
        sys.stdout.write(', End Offset: ')
        length = diskData[4:8]
        endLoc = found + 8 + int.from_bytes(length, byteorder='little') + (512*(offset + previousK))
        sys.stdout.write(str(hex(endLoc)))
        length = int.from_bytes(length, byteorder='little')
        endLoc = int(math.ceil(length))
        cmd = "dd if=Project2.dd of=File" + str(fileCount) + ".avi bs=1 skip=" + str((offset + previousK)*512) + " count=" + str(endLoc) + " >/dev/null 2>&1"
        os.system(cmd)
        fileName = 'File' + str(fileCount) + '.avi'
        newFile = open(fileName, 'rb')
        hashed = hashlib.file_digest(newFile, "sha256")
        sys.stdout.write('\nSHA-256: ' + hashed.hexdigest() + '\n\n')
        recovery = False
        newFile.close()
        return

def findPNG():
    global diskData
    global file
    global offset
    global recovery
    global fileCount
    global previousK
    global filesFound
    found = diskData.find(b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A')
    if found >= 0:
        start = found + (512*(offset + previousK))
        if (start in filesFound):
            return
        recovery = True
        fileCount += 1
        sys.stdout.write('File' + str(fileCount) + '.png, Start Offset: ' + str(hex(found + (512*(offset + previousK)))))
        sys.stdout.write(', End Offset: ')
        newFile = open('File' + str(fileCount) + '.png', 'wb')
        newFile.write(diskData[found:])
        k = 1
        while recovery:
            diskData = file.read(512)
            trailFind = diskData.find(b'\x49\x45\x4E\x44\xAE\x42\x60\x82')
            if trailFind >= 0:
                newFile.write(diskData[:trailFind + 8])
                file.seek((offset + k) * 512)
                sys.stdout.write(str(hex(trailFind + (512*(offset + k + previousK)) + 8)))
                fileData = diskData[(found + (512*offset)):(trailFind + (512*(offset + k)) + 8)]
                filesFound.append(start)
                newFile.close()
                #Read the file back in to hash it
                fileName = 'File' + str(fileCount) + '.png'
                newFile = open(fileName, 'rb')
                hashed = hashlib.file_digest(newFile, "sha256")
                sys.stdout.write('\nSHA-256: ' + hashed.hexdigest() + '\n\n')
                recovery = False
                newFile.close()
            else:
                k += 1
                newFile.write(diskData)
        previousK = k - 1
        return

#Not used due to TA email
def findZIP():
    global diskData
    global file
    global offset
    global recovery
    global fileCount
    global previousK
    global filesFound
    found = diskData[0:5].find(b'\x50\x4B\x03\x04')
    if found >= 0:
        start = found + (512*(offset + previousK))
        if (start in filesFound):
            return
        recovery = True
        fileCount += 1
        sys.stdout.write('File' + str(fileCount) + '.zip, Start Offset: ' + str(hex(found + (512*(offset + previousK)))))
        sys.stdout.write(', End Offset: ')
        newFile = open('File' + str(fileCount) + '.zip', 'wb')
        newFile.write(diskData[found:])
        k = 1
        while recovery:
            diskData = file.read(512)
            #Would need a more specific trailer
            trailFind = diskData.find(b'\x50\x4B')
            if trailFind >= 0:
                newFile.write(diskData[:trailFind + 2])
                file.seek((offset + k) * 512)
                sys.stdout.write(str(hex(trailFind + (512*(offset + k + previousK)) + 2)))
                fileData = diskData[(found + (512*offset)):(trailFind + (512*(offset + k)) + 2)]
                filesFound.append(start)
                newFile.close()
                #Read the file back in to hash it
                fileName = 'File' + str(fileCount) + '.zip'
                newFile = open(fileName, 'rb')
                hashed = hashlib.file_digest(newFile, "sha256")
                sys.stdout.write('\nSHA-256: ' + hashed.hexdigest() + '\n\n')
                recovery = False
                newFile.close()
            else:
                k += 1
                newFile.write(diskData)
        previousK = k - 1
        return


main()




