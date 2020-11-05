import xlrd
import shutil,os
from Logger_module import logger
from xml.dom import minidom
from xml.etree import ElementTree  # 导入ElementTree模块
from ConfigManager import configs

class write_to_general_xml():
    def __init__(self):

        self.temp_file='temp.xml'
        self.excelpath=configs.excelpath
        self.dispathpath=configs.dispathpath
        self.enginepath=configs.enginepath
        self.dispath_config_path=configs.dispath_config_path
        self.agv_info_path=configs.agv_info_path
        self.layoutpath=configs.layoutpath
        self.i_monitorpath=configs.i_monitorpath

    def prettyXml( self,element,level=0):  # elemnt为传进来的Elment类，参数indent用于缩进，newline用于换行
        indent= '\t'
        newline='\n'
        if element:  # 判断element是否有子元素
            if element.text == None or element.text.isspace():  # 如果element的text没有内容
                element.text = newline + indent * (level + 1)
            else:
                element.text = newline + indent * (level + 1) + element.text.strip() + newline + indent * (level + 1)
                # else:  # 此处两行如果把注释去掉，Element的text也会另起一行
            # element.text = newline + indent * (level + 1) + element.text.strip() + newline + indent * level
        temp = list(element)  # 将elemnt转成list
        for subelement in temp:
            if temp.index(subelement) < (len(temp) - 1):  # 如果不是list的最后一个元素，说明下一个行是同级别元素的起始，缩进应一致
                subelement.tail = newline + indent * (level + 1)
            else:  # 如果是list的最后一个元素， 说明下一行是母元素的结束，缩进应该少一个
                subelement.tail = newline + indent * level
            self.prettyXml(subelement,level=level + 1)  # 对子元素进行递归操作

        # ElementTree.dump(element)  # 显示出美化后的XML内容

    def petty_filename(self,file,newfile):
        tree = ElementTree.parse(file)  # 解析test.xml这个文件，该文件内容如上文
        element= tree.getroot()  # 得到根元素，Element类
        self.prettyXml(element)
        tree.write(newfile)

    def get_excel_info(self):
        try:
            workbook = xlrd.open_workbook(self.excelpath)
            sheet_names=workbook.sheet_names()
            for i  in sheet_names:
                sheet=workbook.sheet_by_name(i)
                num=sheet.nrows-1
                title_list = sheet.row_values(0)
                logger.info('Excel表{}的标题栏是：{},内容有{}行'.format(i,title_list,num))
        except Exception as e:
            logger.error('get_excel_info error!原因：{}'.format(e))

    def modify_xml_attribute_value(self, title_list, row_value, agv_node, j):
         try:
            config_title=[]
            xmlkeys=list(agv_node[j].attributes.keys())
            for title in title_list:
               rawVal = row_value[title_list.index(title)]
               if isinstance(rawVal, str):
                   value = rawVal
               else:
                   value = float(rawVal)

               if (value == ''or value==None):
                   if(agv_node[j].getAttribute(title) ):
                        # agv_node[j].getAttribute(title).parentNode.removeChild(title)
                        agv_node[j].removeAttribute(title)
               else:
                    if(title in ['dock_id','id','location_type','priority','exit_dock','max_tasking_agv_num',
                                 'ancestor_node_id','distance','node_id',
                                 'id','type','port','shell_port','layout_id','fts_port','simulation','jess_port',
                                 'id','object_type_id','fit_location_id','error_code','pallet_type','home_node_id','current_node_id']):
                       value=int(value)
                    agv_node[j].setAttribute(title, str(value))
                    config_title.append(title)
            x=[item for item in xmlkeys if item not in config_title]
            if x:
                for d in x:
                    agv_node[j].removeAttribute(d)
         except Exception as e:
             logger.error('modify xml value error!原因：{}'.format(e))

   #objectxml值为空也要填写
    def modify_xml_attribute_object_value(self, title_list, row_value, agv_node, j):
         try:
            config_title=[]
            xmlkeys=list(agv_node[j].attributes.keys())
            for title in title_list:
               rawVal = row_value[title_list.index(title)]

               if isinstance(rawVal, str):
                   value = rawVal
               else:
                   value = float(rawVal)
               # print("要修改的title为：{},rawVal={},typerawval={},value={}".format(title, rawVal, type(rawVal),value))
               if (value == ''or value==None ):
                   if title in [ 'id','object_type',	'physical_label',
                                     'length','width','height',
                                     'fit_location_id','error_code',
                                     'pallet_type	home_node_id','current_node_id',
                                 ' pallet_type','home_node_id']:
                           # print("要修改的title为：{},rawVal={},typerawval={},value={}".format(title, rawVal, type(rawVal),
                           #                                                               value))
                           agv_node[j].setAttribute(title, value)
                           config_title.append(title)
                   elif (agv_node[j].getAttribute(title)):
                           # agv_node[j].getAttribute(title).parentNode.removeChild(title)
                           agv_node[j].removeAttribute(title)
               else:
                    if(title in ['dock_id','id','location_type','priority','exit_dock','max_tasking_agv_num',
                                 'ancestor_node_id','distance','node_id',
                                 'id','type','port','shell_port','layout_id','fts_port','simulation','jess_port',
                                 'id','object_type','fit_location_id','error_code','pallet_type','home_node_id','current_node_id']):
                       value=int(value)
                    agv_node[j].setAttribute(title, str(value))
                    config_title.append(title)
            x=[item for item in xmlkeys if item not in config_title]
            if x:
                for d in x:
                    agv_node[j].removeAttribute(d)
         except Exception as e:
             logger.error('modify xml value error!原因：{}'.format(e))

    def modify_dispatchxml_location(self):

        excelfilepath=self.excelpath
        dispatchxmlpath=self.dispath_config_path
        for filepath in [excelfilepath, dispatchxmlpath]:
            if not os.path.exists(filepath):
                logger.error('error!!!文件：{}不存在！'.format(filepath))

        if os.path.exists(dispatchxmlpath) and os.path.exists(excelfilepath):
            xmlDom = minidom.parse(dispatchxmlpath)
            # excel表格为modify的内容，获取他要修改的行数和标题栏
            workbook = xlrd.open_workbook(excelfilepath)

            try:
                logger.info('---------------------------------start Location config ....----------------------------------------------')
                sheet_name1='Location'
                sheet = workbook.sheet_by_name(sheet_name1)
                config_location_num=sheet.nrows-1
                title_list= sheet.row_values(0)
                location_title_list=['id', 'name', 'location_type', 'dock_id', 'exit_dock', 'priority', 'agv_type_filter_mode', 'fit_agv_type', 'agv_id_filter_mode', 'fit_agv_id']
                while 1:
                    commnad_location = xmlDom.getElementsByTagName("Location")[1]
                    location_node=commnad_location.getElementsByTagName("node")
                    node_num=len(location_node)
                    print('目前node_num={},config_location_num={}'.format(node_num,config_location_num))
                    if (node_num<config_location_num):
                        need_add_node_num=config_location_num-node_num
                        for i in range(0,need_add_node_num):
                            newCDATA = xmlDom.createElement("node")
                            getlocation = xmlDom.getElementsByTagName("Location")[1]
                            getlocation.appendChild(newCDATA)
                    elif (node_num>config_location_num):
                       need_delete_node_num=node_num-config_location_num
                       for i in range(config_location_num,node_num):
                           location_node[i].parentNode.removeChild(location_node[i])
                    else:
                        break
                if (config_location_num> 0):
                    for j in range(0, config_location_num):
                        row_value = sheet.row_values(j + 1)
                        self.modify_xml_attribute_value(title_list, row_value, location_node, j)

                else:
                    logger.info('location 没有配置,不需要写入xml')

                f = open(self.temp_file, "w", encoding='utf-8')
                xmlDom.writexml(f)
                f.close()
                if os.path.exists(self.temp_file):
                    self.petty_filename(self.temp_file, dispatchxmlpath)
                    os.unlink(self.temp_file)

                logger.info(
                    '---------------------------------end Location config ....----------------------------------------------')
            except Exception as e:
                logger.error('location xml error!原因：{}'.format(e))

    def modify_dispatchxml_location_relation(self):
        excelfilepath = self.excelpath
        dispatchxmlpath = self.dispath_config_path

        for filepath in [excelfilepath, dispatchxmlpath]:
            if not os.path.exists(filepath):
                logger.error('error!!!文件：{}不存在！'.format(filepath))

        if os.path.exists(dispatchxmlpath) and os.path.exists(excelfilepath):
            xmlDom = minidom.parse(dispatchxmlpath)
            # excel表格为modify的内容，获取他要修改的行数和标题栏
            workbook = xlrd.open_workbook(excelfilepath)

            logger.info('---------------------------------start Location relation config ....----------------------------------------------')
            try:
                sheet_name='Location Relation'
                sheet = workbook.sheet_by_name(sheet_name)
                config_num = sheet.nrows - 1
                title_list = sheet.row_values(0)

                # xml为最终输出的格式，修改后放在临时的temp.xml表里面。
                # 获取node的总数量,通过判断父节点属性Location还是Location_location的节点。
                # 计数，若是多于表格需要配置的栏数则进行删除

                # 将node xml 与excel进行修正
                while 1:
                    commnad_location_relation = xmlDom.getElementsByTagName("location_relation")[1]
                    location_relation_node = commnad_location_relation.getElementsByTagName("node")
                    node_num = len(location_relation_node)
                    print( '目前node_num={},config_num={}'.format(node_num,config_num))


                    if (node_num< config_num):
                        need_add_node_num = config_num - node_num
                        for m in range(0, need_add_node_num):
                            newCDATA2 = xmlDom.createElement("node")
                            get_location_location = xmlDom.getElementsByTagName("location_relation")[1]
                            get_location_location.appendChild(newCDATA2)
                    elif (node_num>config_num) :
                        need_delete_node_num= node_num-config_num
                        for i in range(config_num,node_num):
                            location_relation_node[i].parentNode.removeChild(location_relation_node[i])
                    else:
                        break

                if ( config_num>0):
                    for j in range(0, config_num):
                        row_value = sheet.row_values(j + 1)
                        self.modify_xml_attribute_value(title_list, row_value, location_relation_node, j)

                else:
                    logger.info('location_relation没有配置，不需要写入xml')

                f = open(self.temp_file, "w", encoding='utf-8')
                xmlDom.writexml(f)
                f.close()
                if os.path.exists(self.temp_file):
                    self.petty_filename(self.temp_file, dispatchxmlpath)
                    os.unlink(self.temp_file)
                logger.info('---------------------------------end Location relation config ....----------------------------------------------')
            except Exception as e:
                logger.error('location relation xml error!原因：{}'.format(e))

    def modify_dispatchxml_object(self):
        excelfilepath = self.excelpath
        dispatchxmlpath = self.dispath_config_path

        for filepath in [excelfilepath, dispatchxmlpath]:
            if not os.path.exists(filepath):
                logger.error('error!!!文件：{}不存在！'.format(filepath))

        if os.path.exists(dispatchxmlpath) and os.path.exists(excelfilepath):
            xmlDom = minidom.parse(dispatchxmlpath)
            # excel表格为modify的内容，获取他要修改的行数和标题栏
            workbook = xlrd.open_workbook(excelfilepath)

            logger.info('---------------------------------start object config ....----------------------------------------------')
            # try:
            sheet_name='Object'
            sheet = workbook.sheet_by_name(sheet_name)
            config_num = sheet.nrows - 1
            title_list = sheet.row_values(0)

            # xml为最终输出的格式，修改后放在临时的temp.xml表里面。
            # 获取node的总数量,通过判断父节点属性Location还是Location_location的节点。
            # 计数，若是多于表格需要配置的栏数则进行删除

            # 将node xml 与excel进行修正
            while 1:
                commnad_object_info = xmlDom.getElementsByTagName("object_info")[0]
                object_info_node = commnad_object_info.getElementsByTagName("node")
                node_num = len(object_info_node)
                print( '目前node_num={},config_num={}'.format(node_num,config_num))


                if (node_num< config_num):
                    need_add_node_num = config_num - node_num
                    for m in range(0, need_add_node_num):
                        newCDATA2 = xmlDom.createElement("node")
                        get_object_info = xmlDom.getElementsByTagName("object_info")[0]
                        get_object_info.appendChild(newCDATA2)
                elif (node_num>config_num) :
                    need_delete_node_num= node_num-config_num
                    for i in range(config_num,node_num):
                        object_info_node[i].parentNode.removeChild(object_info_node[i])
                else:
                    break

            if ( config_num>0):
                for j in range(0, config_num):
                    row_value = sheet.row_values(j + 1)
                    self.modify_xml_attribute_object_value(title_list, row_value, object_info_node, j)

            else:
                logger.info('object_info没有配置，不需要写入xml')

            f = open(self.temp_file, "w", encoding='utf-8')
            xmlDom.writexml(f)
            f.close()
            if os.path.exists(self.temp_file):
                self.petty_filename(self.temp_file, dispatchxmlpath)
                os.unlink(self.temp_file)
            logger.info('---------------------------------end object_info config ....----------------------------------------------')
            # except Exception as e:
            #     logger.error('object_info xml error!原因：{}'.format(e))

    def modify_agv_infoxml(self):
        for filepath in [self.excelpath, self.agv_info_path]:
            if not os.path.exists(filepath):
                logger.error('error!!!文件：{}不存在！'.format(filepath))

        if os.path.exists(self.agv_info_path) and os.path.exists(self.excelpath):
            xmlDom = minidom.parse(self.agv_info_path)
            # excel表格为modify的内容，获取他要修改的行数和标题栏
            workbook = xlrd.open_workbook(self.excelpath)
            try:
                logger.info(
                    '---------------------------------start agv info config ....----------------------------------------------')
                sheet = workbook.sheet_by_name('Agv_info')
                config_agv_num = sheet.nrows - 1
                title_list = sheet.row_values(0)

                while 1:
                    agvs = xmlDom.getElementsByTagName("agvs")[0]
                    agv_node = agvs.getElementsByTagName("agv")
                    node_num = len(agv_node)


                    if (node_num < config_agv_num):
                        need_add_node_num =config_agv_num - node_num
                        for i in range(0, need_add_node_num):
                            newCDATA = xmlDom.createElement("agv")
                            getlocation = xmlDom.getElementsByTagName("agvs")[0]
                            getlocation.appendChild(newCDATA)
                    elif (node_num > config_agv_num):
                        need_delete_node_num = node_num - config_agv_num
                        for i in range(config_agv_num,  node_num):
                            agv_node[i].parentNode.removeChild( agv_node[i])

                    else:
                        break

                if (config_agv_num > 0):
                    for j in range(0, config_agv_num):
                        row_value = sheet.row_values(j + 1)
                        self.modify_xml_attribute_value(title_list, row_value, agv_node, j)
                        #
                        # for title in title_list:
                        #     #1.1.0.09.4日代码修改
                        #     rawVal=row_value[title_list.index(title)]
                        #     if isinstance(rawVal, str):
                        #         value=rawVal
                        #     else:
                        #         if(title in ['pos_x','pos_y','pos_angle']):
                        #             value = float(rawVal)
                        #         else:
                        #             value=int(rawVal)
                        #
                        #     if(value==None or value==''):
                        #         if(agv_node[j].getAttribute(title)):
                        #             # agv_node[j].getAttribute(title).parentNode.removeChild(title)
                        #             agv_node[j].removeAttribute(title)
                        #     else:
                        #         agv_node[j].setAttribute(title, str(value))

                else:
                    logger.info('agv_ino没有配置，不需要写入xml')



                f = open(self.temp_file, "w", encoding='utf-8')
                xmlDom.writexml(f)
                f.close()
                if os.path.exists(self.temp_file):
                    self.petty_filename(self.temp_file, self.agv_info_path)
                    os.unlink(self.temp_file)
                logger.info(
                    '---------------------------------end agv info config----------------------------------------------')
            except Exception as e:
                logger.error('agv_info xml error!原因：{}'.format(e))



    def detele_path(self,path):
       try:
        if os.path.exists(path):

            for root, dirs, files in os.walk(path, topdown=False):
                for name in files:
                    if (name.find('dbconnect.xml') > -1):
                        logger.info('文件不删除！！')
                    else:
                        os.remove(os.path.join(root, name))
                        logger.info('start detele path :{} files:{}!'.format(path, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
                    logger.info('start detele path :{} dirs:{}!'.format(path, name))
        else:
            logger.info('path :{}not exists!'.format(path))
       except Exception as e:
           logger.error('detele path :{} dirs/files error!原因：{}'.format(path,e))

    def detele_path_files(self,path,de_file):
       try:
        de_path=os.path.join(path,de_file)
        if os.path.exists(de_path):
            os.remove(de_path)
            logger.info('start detele path :{} files:{}!'.format(path, de_file))
        else:
            logger.info('path :{}not exists!'.format(de_path))
       except Exception as e:
           logger.error('detele path :{} files error!原因：{}'.format(path,e))

    def copy_ts_to_OM(self):
        try:
            logger.info('start copy_ts_to_OM !')
            omtspath=os.path.join(configs.ompath,'TS')
            if os.path.exists(configs.tsfilespath):
                if os.path.exists(omtspath) and omtspath!=configs.tsfilespath:
                    self.detele_path(omtspath)
                if not os.path.exists(omtspath):
                    os.makedirs(omtspath)
                dirlist = os.listdir(configs.tsfilespath)
                for dir in dirlist:
                    if dir.find('.py')>-1:
                        source = os.path.join(configs.tsfilespath, dir)
                        shutil.copy(source,omtspath)
            logger.info('end copy_ts_to_OM !')
        except Exception as e:
            logger.error('copy_ts_to_OM error!原因：{}'.format(e))




    def copy_layout_to_general_process(self):
        try:
            logger.info('------start copy layout and eg.-----')
            dispath_l=os.path.join(self.dispathpath,'etc')
            enginepath_l=os.path.join(self.enginepath,'etc')
            if not os.path.exists(dispath_l):
                os.makedirs(dispath_l)
            if not os.path.exists(enginepath_l):
                os.makedirs(enginepath_l)
            # 清空文件
            self.detele_path(dispath_l)
            self.detele_path(enginepath_l)
            # 复制文件
            dirlist=os.listdir(self.layoutpath)
            for dir in dirlist:
                source=os.path.join(self.layoutpath,dir)
                if (dir == 'docks.xml' or dir == 'layout.xml'):
                    shutil.copy(source, dispath_l)
                    logger.info('copy dir:{} to "{}"'.format(source, dispath_l))
                    shutil.copy(source, enginepath_l)
                    logger.info('copy dir:{} to "{}"'.format(source, enginepath_l))
                else:
                    shutil.copy(source, enginepath_l)
                    logger.info('copy dir:{} to "{}"'.format(source, enginepath_l))
            logger.info('------end copy layout and eg.-----')
        except Exception as e:
            logger.error('copy layout error!原因：{}'.format(e))

    def copy_layout_to_vehicles(self):
        try:
            if os.path.exists(configs.simpath):
                logger.info('------start copy layout to vehicles-----')
                for i in os.listdir(configs.simpath):
                    if os.path.isdir(i):
                        vehiclespath = os.path.join(configs.simpath, i)
                        mappath = os.path.join(vehiclespath, 'etc\map')
                        if not os.path.exists(mappath):
                            os.makedirs(mappath)
                        # 清空文件
                        self.detele_path(mappath)
                        # 复制文件
                        dirlist=os.listdir(self.layoutpath)
                        for dir in dirlist:
                            source=os.path.join(self.layoutpath,dir)
                            if (dir == 'docks.xml' or dir == 'layout.xml'):
                                shutil.copy(source, mappath)
                                logger.info('copy dir:{} to "{}"'.format(source, mappath))
                logger.info('------end copy layout to vehicles-----')
            else:
                logger.info('path:{} not exists!'.format(configs.simpath))
        except Exception as e:
            logger.error('copy layout to vehicles error!原因：{}'.format(e))

    def copy_layout_to_old_general_process(self):
        try:
            logger.info('------start copy layout and eg.-----')
            dispath_l = os.path.join(self.dispathpath, 'etc')
            enginepath_l = os.path.join(self.enginepath, 'etc')
            monitor_l=os.path.join(configs.bsmonitorpath, 'configFiles')
            if not os.path.exists(dispath_l):
                os.makedirs(dispath_l)
            if not os.path.exists(enginepath_l):
                os.makedirs(enginepath_l)
            # 清空文件
            self.detele_path(dispath_l)
            self.detele_path(enginepath_l)
            self.detele_path (monitor_l)

            # 复制文件
            dirlist = os.listdir(self.layoutpath)
            for dir in dirlist:
                source = os.path.join(self.layoutpath, dir)
                shutil.copy(source, enginepath_l)
                logger.info('copy dir:{} to "{}"'.format(source, enginepath_l))
                shutil.copy(source, monitor_l)
                logger.info('copy dir:{} to "{}"'.format(source, monitor_l))

                # if (dir == 'docks.xml' or dir == 'layout.xml'):
                #     shutil.copy(source, enginepath_l)
                #     logger.info('copy dir:{} to "{}"'.format(source, enginepath_l))
                #     shutil.copy(source, monitor_l)
                #     logger.info('copy dir:{} to "{}"'.format(source, monitor_l))
                # else:
                #     shutil.copy(source, enginepath_l)
                #     logger.info('copy dir:{} to "{}"'.format(source, enginepath_l))
            logger.info('------end copy layout and eg.-----')
        except Exception as e:
            logger.error('copy layout error!原因：{}'.format(e))



    def copy_layout_to_i_process(self):
        try:
            logger.info('------start copy layout and eg.-----')
            dispath_etc = os.path.join(self.dispathpath, 'etc')
            enginepath_etc = os.path.join(self.enginepath, 'etc')
            #清空文件
            self.detele_path(dispath_etc )
            self.detele_path(enginepath_etc)
            etc_file_name=['dock.xml','layout.xml']
            for x in etc_file_name:
                self.detele_path_files(self.i_monitorpath,x)
            #复制文件
            dirlist = os.listdir(self.layoutpath)
            for dir in dirlist:
                source = os.path.join(self.layoutpath, dir)
                if (dir == 'docks.xml' or dir == 'layout.xml'):
                    shutil.copy(source, dispath_etc )
                    logger.info('copy dir:{} to "{}"'.format(source, dispath_etc ))
                    shutil.copy(source, enginepath_etc)
                    logger.info('copy dir:{} to "{}"'.format(source, enginepath_etc))
                    shutil.copy(source, self.i_monitorpath)
                    logger.info('copy dir:{} to "{}"'.format(source, self.i_monitorpath))
                else:
                    shutil.copy(source, enginepath_etc)
                    logger.info('copy dir:{} to "{}"'.format(source, enginepath_etc))
            logger.info('------end copy layout and eg.-----')
        except Exception as e:
            logger.error('copy layout error!原因：{}'.format(e))

if __name__ == '__main__':

    #  write_to_general_xml().check_excel()
    #  write_to_general_xml().write_dispathxml()
    #  write_to_general_xml().write_agv_infoxml()
    # write_to_general_xml().modify_agv_infoxml()
    # write_to_general_xml().petty_filename(r'E:\agv\sim\F-1\etc\map\docks.xml',r'E:\agv\sim\F-1\etc\map\docks1.xml')
    excelfilepath = r'E:\meite\general_meite.xlsx'
    dispatchxmlpath = r'E:\meite\softwares\Dispatch\dispatch_config.xml'

    for filepath in [excelfilepath, dispatchxmlpath]:
        if not os.path.exists(filepath):
            logger.error('error!!!文件：{}不存在！'.format(filepath))

    if os.path.exists(dispatchxmlpath) and os.path.exists(excelfilepath):
        xmlDom = minidom.parse(dispatchxmlpath)
        # excel表格为modify的内容，获取他要修改的行数和标题栏
        workbook = xlrd.open_workbook(excelfilepath)

        logger.info('---------------------------------start object config ....----------------------------------------------')
        # try:
        sheet_name='Object'
        sheet = workbook.sheet_by_name(sheet_name)
        config_num = sheet.nrows - 1
        title_list = sheet.row_values(0)

        # xml为最终输出的格式，修改后放在临时的temp.xml表里面。
        # 获取node的总数量,通过判断父节点属性Location还是Location_location的节点。
        # 计数，若是多于表格需要配置的栏数则进行删除

        # 将node xml 与excel进行修正
        while 1:
            commnad_object_info = xmlDom.getElementsByTagName("object_info")[0]
            object_info_node = commnad_object_info.getElementsByTagName("node")
            node_num = len(object_info_node)
            print( '目前node_num={},config_num={}'.format(node_num,config_num))


            if (node_num< config_num):
                need_add_node_num = config_num - node_num
                for m in range(0, need_add_node_num):
                    newCDATA2 = xmlDom.createElement("node")
                    get_object_info = xmlDom.getElementsByTagName("object_info")[0]
                    get_object_info.appendChild(newCDATA2)
            elif (node_num>config_num) :
                need_delete_node_num= node_num-config_num
                for i in range(config_num,node_num):
                    object_info_node[i].parentNode.removeChild(object_info_node[i])
            else:
                break

        if ( config_num>0):
            for j in range(0, config_num):
                row_value = sheet.row_values(j + 1)
                write_to_general_xml().modify_xml_attribute_value(title_list, row_value, object_info_node, j)

        else:
            logger.info('object_info没有配置，不需要写入xml')
        temp_file='temp.xml'
        f = open(temp_file, "w", encoding='utf-8')
        xmlDom.writexml(f)
        f.close()
        if os.path.exists(temp_file):
            write_to_general_xml().petty_filename(temp_file, dispatchxmlpath)
            os.unlink(temp_file)
        logger.info('---------------------------------end object_info config ....----------------------------------------------')
        # except Exception as e:
        #     logger.error('object_info xml error!原因：{}'.format(e))

