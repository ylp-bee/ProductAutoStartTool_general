# -*- coding: utf-8 -*-
from function_db_and_procss import Opera_DB
from function_db_and_procss import modify_general_config_and_process_opra as mgo
from function_db_and_procss import modify_induct_config_and_process_opra as mio
import time
from function_write_to_xml import write_to_general_xml as wg
from Logger_module import logger
from ConfigManager import configs
from version import program_version_no as v ,modify_content as mc

logger.info('''********************使用说明**********************************
【前置条件】
      1.主程序为ProductAutoStartTool;在config.ini[setconfig]配置is_general=False为工业框架，is_general=True为通用框架
      2.准备好数据库备份包、角色创建文件、数据库清除脚本，并且将路径写到配置文件config.ini的[dbpath]中；
      3.将数据库名等信息写入到config.ini的[database_connection]中；
      4.将location、location_relation、agv_info信息写入到excel文件里面，并将路径记录到config.ini的[excelpath]；
      5.将地图放在etc文件里面，并将路径记录到config.ini的[layoutpath]；
      5.将程序的路径、文件名写入到config.ini的[path]里面。
【操作说明】
在界面根据提示输入数字，含义分别表示：
        1.一键更改数据库配置文件；
        2.一键创建恢复数据库backup；
        3.一键清理数据库；
        4.关闭所有的进程(不包含仿真车载进程)；
        5.一键启动进程（不包含仿真车载进程；先清理log，再启动进程；）；
             55.一键重启webmonitor（关闭、清理log、启动）
             56.一键重启OM（关闭、清理log、启动）
        6.查询需要配置的xml文件；
        7.修改dispatch_config.xml文件（包含location、location_relation、object，可为空）；
        8.修改agv_info.xml文件；
        9.复制layout（程序进程目录会优先进行清理）；
        10.执行sql脚本路径；
        11.获取当前版本号；
        12.复制OM的TS模板；
        13.一键重启车载（关闭、清理log、启动）
          131.一键关闭仿真车载
          132.一键启动仿真车载进程
          133.一键清理车载log
        14.清理调度引擎log。
    0.退出。
**************************************************************''')
flag=10
is_general=configs.is_general
is_new_general=configs.is_new_general
if(is_general==True):
    if (is_new_general == True):
        content = 'BS通用框架'
        flag=1
    else:
        content = 'CS通用框架'
        flag = 2
else:
    content='工业框架'
    flag = 0

time.sleep(0.1)
logger.info('目前进行{}的自动化部署'.format(content))
while 1:
    time.sleep(0.5)
    put_num=input('''选择数字0-11。查看数字代表操作请输入i,请输入：''')
    try:
        if(int(put_num)==1):
            #写数据库配置
            if (flag==1):
                    mgo().Modify_new_general_config()
            if (flag == 2):
                    mgo().Modify_old_general_config()
            if (flag == 0):
                mio().modify_config()
        elif(int(put_num)==2):
            # 数据库备份
            while 1:
                put1=input('该操作将删除数据库，然后新建，创建角色，恢复备份！请确认需要一键创建，Y or N!!请输入：')
                try:
                    if (put1== 'Y' or put1== 'y'):
                       Opera_DB().db_create()
                       break
                    else:
                        break
                except:
                    print("请输入'Y'or 'N'!")
        elif(int(put_num)==3):
            #清理数据库
            Opera_DB().db_clear()
        elif(int(put_num)==4):
            #关闭所有的进程(不包含仿真车载进程)
            if (flag==1 or flag==2):
                mgo().kill_general_all()
            if (flag == 0):
                mio().kill_all()
        elif(int(put_num)==5):
            #5.一键启动进程（不包含仿真车载进程；先清理log，再启动进程；）；
            if (flag == 1):
                    mgo().Start_new_general_all()
            if (flag == 2):
                    mgo().Start_old_general_all()
            if (flag == 0):
                mio().func_all()
        elif (int(put_num) == 55):
            #55.一键重启webmonitor（关闭、清理log、启动）
            if (flag == 1):
               mgo().onestart_webmonitor()
            else:
                print('选择的框架没有 webmonitor')
        elif (int(put_num) == 56):
            # 55.一键重启om（关闭、清理log、启动）
            if (flag == 1):
                mgo().onestart_om()
            else:
                print('选择的框架没有om')
        elif (int(put_num) == 6):
            wg().get_excel_info()
        elif (int(put_num) == 7):
            if (flag == 1):
                wg().modify_dispatchxml_location()
                wg().modify_dispatchxml_location_relation()
                wg().modify_dispatchxml_object()
            else:
                print('选择的框架不需要使用dispatch_config.xml，不需要更改')
        elif (int(put_num) == 8):
            wg().modify_agv_infoxml()
        elif (int(put_num) == 9):
            if (flag == 1):
                    wg().copy_layout_to_general_process()
            if (flag == 2):
                    wg().copy_layout_to_old_general_process()
            if (flag == 0):
                wg().copy_layout_to_i_process()
            wg().copy_layout_to_vehicles()
        elif (int(put_num) == 10):
            sql=input('请输入sql的完整路径：')
            Opera_DB().psql_db(sql)
        elif (int(put_num) == 11):
            print('当前版本号：{};\n当前更新内容：{}'.format(v,mc))
        elif (int(put_num) == 12):
            if (flag == 1):
                wg().copy_ts_to_OM()
            else:
                print('选择的框架没有 OM')
        elif (int(put_num) == 13):
          ''' 13.一键重启车载（关闭、清理log、启动）
         '''
          mgo().onestart_vehicles()
        elif (int(put_num) == 131):
            '''131.
            一键关闭仿真车载
           '''
            mgo().kill_vehicles()
        elif (int(put_num) == 132):
            ''' 132.
            一键启动仿真车载进程
           '''
            mgo().func_vehicles()
        elif (int(put_num) == 133):
            ''' 133.
            一键清理车载log'''
            mgo().delete_vehicles_log()
        elif (int(put_num) == 14):
            if (flag == 1):
                mgo().delete_new_general_log()
            if (flag == 2):
                mgo().delete_old_general_log()
            if (flag == 0):
                mio().delete_induct_log()
        elif(int(put_num)==0):
            print('退出程序')
            break

        else:
            print('输入错误，请继续输入!!')

    except:
        if (put_num == 'i'):
            print('''【操作说明】
            在界面根据提示输入数字,含义分别表示：
        1.一键更改数据库配置文件；
        2.一键创建恢复数据库backup；
        3.一键清理数据库；
        4.关闭所有的进程(不包含仿真车载进程)；
        5.一键启动进程（不包含仿真车载进程；先清理log，再启动进程；）；
             55.一键重启webmonitor（关闭、清理log、启动）
             56.一键重启OM（关闭、清理log、启动）
        6.查询需要配置的xml文件；
        7.修改dispatch_config.xml文件（包含location、location_relation、object，可为空）；
        8.修改agv_info.xml文件；
        9.复制layout（程序进程目录会优先进行清理）；
        10.执行sql脚本路径；
        11.获取当前版本号；
        12.复制OM的TS模板；
        13.一键重启车载（关闭、清理log、启动）
          131.一键关闭仿真车载
          132.一键启动仿真车载进程
          133.一键清理车载log
        14.清理调度引擎log。
            0.退出。''')
        else:
            print('输入错误，请继续输入!!')



