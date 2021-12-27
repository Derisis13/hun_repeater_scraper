#!/usr/bin/python

# Copyright [2021] [László Párkányi]
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pandas as pd


def is_tone(ctcss_freqs):
    rtonefreq = ctcss_freqs.partition("/")[0]
    ctonefreq = ctcss_freqs.partition("/")[2]

    if ctonefreq == "--" and rtonefreq == "--":
        return "", "88.5", "88.5"
    else:
        if rtonefreq == "--":
            rtonefreq = "88.5"
        if ctonefreq == "--":
            ctonefreq = "88.5"
        return "Tone", rtonefreq, ctonefreq


def calculate_ctcss(repeaters):
    Tones, cToneFreqs, rToneFreqs = [], [], []
    for i in repeaters.Ctone:
        Tone, cToneFreq, rToneFreq = is_tone(i)
        Tones.append(Tone)
        cToneFreqs.append(cToneFreq)
        rToneFreqs.append(rToneFreq)
    repeaters["Tone"] = Tones
    repeaters["rToneFreq"] = rToneFreqs
    repeaters["cToneFreq"] = cToneFreqs
    repeaters = repeaters.drop(["Ctone"], axis=1)
    return repeaters


def trunc_mode(repeaters):
    modes = []
    for i in repeaters.Mode:
        modes.append(i.partition("/")[0])
    return modes


def get_repeaters(link):
    repeaters = pd.read_html(link, encoding='utf8', match='Echolink')[0]
    repeaters = (repeaters[~repeaters.Állapot.str.contains("inaktív")])  # sorting out inactive repeaters
    repeaters = repeaters.drop(["Csat.új", "Csat.régi", "Echolink", "QTH Lokátor",
                                "ASL", "Állapot"], axis=1)  # letting go of unnecessary columns
    repeaters = repeaters.rename({"Hívójel": "Name", "QTH/Név": "Comment", "Felmenő[kHz]": "Frequency",
                                  "Elt.[kHz]": "Offset", "Üzemmód": "Mode", "CTCSSDL/UL [Hz]": "Ctone",
                                  "Lejövő [kHz]": "Downlink"}, axis=1)

    repeaters = calculate_ctcss(repeaters)

    repeaters["Offset"] = (repeaters.Downlink - repeaters.Frequency) / 1000
    repeaters = repeaters.drop(["Downlink"], axis=1)

    repeaters["Mode"] = trunc_mode(repeaters)

    repeaters["Duplex"] = '-'
    repeaters["DtcsCode"] = '023'
    repeaters["DtcsPolarity"] = 'NN'
    repeaters["TStep"] = '5.00'
    repeaters["Skip"] = ''
    repeaters["URCALL"] = ''
    repeaters["RPT1CALL"] = ''
    repeaters["RPT2CALL"] = ''
    repeaters["DVCODE"] = ''

    # repeaters = repeaters.rename(dict(zip(repeaters.index, range(4, repeaters.shape[0] + 5))))
    return repeaters


def generate_csv(repeaters):
    for r in repeaters:
        print(r)


if __name__ == '__main__':
    repeatercsv = open("repeater.csv", "w+")
    call_dataframe = pd.DataFrame({"Name": ["2M CALL", "2M SSTV", "70CM CALL", "70CM SSTV"],
                                   "Frequency": ["145.500000", "144.500000", "433.500000", "433.400000"],
                                   "Duplex": ["", "", "", ""],
                                   "Offset": ["0.000000", "0.000000", "0.000000", "0.000000"],
                                   "Tone": ["", "", "", ""],
                                   "rToneFreq": ["88.5", "88.5", "88.5", "88.5"],
                                   "cToneFreq": ["88.5", "88.5", "88.5", "88.5"],
                                   "DtcsCode": ["023", "023", "023", "023"],
                                   "DtcsPolarity": ["NN", "NN", "NN", "NN"],
                                   "Mode": ["FM", "FM", "FM", "FM"],
                                   "TStep": ["5.00", "5.00", "5.00", "5.00"],
                                   "Skip": ["", "", "", ""],
                                   "Comment": ["2m-es hivofrekvencia", "2m-es SSTV hivofrekvencia",
                                               "70cm-es hivofrekvencia", "70cm-es SSTV hivofrekvencia"],
                                   "URCALL": ["", "", "", ""],
                                   "RPT1CALL": ["", "", "", ""],
                                   "RPT2CALL": ["", "", "", ""],
                                   "DVCODE": ["", "", "", ""]})
    repeater_dataframe = call_dataframe.append(get_repeaters('http://ha2to.orbel.hu/content/repeaters/hu/index.html'),
                                               ignore_index=True)
    repeater_dataframe.index.name = "Location"
    repeater_dataframe = repeater_dataframe.rename(
        dict(zip(repeater_dataframe.index, range(1, repeater_dataframe.shape[0] + 1))))
    repeater_dataframe.to_csv(repeatercsv)
    # HTTP Header
    print("Content-Type:application/octet-stream; name = \"repeaters.csv\"\r\n")
    print("Content-Disposition: attachment; filename = \"repeaters.csv\"\r\n\n")
    repeatercsv.seek(0)
    print(repeatercsv.read())
    repeatercsv.close()

