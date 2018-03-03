import os
from math import radians, cos, sin, asin, sqrt
import csv

#容忍的最小距离
tolerance = 2000

#文件保存地址
fileSave = 'C:\Temp\map\jieguo.csv'

class LeastCover:
	"""
	最小覆盖矩形
	"""

	# def __init__(self,up,down,left,right):
	# 	self.up = up
	# 	self.down = down
	# 	self.left = left
	# 	self.right = right


	def __init__(self,jingweidu):
		self.up = max(jingweidu.weiduList)
		self.down = min(jingweidu.weiduList)
		self.left = min(jingweidu.jingduList)
		self.right = max(jingweidu.jingduList)
		
	def toString(self):
		print("up:"+ str(self.up) + "	down:" + str(self.down) + "	left:" + str(self.left) + "	right:" + str(self.right))


class JingWeiDu:
	"""
	两个List分别放经度和维度
	"""

	def __init__(self):
		self.jingduList = list()
		self.weiduList = list()
	def insert(self,jingdu,weidu):
		self.jingduList.append(jingdu)
		self.weiduList.append(weidu)


class Measure:
	"""
	经纬度的处理
	"""

	def haversine(self,lon1, lat1, lon2, lat2): 
		""" 
		经度1，纬度1，经度2，纬度2 （十进制度数）  
		"""  

		# 将十进制度数转化为弧度  
		lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

		# haversine公式  
		dlon = lon2 - lon1   
		dlat = lat2 - lat1   
		a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2  
		c = 2 * asin(sqrt(a))   
		r = 6371 # 地球平均半径，单位为公里  
		return c * r * 1000 

	def isShortEnough(self,zoneA,zoneB):
		""" 
		两矩形的最短距离是否大致小于tolerance，是返回true，否返回false
		"""  

		#纬度越高，经度单位差值越短
		stdweidu = max(zoneA.up,zoneB.up)


		#扩张区域A，直至上下左右都移出至少两公里
		leftC = zoneA.left
		while self.haversine(leftC,stdweidu,zoneA.left,stdweidu) < tolerance:
			leftC = leftC - 0.01

		rightC = zoneA.right
		while self.haversine(rightC,stdweidu,zoneA.right,stdweidu) < tolerance:
			rightC = rightC + 0.01


		upC = zoneA.up
		while self.haversine(zoneA.left,upC,zoneA.left,zoneA.up) < tolerance:
			upC = upC + 0.01

		downC = zoneA.down
		while self.haversine(zoneA.left,downC,zoneA.left,zoneA.down) < tolerance:
			downC = downC - 0.01

		# A的扩展矩形和B是否相交，如果相交返回true
		if downC > zoneB.up or leftC > zoneB.right or zoneB.down > upC or zoneB.left > rightC:
			return False
		else:
			return True


	def shortestDis(self,setA,setB):
		""" 
		返回两个集合的最短距离
		"""  
		shortest = 100000
		lenA = len(setA.jingduList)
		lenB = len(setB.jingduList)
		for i in range(lenA):
			for j in range(lenB):
				# print(str(setA.jingduList[i])+ ',' + str(setA.weiduList[i]) + ',' + str(setB.jingduList[j]) + ',' + str(setB.weiduList[j]))
				temp = self.haversine(setA.jingduList[i],setA.weiduList[i],setB.jingduList[j],setB.weiduList[j])
				# print(temp)
				if temp < shortest:
					shortest = temp
		return shortest




class FileHandle(object):
	"""
	处理目录以及kml文件相关操作
	"""

	def __init__(self,file_dir):  
		"""
		初始化时输入文件目录 
		"""
		for root, dirs, files in os.walk(file_dir):  
			self.root = root
			self.files = files
			# 2表示未定义，1表示相邻，0表示不相邻
			self.matrix = [[2 for i in range(len(files))] for i in range(len(files))]
			for i in range(len(files)):
				self.matrix[i][i] = 1 

	def kmlReader(self,filename):
		"""
		处理kml文件，获取所有经纬度对
		"""
		with open(filename,'r',encoding = 'UTF-8') as f:
			k = f.read()
			templist = k.split("<coordinates>")
			listlength = len(templist)
			tempstring = ""
			# 预防出现几个不相连的区域
			for i in range(1,listlength):
				if i == 1:
					tempstring = tempstring + templist[i].split("</coordinates>")[0]
				else:
					tempstring = tempstring + " " + templist[i].split("</coordinates>")[0]
			jingweipair = tempstring.split(' ')
			#最小矩形覆盖的实例
			jingweidu = JingWeiDu()
			for k in jingweipair:
				pair = k.split(',')
				jingdu = float(pair[0])
				weidu = float(pair[1])
				jingweidu.insert(jingdu,weidu)
			leastCover = LeastCover(jingweidu)
			print(filename + " done")
		return([jingweidu,leastCover])


	def getBoundList(self):
		"""
		获取所有县的上下左右边界
		"""
		self.boundList = list()
		self.areaList = list()
		for file in self.files:
			filename = self.root + '\\' + file
			tt = self.kmlReader(filename)
			self.boundList.append(tt[1])
			self.areaList.append(tt[0])
		# for item in boundList:
		# 	item.toString()


	def initialMatrix(self):
		"""
		初始化矩阵，第一个被调用
		"""
		me = Measure()
		self.getBoundList()
		for i in range(len(self.boundList)):
			for j in range(i):
				if not me.isShortEnough(self.boundList[i],self.boundList[j]):
					self.matrix[i][j] = 0
					self.matrix[j][i] = 0

	def ultimateProcessor(self):
		"""
		计算最终矩阵
		"""
		me = Measure()
		for i in range(len(self.areaList)):
			for j in range(i):
				#如果不是距离特别远则进入这步计算
				if self.matrix[i][j] == 2:
					#比较这两个集合中的所有点之间的距离，取最小的
					shortest = me.shortestDis(self.areaList[i],self.areaList[j])
					print(shortest)
					#如果两个集合之间的最短距离小于容忍度，则记为两县交界，否则记为不交界
					if shortest < tolerance:
						self.matrix[i][j] = 1
						self.matrix[j][i] = 1
					else:
						self.matrix[i][j] = 0
						self.matrix[j][i] = 0

	#todo 打印成csv
	def printCsv(self):
		"""
		打印最终矩阵
		"""
		with open(fileSave,'w') as f:
			#写第一行
			f.write('')
			for i in range(len(self.files)):
				f.write(',' + self.files[i].split(".kml")[0])
			f.write('\n')
			#写之后所有行
			for i in range(len(self.files)):
				f.write(self.files[i].split(".kml")[0])
				for j in range(len(self.files)):
					f.write(',' + str(self.matrix[i][j]))
				f.write('\n')


		





me = Measure()
k = FileHandle('C:\maps')
k.initialMatrix()
k.ultimateProcessor()
k.printCsv()

# print(k.files[1])
# print(k.areaList[1].jingduList)
# print(k.areaList[1].weiduList)


# print(k.files[2])
# print(k.areaList[2].jingduList)
# print(k.areaList[2].weiduList)


# mindis = me.shortestDis(k.areaList[1],k.areaList[2])
# print(mindis)


# for i in range(len(k.matrix)):
# 	for j in range(len(k.matrix)):
# 		print(k.matrix[i][j])
# 	print('\n')






# temp = me.haversine(k.areaList[1].jingduList[0],k.areaList[1].weiduList[0],k.areaList[2].jingduList[0],k.areaList[2].weiduList[0])
# print(temp)



