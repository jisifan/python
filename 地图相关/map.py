import os
from math import radians, cos, sin, asin, sqrt

class LeastCover:
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
	def __init__(self):
		self.jingduList = list()
		self.weiduList = list()
	def insert(self,jingdu,weidu):
		self.jingduList.append(jingdu)
		self.weiduList.append(weidu)


class Measure:
	"""经纬度的处理"""

	def haversine(self,lon1, lat1, lon2, lat2): # 经度1，纬度1，经度2，纬度2 （十进制度数）  
		""" 
		Calculate the great circle distance between two points  
		on the earth (specified in decimal degrees) 
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
		两矩形的最短距离是否大致小于两公里，是返回true，否返回false
		"""  

		#纬度越高，经度单位差值越短
		stdweidu = max(zoneA.up,zoneB.up)


		#扩张区域A，直至上下左右都移出至少两公里
		leftC = zoneA.left
		while self.haversine(leftC,stdweidu,zoneA.left,stdweidu) < 2000:
			leftC = leftC - 0.01

		rightC = zoneA.right
		while self.haversine(rightC,stdweidu,zoneA.right,stdweidu) < 2000:
			rightC = rightC + 0.01


		upC = zoneA.up
		while self.haversine(zoneA.left,upC,zoneA.left,zoneA.up) < 2000:
			upC = upC + 0.01

		downC = zoneA.down
		while self.haversine(zoneA.left,downC,zoneA.left,zoneA.down) < 2000:
			downC = downC - 0.01


		# A的扩展矩形和B是否相交，如果相交返回true
		if downC > zoneB.up or leftC > zoneB.right or zoneB.down > upC or zoneB.left > rightC:
			return False
		else:
			return True




class FileHandle(object):
	"""处理目录以及kml文件相关操作"""

	# 初始化时输入文件目录
	def __init__(self,file_dir):   
		for root, dirs, files in os.walk(file_dir):  
			self.root = root
			self.files = files
			# 2表示未定义，1表示相邻，0表示不相邻
			self.matrix = [[3 for i in range(len(files))] for i in range(len(files))]


	# 处理kml文件，获取所有经纬度对
	def kmlReader(self,filename):
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


	# 获取所有县的上下左右边界
	def getBoundList(self):
		self.boundList = list()
		for file in self.files:
			filename = self.root + '\\' + file
			tt = self.kmlReader(filename)
			self.boundList.append(tt[1])
		# for item in boundList:
		# 	item.toString()


	def initialMatrix(self):
		me = Measure()
		self.getBoundList()
		for i in range(len(self.boundList)):
			for j in range(i):
				if not me.isShortEnough(self.boundList[i],self.boundList[j]):
					self.matrix[i][j] = 0
					self.matrix[j][i] = 0



k = FileHandle('C:\maps')
k.initialMatrix()
for i in range(len(k.matrix)):
	for j in range(len(k.matrix)):
		print(k.matrix[i][j])
	print('\n')





# me = Measure()
# temp = me.haversine(88.09763609415891,10.9655101537407369,88.09763609415891,10.9755101537407369)
# print(temp)



