//main.cpp
/**
* @file main.cpp
*
* Copyright (C) 2020. Huawei Technologies Co., Ltd. All rights reserved.
*
* This program is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
*/
#include "sample_process.h"
#include "utils.h"
#include<getopt.h>
using namespace std;
 

bool f_isTXT = false;
bool g_isDevice = false;
int loop = 1;
string input_Ftype = ".bin";
string model_Ftype = ".om";
string check = "";
 
 
void InitAndCheckParams(int argc, char* argv[], vector<string>& params, vector<string>& inputs)
{
    
    const char *optstring="m::i::o::f::hd::p::l::y::";
    int c,deb,index;
    struct option opts[]={{"model",required_argument,NULL,'m'},
                          {"input",required_argument,NULL,'i'},
                          {"output",required_argument,NULL,'o'},
                          {"outfmt",required_argument,NULL,'f'},
                          {"help",no_argument,NULL,1},
                          {"dumpConf",required_argument,NULL,'d'},
                          {"profConf",required_argument,NULL,'p'},        
                          {"loop",required_argument,NULL,'l'},
                          {"dymBatch",required_argument,NULL,'y'},                                                      
                          {0,0,0,0}};
    while((c=getopt_long(argc,argv,optstring,opts,&index))!=-1)
    {
       
        switch(c)
        {
        case 'm':
			check = optarg;
			if (check.find(model_Ftype) != string::npos){
				params.push_back(optarg);
				break;
			}
			else {
				printf("input model file type is not .om , please check your model type!\n");
				exit(0);
			}
        case 'i':
			check = optarg;
			if (check.find(input_Ftype) == string::npos){
				printf("input data file type is not .bin , please check your input file type!\n");
				exit(0);
			}
            params.push_back(optarg);
            Utils::SplitString(params[1], inputs, ',');
            break;
        case 'o':
            params.push_back(optarg);
            break;
        case 'f':
            params.push_back(optarg);
            break;
        case '?':
            printf("unknown paramenter\n");
            printf("Execute sample failed.\n");
            exit(0);
        case 'd':
			params.push_back(optarg);
            break;
        case 'p':
            params.push_back(optarg);
            break;
        case 'l':
            loop = Utils::str2num(optarg);
	    cout << "loop:" << loop << endl;
			if (loop > 100 || loop < 1)
			{
				printf("loop must in 1 to 100\n");
				exit(0);	
			} 
            break;
        case 'y':
            params.push_back(optarg);
            break;
        case 1:
            Utils::printHelpLetter();
            exit(0);
        default:
            printf("unknown paramenter\n");
            printf("Execute sample failed.\n");
            exit(0);
        }
    }
}

int main(int argc, char* argv[])
{
    vector<string> params;
    vector<string> inputs;
    InitAndCheckParams(argc, argv, params, inputs);
    printf("******************************\n");
    printf("Test Start!\n");
 

    if (params.empty() || inputs.empty()) {
        printf("Invalid params.\n");
        printf("Execute sample failed.\n");
        return FAILED;
    }
    
    SampleProcess processSample;
   
    Result ret = processSample.InitResource();
    if (ret != SUCCESS) {
        ERROR_LOG("Sample init resource failed.");
        return FAILED;
    }

    ret = processSample.Process(params, inputs);
    if (ret != SUCCESS) {
        ERROR_LOG("Sample process failed.");
        return FAILED;
    }

    INFO_LOG("Execute sample success.");
    printf("Test Finish!\n");
    printf("******************************\n");
   
    return SUCCESS;
}
