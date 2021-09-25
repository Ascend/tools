/**
* Copyright 2020 Huawei Technologies Co., Ltd
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at

* http://www.apache.org/licenses/LICENSE-2.0

* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/

#include "sample_process.h"
#include "utils.h"
#include <getopt.h>
using namespace std;

bool g_is_txt = false;
bool g_is_device = false;
int g_loop = 1;
int32_t g_device_id = 0;
bool g_is_profi = false;
bool g_is_dump = false;
bool g_is_debug = false;
bool g_is_dymdims = false;
bool g_is_dymShape = false;
bool g_is_dymHW = false;
bool g_is_dymbatch = false;
size_t g_dymindex = -1;
size_t g_dym_gear_count = 0;
uint64_t g_dymbatch_size = 0;
pair<uint64_t, uint64_t> g_dynamicHW;
vector<int> g_output_size;

void InitAndCheckParams(int argc, char* argv[], map<char, string>& params, vector<string>& inputs)
{
    const char* optstring = "m::i::o::f::hd::p::l::y::e::g::";
    string model_file_type = ".om";
    string check = "";
    int c = -1;
    int index = 0;
    vector<string> hw;
    vector<string> outputsize_str;
    struct option opts[] = { { "model", required_argument, NULL, 'm' },
        { "input", required_argument, NULL, 'i' },
        { "output", required_argument, NULL, 'o' },
        { "outfmt", required_argument, NULL, 'f' },
        { "help", no_argument, NULL, 1 },
        { "dump", required_argument, NULL, 'd' },
        { "profiler", required_argument, NULL, 'p' },
        { "loop", required_argument, NULL, 'l' },
        { "dymBatch", required_argument, NULL, 'y' },
        { "dymDims", required_argument, NULL, 'h' },
        { "dymHW", required_argument, NULL, 'w' },
        { "dymShape", required_argument, NULL, 's' },
        { "device", required_argument, NULL, 'e' },
        { "outputSize", required_argument, NULL, 't' },
        { "debug", required_argument, NULL, 'g' }};
    while ((c = getopt_long(argc, argv, optstring, opts, &index)) != -1) {
        switch (c) {
        case 'm':
            check = optarg;
            if (check.find(model_file_type) != string::npos) {
                params['m'] = optarg;
                break;
            } else {
                ERROR_LOG("input model file type is not .om , please check your model type!\n");
                exit(0);
            }
        case 'i':
            check = optarg;
            params['i'] = optarg;
            Utils::SplitString(params['i'], inputs, ',');
            break;
        case 'o':
            params['o'] = optarg;
            break;
        case 'f':
            params['f'] = optarg;
            break;
        case '?':
            ERROR_LOG("unknown paramenter\n");
            ERROR_LOG("Execute sample failed\n");
            Utils::printHelpLetter();
            exit(0);
        case 'd':
            params['d'] = optarg;
            break;
        case 'p':
            params['p'] = optarg;
            break;
        case 'l':
            g_loop = Utils::str2num(optarg);
            if (g_loop > 100 || g_loop < 1) {
                ERROR_LOG("loop must in 1 to 100\n");
                exit(0);
            }
            break;
        case 'y':
            g_dymbatch_size = Utils::str2num(optarg);
            if (g_dymbatch_size > 2048 || g_loop < 1) {
                ERROR_LOG("dymBatch must in 1 to 2048\n");
                exit(0);
            }
            params['y'] = optarg;
            break;
        case 'e':
            g_device_id = Utils::str2num(optarg);
            if (g_device_id > 255 || g_device_id < 0) {
                ERROR_LOG("device id must in 0 to 255\n");
                exit(0);
            }
            break;
        case 'g':
            params['g'] = optarg;
            break;
        case 'w':
            params['w'] = optarg;
            Utils::SplitStringWithPunctuation(params['w'], hw, ',');
            if (hw.size() != 2) {
                ERROR_LOG("input dynamiHW size error , this lens must be 2 , you input size = %d", static_cast <int> (hw.size()));
            }
            g_dynamicHW = {atoi(hw[0].c_str()), atoi(hw[1].c_str())};         
            break;
        case 'h':
            params['h'] = optarg;

            break;
        case 's':
            params['s'] = optarg;
            break;
        case 't':
            params['t'] = optarg;
            Utils::SplitStringWithPunctuation(params['t'], outputsize_str, ',');
            transform( outputsize_str.begin(), outputsize_str.end(), back_inserter(g_output_size), Utils::ToInt);
            break;
        case 1:
            Utils::printHelpLetter();
            exit(0);
        default:
            ERROR_LOG("unknown paramenter\n");
            ERROR_LOG("Execute sample failed\n");
            Utils::printHelpLetter();
            exit(0);
        }
    }
}

int main(int argc, char* argv[])
{
    map<char, string> params;
    vector<string> inputs;
    InitAndCheckParams(argc, argv, params, inputs);

    if (params.empty()) {
        ERROR_LOG("Invalid params\n");
        ERROR_LOG("Execute sample failed\n");
        Utils::printHelpLetter();
        return FAILED;
    }

    if (params['d'].compare("true") == 0) {
        g_is_dump = true;
    }
    if (params['p'].compare("true") == 0) {
        g_is_profi = true;
    }
    if (params['g'].compare("true") == 0) {
        g_is_debug = true;
    }
    if (g_is_profi && g_is_dump) {
        ERROR_LOG("dump and profiler can not both be true");
        return FAILED;
    }
    if (params.count('h') + params.count('y') + params.count('w') + params.count('s') > 1){
        ERROR_LOG("dymBatch dymDims dymHW dymShape cannot be set at the same time");
        return FAILED;
    }

    Utils::ProfilerJson(g_is_profi, params);
    Utils::DumpJson(g_is_dump, params);

    SampleProcess processSample;

    Result ret = processSample.InitResource();
    if (ret != SUCCESS) {
        ERROR_LOG("Sample init resource failed");
        return FAILED;
    }

    ret = processSample.Process(params, inputs);
    if (ret != SUCCESS) {
        ERROR_LOG("Sample process failed");
        return FAILED;
    }

    INFO_LOG("Execute sample success");

    return SUCCESS;
}
