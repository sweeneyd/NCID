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
    def __init__(self, root_directory='/Users/Dan/Desktop/ALDH+/', write2File=False, TOLERANCE=50):
        self.directory = root_directory + 'RGB/'
        self.TOLERANCE = TOLERANCE
        self.units = {'cm': 1e-2, 'mm': 1e-3, 'µm': 1e-6}
        self.SCALE = self.getScaleDict(root_directory)
        self.cellsByImage = []
        self.cells = []
        self.file_list = self.getFilenames(self.directory)
        for i in self.file_list:
            cellsInImage = self.findCells(self.directory+i)
            self.cellsByImage.append(cellsInImage)
            for cell in cellsInImage:
                self.cells.append([cell, i])
                print str(i) + ' %s/%s cells' %(cellsInImage.index(cell)+1, len(cellsInImage))
        if write2File == True:
            self.genDataFile(self.directory)
            
    def getScaleDict(self, directory='/Users/Dan/Desktop/ALDH+/'):
        a = np.array(self.getFilenames(directory))
        types = [i.split('.')[-1] for i in a]
        data_filelist = []
        scale = {}
        for i in range(len(types)):
            if types[i] == 'xml' and a[i].endswith('Properties.xml'):
                scale['%s'%(a[i].split('_')[0]+'_RGB.tif')] = self.getScale(directory+a[i])
                data_filelist.append(a[i])
        return scale
        
    def getScale(self, path):
        f = open(path)
        fline = f.readlines()
        f.close()
        for line in fline:
            if 'DimID="X"' in line:
                xNoE = float(line.split('NumberOfElements=')[-1].split('"')[1])
                xLength = float(line.split('Length=')[-1].split('"')[1])
                xUnits = self.units[line.split('Unit=')[-2].split('"')[1]]
                xCalLength = xLength*xUnits
                xScale = float(xCalLength)/float(xNoE)
                
#            if 'DimID="Y"' in line:
#                yNoE = float(line.split('NumberOfElements=')[-1].split('"')[1])
#                yLength = float(line.split('Length=')[-1].split('"')[1])
#                yUnits = line.split('Units=')[-1].split('"')[1]
#                yCalLength = yLength*self.units[yUnits]
#                yScale = float(yCalLength)/float(yNoE)
            
        return xScale

    def genDataFile(self, directory, delimiter=','):
        if 'cellData.csv' in self.getFilenames(directory):
            os.remove(directory + 'cellData.csv')
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
            spamwriter.writerow([';cellNo,centerCytoX,centerCytoY,majCytoAxis,minCytoAxis,tiltCytoAngle,centerNucX,centerNucY,majNucAxis,minNucAxis,tiltNucAngle,NCRatio,xScale,Reff,Veff,imageID'])
            for i in self.cells:
                spamwriter.writerow([self.cells.index(i), i[0][0][0][0], i[0][0][0][1], i[0][0][1][0], i[0][0][1][1], i[0][0][2],
                                     i[0][1][0][0], i[0][1][0][1], i[0][1][1][0], i[0][1][1][1], i[0][1][2],
                                     i[0][2], self.SCALE[i[1]], i[0][4], i[0][5], i[1]])
        csvfile.close()
        return True
    

    def getFilenames(self, directory):
        file_list = [i for i in os.listdir(directory) if os.path.isfile(os.path.join(directory, i))]
        if '.DS_Store' in file_list:
            os.remove(directory+'/.DS_Store')
        return file_list
        
    def findCells(self, filename, show = False):
        img = cv2.imread(filename)
        name = filename.split('/')[-1]
        blue, green, red = cv2.split(img)
        cyto_ellipses = self.rmDuplicates(self.getEllipses(green))
        nuc_ellipses = self.rmDuplicates(self.getEllipses(blue))
        matches = self.matchNuc2Cyto(cyto_ellipses, nuc_ellipses, self.SCALE[name])
        return matches
        
    def matchNuc2Cyto(self, cyto_ellipses, nuc_ellipses, scale):
        matches = []
        matched_cyto = []
        matched_nuc = []
        blank_ellipse = ((0, 0), (0, 0), 0)
        for i in range(len(cyto_ellipses)):
            for j in range(len(nuc_ellipses)):
                if self.getDist(cyto_ellipses[i], nuc_ellipses[j]) < self.TOLERANCE:
                    matches.append([cyto_ellipses[i], nuc_ellipses[j], 
                                    self.getNCRatio(cyto_ellipses[i], nuc_ellipses[j], scale), 
                                    scale, 
                                    self.getReff(cyto_ellipses[i], scale), 
                                    self.getVeff(cyto_ellipses[i], scale)])
                    matched_cyto.append(i)
                    matched_nuc.append(j)
        if len(cyto_ellipses) > len(matches):
            for i in range(len(cyto_ellipses)):
                if i not in matched_cyto:
                    matches.append([cyto_ellipses[i], blank_ellipse, 
                                    0., 
                                    scale,
                                    self.getReff(cyto_ellipses[i], scale), 
                                    self.getVeff(cyto_ellipses[i], scale)])
        return matches
        
    def getReff(self, ellipse, scale):
        Rmaj = ellipse[1][1] * scale/2
        Rmin = ellipse[1][0] * scale/2
        Reff = np.sqrt(Rmaj*Rmin)
        return Reff
        
    def getVeff(self, ellipse, scale):
        Rmaj = ellipse[1][1] * scale/2
        Rmin = ellipse[1][0] * scale/2
        Veff = (np.sqrt(Rmaj*Rmin))**3 * 4./3. * np.pi
        return Veff
    
    def getNCRatio(self, cytoplasm, nucleus, scale):
        Rmaj_cyto = cytoplasm[1][1] * scale/2
        Rmin_cyto = cytoplasm[1][0] * scale/2
        cytoplasm_radius = float(np.sqrt(Rmaj_cyto * Rmin_cyto))
        cyto_eff_sphere = 4./3.*np.pi*cytoplasm_radius**3
        
        Rmaj_nuc = nucleus[1][1] * scale/2
        Rmin_nuc = nucleus[1][0] * scale/2
        nuclear_radius = float(np.sqrt(Rmaj_nuc * Rmin_nuc))
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