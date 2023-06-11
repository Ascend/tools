/*
 * Copyright(C) 2021. Huawei Technologies Co.,Ltd. All rights reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
#ifndef TENSOR_SHAPE_H
#define TENSOR_SHAPE_H

namespace Base {

class TensorShape
{
public:
    TensorShape() = default;
    ~TensorShape() = default;

    template <typename T>
    TensorShape(std::vector<T> shape)
    {
        shape_.clear();
        for(auto s:shape) {
            shape_.push_back((size_t)s);
        }
    }

    uint32_t GetDims() const
    {
        return shape_.size();
    }

    void SetShape(std::vector<size_t> shape)
    {
        shape_ = shape;
    }

    std::vector<uint32_t> GetShape() const
    {
        std::vector<uint32_t> shape = {};
        for (auto s : shape_) {
            shape.push_back((uint32_t)s);
        }
        return shape;
    }

    uint32_t GetSize() const
    {
        size_t size = 1;
        for (auto s : shape_) {
            size *= s;
        }
        return size;
    }

    size_t operator[] (uint32_t idx) const
    {
        return shape_[idx];
    }

    size_t &operator[] (uint32_t idx)
    {
        return shape_[idx];
    }

private:
    std::vector<size_t> shape_ = {};
};
}

#endif