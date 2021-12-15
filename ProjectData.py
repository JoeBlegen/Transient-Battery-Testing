import numpy as np
import matplotlib.pyplot as plt
import scipy as sp
from scipy import stats
import pandas as pd
import math
import glob
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
majorFormatter = FormatStrFormatter('%3.4f')
from statsmodels.nonparametric.smoothers_lowess import lowess

class battery_data:
    def __init__(self, file_name):
        self.file_name = file_name
        self.battery = file_name[:-4]

    def intake_data(self):
        self.temp_data = pd.read_csv(self.file_name)
        self.time = self.temp_data['Timestamp [s]']
        self.temp = self.temp_data['Battery Temperature [C]']
        self.current_time = self.temp_data['Timestamp Current']
        self.current = self.temp_data['Current']

    def internal_resistance(self):
        self.battery_ir = []
        if self.battery == 'VTC5':
            self.battery_ir.append(irData(37.056, 1.0857, 80))
            self.battery_ir.append(irData(35.945, 1.6357, 30))
            self.battery_ir.append(irData(47.649, 5.5634, 8))
        elif self.battery == '25R':
            self.battery_ir.append(irData(52.833, 0.5904, 85))
            self.battery_ir.append(irData(53.597, 1.2507, 20))
            self.battery_ir.append(irData(72.811, 5.5059, 5))
        elif self.battery == 'HE2':
            self.battery_ir.append(irData(58.082, 2.9296, 80))
            self.battery_ir.append(irData(59.600, 0.7410, 40))
            self.battery_ir.append(irData(75.342, 6.5408, 5))
        elif self.battery == 'VTC6':
            self.battery_ir.append(irData(41.275, 1.2114, 80))
            self.battery_ir.append(irData(38.924, 0.7398, 45))
            self.battery_ir.append(irData(48.534, 5.1649, 5))

    def specific_heat_intial(self):
        # Values calculated in excel
        if self.battery == 'VTC5':
            self.specific_heat = 3.93
            self.average_curr = 5.26
            self.delt = 4.6
        elif self.battery == '25R':
            self.specific_heat = 4.01
            self.average_curr = 5.196
            self.delt = 6.33
        elif self.battery == 'HE2':
            self.specific_heat = 4.75
            self.average_curr = 4.91
            self.delt = 9.1
        elif self.battery == 'VTC6':
            self.specific_heat = 4.94
            self.average_curr = 5.31
            self.delt = 4.2


    def smooth_data(self):
        filtered = lowess(self.temp, self.time, is_sorted=True, frac=0.025, it=0)
        # filtered = lowess(temp, time, is_sorted=True, frac=0.01, it=0)
        return filtered[:,0], filtered[:,1]

    def specific_heat_uncert(self):
        curr_uncert = 0.00976
        temp_uncert = 2
        res_uncert = self.battery_ir[0].std
        res = self.battery_ir[0].res

        self.Cp_uncert = math.sqrt(((2*curr_uncert/self.average_curr)**2)+((res_uncert/res)**2)+((temp_uncert/self.delt)**2))



    def plot_ir_helper(self):
        #Need to pass all data out of class
        return self.battery_ir

    def plot_temp_data(self):
        fig = plt.figure()
        ax=fig.add_subplot(111)
        for axis in ['top','bottom','left','right']:
           ax.spines[axis].set_linewidth(2)
        ax.tick_params(direction='in', length=6, width=2, colors='k')
        ax.tick_params(labelcolor='k', labelsize=14)
        plt.plot(self.time,self.temp,'r')
        filt_time, filt_temp = self.smooth_data()
        plt.plot(filt_time,filt_temp,'b')
        # m, b, R, p ,sem = sp.stats.linregress(self.time,self.temp)
        # y_fit = m*self.time + b
        # plt.plot(self.time,y_fit,'b')
        plt.xlabel('Time (Sec)',fontsize=14)
        plt.ylabel('Temperature (C)',fontsize=14)
        plt.title("Temperature of Battery Through Discharge - " + self.battery, fontsize = 14)
        plt.grid()
        plt.legend(loc='upper left')
        plt.show()

class irData:
    def __init__(self, res, std, soc):
        self.soc = soc
        self.res = res
        self.std = std

def plot_ir_data(ir_list):
    fig = plt.figure()
    ax=fig.add_subplot(111)
    for axis in ['top','bottom','left','right']:
       ax.spines[axis].set_linewidth(2)
    ax.tick_params(direction='in', length=6, width=2, colors='k')
    ax.tick_params(labelcolor='k', labelsize=14)

    vtc5_points = []
    vtc6_points = []
    he2_points = []
    r25_points = []

    for irs in ir_list:
        for ir in irs[1]:
            if irs[0] == "VTC5":
                vtc5_points.append([ir.soc,ir.res,ir.std,irs[0]])
            elif irs[0] == "VTC6":
                vtc6_points.append([ir.soc,ir.res,ir.std,irs[0]])
            elif irs[0] == "HE2":
                he2_points.append([ir.soc,ir.res,ir.std,irs[0]])
            elif irs[0] == "25R":
                r25_points.append([ir.soc,ir.res,ir.std,irs[0]])

    vtc5_points = np.asarray(vtc5_points)
    vtc6_points = np.asarray(vtc6_points)
    he2_points = np.asarray(he2_points)
    r25_points = np.asarray(r25_points)

    # print(he2_points[:,0])

    plt.plot(vtc5_points[:,0].astype(float),vtc5_points[:,1].astype(float),'--ro',label=vtc5_points[0][3])
    plt.errorbar(vtc5_points[:,0].astype(float),vtc5_points[:,1].astype(float),vtc5_points[:,2].astype(float),fmt='.',color='r')
    plt.plot(vtc6_points[:,0].astype(float),vtc6_points[:,1].astype(float),'--bo',label=vtc6_points[0][3])
    plt.errorbar(vtc6_points[:,0].astype(float),vtc6_points[:,1].astype(float),vtc6_points[:,2].astype(float),fmt='.',color='b')
    plt.plot(he2_points[:,0].astype(float),he2_points[:,1].astype(float),'--go',label=he2_points[0][3])
    plt.errorbar(he2_points[:,0].astype(float),he2_points[:,1].astype(float),he2_points[:,2].astype(float),fmt='.',color='g')
    plt.plot(r25_points[:,0].astype(float),r25_points[:,1].astype(float),'--ko',label=r25_points[0][3])
    plt.errorbar(r25_points[:,0].astype(float),r25_points[:,1].astype(float),r25_points[:,2].astype(float),fmt='.',color='k')

    plt.xlabel('Depth of Discharge',fontsize=14)
    plt.ylabel(u'Internal Resistance (mΩ)',fontsize=14)
    plt.title("Internal Resistances of Batteries Through Discharge", fontsize = 14)
    plt.grid()
    plt.gca().invert_xaxis()
    plt.xlim(100,0)
    plt.legend(loc='upper left')
    plt.show()

if __name__ == '__main__':
    data = ['25R.csv','HE2.csv','VTC5.csv','VTC6.csv']
    bat_list = []
    ir_list = []

    for readings in data:
        bat_list.append(battery_data(readings))

    for battery in bat_list:
        battery.intake_data()
        battery.internal_resistance()
        ir_list.append([battery.battery, battery.plot_ir_helper()])
        battery.specific_heat_intial()
        battery.specific_heat_uncert()
        print(battery.battery,battery.Cp_uncert)
        # battery.plot_temp_data()

    # plot_ir_data(ir_list)
