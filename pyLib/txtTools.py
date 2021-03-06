#!/usr/bin/env python
import sys, fileinput

def openIOFile( fileName , mode='r' ):
  if(mode=='r'):
    message='reading.'
  elif(mode=='w'):
    message='writing.'
  elif(mode=='a'):
    message='appending.'
  else:
    message='reading, by default.'
    mode='r'

  try:
    xfile=file(fileName, mode)
    print(" Opening file {} for {}".format(fileName,message))
  except IndexError:
    print(" Error: "+fileName+" does not exist. Exiting ...")
    sys.exit(1)

  return xfile

# - - - - - - - - - - - - - - - - - - - - - - - #

def checkFixAndWrite( writeFile , xLine , checkDict ):
  changed = False
  for key in checkDict.keys():
    if( key in xLine ):
      writeFile.write(checkDict[key])
      changed = True
      break

  if( not changed ):
    writeFile.write(xLine)

# - - - - - - - - - - - - - - - - - - - - - - - #

def checkAndReplace( iLine , checkStr , aidStr , replaceStr ):
  if(aidStr in iLine and checkStr in iLine):
    return iLine.replace(checkStr,replaceStr)
  else:
    return iLine

# - - - - - - - - - - - - - - - - - - - - - - - #

def replaceEntry( fileName, oldStr , newStr ):
  for line in fileinput.FileInput(fileName , inplace=True):
    line = line.replace(oldStr , newStr )
    print(line.strip())

# - - - - - - - - - - - - - - - - - - - - - - - #

def commentOutLine( fileName, keyDict ):
  for line in fileinput.FileInput(fileName , inplace=True):
    for key in keyDict:
      if( key in line and keyDict[key] in line):
        line=line.replace(line, "!*"+line)
    print( line, )

# - - - - - - - - - - - - - - - - - - - - - - - #
