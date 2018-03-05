import os
from math import radians, cos, sin, asin, sqrt
import csv
import sys
import numpy
import shutil

"""
主要逻辑：
1.获取文件列表，从而得出总文件数n，建立n*n的矩阵，主对角设为0，其余为2。所有计算相邻的结果均存入这个矩阵，矩阵中0表示不相邻，1表示
相邻，2表示待处理。
2.读取各个文件，获取所有kml文件中的<coordinates>节点中的经纬度数据，存入JingWeiDu这个对象中（包含两个List，分别存有经度和纬度），
将这个对象视为一个集合，接下来计算能覆盖这个集合的最小矩形，放入LeastCover对象中（分别记录上下的纬度坐标和左右的经度坐标）。
3.将各个文件处理完的JingWeiDu对象装入一个list放入内存中，对LeastCover对象进行相同的处理。
4.处理各集合中的最小覆盖矩形的距离问题，采用的办法是：
	A和B比较时，则先计算出A矩形的扩张矩形Aplus(每条边往外移动tolerance米)，然后判断Aplus和B是否有重合（Aplus左经度大于B右经度
	or B的左经度大于Aplus的右经度 or Aplus的下纬度大于B的上纬度 or B的下纬度大于Aplus的上纬度，满足其中一项则视为不重合，不满足
	任何一项则视为重合），
		如果没有重合，则最终结果矩阵中matrix[A][B] = matrix[B][A] = 0。
		如果有重合则记录下B和Aplus的重合区域（也是一个矩形，计算方法是把Aplus的上下纬度和B的上下纬度放到一起排序，取第二大和
		第三大的为重合区域的上下纬度，经度算法类似），计这个重合区域为chonghe[B][A]；采用类似方法算出A和Bplus的重合区域chonghe[A][B]。
5.处理最终结果矩阵中仍然为2（即通过了最小覆盖矩形距离测试的点）的点。
	A和B比较时，计A集合中所有属于区域chonghe[A][B]的点的集合为setA，B集合中所有属于区域chonghe[B][A]的点的集合为setB。分别遍历这两个
	集合，从两个集合中各取出一点来计算距离，如果距离小于tolerance则直接返回，并给最终结果矩阵赋值matrix[A][B] = matrix[B][A] = 1。
	如果直至遍历完两个集合仍然没有两点距离小于tolerance，则给最终结果矩阵赋值matrix[A][B] = matrix[B][A] = 0
6.打印结果

代码说明：
LeastCover类存放覆盖矩形的数据结构，视作一个区域
JingWeiDu类存放每个城市边界中所有点，视作一个集合
Measure类负责测量距离，包括三个方法，分别负责点与点、区域与区域、集合与集合距离的测量
FileHandler类负责和文件交互以及各种数据的存储，其调用Measure类


配置：
所有可配置项均紧接本注释以后。
tolerance变量是容忍的最小距离，单位是米。（可修改）
fileXianglin变量是是输出的中文相邻县城的文件地址。（需修改）
fileSave本来是输出对称矩阵的地址，已废弃。（无需修改）
mapLocate是所有kml文件所在的文件夹地址（需修改）
bianmaLocate是提前给定的编码表所在地址（需修改）
fileBiaoyi是表一的输出位置（需修改）
fileBiaoer是表二的输出位置（需修改）
"""


# 容忍的最小距离
tolerance = 2000

# 文件保存地址(文件存放位置),已废弃,不用更改
fileSave = 'C:\\Users\\tangheng\\Dropbox\\数据相关\\地图相关\\中国所有相邻的县\\中国所有县级城市相邻关系.csv'

# 相邻城市文件(输出文件存放位置)
fileXianglin = 'C:\\Users\\tangheng\\Dropbox\\数据相关\\地图相关\\中国所有相邻的县\\中国所有县级城市的相邻城市.csv'

# 地图所在地址(内容需提前给定)
mapLocate = 'C:\\Users\\tangheng\\Dropbox\\数据相关\\地图相关\\中国各县级地区边界数据'

# 编码表(内容需提前给定)
bianmaLocate = 'C:\\Users\\tangheng\\Dropbox\\数据相关\\地图相关\\编码表.csv'

# 符合规则的表一位置(输出文件存放位置)
fileBiaoyi = 'C:\\Users\\tangheng\\Dropbox\\数据相关\\地图相关\\中国所有相邻的县\\表一.csv'

