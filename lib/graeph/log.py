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


__author__ = "Erwin Marsi <e.marsi@gmail.com>"



import logging

logging.basicConfig(format='%(levelname)s @ %(name)s: %(message)s')


class PubsubFilter(logging.Filter):
    """
    filter to prevent logging of uninteresting events
    as defined by self.hidden_topics
    """

    hidden_topics = ["statusDescription"]
    
    def filter(self, record):
        for topic in self.hidden_topics:
            if topic in record.args:
                return False
        else:
            return True


pubsub_logger = logging.getLogger("algraeph.pubsub")
pubsub_logger.addFilter(PubsubFilter())

graphviz_logger = logging.getLogger("algraeph.graphviz")


# set log level here:

pubsub_logger.setLevel(logging.DEBUG)
graphviz_logger.setLevel(logging.DEBUG)