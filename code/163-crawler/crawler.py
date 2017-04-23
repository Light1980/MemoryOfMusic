# -*- coding: utf-8 -*-
"""
Created on Fri Apr 21 01:01:25 2017

@author: ppeng
@project: 163 music playlist crawler
@Acknowledgement: 
    + Github： @pengshiqi - 获取热评部分代码
    + Personal website: @Moonlib - 云音乐关键API
"""



import requests
import json
import os
import time
import csv
import codecs
#import NetEaseMusicCrawl as commentCrawl




# 构造一个简单的云音乐爬虫对象

class neteaseMusicCrawler():
    def __init__(self, playlist_id):
        """
        从API获取JSON资源
        
        params: + playlist_id 歌单ID
        output: + self.playlist_dict 从JSON资源转换得到的字典
                     + self.playlist_len 歌单总长度
        """

        my_headers = {'Host': 'music.163.com',
              'Connection': 'keep-alive',
              'Content-Type': "application/x-www-form-urlencoded; charset=UTF-8",
              'Referer': 'http://music.163.com/',
              "User-Agent": "Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"}
        self.playlist_dict = json.loads(requests.get('http://music.163.com/api/playlist/detail?id={}&updateTime=-1'.format(playlist_id), headers = my_headers).content)
        if self.playlist_dict["code"] != 200:
            print("请确认自己是否输入了正确的歌单ID")
            print("请重新运行此脚本")
            self.status = "error"
        else:
            self.status = 200
            print("相关方法")
            print("+ crawler.crawlAlbumImgs() 该方法将增量下载当前歌单下所有歌曲的专辑封面")
            print("+ crawler.crawlCustomAlbumImgs(width, height) 该方法将增量下载当前歌单下所有歌曲自定义宽度和长度的专辑封面，自行替换成对应数字")
            print("+ crawler.singleMusicDownload(music_id) 该方法将下载歌单内的指定歌曲，自行替换成对应歌曲id")
            print("+ crawler.albumHotComments() （未完成）该方法将下载歌单内的全部歌曲的热门评论，以MD格式排版")
            print("+ crawler.singleMusicHotComments(music_id) （未完成）该方法将下载歌单内的指定歌曲的热门评论，以MD格式排版，自行替换成对应歌曲id")
            
            
        # self.playlist_len = len(self.playlist_dict["result"]["tracks"])
        self.illegalchar = ['/','\\','*', '?', "<", ">" , '"', "|", ":"]    
            

    def crawlAlbumImgs(self):
        """
        下载歌单里所有歌曲的专辑图片
        """
        
        try:
            os.mkdir("album_imgs")
            print("成功创建album_img文件夹")
        except:
            print("album_imgs文件夹已存在，无需创建")
            
        # 在创建新csv时删掉旧的，避免冲突  
        csv_list = os.listdir("album_imgs/")
        if "songs-info.csv" in csv_list:
            os.remove("album_imgs/songs-info.csv")
        
        # 通过扫描已有的图片列表实现增量爬取
        img_os_list = os.listdir("album_imgs/")
        img_list = []
        for i in img_os_list:
            i = i.replace(".jpg","")
            img_list.append(int(i))
        #print(img_list)
        playlist_list = []
        for music in self.playlist_dict["result"]["tracks"]:
            playlist_list.append(music["id"])
        #print(playlist_list)
        crawl_list = [e for e in playlist_list if e not in img_list]
        crawl_list_len = len(crawl_list)
        #print(crawl_list)
        
        count = 1
        
        for music1 in crawl_list:
            for music2 in self.playlist_dict["result"]["tracks"]:
                if music1 == music2["id"]:
