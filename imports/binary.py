import math

def toBinary(string):
  l,m=[],[]
  for i in string:
    l.append(ord(i))
  for i in l:
    m.append(str(int(bin(i)[2:])))
  return m

def toString(binary):
  l=[]
  m=""
  for i in binary:
    b=0
    c=0
    k=int(math.log10(i))+1
    for j in range(k):
      b=((i%10)*(2**j))   
      i=i//10
      c=c+b
    l.append(c)
  for x in l:
    m=m+chr(x)
  return m