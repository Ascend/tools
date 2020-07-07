//Util.cpp
 
/**
* @file utils.cpp
*
* Copyright (C) 2020. Huawei Technologies Co., Ltd. All rights reserved.
*
* This program is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
*/
#include "utils.h"
#include <sys/time.h>
#include "acl/acl.h"
using namespace std;
extern bool g_isDevice;
extern bool f_isTXT;
 
void* Utils::ReadBinFile(std::string fileName, uint32_t &fileSize)
{
    std::ifstream binFile(fileName, std::ifstream::binary);
    if (binFile.is_open() == false) {
        ERROR_LOG("open file %s failed", fileName.c_str());
        return nullptr;
    }
 
    binFile.seekg(0, binFile.end);
    uint32_t binFileBufferLen = binFile.tellg();
    if (binFileBufferLen == 0) {
        ERROR_LOG("binfile is empty, filename is %s", fileName.c_str());
        binFile.close();
        return nullptr;
    }
 
    binFile.seekg(0, binFile.beg);
 
    void* binFileBufferData = nullptr;
    aclError ret = ACL_ERROR_NONE;
    if (!g_isDevice) {
        ret = aclrtMallocHost(&binFileBufferData, binFileBufferLen);
        if (binFileBufferData == nullptr) {
            ERROR_LOG("malloc binFileBufferData failed");
            binFile.close();
            return nullptr;
        }
    } else {
        ret = aclrtMalloc(&binFileBufferData, binFileBufferLen, ACL_MEM_MALLOC_NORMAL_ONLY);
        if (ret != ACL_ERROR_NONE) {
            ERROR_LOG("malloc device buffer failed. size is %u", binFileBufferLen);
            binFile.close();
            return nullptr;
        }
    }
		
    binFile.read(static_cast<char *>(binFileBufferData), binFileBufferLen);
    binFile.close();
    fileSize = binFileBufferLen;
    return binFileBufferData;
}
 
void* Utils::GetDeviceBufferOfFile(std::string fileName, uint32_t &fileSize)
{
    uint32_t inputHostBuffSize = 0;
    void* inputHostBuff = Utils::ReadBinFile(fileName, inputHostBuffSize);
    if (inputHostBuff == nullptr) {
        return nullptr;
    }
    if (!g_isDevice) {
        void *inBufferDev = nullptr;
        uint32_t inBufferSize = inputHostBuffSize;
        aclError ret = aclrtMalloc(&inBufferDev, inBufferSize, ACL_MEM_MALLOC_NORMAL_ONLY);
        if (ret != ACL_ERROR_NONE) {
            ERROR_LOG("malloc device buffer failed. size is %u", inBufferSize);
            aclrtFreeHost(inputHostBuff);
            return nullptr;
        }
 
        ret = aclrtMemcpy(inBufferDev, inBufferSize, inputHostBuff, inputHostBuffSize, ACL_MEMCPY_HOST_TO_DEVICE);
        if (ret != ACL_ERROR_NONE) {
            ERROR_LOG("memcpy failed. device buffer size is %u, input host buffer size is %u",
                inBufferSize, inputHostBuffSize);
            aclrtFree(inBufferDev);
            aclrtFreeHost(inputHostBuff);
            return nullptr;
        }
        aclrtFreeHost(inputHostBuff);
        fileSize = inBufferSize;
        return inBufferDev;
    } else {
        fileSize = inputHostBuffSize;
        return inputHostBuff;
    }
}
 
void Utils::SplitString(std::string& s, std::vector<std::string>& v, char c)
{
  std::string::size_type pos1, pos2;
  pos2 = s.find(c);
  pos1 = 0;
  while(std::string::npos != pos2)
  {
    v.push_back(s.substr(pos1, pos2-pos1));
    pos1 = pos2 + 1;
    pos2 = s.find(c, pos1);
  }
  if(pos1 != s.length())
    v.push_back(s.substr(pos1));
}
 
int Utils::str2num(char *str)
{
    int n = 0;
    int flag = 0;
    while(*str >= '0' && *str <= '9')
    {
        n = n*10 + (*str - '0');
        str++;
    }
    if(flag == 1)
    {
        n = -n;
    }
    return n;
}

std::string Utils::modelName(string& s)
{
	string::size_type position1,position2;
	position1 = s.find_last_of("/");
	if (position1 == s.npos)
	{
		position1 = 0;
	}
	position2 = s.find_last_of(".");
	std::string modelName = s.substr(position1,position2-position1);
	return modelName;
}

std::string  Utils::TimeLine()
{
	time_t currentTime = time(NULL);
	char chCurrentTime[64];
	strftime(chCurrentTime, sizeof(chCurrentTime), "%Y%m%d_%H%M%S", localtime(&currentTime)); 
	std::string stCurrentTime = chCurrentTime;
	return stCurrentTime;
}

void Utils::printCurrentTime()
{
    char szBuf[256] = {0};
    struct timeval    tv;
    struct timezone   tz;
    struct tm         *p;

    gettimeofday(&tv, &tz);
    p = localtime(&tv.tv_sec);
    printf("%02d-%02d-%02d %02d:%02d:%02d.%06ld\n", p->tm_year + 1900, p->tm_mon + 1, p->tm_mday, p->tm_hour, p->tm_min, p->tm_sec, tv.tv_usec);

}
void Utils::printHelpLetter()
{
	cout<< "generate offline model inference output file example:" << endl;
	cout<< "./amexec --model /home/HwHiAiUser/ljj/colorization.om --input /home/HwHiAiUser/ljj/colorization_input.bin --output /home/HwHiAiUser/ljj/AMEXEC/out/output1 --outfmt TXT --loop 2" << endl << endl;

	cout<< "arguments explain:" << endl;
	cout<< "  --model       Model file path" << endl;
	cout<< "  --input	Input data path(only accept binary data file) 	If there are several file, please seprate by ','" << endl;
	cout<< "  --output	Output path(User needs to have permission to create directories)" <<  endl;
	cout<< "  --outfmt	Output file format (TXT or BIN)" << endl;
	cout<< "  --loop 	loop time(must in 1 to 100)" << endl;
	cout<< "  --dumpConf	dump configure file path (Do not support now)" << endl;
	cout<< "  --profConf	profiling configure file path (Do not support now)" << endl;
	cout<< "  --dymBatch 	dynamic batch (Do not support now)" << endl << endl << endl;
	  
	  
	cout<< "NOTECE: " << endl;
	cout<< "	The order of parameter must follow in --model --input --output --outfmt --loop " << endl;
}

double Utils::printDiffTime(time_t begin, time_t end)
{
    double diffT = difftime(begin, end);
    printf("The inference time is: %f millisecond\n", 1000*diffT);
    return diffT * 1000;
}

double Utils::InferenceTimeAverage(double *x, int len)
{
    double sum = 0;
    for (int i = 0; i < len; i++)
        sum += x[i];
    return sum / len;
}

double Utils::InferenceTimeAverageWithoutFirst(double *x, int len)
{
    double sum = 0;
    for (int i = 0; i < len; i++)
		if (i !=0){
		    sum += x[i];
		}
        
    return sum / (len - 1);
}
