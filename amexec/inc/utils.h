//Util.h
 
/**
* @file utils.h
*
* Copyright (C) 2020. Huawei Technologies Co., Ltd. All rights reserved.
*
* This program is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
*/
#pragma once
#include <iostream>
#include <sstream>
#include <fstream>
#include <cstring>
#include <string>
#include <map>
#include <vector>
#include <algorithm>
#include <stdio.h>
#include <time.h>
#include <sys/time.h>
 
#define INFO_LOG(fmt, args...) fprintf(stdout, "[INFO] " fmt "\n", ##args)
#define WARN_LOG(fmt, args...) fprintf(stdout, "[WARN] " fmt "\n", ##args)
#define ERROR_LOG(fmt, args...) fprintf(stdout, "[ERROR] " fmt "\n", ##args)
 
using namespace std;
//static size_t loop = 1;
typedef enum Result {
    SUCCESS = 0,
    FAILED = 1
} Result;

 
/**
* Utils
*/
class Utils {
public:
    /**
    * @brief create device buffer of file
    * @param [in] fileName: file name
    * @param [out] fileSize: size of file
    * @return device buffer of file
    */
    static void *GetDeviceBufferOfFile(std::string fileName, uint32_t &fileSize);
 
    /**
    * @brief create buffer of file
    * @param [in] fileName: file name
    * @param [out] fileSize: size of file
    * @return buffer of pic
    */
    static void* ReadBinFile(std::string fileName, uint32_t& fileSize);
 
    static void SplitString(std::string& s, std::vector<std::string>& v, char c);
        
    static int str2num(char *str);
	
	static std::string modelName(string& s);
	
	static std::string TimeLine();
	
	static void printCurrentTime();
	
	static void printHelpLetter();	

    static double printDiffTime(time_t begin, time_t end);
	
    static double InferenceTimeAverage(double *x, int len);
	
	static double InferenceTimeAverageWithoutFirst(double *x, int len);
};
 
#pragma once
