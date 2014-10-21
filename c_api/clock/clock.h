/* Copyright 2012-2014 Gilbert Romer */

/* This file is part of gmidilooper. */

/* gmidilooper is free software: you can redistribute it and/or modify */
/* it under the terms of the GNU General Public License as published by */
/* the Free Software Foundation, either version 3 of the License, or */
/* (at your option) any later version. */

/* gmidilooper is distributed in the hope that it will be useful, */
/* but WITHOUT ANY WARRANTY; without even the implied warranty of */
/* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the */
/* GNU General Public License for more details. */

/* You should have received a copy of the GNU General Public License */
/* along with gmidilooper.  If not, see <http://www.gnu.org/licenses/>. */


#ifndef CLOCK_H
#define CLOCK_H

#include <time.h>
#include "tool/tool.h"

typedef struct
{
  struct timespec time;
  uint_t    number;
} clocktick_t;

typedef enum
  {
    CONTINUE = 0,
    STOP
  } clock_req_t;

typedef clock_req_t (*clockloop_cb)(void *arg);

typedef struct
{
  clocktick_t     clocktick;
  clockloop_cb    cb_func;
  void            *cb_arg;
  struct timespec res;
} clockloop_t;

bool_t clockloop(clockloop_t *looph);

void free_clockloop_struct(clockloop_t *clockloop);
void set_bpmnppq_to_timespec(struct timespec *res, uint_t ppq, uint_t bpm);
void set_msnppq_to_timespec(struct timespec *res, uint_t ppq, uint_t ms);
void set_clockloop_bpm_ppq(clockloop_t *clockloop,
                           uint_t bpm,
                           uint_t ppq,
                           clockloop_cb cb_func,
                           void *cb_arg);
void set_clockloop_ms_ppq(clockloop_t *clockloop,
                          uint_t ms,
                          uint_t ppq,
                          clockloop_cb cb_func,
                          void *cb_arg);

#endif
