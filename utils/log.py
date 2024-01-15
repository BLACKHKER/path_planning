"""
@Author  ：BLACKHKER
@Date    ：2024/8/1 13:42
@File    ：log.py
@Description: 寻找打印位置工具类
@Version 1.0
"""
import sys
import traceback

# 追踪print打印位置
old_f = sys.stdout


class FindPrint:
    def write(self, x):
        old_f.write(x.replace("\n", " [%s]\n" % str(traceback.extract_stack())))


sys.stdout = FindPrint()
