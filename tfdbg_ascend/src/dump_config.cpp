/* Copyright (C) 2022. Huawei Technologies Co., Ltd. All rights reserved.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
==============================================================================*/
#include <pybind11/pybind11.h>
#include <cstdint>
#include <string>
#include "tensorflow/core/platform/logging.h"
#include "dump_config.h"

namespace py = pybind11;
using namespace std;
constexpr int MAX_PATH_LEN = 256;

struct ConfigData g_dumpConfig;

class FileUtils {
public:
    static bool GetFileStat(string &path, int maxLen, struct stat *statPtr);
    static bool IsDirectory(string &path, int maxLen);
    static bool IsLinkPath(string &path, int maxLen);
    static bool IsExist(string &path, int maxLen);
    static bool IsWritable(string &path, int maxLen);
    static bool CreateCurrDir(string &path, int maxLen);
    static bool CreateDir(string &path, int maxLen);
};

bool FileUtils::GetFileStat(string &path, int maxLen, struct stat *statPtr)
{
    if (path.empty()) {
        return false;
    }
    if (path.length() > (unsigned int)maxLen) {
        return false;
    }

    (void)memset(statPtr, 0, sizeof(struct stat));
    int ret = lstat(path.c_str(), statPtr);
    if (ret < 0) {
        return false;
    }
    return true;
}

bool FileUtils::IsDirectory(string &path, int maxLen)
{
    struct stat fileStat;
    if (!GetFileStat(path, maxLen, &fileStat)) {
        return false;
    }

    if (S_ISDIR(fileStat.st_mode) == 0) {
        return false;
    }

    return true;
}

bool FileUtils::IsLinkPath(string &path, int maxLen)
{
    struct stat fileStat;
    if (!GetFileStat(path, maxLen, &fileStat)) {
        return false;
    }

    if (S_ISLNK(fileStat.st_mode) == 0) {
        return false;
    }

    return true;
}

bool FileUtils::IsExist(string &path, int maxLen)
{
    if (path.empty()) {
        return false;
    }

    if (access(path.c_str(), F_OK) == 0) {
        return true;
    }

    return false;
}

bool FileUtils::IsWritable(string &path, int maxLen)
{
    if (path.empty()) {
        return false;
    }
    if (path.length() > (unsigned int)maxLen) {
        return false;
    }

    if (access(path.c_str(), R_OK | W_OK) != 0) {
        return false;
    }

    return true;
}

bool FileUtils::CreateCurrDir(string &path, int maxLen)
{
    if (IsExist(path, maxLen)) {
        if (IsDirectory(path, maxLen) && IsWritable(path, maxLen)) {
            return true;
        } else {
            return false;
        }
    }

    if (mkdir(path.c_str(), S_IRWXU | S_IRGRP | S_IXGRP) != 0) {
        return false;
    }
    return true;
}

bool FileUtils::CreateDir(string &path, int maxLen)
{
    if (path.empty()) {
        return false;
    }

    // Check whether the path is an absolute path.
    if (path[0] != '/') {
        return false;
    }

    int lastPos = path.length() - 1;
    int lastSplitPos = 0;

	// skip the root path
    for (int i = 1; i <= lastPos; i++) {
        if (path[i] == '/') {
            lastSplitPos = i;
            path[i] = '\0';
            if (!CreateCurrDir(path, maxLen)) {
                path[i] = '/';
                return false;
            }
            path[i] = '/';
        }
    }

    if ((lastPos - lastSplitPos) > 0 && !CreateCurrDir(path, maxLen)) {
        return false;
    }

    return true;
}

class ConfigCtrl {
public:
    ConfigCtrl(int dumpSwitch, const std::string &dumpPath);
    void DumpEnable();
    void DumpDisable();
    bool GetDumpSwitch() const;
    void SetDumpPath(const std::string &dumpPath);
    string GetDumpPath() const;
    ~ConfigCtrl() {};
};

ConfigCtrl::ConfigCtrl(int dumpSwitch, const string &dumpPath)
{
    g_dumpConfig.dumpSwitch  = dumpSwitch;
    g_dumpConfig.dumpPath = dumpPath;
}

void ConfigCtrl::DumpDisable()
{
    g_dumpConfig.dumpSwitch = false;
}

void ConfigCtrl::DumpEnable()
{
    g_dumpConfig.dumpSwitch = true;
}

bool ConfigCtrl::GetDumpSwitch() const
{
    return g_dumpConfig.dumpSwitch;
}

string ConfigCtrl::GetDumpPath() const
{
    return g_dumpConfig.dumpPath;
}

void ConfigCtrl::SetDumpPath(const std::string &dumpPath)
{
    string tmpDumpPath = dumpPath;
    int dumpPathLen = dumpPath.length();

    if (FileUtils::CreateDir(tmpDumpPath, MAX_PATH_LEN)) {
        if (dumpPath[dumpPathLen - 1] != '/') {
            tmpDumpPath = dumpPath + '/';
        }
        g_dumpConfig.dumpPath = tmpDumpPath;
        if (VLOG_IS_ON(1)) {
            VLOG(1) << "Set dumpPath is:" << tmpDumpPath << endl;
        }
    } else {
        if (VLOG_IS_ON(1)) {
            VLOG(1) << "Set dumpPath failed!" << endl;
        }
    }
}

PYBIND11_MODULE(_tfdbg_ascend, m) {
    m.doc() = "tfdbg_dump config module";
    py::class_<ConfigCtrl>(m, "cfg")
        .def(py::init<int, const std::string &>())
        .def("Enable", &ConfigCtrl::DumpEnable)
        .def("Disable", &ConfigCtrl::DumpDisable)
        .def("GetDumpSwitch", &ConfigCtrl::GetDumpSwitch)
        .def("SetDumpPath", &ConfigCtrl::SetDumpPath)
        .def("GetDumpPath", &ConfigCtrl::GetDumpPath);
}
