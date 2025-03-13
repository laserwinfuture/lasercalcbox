#★从EXCEL文件读取信息的时候也是按行读取的，每行都是一个列表（按列索引）；
import csv,sys


#我封装好的excel读取函数，输入变量是文件名，输出需要的列数据，每个列都是一个列表
#按列为单位读取数据，#第一列是row[0]，依次为row[1]......
#读取到的都是字符串，如果当数字用的话注意类型转换。
def read_z_wx_wy(path):  #，path为文件名字符型
    z=[]   #第1列z (从第o列开始算起)
    wx=[]  #第6列wx即dx^2
    wy=[]  #第7列wy即dy^2
    with open(path, 'r') as f:
        reader = csv.reader(f)
        for i,row in enumerate(reader):   #元祖化，i是列，row是行
            if i>=4:  #去掉第一行数据头header                                            
                z.append( float(row[1]))  
                wx.append(float(row[6]))   
                wy.append(float(row[7]))   
    return z,wx,wy

if __name__=='__main__':
    path=sys.path[0]+'\\data.csv'    
    print('函数返回数据类型:',type(read_z_wx_wy(path)),',列表长度：',len(read_z_wx_wy(path)))    
    z=read_z_wx_wy(path)[0]       #函数返回来的是列表型数据，第0个数据是z
    wx=read_z_wx_wy(path)[1]      #函数返回来的是列表型数据，第1个数据是wx
    wy=  read_z_wx_wy(path)[2]    #函数返回来的是列表型数据，第2个数据是wy
    print('z列表：',z) 
    print('wx列表：',wx) 
    print('wy列表：',wy)



