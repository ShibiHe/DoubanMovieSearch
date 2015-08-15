# -*- coding: utf-8 -*-

import scrapy

class MovieItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    A_movieTitle = scrapy.Field()
    A_movieAlias = scrapy.Field()
    B_movieYear = scrapy.Field()
    C_movieDirector = scrapy.Field()
    D_movieRating = scrapy.Field()
    E_movieIntro = scrapy.Field()
    F_movieLink = scrapy.Field()
    movieBetterThan = scrapy.Field()
    movieWriter = scrapy.Field()
    movieActor = scrapy.Field()
    movieInfo = scrapy.Field()
    movieCommentAmount = scrapy.Field()

class ReviewItem(scrapy.Item):
    A_reviewTitle = scrapy.Field()
    B_reviewMovie = scrapy.Field()
    C_reviewWriter = scrapy.Field()
    D_reviewContent = scrapy.Field()