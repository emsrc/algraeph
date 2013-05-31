# -*- coding: utf-8 -*-
#
# Copyright (C) 2007-2013 by 
# Erwin Marsi and TST-Centrale
#
#
# This file is part of the Algraeph program.
#
# The Algraeph program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# The Algraeph program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
wraps methods from wx.lib.pubsub so they can be logged
"""

__author__ = "Erwin Marsi <e.marsi@gmail.com>"



from wx.lib.pubsub import Publisher

try:
    from wx.lib.pubsub import ALL_TOPICS
except ImportError:
    from wx.lib.pubsub.pub import ALL_TOPICS

from graeph.log import pubsub_logger


def name(method):
    """
    return class path plus method as a string
    """
    if hasattr(method, "im_class"):
        class_path = str(method.im_class).split("'")[1]
        method_name = method.__name__
        return class_path + "." + method_name
    else:
        # ordinary function
        return method.__name__


def subscribe(listener, topic=ALL_TOPICS):
    """
    subscribe listener to topic and log event
    """
    
    if is_subscribed(listener, topic):
        pubsub_logger.warning("%s already subscribed to topic %s!", name(listener), topic)
        
    pubsub_logger.debug("SUBSCRIBE: %s subscribes to topic %s", name(listener), topic)
    Publisher().subscribe(listener, topic)
    
    
def save_subscribe(listener, topic=ALL_TOPICS):
    """
    subscribe listener to topic and log event,
    unless listener is already subscribed
    """
    if not is_subscribed(listener, topic):
        subscribe(listener, topic)
    else:
        pubsub_logger.debug("save_subscribe prevented %s second subscription to topic %s", 
                            name(listener), topic)


def unsubscribe(listener, topics=None):
    """
    unsubscribe listener from topic and log event
    """
    pubsub_logger.debug("UNSUBSCRIBE : %s unsubsrcibes from topic(s) %s", name(listener), topics)
    Publisher().unsubscribe(listener, topics)
    

def send(talker, topic=ALL_TOPICS, data=None):
    """
    send message from talker to topic and log event
    """
    pubsub_logger.debug(10 * "-" + " %s " + 60 * "-", topic)
    
    if data:
        pubsub_logger.debug("SEND: %s sends message for topic %s with data %s",
                            name(talker), topic, repr(data))
    else:
        pubsub_logger.debug("SEND: %s sends message for topic %s", name(talker),
                            topic)
        
    Publisher().sendMessage(topic, data)

    
def receive(listener, message):
    """
    log reception of message by listener
    """    
    if not message:
        pubsub_logger.debug("RECEIVE: %s receives message", name(listener))
    elif message.data:
        pubsub_logger.debug("RECEIVE: %s receives message with topic %s and data %s",
                            name(listener), ".".join(message.topic), repr(message.data))
    else:
        pubsub_logger.debug("RECEIVE: %s receives message with topic %s",
                            name(listener), ".".join(message.topic))
    

def is_subscribed(listener, topic):
    """
    test if listener is subscribed to topic
    """
    try:
        return Publisher().isSubscribed(listener, topic)
    except KeyError:
        pass