#==============================================================================
#                     # 防止歌名出现非法字符时下载出错
#                     for char in self.illegalchar:
#                         if char in music1:
#                             music1 = music1.replace(char, "-")
#==============================================================================
                    try:
                        with open("album_imgs/" + str(music2["id"]) + '.jpg', "wb") as f:
                            f.write(requests.get(music2["album"]["picUrl"], timeout = 5).content)
                        print("已下载 {}封面，总进度{}/{}".format(music2["name"], count, crawl_list_len))
                    except:
                        try:
                            with open("album_imgs/" + str(music2["id"]) + '.jpg', "wb") as f:
                                f.write(requests.get(music2["album"]["picUrl"], timeout = 5).content)
                            print("已下载 {}封面，总进度{}/{}".format(music2["name"], count, crawl_list_len))
                        except requests.exceptions.Timeout or ConnectionError as e:
                            print("========下载{}.jpg超时=========".format(music1))
            
            count += 1
            time.sleep(0.1)
        
        # 创建一个歌名-ID对照表
        name_id_dict = {}
        name_id_dict_count = 1
        for k in self.playlist_dict["result"]["tracks"]:
            name_id_dict[str(name_id_dict_count)] = {"name": k["name"], "id": k["id"], "album": k["album"]["name"], "artists": k["artists"][0]["name"]}
            name_id_dict_count += 1
            
        with open("album_imgs/songs-info.csv", "wb") as csvfile:
            csvfile.write(codecs.BOM_UTF8)
        
        with open("album_imgs/songs-info.csv", "a", newline='', encoding="utf-8") as csvfile:
            fieldnames = ["name", "id","album", "artists"]
            writer = csv.DictWriter(csvfile, fieldnames = fieldnames)
            writer.writeheader()
            
            for g in name_id_dict:
                temp_dict = name_id_dict[g]
                writer.writerow(temp_dict)       

    def crawlCustomAlbumImgs(self, width, height):
        """
        下载歌单里所有歌曲的自定义长宽专辑图片
        
        params: + width 图片宽度
                + height 图片长度
        """
        
        width = str(width)
        height = str(height)
        
        try:
            os.mkdir("custom_album_imgs_{}_{}/".format(width, height))
            print("成功创建custom_album_img_{}_{}文件夹".format(width, height))
        except:
            print("custom_album_imgs_{}_{}文件夹已存在，无需创建".format(width, height))
        # 在创建新csv时删掉旧的，避免冲突  
        csv_list = os.listdir("custom_album_imgs_{}_{}/".format(width, height))
        if "songs_info_{}_{}.csv".format(width,height) in csv_list:
            os.remove("custom_album_imgs_{}_{}/songs_info_{}_{}.csv".format(width, height,width,height))
        
        
        # 通过扫描已有的图片列表实现增量爬取
        img_os_list = os.listdir("custom_album_imgs_{}_{}/".format(width, height))
        img_list = []
        for i in img_os_list:
            i = i.replace(".jpg","")
            img_list.append(int(i))
        #print(img_list)
        playlist_list = []
        for music in self.playlist_dict["result"]["tracks"]:
            playlist_list.append(music["id"])
        #print(playlist_list)
        crawl_list = [e for e in playlist_list if e not in img_list]
        crawl_list_len = len(crawl_list)
        #print(crawl_list)
        
        count = 1
        payload = {"params": width + "y" + height}
        for music1 in crawl_list:
            for music2 in self.playlist_dict["result"]["tracks"]:
                if music1 == music2["id"]:
                    try:
                        with open("custom_album_imgs_{}_{}/".format(width, height) + str(music2["id"]) + '.jpg', "wb") as f:
                            f.write(requests.get(music2["album"]["picUrl"], params = payload, timeout = 5).content)
                        print("已下载 {}封面，总进度{}/{}".format(music2["name"], count, crawl_list_len))
                    except:
                        try:
                            with open("custom_album_imgs_{}_{}/".format(width, height) + str(music2["id"]) + '.jpg', "wb") as f:
                                f.write(requests.get(music2["album"]["picUrl"], params = payload, timeout = 5).content)
                            print("已下载 {}封面，总进度{}/{}".format(music2["name"], count, crawl_list_len))
                        except requests.exceptions.Timeout or ConnectionError as e:
                            print("========下载{}.jpg超时=========".format(music1))
            count += 1
            time.sleep(0.1)
        
        # 创建一个歌曲相关信息表格        
            
        name_id_dict = {}
        name_id_dict_count = 1
        for k in self.playlist_dict["result"]["tracks"]:
            name_id_dict[str(name_id_dict_count)] = {"name": k["name"], "id": k["id"], "album": k["album"]["name"], "artists": k["artists"][0]["name"]}
            name_id_dict_count += 1
            
        with open("custom_album_imgs_{}_{}/songs_info_{}_{}.csv".format(width, height,width,height), "wb") as csvfile:
            csvfile.write(codecs.BOM_UTF8)
        
        with open("custom_album_imgs_{}_{}/songs_info_{}_{}.csv".format(width, height,width,height), "a", newline='', encoding="utf-8") as csvfile:
            fieldnames = ["name", "id","album", "artists"]
            writer = csv.DictWriter(csvfile, fieldnames = fieldnames)
            writer.writeheader()
            
            for g in name_id_dict:
                temp_dict = name_id_dict[g]
                writer.writerow(temp_dict)
            
                



    def crawlHotComment(self):
        pass
    
    def singleMusicDownload(self, music_id):
        """
        单独歌曲下载
        """
        try:
            os.mkdir("music")
            print("成功创建music文件夹，音乐将保存到此文件夹内")
        except:
            pass
        
        music_name_searched = 0
        for music in self.playlist_dict["result"]["tracks"]:
            if music["id"] == int(music_id):
                music_name = music["name"]
                music_url = music["mp3Url"]
                music_name_searched = 1
                break
        if music_name_searched == 0:
            print("无法在本歌单内搜索到该歌曲，请检查歌曲ID是否输入正确。")
            music_name = "You are my song shine"
            music_url = 'http://m2.music.126.net/qQptWzl8SX_f7Xk2VUvw8A==/3348012906737064.mp3'
            
        
        music_list = os.listdir("music/")
        
        music_downloaded = 0
        for m_name in music_list:
            if music_name in m_name:
                print("{}已存在，无需再次下载".format(m_name))
                music_downloaded = 1
                break;
                
        if music_downloaded == 0:
            if music_name_searched == 0:
                try:
                    with open("music/" + music_name + '.mp3', "wb") as f:
                            f.write(requests.get(music_url, timeout = 20).content)
                    print("已下载我自己这段时间最喜欢的音乐 {}.mp3".format(music_name))
                except:
                    print("下载超时，请重试或下载别的歌")
            elif music_name_searched == 1:
                try:
                    with open("music/" + music_name + '.mp3', "wb") as f:
                            f.write(requests.get(music_url, timeout = 20).content)
                    print("已下载 {}.mp3".format(music_name))
                except:
                    print("下载超时，请重试或下载别的歌")

