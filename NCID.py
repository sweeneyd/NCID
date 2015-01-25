# -*- coding: utf-8 -*-
"""
Created on Wed Jan 21 13:08:53 2015

@author: Dan
"""

import os
import cv2
import numpy as np
import csv

class NCID(object):
    def __init__(self, directory='/Users/Dan/Desktop/ALDH+RGB/', write2File=False, TOLERANCE=50):
        self.TOLERANCE = TOLERANCE
        self.SCALE = 1
        self.cellsByImage = []
        self.cells = []
        self.file_list = self.getFilenames(directory)
        for i in self.file_list:
            cellsInImage = self.findCells(directory+i)
            self.cellsByImage.append(cellsInImage)
            for cell in cellsInImage:
                self.cells.append([cell, i])
                print str(i) + ' %s/%s cells' %(cellsInImage.index(cell)+1, len(cellsInImage))
        if write2File == True:
            self.genDataFile(directory)

    def genDataFile(self, directory, delimiter=','):
        with open(directory + 'cellData.csv', 'wb') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=delimiter,
                                    quotechar=';', quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerow([';Analysis performed on 8-bit RGB using CNID module'])
            spamwriter.writerow([';Written by Dan Sweeney, Virginia Tech BEAM (Jan. 2014)'])
            spamwriter.writerow([';Data processed from cells in %s' %directory])
            spamwriter.writerow([';Total Images = %s' %len(self.cellsByImage)])
            spamwriter.writerow([';Total Cells = %s' %len(self.cells)])
            spamwriter.writerow([';NOTE: Effective nuclear and cytoplasmic radii are calculated by R_eff = sqrt(majAxis*minAxis).'])
            spamwriter.writerow([';      Volume was calculated by 4/3*pi*R_eff^3 and N/C ratio given by NC = Vnuc/Vcyto.'])
            spamwriter.writerow([';cellNo,centerCytoX,centerCytoY,majCytoAxis,minCytoAxis,tiltCytoAngle,centerNucX,centerNucY,majNucAxis,minNucAxis,tiltNucAngle,NCRatio,Scale,imageID'])
            for i in self.cells:
                spamwriter.writerow([self.cells.index(i), i[0][0][0][0], i[0][0][0][1], i[0][0][1][0], i[0][0][1][1], i[0][0][2],
                                     i[0][1][0][0], i[0][1][0][1], i[0][1][1][0], i[0][1][1][1], i[0][1][2],
                                     i[0][2], i[0][3], i[1]])
        csvfile.close()
        return True
    

    def getFilenames(self, directory):
        file_list = [i for i in os.listdir(directory) if os.path.isfile(os.path.join(directory, i))]
        return file_list
        
    def findCells(self, filename, show = False):
        img = cv2.imread(filename)
        blue, green, red = cv2.split(img)
        cyto_ellipses = self.rmDuplicates(self.getEllipses(green))
        nuc_ellipses = self.rmDuplicates(self.getEllipses(blue))
        matches = self.matchNuc2Cyto(cyto_ellipses, nuc_ellipses)
        return matches
        
    def matchNuc2Cyto(self, cyto_ellipses, nuc_ellipses):
        matches = []
        matched_cyto = []
        matched_nuc = []
        blank_ellipse = ((0, 0), (0, 0), 0)
        for i in range(len(cyto_ellipses)):
            for j in range(len(nuc_ellipses)):
                if self.getDist(cyto_ellipses[i], nuc_ellipses[j]) < self.TOLERANCE:
                    matches.append([cyto_ellipses[i], nuc_ellipses[j], self.getNCRatio(cyto_ellipses[i], nuc_ellipses[j]), self.SCALE])
                    matched_cyto.append(i)
                    matched_nuc.append(j)
        if len(cyto_ellipses) > len(matches):
            for i in range(len(cyto_ellipses)):
                if i not in matched_cyto:
                    matches.append([cyto_ellipses[i], blank_ellipse, 0., self.SCALE])
        return matches
    
    def getNCRatio(self, cytoplasm, nucleus):
        cytoplasm_radius = float(np.sqrt(np.product(cytoplasm[1])))
        nuclear_radius = float(np.sqrt(np.product(nucleus[1])))
        cyto_eff_sphere = 4./3.*np.pi*cytoplasm_radius**3
        nuc_eff_sphere = 4./3.*np.pi*nuclear_radius**3
        NCRatio = nuc_eff_sphere / cyto_eff_sphere 
        return NCRatio
        
    def rmDuplicates(self, data_array):
        data_array.sort()
        dist_array = [1.15*self.TOLERANCE]
        for i in range(1, len(data_array)):
            if len(data_array[i]) > 1:
                dist_array.append(self.getDist(data_array[i], data_array[i-1]))
        data_copy = [data_array[i] for i in range(len(data_array)) if dist_array[i] > self.TOLERANCE]
        return data_copy
        
    def getDist(self, pt1, pt2):
        dist = np.sqrt((pt1[0][0] - pt2[0][0])**2 + (pt1[0][1] - pt2[0][1])**2)
        return dist
            
    def getBinary(self, img, threshold):
        img = cv2.erode(img, None, 10)
        img = cv2.dilate(img, None, 10)
        binary = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
        return binary
        
    def getEllipses(self, img):
        contours, hierarchy = cv2.findContours(img, 
                                               mode=cv2.RETR_LIST, 
                                               method=cv2.CHAIN_APPROX_SIMPLE)
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        shapes = []
        for i in range(len(contours)): 
            if len(contours[i]) >= 5:
                # ellipse == ((center_x, center_y), (minor_axis, major_axis), angle_in_degrees)
                ellipse = cv2.fitEllipse(contours[i])
                if min(ellipse[1]) > self.TOLERANCE:
                    shapes.append(ellipse)
                cv2.ellipse(img, ellipse, (0, 255, 0), -1)
        return shapes
        
    def showEllipses(self, img, ellipses, color=(0,255,0)):
        for i in ellipses:
            cv2.ellipse(img, i, color, -1)
        cv2.imshow('%s'%str(img), img)
        return True
    
if __name__ == '__main__':
    print 'ERROR: Pass this module a directory containing 8-bit RGB images to analyze'        