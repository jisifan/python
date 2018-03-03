import os
from math import radians, cos, sin, asin, sqrt

class LeastCover:
	def __init__(self,jingweidu):
		self.up = max(jingweidu.weiduList)
		self.down = min(jingweidu.weiduList)
		self.left = min(jingweidu.jingduList)
		self.right = max(jingweidu.jingduList)
		
	def toString(self):
		print("up:"+ str(self.up) + "    down:" + str(self.down) + "    left:" + str(self.left) + "    right:" + str(self.right))
	



class JingWeiDu:
	def __init__(self):
		self.jingduList = list()
		self.weiduList = list()
	def insert(self,jingdu,weidu):
		self.jingduList.append(jingdu)
		self.weiduList.append(weidu)


class (object):
	"""经纬度的处理"""
	def __init__(self, arg):
		super(, self).__init__()
		self.arg = arg
		


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
		boundList = list()
		for file in self.files:
			filename = self.root + '\\' + file
			tt = self.kmlReader(filename)
			boundList.append(tt[1])
		for item in boundList:
			item.toString()

			


k = FileHandle('C:\maps')
BoundList = k.getBoundList()



