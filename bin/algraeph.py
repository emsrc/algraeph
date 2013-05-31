#!/usr/bin/env pythonw
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


from daeso.utils.cli import DaesoArgParser
from graeph.release import version, description

parser = DaesoArgParser(description=description.strip(), 
                        version=version)

parser.add_argument(
    "corpus_file",
    metavar="FILE",
    nargs="?", 
    help="parallel graph corpus file")

parser.add_argument(
    "-d", "--dot_exec",
    metavar="FILE", 
    help='"dot" graph drawing program')

parser.add_argument(
    "-r", "--redirect",
    action='store_true',
    help="redirect output written to stdout and stderr streams "
    "to a pop-up window")

args = parser.parse_args()


# delay import of gui stuff until here, so commd line help comes quickly
from graeph.gui import Algraeph

app = Algraeph(cl_args=args, redirect=args.redirect)
app.MainLoop()
    

