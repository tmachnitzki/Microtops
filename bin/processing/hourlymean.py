#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 30 08:47:23 2019

@author: julia
"""
import pandas as pd
import read_save_csv as rs_csv

def hourlymean(data):
    # make column selection
    cols = ["latitude", "longitude", "altitude", "pressure", "sza", "am", "sdcorr",
            "temp", "id", "aot380", "aot440", "aot675", "aot870", "aot936", "water"]
    data = data[cols]
    
    # setting timedeltas
    week = pd.Timedelta("7Day")
    threemins = pd.Timedelta("3Min")
    twomins = pd.Timedelta("2Min")
    
    # check for single measurements and delete them
    diff1 = abs(data.index[1:] - data.index[:-1])
    diff2 = abs(data.index[:-1] - data.index[1:])
    data = data.assign(timediff1=pd.TimedeltaIndex([threemins]).append(diff1))
    data = data.assign(timediff2=diff2.append(pd.TimedeltaIndex([twomins])))
    data = data[(data["timediff1"] < week) & (data["timediff2"] < week)]
    
    # mask starting points of measurement blocks
    diff1 = abs(data.index[1:] - data.index[:-1])
    data = data.assign(timediff1=pd.TimedeltaIndex([threemins]).append(diff1))
    masked = data[(data["timediff1"] > twomins)]
    
    # loop through starting points
    df_min = pd.DataFrame()
    for ix in range(0,len(masked)):
        r1 = data.index.get_loc(masked.index[ix])
        try:
            r2 = data.index.get_loc(masked.index[ix + 1])
            df = data.iloc[r1:r2]
        except IndexError:
            df = data.iloc[r1:]
        if len(df) < 5:
            continue
        temp_min = pd.DataFrame(df.loc[df.aot936.idxmin()]).T
        df_min = pd.concat([df_min, temp_min])
    
    df_min = df_min.drop(["timediff1", "timediff2"], axis=1)
    df_min = df_min.astype(float)
    
    # calculate hourly mean values
    sampled = df_min.resample("H")
    df_mean = sampled.mean().round(3).dropna(how="all")
    df_mean = df_mean.assign(size=sampled.size())
    
    return df_mean

path = "/Users/julia/Documents/MPI_Sonne/microtops/data/"
readfile = "20190530c.txt"
savefile = "20190530c_hourlymean.txt"
data = rs_csv.read_data(path, readfile)
data_mean = hourlymean(data)
rs_csv.save_data(path, savefile, data_mean)
