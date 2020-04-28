import os
import numpy as np
import vtk

class LineFitter():
    # instantiate the variables for line fitting
    def __init__(self, pts=None, limit=10000, length=3, dimensions=3, debug=False):
        self.points = vtk.vtkPoints()
        self.polydata = vtk.vtkPolyData()
        self.vertex_filter = vtk.vtkVertexGlyphFilter()
        self.append_list = vtk.vtkAppendPolyData()
        self.line = vtk.vtkLineSource()
        self.limit = limit
        self.length = length
        self.pts = pts
        self.line_fit = None
        
        if dimensions != 3 and dimensions != 2:
            print("You have provided an inadequate dimension to fit to. Dimensions can be: 2, 3")
            return
        
        self.fit_dimensions = dimensions
        self.debug = debug
    
    # input -> filename is a string
    # input -> data is a vtk type (either ".vti" or ".vtp")
    def WriteData(self, filename, data):
        writer = None
        extension = os.path.basename(filename).split('.')[-1]
        
        if extension == "vti":
            writer = vtk.vtkXMLImageDataWriter()
        elif extension == "vtp":
            writer = vtk.vtkXMLPolyDataWriter()
        else:
            print("File Extension's Unknown")
            return
        
        writer.SetFileName(filename)
        writer.SetInputData(data)
        writer.Write()
    
    # use a generator for making 2d points
    def generate_pts_2d(self):
        self.pts = []
        x = np.random.rand(1)[0]
        y = np.random.rand(1)[0]
        
        for i in range(self.limit):
            self.pts.append([x, y])
            x = np.random.rand(1)[0] + np.random.randint(0, 100) + i
            y = np.random.rand(1)[0] + np.random.randint(0, 100) + i
    
    # use a generator for making 3d points
    def generate_pts_3d(self):
        self.pts = []
        x = np.random.rand(1)[0]
        y = np.random.rand(1)[0]
        z = np.random.rand(1)[0]
        
        for i in range(self.limit):
            self.pts.append([x, y, z])
            x = np.random.rand(1)[0] + np.random.randint(0, 100) + i
            y = np.random.rand(1)[0] + np.random.randint(0, 100) + i
            z = np.random.rand(1)[0] + np.random.randint(0, 100) + i
    
    # fit the line in 2 dimensions
    def line_fitter_2d(self):
        if isinstance(self.pts, np.ndarray):
            pass
        else:
            self.pts = np.asarray(self.pts)
        
        x = self.pts.T[0]
        y = self.pts.T[1]
        
        x_mean = x.mean()
        y_mean = y.mean()
        
        x_dirs, y_dirs = [], []
        
        p1 = [x_mean, y_mean]
        for i in range(self.pts.shape[0]):
            p2 = self.pts[i]
            if p2[0] < x_mean:
                x_dirs.append(p1[0] - p2[0])
                y_dirs.append(p1[1] - p2[1])
            else:
                x_dirs.append(p2[0] - p1[0])
                y_dirs.append(p2[1] - p1[1])
        
        x_dirs_mean = np.mean(x_dirs)
        y_dirs_mean = np.mean(y_dirs)
        
        one_side_of_datamean = -1 * np.array([x_dirs_mean, y_dirs_mean])
        other_side_of_datamean = np.array([x_dirs_mean, y_dirs_mean])
        
        p3 = np.array(p1) + self.length * one_side_of_datamean
        p4 = np.array(p1) + self.length * other_side_of_datamean
        
        self.line_fit = []
        self.line_fit.append(p3)
        self.line_fit.append(p4)
        print("Fit Result: (p1) {0}, (p2) {1}".format(p3, p4))
    
    # fit the line in 3 dimensions
    def line_fitter_3d(self):
        if isinstance(self.pts, np.ndarray):
            pass
        else:
            self.pts = np.asarray(self.pts)
        
        x = self.pts.T[0]
        y = self.pts.T[1]
        z = self.pts.T[2]
        
        x_mean = x.mean()
        y_mean = y.mean()
        z_mean = z.mean()
        
        x_dirs, y_dirs, z_dirs = [], [], []
        
        p1 = [x_mean, y_mean, z_mean]
        for i in range(self.pts.shape[0]):
            p2 = self.pts[i]
            if p2[0] < x_mean and p2[1] < y_mean:
                x_dirs.append(p1[0] - p2[0])
                y_dirs.append(p1[1] - p2[1])
                z_dirs.append(p1[2] - p2[2])
            else:
                x_dirs.append(p2[0] - p1[0])
                y_dirs.append(p2[1] - p1[1])
                z_dirs.append(p2[2] - p1[2])
        
        x_dirs_mean = np.mean(x_dirs)
        y_dirs_mean = np.mean(y_dirs)
        z_dirs_mean = np.mean(z_dirs)
        
        one_side_of_datamean = -1 * np.array([x_dirs_mean, y_dirs_mean, z_dirs_mean])
        other_side_of_datamean = np.array([x_dirs_mean, y_dirs_mean, z_dirs_mean])
        
        p3 = np.array(p1) + self.length * one_side_of_datamean
        p4 = np.array(p1) + self.length * other_side_of_datamean
        
        self.line_fit = []
        self.line_fit.append(p3)
        self.line_fit.append(p4)
        print("Fit Result: (p1) {0}, (p2) {1}".format(p3, p4))
    
    def FitLineToData(self):
        # if the pts object is None, generate points
        try:
            if self.pts == None:
            # generate the data according to however many dimensions specified (only 2 or 3)
                if self.fit_dimensions == 3:
                    self.generate_pts_3d()
                
                if self.fit_dimensions == 2:
                    self.generate_pts_2d()
        except ValueError:
            print("Point list is already filled out")
        
        # check if the data is a list or numpy array
        if isinstance(self.pts, np.ndarray):
            pass
        else:
            self.pts = np.asarray(self.pts)
        
        if self.debug == True:
        # create a feature array in order to see the color difference between points and the line fit
            points_feature = vtk.vtkIntArray()
            points_feature.SetName("Feature")
        
        # iterate through the length of the points in order to add to vtkPoints
            for i in range(len(self.pts)):
                if self.pts.shape[1] == 3:
                    self.points.InsertNextPoint(self.pts[i])
                    
                if self.pts.shape[1] == 2:
                    self.points.InsertNextPoint(self.pts[i][0], self.pts[i][1], 0)
                
                points_feature.InsertNextValue(0)
        
        # create vertex data for the polydata in order to save it in the append polydata list
            self.polydata.SetPoints(self.points)
            
            self.vertex_filter.SetInputData(self.polydata)
            self.vertex_filter.Update()
            self.vertex_filter.GetOutput().GetPointData().AddArray(points_feature)
            
            self.append_list.AddInputData(self.vertex_filter.GetOutput())
        
        # according to the shape of the array, fit the line accordingly
        if self.pts.shape[1] == 3:
            self.line_fitter_3d()
            
        if self.pts.shape[1] == 2:
            self.line_fitter_2d()
        
        # do the same thing for the line fit (for visualization) in order to add the line
        # source to the append polydata
        if self.debug == True:
            if self.pts.shape[1] == 3:
                self.line.SetPoint1(self.line_fit[0])
                self.line.SetPoint2(self.line_fit[1])
                
            if self.pts.shape[1] == 2:
                lf = self.line_fit
                self.line.SetPoint1(lf[0][0], lf[0][1], 0)
                self.line.SetPoint2(lf[1][0], lf[1][1], 0)
            
            self.line.Update()
            
            line_feature = vtk.vtkIntArray()
            line_feature.SetName("Feature")
            for i in range(len(self.pts)):
                line_feature.InsertNextValue(1)
            
            self.line.GetOutput().GetPointData().AddArray(line_feature)
            
            self.append_list.AddInputData(self.line.GetOutput())
            self.append_list.Update()
        
        # save the data to a polydata file
            self.WriteData("fit.vtp", self.append_list.GetOutput())
