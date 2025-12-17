# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/database/models.py
# GitHub: https://github.com/NanmiCoder
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1
#
# 声明：本代码仅供学习和研究目的使用。使用者应遵守以下原则：
# 1. 不得用于任何商业用途。
# 2. 使用时应遵守目标平台的使用条款和robots.txt规则。
# 3. 不得进行大规模爬取或对平台造成运营干扰。
# 4. 应合理控制请求频率，避免给目标平台带来不必要的负担。
# 5. 不得用于任何非法或不当的用途。
#
# 详细许可条款请参阅项目根目录下的LICENSE文件。
# 使用本代码即表示您同意遵守上述原则和LICENSE中的所有条款。

from sqlalchemy import create_engine, Column, Integer, Text, String, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


Base = declarative_base()


class WeiboNote(Base):
    __tablename__ = 'weibo_note'
    id = Column(Integer, primary_key=True)
    user_id = Column(String(255))
    nickname = Column(Text)
    avatar = Column(Text)
    gender = Column(Text)
    profile_url = Column(Text)
    ip_location = Column(Text, default='')
    add_ts = Column(BigInteger)
    last_modify_ts = Column(BigInteger)
    note_id = Column(BigInteger, index=True)
    content = Column(Text)
    create_time = Column(BigInteger, index=True)
    create_date_time = Column(String(255), index=True)
    liked_count = Column(Text)
    comments_count = Column(Text)
    shared_count = Column(Text)
    note_url = Column(Text)
    source_keyword = Column(Text, default='')


class WeiboNoteComment(Base):
    __tablename__ = 'weibo_note_comment'
    id = Column(Integer, primary_key=True)
    user_id = Column(String(255))
    nickname = Column(Text)
    avatar = Column(Text)
    gender = Column(Text)
    profile_url = Column(Text)
    ip_location = Column(Text, default='')
    add_ts = Column(BigInteger)
    last_modify_ts = Column(BigInteger)
    comment_id = Column(BigInteger, index=True)
    note_id = Column(BigInteger, index=True)
    content = Column(Text)
    create_time = Column(BigInteger)
    create_date_time = Column(String(255), index=True)
    comment_like_count = Column(Text)
    sub_comment_count = Column(Text)
    parent_comment_id = Column(String(255))


class WeiboCreator(Base):
    __tablename__ = 'weibo_creator'
    id = Column(Integer, primary_key=True)
    user_id = Column(String(255))
    nickname = Column(Text)
    avatar = Column(Text)
    ip_location = Column(Text)
    add_ts = Column(BigInteger)
    last_modify_ts = Column(BigInteger)
    desc = Column(Text)
    gender = Column(Text)
    follows = Column(Text)
    fans = Column(Text)
    tag_list = Column(Text)
