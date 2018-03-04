import os
from math import radians, cos, sin, asin, sqrt
import csv
import sys
import numpy

# 容忍的最小距离
tolerance = 2000

# 文件保存地址
fileSave = 'C:\\Users\\tangheng\\Dropbox\\数据相关\\中国所有相邻的县\\中国所有县级城市相邻关系.csv'
# 地图所在地址
mapLocate = 'C:\\Users\\tangheng\\Dropbox\\数据相关\\中国各县级地区边界数据'

class LeastCover:
	"""
	最小覆盖矩形
	"""

	def __init__(self,jingweidu):
		self.up = max(jingweidu.weiduList)
		self.down = min(jingweidu.weiduList)
		self.left = min(jingweidu.jingduList)
		self.right = max(jingweidu.jingduList)
		
	def toString(self):
		return "up:"+ str(self.up) + "	down:" + str(self.down) + "	left:" + str(self.left) + "	right:" + str(self.right)


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

		#  haversine公式  
		dlon = lon2 - lon1
		dlat = lat2 - lat1
		a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
		c = 2 * asin(sqrt(a))
		# 地球半径(公里)
		r = 6371
		return c * r * 1000

	def isShortEnough(self,zoneA,zoneB):
		""" 
		两矩形的最短距离是否大致小于tolerance，是返回true，否返回false
		"""  

		# 纬度越高，经度单位差值越短
		stdweidu = max(zoneA.up,zoneB.up)


		# 扩张区域A，直至上下左右都移出至少两公里
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

		#  A的扩展矩形和B是否相交，如果相交返回true
		if downC > zoneB.up or leftC > zoneB.right or zoneB.down > upC or zoneB.left > rightC:
			return [False,0,0,0,0,0,0,0,0]
		else:
			leftD = zoneB.left
			while self.haversine(leftD,stdweidu,zoneB.left,stdweidu) < tolerance:
				leftD = leftD - 0.01

			rightD = zoneB.right
			while self.haversine(rightD,stdweidu,zoneB.right,stdweidu) < tolerance:
				rightD = rightD + 0.01


			upD = zoneB.up
			while self.haversine(zoneB.left,upD,zoneB.left,zoneB.up) < tolerance:
				upD = upD + 0.01

			downD = zoneB.down
			while self.haversine(zoneB.left,downD,zoneB.left,zoneB.down) < tolerance:
				downD = downD - 0.01

			# A和B的扩展矩形的交集
			upA = sorted([zoneA.up,zoneA.down,upD,downD])[2]
			downA = sorted([zoneA.up,zoneA.down,upD,downD])[1]
			leftA = sorted([zoneA.left,zoneA.right,leftD,rightD])[1]
			rightA = sorted([zoneA.left,zoneA.right,leftD,rightD])[2]

			# B和A的扩展矩形的交集
			upB = sorted([zoneB.up,zoneB.down,upC,downC])[2]
			downB = sorted([zoneB.up,zoneB.down,upC,downC])[1]
			leftB = sorted([zoneB.left,zoneB.right,leftC,rightC])[1]
			rightB = sorted([zoneB.left,zoneB.right,leftC,rightC])[2] 

			return [True,upA,downA,leftA,rightA,upB,downB,leftB,rightB]


	def shortestDis(self,rowsetA,rowsetB,A,B,chonghequyu):
		""" 
		返回两个集合的最短距离
		"""  
		shortest = 100000

		lenA = len(rowsetA.jingduList)
		lenB = len(rowsetB.jingduList)

		setA = JingWeiDu()
		setB = JingWeiDu()

		# 缩小A集合的大小
		for i in range(lenA):
			if rowsetA.jingduList[i] >= chonghequyu[A][B][2] and rowsetA.jingduList[i] <= chonghequyu[A][B][3] \
				and rowsetA.weiduList[i] >= chonghequyu[A][B][1] and rowsetA.weiduList[i] <= chonghequyu[A][B][0]:
				setA.jingduList.append(rowsetA.jingduList[i])
				setA.weiduList.append(rowsetA.weiduList[i])

		# 缩小B集合的大小
		for i in range(lenB):
			if rowsetB.jingduList[i] >= chonghequyu[B][A][2] and rowsetB.jingduList[i] <= chonghequyu[B][A][3] \
				and rowsetB.weiduList[i] >= chonghequyu[B][A][1] and rowsetB.weiduList[i] <= chonghequyu[B][A][0]:
				setB.jingduList.append(rowsetB.jingduList[i])
				setB.weiduList.append(rowsetB.weiduList[i])

		lenA = len(setA.jingduList)
		lenB = len(setB.jingduList)

		for i in range(lenA):
			for j in range(lenB):
				#  print(str(setA.jingduList[i])+ ',' + str(setA.weiduList[i]) + ',' + str(setB.jingduList[j]) + ',' + str(setB.weiduList[j]))
				temp = self.haversine(setA.jingduList[i],setA.weiduList[i],setB.jingduList[j],setB.weiduList[j])
				#  print(temp)
				if temp <= tolerance:
					return tolerance
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
			#  2表示未定义，1表示相邻，0表示不相邻
			self.matrix = [[2 for i in range(len(files))] for i in range(len(files))]
			for i in range(len(files)):
				self.matrix[i][i] = 1 
			# 重合三维矩阵：格式为A和B距离足够近时，若A和B匹配上，则A选择包含在chonghequyu[A][B]内的点和B包含在chonghequyu[B][A]内的点算距离,
			# 这个三维矩阵最后一位0-3分别对应 ： 上，下，左，右
			self.chonghequyu = numpy.zeros((len(files),len(files),4))

	def kmlReader(self,filename):
		"""
		处理kml文件，获取所有经纬度对
		"""
		with open(filename,'r',encoding = 'UTF-8') as f:
			k = f.read()
			templist = k.split("<coordinates>")
			listlength = len(templist)
			tempstring = ""
			#  预防出现几个不相连的区域
			for i in range(1,listlength):
				if i == 1:
					tempstring = tempstring + templist[i].split("</coordinates>")[0]
				else:
					tempstring = tempstring + " " + templist[i].split("</coordinates>")[0]
			jingweipair = tempstring.split(' ')
			# 最小矩形覆盖的实例
			jingweidu = JingWeiDu()
			for k in jingweipair:
				pair = k.split(',')
				jingdu = float(pair[0])
				weidu = float(pair[1])
				jingweidu.insert(jingdu,weidu)
			leastCover = LeastCover(jingweidu)
			#  print(filename + " done")
		return([jingweidu,leastCover])

	def fileCheck(self):
		"""
		检测文件有没有下错的
		"""
		for file in self.files:
			filename = self.root + '\\' + file
			with open(filename,'r',encoding = 'UTF-8') as f:
				k = f.read()
				countyName = k.split("<name>")[2].split("</name>")[0]
				if countyName != file.split(',')[0]:
					sys.stdout.write(str(file)+"	"+countyName+'\n')


	def getBoundList(self):
		"""
		获取所有县的上下左右边界
		"""
		self.boundList = list()
		self.areaList = list()
		count = 0
		for file in self.files:
			filename = self.root + '\\' + file
			tt = self.kmlReader(filename)
			self.boundList.append(tt[1])
			self.areaList.append(tt[0])
			count = count + 1
			if count % 100 == 0:
				print("已读入文件： " + str(count) + " 个")
		print("共读入文件： " + str(count) + " 个")
		#  for item in boundList:
		#  	print(item.toString())


	def initialMatrix(self):
		"""
		初始化矩阵，第一个被调用
		"""
		me = Measure()
		self.getBoundList()
		for i in range(len(self.boundList)):
			for j in range(i):
				# 参数顺序一定不能错
				temp = me.isShortEnough(self.boundList[i],self.boundList[j])
				if not temp[0]:
					# 如果相聚很远，则相邻矩阵赋0
					self.matrix[i][j] = 0
					self.matrix[j][i] = 0
				else:
					# 如果足够近，则给重合矩阵赋值
					for k in range(4):
						self.chonghequyu[i][j][k] = temp[k+1]
						self.chonghequyu[j][i][k] = temp[k+5] 
					
			if i%50 == 0:
				print('initial '+ str(i) + ' done!')
		

	def ultimateProcessor(self):
		"""
		计算最终矩阵
		"""
		me = Measure()
		count_0 = 0
		count_1 = 0
		for i in range(len(self.areaList)):
			for j in range(i):
				# 如果不是距离特别远则进入这步计算
				if self.matrix[i][j] == 2:
					# 比较这两个集合中的所有点之间的距离，取最小的。参数顺序一定不能错
					shortest = me.shortestDis(self.areaList[i],self.areaList[j],i,j,self.chonghequyu)
					# 如果两个集合之间的最短距离小于容忍度，则记为两县交界，否则记为不交界
					if shortest <= tolerance:
						self.matrix[i][j] = 1
						self.matrix[j][i] = 1
						count_1 = count_1 + 1
					else:
						self.matrix[i][j] = 0
						self.matrix[j][i] = 0
						count_0 = count_0 + 1
			if (count_0 + count_1) > 0 and (count_0 + count_1) % 100 == 0:
				print('ultimate ' + str(count_0 + count_1) + ' done!' + '  相邻: ' + str(count_1) + '个;' + '  不相邻: ' + str(count_0) + '个')

	# todo 打印成csv
	def printCsv(self):
		"""
		打印最终矩阵
		"""
		with open(fileSave,'w') as f:
			# 写第一行
			f.write('')
			for i in range(len(self.files)):
				f.write(',' + self.files[i].split(".kml")[0].replace(',','_'))
			f.write('\n')
			# 写之后所有行
			for i in range(len(self.files)):
				f.write(self.files[i].split(".kml")[0].replace(',','_'))
				for j in range(len(self.files)):
					f.write(',' + str(self.matrix[i][j]))
				f.write('\n')

# 主程序
k = FileHandle(mapLocate)
# 检查文件是否有下载错误，以及命名的不同，只需要用一次
# k.fileCheck()
# 初始化
k.initialMatrix()
# 具体计算
k.ultimateProcessor()
# 打印成csv格式
k.printCsv()
# 回车退出程序
input("所有数据处理结束") 