# 询问歌单ID，创建一个爬虫对象

playlist_id = input("请输入需要提取的歌单ID：")
crawler = neteaseMusicCrawler(playlist_id)

if crawler.status != "error":
    judge_0 = 0
    while judge_0 == 0:
        crawl_playlist = input("是否获取当前歌单下的所有歌曲的专辑封面？(Y/N)")
        crawl_playlist = crawl_playlist.lower()
        if crawl_playlist == "y":
            crawler.crawlAlbumImgs()
            judge_0 = 1
        elif crawl_playlist == "n":
            judge_0 = 1
        else:
            pass
        
    judge_1 = 0
    while judge_1 == 0:
        crawl_custom_playlist = input("是否获取当前歌单下的所有歌曲自定义宽长的专辑封面？(Y/N)")
        crawl_custom_playlist = crawl_custom_playlist.lower()
        if crawl_custom_playlist == "y":
            width = input("请输入所需宽度 ")
            height = input("请输入所需长度 ")
            crawler.crawlCustomAlbumImgs(width, height)
            judge_1 = 1
        elif crawl_custom_playlist == "n":
            judge_1 = 1
        else:
            pass
    
    judge_2 = 0
    while judge_2 == 0:
        crawl_music = input("是否要下载歌单内指定的音乐？(Y/N)")
        crawl_music = crawl_music.lower()
        if crawl_music == "y":
            judge_3 = 0
            while judge_3 == 0:
                music_id = input("请输入需要下载歌曲的ID ")
                crawler.singleMusicDownload(music_id)
                download_exit = input("是否需要继续下载别的歌曲？(Y/N)")
                download_exit = download_exit.lower()
                if download_exit != "y":
                    judge_3 = 1
                    judge_2 = 1
        elif crawl_music == "n":
            judge_2 = 1
        else:
            pass
    print()    
    print("Love will always guide us.")            
    print("Bye :)")


    