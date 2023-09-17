"""
# -----------------------------------------------------------------------------#
#                                                                              #
#                            Python script                                     #
#                                                                              #
# -----------------------------------------------------------------------------#
Description  :
File for keeping commonly used enums

# -----------------------------------------------------------------------------#
#                                                                              #
#       Copyright (c) 2023 , Ali Yavuz Kahveci.                                #
#                         All rights reserved                                  #
#                                                                              #
# -----------------------------------------------------------------------------#
"""
import enum


class FeedType(enum.StrEnum):
    XML = "Xml"
    JSON = "Json"
    PLAIN = "Plain"
    UNDEFINED = "Undefined"


class FeedSourceType(enum.StrEnum):
    REST = "Rest"
    UNDEFINED = "Undefined"
