# n=1234
# num=n
# result=0
# while num>0:
#   lst_digit=num%10
#   result=(result*10)+lst_digit
#   num=num//10

# if n==result:
#     print("the given number is palindrom")

# else:
   
#     print("not palindrom")

# n=153
# num=n
# nod=len(str(n))
# total=0
# while num>0:
#     ld=num%10
#     total=total+(ld**nod)
#     num=num//10
# if total==n:
#     print("the given no is armstrong no")

# else:
#     print("not armstrong")
# from math import sqrt
# n=36
# List=[]
# for i in range (1,int(sqrt(n))+1):
#     if n%i==0:
#         List.append(i)
#         if n//i !=i:
#             List.append(n//i)
#             List.sort()
# print(List)
        
# list=[5,6,7,7,8,111,1,1,5,1,1]
# freq_map=dict()
# for i in range(0,len(list)):
#     if list[i] in freq_map:
#         freq_map[list[i]]+=1

#     else:
#         freq_map[list[i]]=1

# print(freq_map)

# has_map=dict()
# n=len(list)
# for i in range (0,n):
#     has_map[list[i]]=has_map.get(list[i],0)+1

# print(has_map)
# n=[5,3,2,2,1,5,5,7,5,10]
# m=[10,111,1,9,5,67,2]
# hash_list=[0]*11
# for num in n:
#     hash_list[num]+=1
# for num in m:
#     if num<1 or num>10:
#         print(0)
#     else:
#         n=[5,3,2,2,1,5,5,7,5,10]
# m=[10,111,1,9,5,67,2]
# hash_list=[0]*11
# Create hash list (frequency array)
# hash_list = [0] * 11  # index 0 to 10

# # Count frequency
# for num in n:
#     if 1 <= num <= 10:
#         hash_list[num] += 1

# # Query frequencies
# for num in m:
#     if 1 <= num <= 10:
#         print(hash_list[num])
#     else:
#         print(0)


# n=[5,3,2,2,1,5,5,7,5,10]
# m=[10,111,1,9,5,67,2]

# frq_map=dict()
# for i in range(0,len(n)):
#     if n[i] in frq_map:
#         frq_map[n[i]]+=1
#     else:
#         frq_map[n[i]]=1

# for r in m:
#     if r in frq_map:
#         print(frq_map[r])
#     else:
#         print(0)
# recursion(head type)
# def fun(x,n):
#     if n==0:
#         return
#     print(x)
#     fun(x,n-1)   
# fun(5,3)

# recursion(tail type)
# def fun(x,n):
#     if n==0:
#         return
#     fun(x,n-1)   
#     print(x)
# fun(5,5)

# def fun(n):
#     if n==0:
#         return
#     print(n)
#     fun(n-1)
# fun(5)

# def fun(n):
#     if n==1:
#         return 1
#     return n+fun(n-1)
# print(fun(6))

# def fun(sum,i,n):
#     if i>n:
#         print(sum)
#         return
#     fun(sum+i,i+1,n)
# fun(0,1,10)
    
# def fact(n):
#     if n==0 or n==1:
#         return 1
#     return(n*fact(n-1))
# print(fact(5))

#reverse an array using recursion
# arr=[4,5,3,2,7,8,1]
# def reverece(arr,left,right):
#     if left>=right:
#         return
#     arr[left], arr[right]=arr[right],arr[left]
#     reverece(arr,left+1,right-1)

# reverece(arr,0,len(arr)-1)
# print(arr)

# usinh for loop
# n= len(arr)
# for i in range (n//2):
#     arr[i],arr[n-i-1]=arr[n-i-1],arr[i]

# print(arr)

# check a string is palindrome or no
# s='mom'
# lst=[s]
# k=lst[::-1]
# if lst==k:
#     print("the given str is palindrome ")
# else:
#     print("not palindrome")


# check a list was palindrom or not using while loop
# s='mom'
# n=len(s)
# left=0
# right=n-1
# while right>left:
#     left+=1
#     right-=1
#     if s[left]!=s[right]:
#         print("not palindrome")
#     else:
#         print("is palindrome")

# using reursion / s='mom'
# def fun(s,left,right):
#     if left>=right:
#         return True
#     if s[left]!=s[right]:
#         return False
#     return fun(s,left+1,right-1)

# print(fun('mom',0,len('mom')-1))

#  reverece the list or arry using recursion
# def fun(s,left,right):
#     if left>=right:
#         return s
#     s[left],s[right]=s[right],s[left]
#     return fun(s,left+1,right-1)
# s=[4,3,6,8,4,3,2,1]
# print(fun(s,0,len(s)-1))

# sorting algorothm (selection sort)
s=[4,5,3,7,2,6,1]
n=len(s)
for i in range(0,n):
    for j in range(i+1,n):
        if s[j]<s[i]:
            s[i],s[j]=s[j],s[i]
            # print(s)
print('sorted lst:',s)

# using function
def fun(num):
    n=len(num)
    for i in range(n):
        min_inx=i
        for j in range(i+1,n):
            if num[j]<num[min_inx]:
                min_inx=j
            num[i],num[min_inx]=num[min_inx],num[i]
        print(num)


                  