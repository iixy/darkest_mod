import json
import random
import copy
import shutil
import os

MAX_TRINKETS_NUM = 3

# suffix清理小函数
def clear_suffix(i):
    if i == 0: i = "";
    else: i = "_{}".format(i)
    return i;

# 创建文件夹
def make_folder():
    if not "trinkets" in os.listdir(): os.mkdir("trinkets")
    if not "panels" in os.listdir():
        os.mkdir("panels")
        os.mkdir("panels/icons_equip")
        os.mkdir("panels/icons_equip/trinket")
    if not "localization" in os.listdir():
        os.mkdir("localization")

# 汇总buff
def write_buffs(trinkets):
    buffs_fp = open("./buffs.txt","w")

    # TRINKET buff
    for trinket in trinkets["entries"]:
        buffs = [x for x in trinket["buffs"] if x.startswith("TRINKET")]
        if not buffs: continue
        buffs_string = "\n".join(buffs)
        
        buffs_fp.write(buffs_string);
        buffs_fp.write("\n")

    buffs_fp.close()

    # TB buff
    tb_buffs_fp = open("./tbbuffs.txt","w")
    for trinket in trinkets["entries"]:
        tb_buffs = [x for x in trinket["buffs"] if x.startswith("TB")]
        if not tb_buffs: continue
        buffs_string = "\n".join(tb_buffs)
        
        tb_buffs_fp.write(buffs_string);
        tb_buffs_fp.write("\n")

    tb_buffs_fp.close()

# 为id添加后缀
def creat_id_suffix(trinket,suffix):
    new_trinket = copy.deepcopy(trinket)
    new_trinket["id"] = "{}{}".format(trinket["id"],suffix)
    new_trinket["buffs"] = creat_random_buffs(len(trinket["buffs"]))
    return new_trinket

# 返回随机buff，注意伤害buff有两行，包括DMGL和DMGH
def creat_random_buffs(num):
    # [x] 随机选择buff和tb buff
    filename = random.choice(["buffs.txt","tbbuffs.txt"])
    buffs_fp = open(filename,"r")
    buffs = buffs_fp.readlines()
    
    return_buffs = []
    for i in range(num):
        buff = random.choice(buffs);
        if "DMGL" in buff: return_buffs.append(buff.replace("DMGL","DMGH"))
        if "DMGH" in buff: return_buffs.append(buff.replace("DMGH","DMGL"))
        
        if "DMG_BUFF_L" in buff: return_buffs.append(buff.replace("DMG_BUFF_L","DMG_BUFF_H"))
        if "DMG_BUFF_H" in buff: return_buffs.append(buff.replace("DMG_BUFF_H","DMG_BUFF_L"))
        
        return_buffs.append(buff)
    
    for i in range(len(return_buffs)):
        return_buffs[i] = return_buffs[i].replace("\n","")

    buffs_fp.close()
    return return_buffs

# 创建基本饰品文件，目录：trinkets/base.entries.trinkets.json
def write_base_entries_file(trinkets):
    new_trinkets = [];
    for trinket in trinkets["entries"]:
        # 特殊饰品
        if trinket["id"] == "dd_trinket":
            new_trinkets.append(trinket)
            continue;
        
        for i in range(MAX_TRINKETS_NUM):
            i = clear_suffix(i)
            new_trinkets.append(creat_id_suffix(trinket,i));

    output_fp = open("./trinkets/base.entries.trinkets.json","w")
    json.dump({"entries":new_trinkets},output_fp,indent=3)
    output_fp.close()

# 为有后缀id的饰品创建图像，目录：panels/icons_equip/trinket/inv_trinket+id.png
def change_png_name():
    scr = "./inv_trinket/"
    dst = "./panels/icons_equip/trinket/"

    ls = os.listdir(scr)
    for inv_trinket in ls:
        try:
            _, trinket_id = inv_trinket.split("+")
            trinket_id = trinket_id.replace(".png","")
            
        except ValueError as err:
            shutil.copyfile(scr+inv_trinket,dst+inv_trinket)
            continue;
        
        for i in range(MAX_TRINKETS_NUM):
            i = clear_suffix(i)
            shutil.copyfile("{}{}".format(scr,inv_trinket),"{}inv_trinket+{}{}.png".format(dst,trinket_id,i));

# 创建title, 目录：localization/trinket_english.string_table.xml
# 创建后需将xml文件拖动到../../_windows/localization.exe生成english.loc2，并将文件复制到xml所在目录
def localization():
    file_xml = """<?xml version="1.0" encoding="UTF-8"?>
<root>
  <language id="{language}">
    {title}
  </language>
</root>"""

    title_xml = """<entry id="{id}"><![CDATA[{title}]]></entry>"""
    title_xmls = ""

    for trinket_name in os.listdir("./panels/icons_equip/trinket/"):
        try:
            _, trinket_id = trinket_name.split("+")
        except:
            continue
        trinket_id = trinket_id.replace(".png","")

        try:
            int(trinket_id[-1])
        except:
            continue;
        
        trinket_name = trinket_id.replace("_"," ").capitalize()
        trinket_id = "str_inventory_title_trinket"+trinket_id

        title_xmls += title_xml.format(id=trinket_id,title=trinket_name)
        title_xmls += "\n    "

    fp = open("./localization/random_trinket_english.string_table.xml","w")
    fp.write(file_xml.format(language="english",title=title_xmls))
    fp.close()

    fp_schinese =  open("./localization/random_trinket_schinese.string_table.xml","w")
    fp_schinese.write(file_xml.format(language="schinese",title=title_xmls))
    fp_schinese.close()
    # os.system("START localization/localization.bat")

def clear_file():
    try:
        shutil.rmtree("./trinkets");
    except FileNotFoundError:
        pass

    try:
        shutil.rmtree("./panels")
    except FileNotFoundError:
        pass

    try:
        os.remove("./localization/trinket_english.string_table.xml")
    except FileNotFoundError:
        pass

if __name__ == "__main__":
    trinkets_fp = open("./res","r")
    trinkets = json.loads(trinkets_fp.read())

    clear_file()
    make_folder()
    # write_buffs(trinkets);
    write_base_entries_file(trinkets)
    change_png_name()
    # localization()

    trinkets_fp.close()