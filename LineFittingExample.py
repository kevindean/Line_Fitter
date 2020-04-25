import os
import numpy as np
import vtk

DEBUG = True # if Debug mode true, it will output a polydata file that
             # may be visualized in ParaView (Kitware)
points = None
polydata = None
vertex_filter = None
append_list = None

def generate_pts_2d(limit=10000):
    x = np.random.rand(1)[0]
    y = np.random.rand(1)[0]
    
    for i in range(limit):
        yield x, y
        x = np.random.rand(1)[0] + np.random.randint(0, 100) + i
        y = np.random.rand(1)[0] + np.random.randint(0, 100) + i

def generate_pts_3d(limit=10000):
    x = np.random.rand(1)[0]
    y = np.random.rand(1)[0]
    z = np.random.rand(1)[0]
    
    for i in range(limit):
        yield x, y, z
        x = np.random.rand(1)[0] + np.random.randint(0, 100) + i
        y = np.random.rand(1)[0] + np.random.randint(0, 100) + i
        z = np.random.rand(1)[0] + np.random.randint(0, 100) + i

def line_fitter_2d(pts, length=3):
    x = pts.T[0]
    y = pts.T[1]
    
    x_mean = x.mean()
    y_mean = y.mean()
    
    x_dirs, y_dirs = [], []
    
    p1 = [x_mean, y_mean]
    for i in range(pts.shape[0]):
        p2 = pts[i]
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
    
    p3 = np.array(p1) + length * one_side_of_datamean
    p4 = np.array(p1) + length * other_side_of_datamean
    
    line_fit = []
    line_fit.append(p3)
    line_fit.append(p4)
    print("Fit Result: (p1) {0}, (p2) {1}".format(p3, p4))
    
    return line_fit

# input -> pts is a numpy array
def line_fitter_3d(pts, length=3):
    x = pts.T[0]
    y = pts.T[1]
    z = pts.T[2]
    
    x_mean = x.mean()
    y_mean = y.mean()
    z_mean = z.mean()
    
    x_dirs, y_dirs, z_dirs = [], [], []
    
    p1 = [x_mean, y_mean, z_mean]
    for i in range(pts.shape[0]):
        p2 = pts[i]
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
    
    p3 = np.array(p1) + length * one_side_of_datamean
    p4 = np.array(p1) + length * other_side_of_datamean
    
    line_fit = []
    line_fit.append(p3)
    line_fit.append(p4)
    print("Fit Result: (p1) {0}, (p2) {1}".format(p3, p4))
    
    return line_fit
    

# EXAMPLE EXECUTION for 3D POINTS
if DEBUG == True:
    points = vtk.vtkPoints()
    polydata = vtk.vtkPolyData()
    vertex_filter = vtk.vtkVertexGlyphFilter()
    append_list = vtk.vtkAppendPolyData()

pts = []
for i in generate_pts_3d():
    pts.append(i)
    
    if DEBUG == True:
        points.InsertNextPoint(i)

if DEBUG == True:
    polydata.SetPoints(points)
    vertex_filter.SetInputData(polydata)
    vertex_filter.Update()
    
    points_feature = vtk.vtkIntArray()
    points_feature.SetName("Feature")
    for i in range(len(pts)):
        points_feature.InsertNextValue(0)
    
    vertex_filter.GetOutput().GetPointData().AddArray(points_feature)
    
    append_list.AddInputData(vertex_filter.GetOutput())

%time fit = line_fitter_3d(np.asarray(pts))

if DEBUG == True:
    line = vtk.vtkLineSource()
    line.SetPoint1(fit[0])
    line.SetPoint2(fit[1])
    line.Update()
    
    line_feature = vtk.vtkIntArray()
    line_feature.SetName("Feature")
    for i in range(len(pts)):
        line_feature.InsertNextValue(1)
    
    line.GetOutput().GetPointData().AddArray(line_feature)
    
    append_list.AddInputData(line.GetOutput())
    append_list.Update()
    
    WriteData(os.getenv("HOME") + "/fit.vtp", append_list.GetOutput())
    

