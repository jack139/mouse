#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 交叉遗传，返回所有可能的基因型
# 输入：品系名,基因型(+/-),基因型(+/-),...
# 输出：[... , ... , ... ]
def genetic(L_data, R_data):
	L_list = L_data.split(',')
	R_list = R_data.split(',')
	if len(L_list)==1 or len(R_list)==1: # 只有品系名
		return list(set([L_list[0], R_list[0]]))

	L_list = L_list[1:]
	R_list = R_list[1:]

	child_list = []

	# 生成所有可能
	for x in L_list:
		for y in R_list:
			if x>y:
				child_list.append(u'??,%s,%s'%(y,x))
			else:
				child_list.append(u'??,%s,%s'%(x,y))

	child_list = list(set(child_list)) # 去除重复
	child_list = sorted(child_list) # 排序

	return child_list


