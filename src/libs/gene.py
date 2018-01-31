#!/usr/bin/env python
# -*- coding: utf-8 -*-


# 交叉遗传，返回所有可能的交叉
def cross2(L_list, R_list):
	child_list = []

	# 生成所有可能
	for x in L_list:
		for y in R_list:
			if x>y:
				child_list.append(u'%s,%s'%(y,x))
			else:
				child_list.append(u'%s,%s'%(x,y))

	child_list = list(set(child_list)) # 去除重复
	child_list = sorted(child_list) # 排序

	return child_list

# 格式转换：
# [A(+/-), B(+/-)]  ===>   [A+,A-,B+,B-]
def transfer(data):
	ret = []
	for i in data:
		d = i[:-1]
		a = d.split('(')
		name = a[0]
		tag = a[1].split('/')
		for j in tag:
			ret.append(name+j)
	return ret

# 格式转换：
# ['A+,B+,A+,B+', 'A+,B+,A+,B-']  ===>   ['A(+/+),B(+/+)', 'A(+/+),B(+/-)']
def transfer2(data, gene_name):
	ret = []
	for i in data:
		a = i.split(',')
		a = sorted(a)

		one = ''
		last_name = ''
		for x in a:
			name = x[:-1]
			tag = x[-1]

			if name!=last_name:
				if one=='':
					one = '%s,%s(%s'%(gene_name, name, tag)
				else:
					one = '%s),%s(%s'%(one, name, tag)
				last_name = name
			else:
				one = '%s/%s'%(one, tag)
		one += ')'

		ret.append(one)

	return ret

# 输入： [A(+/-), B(+/-), C(+/-)]
# 输出：[A+B+C+, A+B+C-, ...]
def crossN(in_list):
	if len(in_list)==2:
		return cross2(transfer([in_list[0]]), transfer([in_list[1]]))
	elif len(in_list)==1:
		return transfer(in_list)
	else:
		return cross2(transfer([in_list[0]]), crossN(in_list[1:]))


# 交叉遗传，返回所有可能的基因型
# 输入：品系名,基因型(+/-),基因型(+/-),...
# 输出：[... , ... , ... ]
def genetic2(L_data, R_data):
	L_list = L_data.split(',')
	R_list = R_data.split(',')

	r = list(set([L_list[0], R_list[0]]))
	gene_name = '_'.join(r)

	if len(L_list)==1 or len(R_list)==1: # 只有品系名
		return [gene_name]

	L_list = L_list[1:]
	R_list = R_list[1:]

	#print L_list
	#print R_list

	L_list2 = crossN(L_list)
	R_list2 = crossN(R_list)

	#print L_list2
	#print R_list2

	r2 = cross2(L_list2, R_list2)

	#print r2

	r3 = transfer2(r2, gene_name)

	#print r3

	ret_list = list(set(r3))

	return ret_list