# 符合规则的表二位置(输出文件存放位置)
fileBiaoer = 'C:\\Users\\tangheng\\Dropbox\\数据相关\\地图相关\\中国所有相邻的县\\表二.csv'


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
		测量两个点之间的距离，参数：经度1，纬度1，经度2，纬度2 （十进制度数）  
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
		两矩形区域的最短距离是否大致小于tolerance，是返回true，否返回false
		"""  

		# 纬度越高，经度单位差值越短，所以宁可纬度高，不可低，不然算出来的经度可能偏小
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
		返回两个集合的最短距离，如果小于等于tolerance则返回tolerance
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




class FileHandler(object):
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
				self.matrix[i][i] = 0 
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
		检测文件有没有下错的，以及更改名称（我已检测过，无需再调用）
		"""
		oldfileList = list()
		newfileList = list()
		#找出名称和kml文件中命名不一样的文件
		for file in self.files:
			filename = self.root + '\\' + file
			with open(filename,'r',encoding = 'UTF-8') as f:
				k = f.read()
				countyName = k.split("<name>")[2].split("</name>")[0]
				if countyName != file.split(',')[0]:
					oldfileList.append(self.root + '\\' + file)
					newfileList.append(self.root + '\\' + countyName + ',' + file.split(',')[1] + ',' + file.split(',')[2])
					sys.stdout.write(str(file)+"	"+countyName + ',' + file.split(',')[1] + ',' + file.split(',')[2]+'\n')
		#将这些文件重命名
		for i in range(len(oldfileList)):
			shutil.move(oldfileList[i],newfileList[i])


	def getBoundList(self):
		"""
		读入所有文件，将所有县的边界点集合装入一个list放入内存，同时将所有县的覆盖矩形装入一个list放入内存
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
				print('已初始化: '+ str(i + 1) + ' 个城市')
		

	def ultimateProcessor(self):
		"""
		计算最终矩阵
		"""
		me = Measure()
		count_0 = 0
		count_1 = 0
		for i in range(len(self.areaList)):
			#确保只输出一遍
			sig = 0
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
				# 每计算完100条待确认数据则输出一次
				if (count_0 + count_1) > 0 and (count_0 + count_1) % 100 == 0 and sig == 0:
					print('已确认: ' + str(count_0 + count_1) + ' 条关联关系;' + '  相邻: ' + str(count_1) + '条;' + '  不相邻: ' + str(count_0) + '条')
					sig = 1
		# 最终输出
		print('最终确认: ' + str(count_0 + count_1) + ' 条关联关系;' + '  相邻: ' + str(count_1) + '条;' + '  不相邻: ' + str(count_0) + '条')
				

	# todo 打印成csv
	def printCsv(self):
		"""
		打印最终矩阵
		"""
		# with open(fileSave,'w') as f:
		# 	# 写第一行
		# 	f.write('')
		# 	for i in range(len(self.files)):
		# 		f.write(',' + self.files[i].split(".kml")[0].replace(',','_'))
		# 	f.write('\n')
		# 	# 写之后所有行
		# 	for i in range(len(self.files)):
		# 		f.write(self.files[i].split(".kml")[0].replace(',','_'))
		# 		for j in range(len(self.files)):
		# 			f.write(',' + str(self.matrix[i][j]))
		# 		f.write('\n')

		self.bianmaMap = {}
		# 读入编码表
		with open(bianmaLocate,'r') as f:
			k = f.read()
			self.bianmaList = k.split('\n')
			for i in range(len(self.bianmaList)):
				if len(self.bianmaList[i]) < 5:
					break
				key = self.bianmaList[i].split(',')[0]
				value = self.bianmaList[i].split(',')[1]
				self.bianmaMap[key] = value

		# 写入表一		
		with open(fileBiaoyi,'w') as f:
			for i in range(len(self.bianmaList)):
				# 去除最后的空行
				if len(self.bianmaList[i]) < 5:
					break
				f.write(self.bianmaList[i].split(',')[1] + ',' + self.bianmaList[i].split(',')[0].split('_')[2] + ',' + \
					self.bianmaList[i].split(',')[0].split('_')[0] + ',' + self.bianmaList[i].split(',')[0].split('_')[1])
				f.write('\n')

		# 写入中文的表
		with open(fileXianglin,'w') as f:
			for i in range(len(self.files)):
				fileStringList = self.files[i].split(".kml")[0].split(',')
				f.write(fileStringList[1] + '_' + fileStringList[2] + '_' + fileStringList[0] + ',')
				for j in range(len(self.files)):
					if self.matrix[i][j] != 0:
						fileStringListTemp = self.files[j].split(".kml")[0].split(',')
						f.write(' ' + fileStringListTemp[1] + '_' + fileStringListTemp[2] + '_' + \
							fileStringListTemp[0] + ' ;')
				f.write('\n')

		#写入表二
		with open(fileBiaoer,'w') as f:
			for i in range(len(self.files)):
				fileStringList = self.files[i].split(".kml")[0].split(',')
				firstCountyName = fileStringList[1] + '_' + fileStringList[2] + '_' + fileStringList[0]
				firstCountyCode = self.bianmaMap[firstCountyName]
				for j in range(len(self.files)):
					if self.matrix[i][j] != 0:
						fileStringListTemp = self.files[j].split(".kml")[0].split(',')
						secondCountyName = fileStringListTemp[1] + '_' + fileStringListTemp[2] + '_' + fileStringListTemp[0]
						secondCountyCode = self.bianmaMap[secondCountyName]
						f.write(firstCountyCode + ',' + secondCountyCode + '\n')


# 主程序
k = FileHandler(mapLocate)
# 检查文件是否有下载错误，以及命名的不同（我已经调用过了，不需要再调用了）
# k.fileCheck()
# # 初始化
k.initialMatrix()
# # 具体计算
k.ultimateProcessor()
# # 打印成csv格式
k.printCsv()
# 回车退出程序
input("所有数据处理结束") 





