# Copyright (c) 2018, MD2K Center of Excellence
# - Alina Zaman <azaman@memphis.edu>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from cerebralcortex.core.data_manager.raw.stream_handler import DataSet
from cerebralcortex.cerebralcortex import CerebralCortex
from cerebralcortex.core.datatypes.datastream import DataStream
from cerebralcortex.core.datatypes.datastream import DataPoint
from datetime import datetime, timedelta
from core.computefeature import ComputeFeatureBase

import pprint as pp
import numpy as np
import pdb
import uuid
import json

feature_class_name = 'WorkingDays'


class WorkingDays(ComputeFeatureBase):
    def listing_all_work_days(self, user_id):
        work_data = []
        stream_ids = self.CC.get_stream_id(user_id, "org.md2k.data_analysis.gps_episodes_and_semantic_location")
        for stream_id in stream_ids:
            duration = self.CC.get_stream_duration(stream_id["identifier"])
            start_day = duration['start_time'].date()
            end_day = duration['end_time'].date()
            current_day = None
            while start_day < end_day:
                location_data_stream = self.CC.get_stream(stream_id["identifier"], user_id,
                                                          start_day.strftime("%Y%m%d"))
                # pp.pprint(location_data_stream.data)

                for data in location_data_stream.data:

                    if data.sample[0] != "Work":
                        continue
                    d = DataPoint(data.start_time, data.end_time, data.offset, data.sample)
                    if d.offset:
                        d.start_time += timedelta(milliseconds=d.offset)
                        if d.end_time:
                            d.end_time += timedelta(milliseconds=d.offset)
                        else:
                            continue
                    if d.start_time.date() != current_day:
                        if current_day:
                            temp = DataPoint(data.start_time, data.end_time)
                            temp.start_time = work_start_time
                            temp.end_time = work_end_time
                            temp.sample = 'office'
                            work_data.append(temp)
                        #   pdb.set_trace()
                        work_start_time = d.start_time
                        current_day = d.start_time.date()

                    work_end_time = d.end_time
                start_day += timedelta(days=1)

        try:

            if work_data:
                self.store_stream(filepath="working_days.json",
                                  input_streams=[self.CC.get_stream_id(user_id)], user_id=user_id,
                                  data=work_data)
        except Exception as e:
            print("Exception:", str(e))


    def process(self, user_id, all_days):
        if self.CC is not None:
            print("Processing Working Days")
            self.listing_all_work_days(user_id)