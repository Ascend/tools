
#ifndef _SESSION_OPTIONS_H
#define _SESSION_OPTIONS_H

#include "Base/ModelInfer/utils.h"

namespace Base {

class SessionOptions{
public:

    int log_level = LOG_INFO_LEVEL;
    int loop = 1;
    std::string aclJsonPath = "";
};
}
#endif