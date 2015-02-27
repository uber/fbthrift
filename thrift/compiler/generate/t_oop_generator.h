/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements. See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership. The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License. You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied. See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */

#ifndef T_OOP_GENERATOR_H
#define T_OOP_GENERATOR_H

#include <string>
#include <iostream>

#include "thrift/compiler/globals.h"
#include "thrift/compiler/generate/t_generator.h"

#include <algorithm>

/**
 * Class with utility methods shared across common object oriented languages.
 * Specifically, most of this stuff is for C++/Java.
 *
 */
class t_oop_generator : public t_generator {
 public:
  t_oop_generator(t_program* program) :
    t_generator(program) {}

  /**
   * Scoping, using curly braces!
   */

  void scope_up(std::ostream& out) {
    indent(out) << "{" << std::endl;
    indent_up();
  }

  void scope_down(std::ostream& out, bool semicolon = false) {
    indent_down();
    indent(out) << "}";
    if (semicolon) {
       out << ";";
    }
    out << std::endl;
  }

  std::string upcase_string(std::string original) {
    std::transform(original.begin(), original.end(), original.begin(), (int(*)(int)) toupper);
    return original;
  }

  /**
   * Generates a comment about this code being autogenerated, using C++ style
   * comments, which are also fair game in Java / PHP, yay!
   *
   * @return C-style comment mentioning that this file is autogenerated.
   */
  virtual std::string autogen_comment() {
    return
      std::string("/**\n") +
      " * Autogenerated by Thrift\n" +
      " *\n" +
      " * DO NOT EDIT UNLESS YOU ARE SURE THAT YOU KNOW WHAT YOU ARE DOING\n" +
      " *  @""generated\n" +
      " */\n";
  }
};

#endif

