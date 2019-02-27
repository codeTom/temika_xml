#!/usr/bin/env python3

from EasyTemikaXML import EasyTemikaXML

tilt=[8.4/6965.0,20.0/9943.0]

xml=EasyTemikaXML()
xml.opening()
rgb=xml.rgb_image("/home/fa344/data/grid1/img", [0.1,0.1,0.1],True)
zs=xml.z_stack(5, 40, '', rgb, True)
xml.image_grid([40,40],[40,40],zs, tilt)
xml.closing()
